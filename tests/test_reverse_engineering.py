"""Build the x86-64 lessons and check behavior, boundaries, and ELF mappings."""

import itertools
import os
from pathlib import Path
import platform
import re
import shutil
import string
import subprocess
import tempfile
import unittest


SOURCE_DIR = Path(__file__).resolve().parents[1] / "examples" / "reverse_engineering"
SUPPORTED = platform.system() == "Linux" and platform.machine() == "x86_64"
TOOLS = all(shutil.which(name) for name in ("gcc", "make", "readelf"))


@unittest.skipUnless(SUPPORTED and TOOLS, "Requires Linux x86-64, GCC, make, readelf")
class ReverseEngineeringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory(prefix="reverse-engineering-")
        cls.addClassCleanup(cls.directory.cleanup)
        cls.build = Path(cls.directory.name)
        cls.environment = dict(os.environ, LC_ALL="C")
        subprocess.run(
            ["make", "-C", str(SOURCE_DIR), f"BUILD_DIR={cls.build}",
             "CFLAGS=-std=c17 -Wall -Wextra -Wpedantic -Wconversion -Wshadow "
             "-Werror -O0 -g -fno-omit-frame-pointer"],
            check=True, capture_output=True, text=True, timeout=60, env=cls.environment,
        )

    def command(self, *arguments):
        return subprocess.run(
            list(map(str, arguments)), capture_output=True, text=True,
            timeout=15, env=self.environment,
        )

    def run_program(self, name, *arguments):
        return self.command(self.build / name, *arguments)

    def elf(self, option, name):
        result = self.command("readelf", option, self.build / name)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_accept_and_exit_status(self):
        result = self.run_program("01_build", "trace")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout,
                         "count=3 total=240 grade=B\n"
                         "text=trace bytes=6 length=5\n"
                         "signed_less=1 unsigned_less=0\naccepted\n")

    def test_rejected_content_and_length_boundaries(self):
        for value in ("", "trac", "traceX", "wrong", "Trace", "트레이스", "x" * 4096):
            with self.subTest(value=value[:20]):
                result = self.run_program("01_build", value)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertTrue(result.stdout.endswith("\nrejected\n"))
                self.assertEqual(result.stderr, "")

    def test_usage_is_distinct_from_rejection(self):
        for arguments in ((), ("trace", "extra")):
            with self.subTest(arguments=arguments):
                result = self.run_program("01_build", *arguments)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertIn("usage:", result.stderr)

    def test_staged_object_can_be_linked(self):
        for suffix in ("i", "s", "o"):
            self.assertGreater((self.build / f"01_build.{suffix}").stat().st_size, 0)
        self.assertRegex(self.elf("-hW", "01_build.o"), r"Type:\s+REL\b")
        linked = self.build / "01_linked"
        result = self.command("gcc", "-pie", self.build / "01_build.o", "-o", linked)
        self.assertEqual(result.returncode, 0, result.stderr)
        for argument in ("trace", "wrong", ""):
            expected = self.run_program("01_build", argument)
            actual = self.command(linked, argument)
            self.assertEqual((actual.returncode, actual.stdout, actual.stderr),
                             (expected.returncode, expected.stdout, expected.stderr))

    def test_memory_values_and_layout(self):
        result = self.run_program("02_memory")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith(
            "array_bytes=12 pointer_bytes=8 literal_length=5\n"
            "record_bytes=12 offsets=0,4,8\n"
            "word=12345678 middle=25 record=R/3/5\n"
            "heap=20,50,60 literal=trace global=7\n"))
        self.assertRegex(result.stdout, r"addresses: word=0x[0-9a-f]+ .*global=0x[0-9a-f]+")
        self.assertTrue(result.stdout.endswith("heap released\n"))

    def test_flow_and_register_results(self):
        result = self.run_program("03_flow")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout,
                         "add_bias(4,5)=12\n"
                         "signed(-1)=1 unsigned(UINT_MAX)=0\n"
                         "sum_to(0)=0 sum_to(1)=0 sum_to(4)=6\n"
                         "mix_bits(0x23)=242\n")
        result = self.run_program("03_registers")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "register_demo=305419903\n")

    def test_comparison_and_loop_boundaries(self):
        # Exercise exported lesson functions without relying on printf argument order.
        harness = self.build / "boundaries.c"
        harness.write_text(
            "#include <stdint.h>\n"
            "int choose_signed(int);\n"
            "int choose_unsigned(unsigned int);\n"
            "unsigned int sum_to(unsigned int);\n"
            "uint32_t mix_bits(uint32_t);\n"
            "int main(void) {\n"
            "  int inputs[] = {-1, 9, 10, 11};\n"
            "  int signed_expected[] = {1, 1, 0, 0};\n"
            "  int unsigned_expected[] = {0, 1, 0, 0};\n"
            "  for (int i = 0; i < 4; ++i) {\n"
            "    if (choose_signed(inputs[i]) != signed_expected[i]) return 1;\n"
            "    if (choose_unsigned((unsigned int)inputs[i]) != unsigned_expected[i]) return 2;\n"
            "  }\n"
            "  if (sum_to(0) != 0 || sum_to(1) != 0 || sum_to(4) != 6 || sum_to(5) != 10) return 3;\n"
            "  if (mix_bits(0) != 180 || mix_bits(0x23) != 242 || mix_bits(0xff) != 335) return 4;\n"
            "  return 0;\n"
            "}\n", encoding="utf-8",
        )
        object_file = self.build / "flow_functions.o"
        compiled = self.command("gcc", "-std=c17", "-Wall", "-Wextra", "-Werror",
                                "-Dmain=flow_lesson_main", "-c", SOURCE_DIR / "03_flow.c",
                                "-o", object_file)
        self.assertEqual(compiled.returncode, 0, compiled.stderr)
        binary = self.build / "boundaries"
        linked = self.command("gcc", "-std=c17", "-Wall", "-Wextra", "-Werror",
                              harness, object_file, "-o", binary)
        self.assertEqual(linked.returncode, 0, linked.stderr)
        result = self.command(binary)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_pie_nonpie_and_section_file_mapping(self):
        for name, elf_type in (("04_elf", "DYN"), ("04_elf_nopie", "EXEC")):
            with self.subTest(name=name):
                result = self.run_program(name)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "elf-lab result=35 zeroed[0]=28\n")
                self.assertRegex(self.elf("-hW", name), rf"Type:\s+{elf_type}\b")
                sections = self.elf("-SW", name)
                self.assertRegex(sections, r"\.bss\s+NOBITS\b")
                symbols = self.elf("-sW", name)
                message = re.search(r"^\s*\d+:\s+([0-9a-f]+)\s+8\s+OBJECT\s+GLOBAL\s+DEFAULT\s+\d+\s+message$",
                                    symbols, re.MULTILINE)
                self.assertIsNotNone(message)
                address = int(message.group(1), 16)
                offset = None
                for line in self.elf("-lW", name).splitlines():
                    fields = line.split()
                    if fields and fields[0] == "LOAD":
                        file_offset, virtual, _, file_size = map(lambda x: int(x, 16), fields[1:5])
                        if virtual <= address and address + 8 <= virtual + file_size:
                            offset = file_offset + address - virtual
                            break
                self.assertIsNotNone(offset, "message must be in a file-backed LOAD range")
                with (self.build / name).open("rb") as binary:
                    binary.seek(offset)
                    self.assertEqual(binary.read(8), b"elf-lab\0")

    def test_lookup_decisions_match_in_stripped_build(self):
        expected = {
            "guest": (1, "access denied\n"),
            "analyst": (0, "accepted level=3\n"),
            "retired": (1, "access denied\n"),
            "root": (0, "accepted level=9 admin\n"),
            "nobody": (1, "unknown account\n"),
            "": (1, "unknown account\n"),
            "Guest": (1, "unknown account\n"),
        }
        for name in ("05_lookup", "05_lookup_stripped"):
            for argument, (status, output) in expected.items():
                with self.subTest(binary=name, argument=argument):
                    result = self.run_program(name, argument)
                    self.assertEqual((result.returncode, result.stdout, result.stderr),
                                     (status, output, ""))
            usage = self.run_program(name)
            self.assertEqual((usage.returncode, usage.stdout), (2, ""))
            self.assertIn("usage:", usage.stderr)
        self.assertRegex(self.command("file", self.build / "05_lookup_stripped").stdout,
                         r"\bstripped\b")
        self.assertNotIn("find_account", self.elf("-sW", "05_lookup_stripped"))
        self.assertRegex(self.elf("-sW", "05_lookup"),
                         r"\b64 OBJECT\s+LOCAL\s+DEFAULT\s+\d+ accounts\b")

    def test_lookup_table_records_point_to_rodata_names(self):
        # Week 5: 16-byte records in .data.rel.ro hold relocated name pointers.
        name = "05_lookup_stripped"
        sections = {}
        for line in self.elf("-SW", name).splitlines():
            match = re.search(r"\]\s+(\S+)\s+\S+\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)", line)
            if match:
                sections[match.group(1)] = tuple(int(match.group(i), 16) for i in (2, 3, 4))
        table_address, table_offset, table_size = sections[".data.rel.ro"]
        rodata_address, rodata_offset, rodata_size = sections[".rodata"]
        self.assertEqual(table_size, 64)
        addends = {int(fields[0], 16): int(fields[-1], 16)
                   for fields in map(str.split, self.elf("-rW", name).splitlines())
                   if len(fields) >= 4 and "R_X86_64_RELATIVE" in fields}
        data = (self.build / name).read_bytes()
        records = []
        for index in range(4):
            start = table_offset + index * 16
            level = int.from_bytes(data[start + 8:start + 12], "little")
            flags = int.from_bytes(data[start + 12:start + 16], "little")
            pointer = addends[table_address + index * 16]
            self.assertTrue(rodata_address <= pointer < rodata_address + rodata_size)
            string_start = rodata_offset + pointer - rodata_address
            text = data[string_start:data.index(b"\0", string_start)].decode("ascii")
            records.append((text, level, flags))
        self.assertEqual(records, [("guest", 1, 1), ("analyst", 3, 1),
                                   ("retired", 5, 0), ("root", 9, 5)])

    def test_validate_stages_and_generated_keys(self):
        object_file = self.build / "validate_functions.o"
        compiled = self.command("gcc", "-std=c17", "-Wall", "-Wextra", "-Werror",
                                "-Dmain=validate_lesson_main", "-c",
                                SOURCE_DIR / "07_validate.c", "-o", object_file)
        self.assertEqual(compiled.returncode, 0, compiled.stderr)
        harness = self.build / "validate_harness.c"
        harness.write_text(
            "#include <stdio.h>\n"
            "int check_key(const char *input);\n"
            "int main(int argc, char **argv) {\n"
            "  for (int i = 1; i < argc; ++i) printf(\"%d\\n\", check_key(argv[i]));\n"
            "  return 0;\n"
            "}\n", encoding="utf-8")
        binary = self.build / "validate_harness"
        linked = self.command("gcc", "-std=c17", "-Wall", "-Wextra", "-Werror",
                              harness, object_file, "-o", binary)
        self.assertEqual(linked.returncode, 0, linked.stderr)
        stages = {
            "": 1, "lab7ope": 1, "lab7openx": 1, "lab7ope\u3131": 1,
            "Lab7open": 2, "lab7ope-": 2, "lab7 pen": 2, "wrong-ke": 2,
            "wrongkey": 3, "lab8open": 3, "mab7open": 3,
            "lab7opex": 4, "lab7oepn": 4, "lab7open": 0,
        }
        result = self.command(binary, *stages)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([int(line) for line in result.stdout.split()], list(stages.values()))

        # The week 7 generator method: decode the prefix, compute the last byte.
        allowed = (string.ascii_lowercase + string.digits).encode()
        prefix = bytes(((code - 3 * index) & 0xFF) ^ 0x5A
                       for index, code in enumerate(bytes.fromhex("363e3e76")))
        self.assertEqual(prefix, b"lab7")
        partial = sum(value * (index + 1) for index, value in enumerate(prefix))
        keys = []
        for a, b, c in itertools.product(allowed, repeat=3):
            rest = 3630 - partial - (a * 5 + b * 6 + c * 7)
            if rest % 8 == 0 and rest // 8 in allowed:
                keys.append(prefix + bytes([a, b, c, rest // 8]))
        self.assertEqual(len(keys), 1689)
        self.assertIn(b"lab7open", keys)
        for key in keys[::169] + keys[-1:]:
            for name in ("07_validate", "07_validate_stripped"):
                with self.subTest(key=key, binary=name):
                    accepted = self.run_program(name, key.decode())
                    self.assertEqual((accepted.returncode, accepted.stdout), (0, "accepted\n"))
        for name in ("07_validate", "07_validate_stripped"):
            rejected = self.run_program(name, "lab7opex")
            self.assertEqual((rejected.returncode, rejected.stdout), (1, "rejected\n"))
            usage = self.run_program(name)
            self.assertEqual((usage.returncode, usage.stdout), (2, ""))

    def test_transform_reimplementation_comparison(self):
        reference = self.build / "transform_reference.py"
        reference.write_text(TRANSFORM_REFERENCE, encoding="utf-8")
        floor = self.build / "transform_floor.py"
        floor.write_text(TRANSFORM_REFERENCE.replace("int(signed / 4)", "signed // 4"),
                         encoding="utf-8")
        unsigned = self.build / "transform_unsigned.py"
        unsigned.write_text(TRANSFORM_REFERENCE.replace(
            "value - 256 if value >= 0x80 else value", "value"), encoding="utf-8")
        compare = SOURCE_DIR / "compare_transform.py"
        result = self.command("python3", "-I", compare, self.build / "08_transform", reference)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("21/21 matched", result.stdout)
        for wrong in (floor, unsigned):
            with self.subTest(wrong=wrong.name):
                result = self.command("python3", "-I", compare, self.build / "08_transform", wrong)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("DIFF", result.stdout)

        def run_bytes(data):
            return subprocess.run([self.build / "08_transform"], input=data,
                                  capture_output=True, timeout=15, check=False)

        edge = run_bytes(bytes([0x00, 0x7F, 0x80, 0xFF]))
        self.assertEqual(edge.stdout, b"length=4\nout=a7372cd7\nacc=008448b3\n")
        empty = run_bytes(b"")
        self.assertEqual(empty.stdout, b"length=0\nout=\nacc=00001234\n")
        self.assertEqual(run_bytes(bytes(64)).returncode, 0)
        too_long = run_bytes(bytes(65))
        self.assertEqual((too_long.returncode, too_long.stdout), (2, b""))
        self.assertIn(b"input too long", too_long.stderr)


TRANSFORM_REFERENCE = """\
def transform(data):
    key, accumulator, output = 0xA7, 0x1234, bytearray()
    for index, value in enumerate(data):
        output.append(((value ^ key) + index * 7) & 0xFF)
        key = ((key << 1) | (key >> 7)) & 0xFF
        signed = value - 256 if value >= 0x80 else value
        accumulator = (accumulator * 31 + int(signed / 4)) & 0xFFFFFFFF
    return bytes(output), accumulator
"""


if __name__ == "__main__":
    unittest.main()
