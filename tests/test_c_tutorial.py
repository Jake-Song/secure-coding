"""Compile the C lessons and check observable behavior in temporary directories."""

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SOURCE_DIR = Path(__file__).resolve().parents[1] / "examples" / "c_tutorial"
COMPILER = shutil.which("cc")


@unittest.skipUnless(COMPILER, "C compiler (cc) is not installed")
class CTutorialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.build_directory = tempfile.TemporaryDirectory(prefix="c-tutorial-build-")
        cls.addClassCleanup(cls.build_directory.cleanup)
        cls.bin_dir = Path(cls.build_directory.name)
        for source in sorted(SOURCE_DIR.glob("*.c")):
            subprocess.run(
                [COMPILER, "-std=c17", "-Wall", "-Wextra", "-Wpedantic",
                 "-Wconversion", "-Wshadow", "-Werror", str(source),
                 "-o", str(cls.bin_dir / source.stem)],
                check=True, capture_output=True, text=True, timeout=30,
            )

    def run_program(self, name, *arguments, input_text=None):
        return subprocess.run(
            [str(self.bin_dir / name), *map(str, arguments)],
            input=input_text, capture_output=True, text=True, timeout=5,
        )

    def test_introductory_lessons(self):
        expected = {
            "01_hello": "Hello, C!\n",
            "02_basics": (
                "score=85 ratio=0.85 grade=B passed=1\n"
                "integer division=2 real division=2.50\n"
                "pass\nsum 1..5=15\ngood\n"
            ),
            "03_functions_arrays": "count=3 total=240 average=80.00\n",
            "06_heap": "1 2 3 4 5\n",
        }
        for name, output in expected.items():
            with self.subTest(name=name):
                result = self.run_program(name)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, output)

    def test_pointers_and_structs(self):
        result = self.run_program("04_pointers_strings")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("score=81 pointed value=81\n", result.stdout)
        self.assertIn("name=Mlice bytes=6 length=5\nhello\n", result.stdout)
        result = self.run_program("05_structs")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith("Alice: 85 (pass)\n"))
        self.assertRegex(result.stdout, r"struct bytes=\d+\n")

    def test_valid_line_input(self):
        for text, score in [("0\n", 0), ("100\n", 100), ("  +85 \t\n", 85)]:
            with self.subTest(text=text):
                result = self.run_program("07_input", input_text=text)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(f"accepted={score}\n", result.stdout)

    def test_invalid_line_input(self):
        inputs = ["", "\n", "85", "-1\n", "101\n", "85abc\n", "85 90\n",
                  "3.14\n", "9" * 50 + "\n", "1" * 80 + "\n", "85\0x\n"]
        for text in inputs:
            with self.subTest(text=text):
                result = self.run_program("07_input", input_text=text)
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(result.stderr)
                self.assertNotIn("accepted=", result.stdout)

    def test_line_length_boundary(self):
        for length, accepted in [(62, True), (63, False)]:
            with self.subTest(length=length):
                text = " " * (length - 2) + "85\n"
                result = self.run_program("07_input", input_text=text)
                self.assertEqual(result.returncode == 0, accepted, result.stderr)

    def test_report_contents_and_count_boundaries(self):
        cases = [(["70", "80", "90"], "3,240,80.00"),
                 (["0"], "1,0,0.00"), (["100"] * 100, "100,10000,100.00")]
        with tempfile.TemporaryDirectory(prefix="c-tutorial-reports-") as directory:
            for index, (scores, row) in enumerate(cases):
                with self.subTest(count=len(scores)):
                    report = Path(directory) / f"report {index}.csv"
                    result = self.run_program("08_score_report", report, *scores)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(report.read_text(), f"count,total,average\n{row}\n")

    def test_invalid_scores_do_not_create_file(self):
        cases = [[], ["100"] * 101, [""], ["-1"], ["101"], ["+85"],
                 [" 85"], ["85 "], ["3.14"], ["85x"], ["9" * 100], ["70", "bad"]]
        with tempfile.TemporaryDirectory(prefix="c-tutorial-invalid-") as directory:
            report = Path(directory) / "invalid.csv"
            for scores in cases:
                with self.subTest(scores=scores):
                    result = self.run_program("08_score_report", report, *scores)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertTrue(result.stderr)
                    self.assertFalse(report.exists())

    def test_existing_report_is_preserved(self):
        with tempfile.TemporaryDirectory(prefix="c-tutorial-existing-") as directory:
            report = Path(directory) / "existing.csv"
            report.write_text("keep this content\n")
            result = self.run_program("08_score_report", report, "85")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(report.read_text(), "keep this content\n")

    def test_missing_output_directory(self):
        with tempfile.TemporaryDirectory(prefix="c-tutorial-missing-") as directory:
            report = Path(directory) / "missing" / "scores.csv"
            result = self.run_program("08_score_report", report, "85")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("cannot create report", result.stderr)
            self.assertFalse(report.exists())


if __name__ == "__main__":
    unittest.main()
