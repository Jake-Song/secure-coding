import json
from pathlib import Path
import tempfile
import unittest

from examples.network_security import detection, policy


class PolicyTests(unittest.TestCase):
    def test_allowed_application_paths(self):
        for flow in (policy.Flow("192.0.2.25", "198.51.100.10", "tcp", 443),
                     policy.Flow("198.51.100.10", "203.0.113.20", "tcp", 5432)):
            self.assertTrue(policy.allowed(flow))

    def test_default_deny_wrong_protocol_port_destination_and_reverse(self):
        for flow in (policy.Flow("192.0.2.25", "203.0.113.20", "tcp", 5432),
                     policy.Flow("192.0.2.25", "198.51.100.10", "udp", 443),
                     policy.Flow("192.0.2.25", "198.51.100.10", "tcp", 22),
                     policy.Flow("192.0.2.25", "198.51.100.11", "tcp", 443),
                     policy.Flow("203.0.113.20", "198.51.100.10", "tcp", 5432)):
            self.assertFalse(policy.allowed(flow))

    def test_invalid_ipv4_ipv6_and_ports_fail_closed(self):
        for source in ("not-an-ip", "::1", "192.0.2.256"):
            self.assertFalse(policy.allowed(policy.Flow(source, "198.51.100.10", "tcp", 443)))
        for port in (0, 65536, True, "443"):
            self.assertFalse(policy.allowed(policy.Flow("192.0.2.1", "198.51.100.10", "tcp", port)))


class DetectionTests(unittest.TestCase):
    def event(self, stamp, port=22, kind="deny", source="192.0.2.10", destination="198.51.100.10"):
        return {"time": stamp, "source": source, "destination": destination,
                "port": port, "event": kind}

    def test_sample_has_exactly_two_expected_alerts(self):
        alerts = detection.detect(detection.load_events(detection.SAMPLE))
        self.assertEqual([(a["time"], a["kind"]) for a in alerts],
                         [(4, "many_denied_ports"), (7, "repeated_auth_failures")])

    def test_repeated_same_port_and_allowed_traffic_do_not_trigger_scan_rule(self):
        events = [self.event(i) for i in range(8)]
        self.assertEqual(detection.detect(events), [])
        self.assertEqual(detection.detect([self.event(i, 20 + i, "allow") for i in range(8)]), [])

    def test_time_window_and_host_pair_separation(self):
        self.assertEqual(detection.detect([self.event(i * 20, 20 + i) for i in range(4)]), [])
        self.assertEqual(detection.detect([self.event(i, 20 + i, source=f"192.0.2.{i + 1}")
                                           for i in range(4)]), [])
        self.assertEqual(detection.detect([self.event(i, 20 + i, destination=f"198.51.100.{i + 1}")
                                           for i in range(4)]), [])

    def test_exact_window_boundary_is_included_and_alert_rearms(self):
        events = [self.event(0, 20), self.event(1, 21), self.event(2, 22), self.event(10, 23),
                  self.event(11, 24), self.event(30, 30), self.event(31, 31),
                  self.event(32, 32), self.event(33, 33)]
        self.assertEqual([a["time"] for a in detection.detect(events)], [10, 33])

    def test_invalid_schema_time_order_and_log_limits(self):
        bad_events = [{}, {**self.event(0), "time": float("nan")},
                      {**self.event(0), "time": 10**500},
                      {**self.event(0), "source": []}, self.event(0, True)]
        for event in bad_events:
            with self.subTest(event=event), self.assertRaises(ValueError):
                detection.detect([event])
        with self.assertRaises(ValueError):
            detection.detect([self.event(2), self.event(1)])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            for text in ("{" + "x" * 4096, json.dumps(self.event(2)) + "\n" + json.dumps(self.event(1)),
                         (json.dumps(self.event(0)) + "\n") * (detection.MAX_EVENTS + 1)):
                path.write_text(text)
                with self.assertRaises(ValueError):
                    detection.load_events(path)


if __name__ == "__main__":
    unittest.main()
