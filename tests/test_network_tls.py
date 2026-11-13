from pathlib import Path
import ssl
import tempfile
import unittest

from examples.network_security import tls


class TLSSocketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="network-tls-test-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.directory = tls.create_certificates(cls.temporary.name)
        cls.server = tls.server_context(cls.directory)

    def test_trusted_ca_correct_hostname_and_binary_round_trip(self):
        client = tls.client_context(self.directory / "ca.crt")
        self.assertTrue(client.check_hostname)
        self.assertEqual(client.verify_mode, ssl.CERT_REQUIRED)
        self.assertIsNone(client.keylog_filename)
        payload = bytes(range(256)) * 16
        result, version = tls.exchange(self.server, client, payload=payload)
        self.assertEqual(result, payload)
        self.assertIn(version, ("TLSv1.2", "TLSv1.3"))

    def test_untrusted_ca_is_rejected(self):
        with self.assertRaises(ssl.SSLCertVerificationError):
            tls.exchange(self.server, tls.client_context())

    def test_wrong_hostname_is_rejected_even_with_trusted_ca(self):
        with self.assertRaises(ssl.SSLCertVerificationError):
            tls.exchange(self.server, tls.client_context(self.directory / "ca.crt"), "wrong.test")

    def test_tls12_supported_and_empty_application_frame(self):
        client = tls.client_context(self.directory / "ca.crt")
        client.maximum_version = ssl.TLSVersion.TLSv1_2
        result, version = tls.exchange(self.server, client, payload=b"")
        self.assertEqual((result, version), (b"", "TLSv1.2"))

    def test_certificate_generation_does_not_overwrite_existing_directory(self):
        with self.assertRaises(FileExistsError):
            tls.create_certificates(self.temporary.name)
        for name in ("ca.key", "server.key"):
            self.assertEqual((Path(self.directory) / name).stat().st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()
