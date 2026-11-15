"""Build the x86-64 lessons and check behavior, boundaries, and ELF mappings."""

import os
from pathlib import Path
import platform
import re
import shutil
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


if __name__ == "__main__":
    unittest.main()
