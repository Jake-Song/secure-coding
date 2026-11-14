"""Compile and exercise the standalone C++ and Rust tutorial programs."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
CXX = shutil.which(os.environ.get("CXX", "c++"))
RUSTC = shutil.which(os.environ.get("RUSTC", "rustc"))


class TutorialBehavior:
    """Behavior shared by both languages; this mixin is not a test case."""

    def run_program(self, name, *arguments, input_text=None):
        return subprocess.run(
            [str(self.bin_dir / name), *map(str, arguments)],
            input=input_text, capture_output=True, text=True, timeout=5,
        )

    def test_lesson_outputs(self):
        for name, output in self.expected_outputs.items():
            with self.subTest(name=name):
                result = self.run_program(name)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, output)

    def test_valid_line_input(self):
        for text, score in [("0\n", 0), ("100\n", 100), ("85\n", 85),
                            ("001\n", 1), ("85", 85)]:
            with self.subTest(text=text):
                result = self.run_program("07_input", input_text=text)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(f"accepted={score}\n", result.stdout)

    def test_invalid_line_input(self):
        inputs = ["", "\n", "-1\n", "-0\n", "+85\n", " 85\n", "85 \n",
                  "101\n", "3.14\n", "85abc\n", "85 90\n", "85\0x\n",
                  "８５\n", "9" * 50 + "\n", "1" * 80 + "\n"]
        for text in inputs:
            with self.subTest(text=text):
                result = self.run_program("07_input", input_text=text)
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(result.stderr)
                self.assertNotIn("accepted=", result.stdout)

    def test_line_length_boundary(self):
        for length, accepted in [(62, True), (63, False)]:
            with self.subTest(length=length):
                text = "0" * (length - 2) + "85\n"
                result = self.run_program("07_input", input_text=text)
                self.assertEqual(result.returncode == 0, accepted, result.stderr)

    def test_report_contents_and_count_boundaries(self):
        cases = [(["70", "80", "90"], "3,240,80.00"),
                 (["0"], "1,0,0.00"), (["001"], "1,1,1.00"),
                 (["100"] * 100, "100,10000,100.00")]
        with tempfile.TemporaryDirectory(prefix="tutorial-reports-") as directory:
            for index, (scores, row) in enumerate(cases):
                with self.subTest(count=len(scores)):
                    report = Path(directory) / f"report {index}.csv"
                    result = self.run_program("08_score_report", report, *scores)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout, "report saved\n")
                    self.assertEqual(report.read_text(), f"count,total,average\n{row}\n")

    def test_invalid_scores_do_not_create_file(self):
        cases = [[], ["100"] * 101, [""], ["-1"], ["101"], ["+85"],
                 [" 85"], ["85 "], ["3.14"], ["85x"], ["9" * 100],
                 ["70", "bad"], ["８５"]]
        with tempfile.TemporaryDirectory(prefix="tutorial-invalid-") as directory:
            report = Path(directory) / "invalid.csv"
            for scores in cases:
                with self.subTest(scores=scores):
                    result = self.run_program("08_score_report", report, *scores)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertTrue(result.stderr)
                    self.assertFalse(report.exists())

    def test_existing_report_is_preserved(self):
        with tempfile.TemporaryDirectory(prefix="tutorial-existing-") as directory:
            report = Path(directory) / "existing.csv"
            report.write_text("keep this content\n")
            result = self.run_program("08_score_report", report, "85")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(report.read_text(), "keep this content\n")

    def test_missing_output_directory(self):
        with tempfile.TemporaryDirectory(prefix="tutorial-missing-") as directory:
            report = Path(directory) / "missing" / "scores.csv"
            result = self.run_program("08_score_report", report, "85")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("cannot create report", result.stderr)
            self.assertFalse(report.exists())

    def test_missing_arguments(self):
        result = self.run_program("08_score_report")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("usage:", result.stderr)


@unittest.skipUnless(CXX, "C++ compiler is not installed")
class CppTutorialTests(TutorialBehavior, unittest.TestCase):
    expected_outputs = {
        "01_hello": "Hello, C++!\n",
        "02_basics": "passed=true\nsum 1..5=15\nscore=86 pass\n",
        "03_strings_vectors": "name=Alice Lee bytes=9\ncount=4 average=85.00\nfirst=70\n",
        "04_classes": "Alice: 85 (pass)\nrejected: score must be from 0 to 100\n",
        "05_algorithms": "50 60 80 90\npassed=3\n",
        "06_raii": "owned resource\nold owner empty=true\nnew owner=owned resource\n",
    }

    @classmethod
    def setUpClass(cls):
        directory = tempfile.TemporaryDirectory(prefix="cpp-tutorial-build-")
        cls.addClassCleanup(directory.cleanup)
        cls.bin_dir = Path(directory.name)
        sources = sorted((EXAMPLES / "cpp_tutorial").glob("[0-9][0-9]_*.cpp"))
        if len(sources) != 8:
            raise RuntimeError("expected eight C++ lessons")
        for source in sources:
            result = subprocess.run(
                [CXX, "-std=c++17", "-Wall", "-Wextra", "-Wpedantic", "-Wconversion",
                 "-Wshadow", "-Werror", str(source), "-o", str(cls.bin_dir / source.stem)],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode:
                raise RuntimeError(f"{source.name}: {result.stderr}")


@unittest.skipUnless(RUSTC, "Rust compiler is not installed or RUSTC is unset")
class RustTutorialTests(TutorialBehavior, unittest.TestCase):
    expected_outputs = {
        "01_hello": "Hello, Rust!\n",
        "02_basics": "passed=true\nsum 1..5=15\nscore=86 pass\nfirst=70 count=3\n",
        "03_ownership": "name=Alice bytes=5\nowner=Alice Lee copy=Alice Lee\nfirst word=Alice\n",
        "04_structs": "Alice: 85 (pass)\nrejected: score must be from 0 to 100\n",
        "05_collections": (
            "[50, 60, 80, 90]\ncount=4 total=280 passed=3\nfirst=50\nAlice=2\nBob=1\n"
        ),
        "06_errors": (
            "85: doubled=170\n101: rejected: score must be from 0 to 100\n"
            "bad: rejected: expected ASCII digits representing a score from 0 to 100\n"
        ),
    }

    @classmethod
    def setUpClass(cls):
        directory = tempfile.TemporaryDirectory(prefix="rust-tutorial-build-")
        cls.addClassCleanup(directory.cleanup)
        cls.bin_dir = Path(directory.name)
        sources = sorted((EXAMPLES / "rust_tutorial").glob("[0-9][0-9]_*.rs"))
        if len(sources) != 8:
            raise RuntimeError("expected eight Rust lessons")
        for source in sources:
            result = subprocess.run(
                [RUSTC, "--edition=2021", "-D", "warnings", "--crate-name",
                 f"lesson_{source.stem}", str(source), "-o", str(cls.bin_dir / source.stem)],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode:
                raise RuntimeError(f"{source.name}: {result.stderr}")

    def test_ownership_violations_are_compile_errors(self):
        cases = [
            ('let name = String::from("Alice"); let next = name; '
             'println!("{name} {next}");', "E0382"),
            ('let mut name = String::from("Alice"); let view = &name; '
             'name.push(\'!\'); println!("{view}");', "E0502"),
        ]
        for body, code in cases:
            with self.subTest(code=code):
                source = self.bin_dir / "invalid.rs"
                source.write_text(f"fn main() {{ {body} }}\n")
                result = subprocess.run(
                    [RUSTC, "--edition=2021", str(source), "-o", str(self.bin_dir / "invalid")],
                    capture_output=True, text=True, timeout=30,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(code, result.stderr)

    def test_crlf_line_input(self):
        result = self.run_program("07_input", input_text="85\r\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("accepted=85\n", result.stdout)


if __name__ == "__main__":
    unittest.main()
