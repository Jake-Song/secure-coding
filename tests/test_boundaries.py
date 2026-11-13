from pathlib import Path
import tempfile
import unittest

from examples.boundaries import PUBLIC_URL, command_demo, fetch_fixture, read_file, save_text_upload


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "public").mkdir()
        (self.root / "public/hello.txt").write_text("안녕", encoding="utf-8")
        (self.root / "secret.txt").write_text("fake secret", encoding="utf-8")

    def test_shell_interprets_separator_but_argument_list_does_not(self):
        vulnerable, safe = command_demo()
        self.assertEqual(vulnerable, "helloLAB_MARKER")
        self.assertEqual(safe, "hello; printf LAB_MARKER")

    def test_path_traversal_and_normal_file(self):
        self.assertEqual(read_file(self.root, "../secret.txt", safe=False), "fake secret")
        with self.assertRaises(PermissionError):
            read_file(self.root, "../secret.txt", safe=True)
        self.assertEqual(read_file(self.root, "hello.txt", safe=True), "안녕")

    def test_fixture_guard_and_symlink(self):
        for safe in (False, True):
            with self.assertRaises(PermissionError):
                read_file(self.root, "../../outside", safe=safe)
        (self.root / "public/link.txt").symlink_to(self.root / "secret.txt")
        with self.assertRaises(PermissionError):
            read_file(self.root, "link.txt", safe=True)

    def test_upload_generates_name_and_preserves_content(self):
        directory = self.root / "uploads"
        first = save_text_upload(directory, "../../memo.txt", "메모".encode())
        second = save_text_upload(directory, "../../memo.txt", b"second")
        self.assertEqual(first.parent, directory)
        self.assertNotEqual(first, second)
        self.assertEqual(first.read_text(), "메모")

    def test_upload_rejects_type_size_and_bad_encoding(self):
        for name, data in (("page.html", b"hello"), ("long.txt", b"x" * 1025),
                           ("binary.txt", b"\xff")):
            with self.assertRaises(ValueError):
                save_text_upload(self.root / "uploads", name, data)

    def test_ssrf_fixture_blocks_internal_destination(self):
        self.assertEqual(fetch_fixture("http://internal.lab/config", safe=False), "FAKE_INTERNAL_SECRET")
        with self.assertRaises(PermissionError):
            fetch_fixture("http://internal.lab/config", safe=True)
        self.assertEqual(fetch_fixture(PUBLIC_URL, safe=True), "public catalog")


if __name__ == "__main__":
    unittest.main()
