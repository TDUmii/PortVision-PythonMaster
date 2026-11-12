"""Kiem thu nhanh, khong can tai them pytest."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import core


class TestCore(unittest.TestCase):
    def test_demo_data(self):
        data = core.du_lieu_demo()
        self.assertGreaterEqual(len(data), 10)
        self.assertTrue(all("local_port" in item and "status" in item for item in data))

    def test_compare_new_removed(self):
        sample = core.du_lieu_demo()
        new, removed, changed = core.so_sanh(sample[:2], sample[1:3])
        self.assertEqual((len(new), len(removed), len(changed)), (1, 1, 0))

    def test_compare_status(self):
        old = core.du_lieu_demo()[:1]
        new = [dict(old[0], status="CLOSE_WAIT")]
        a, b, change = core.so_sanh(old, new)
        self.assertEqual((len(a), len(b), len(change)), (0, 0, 1))

    def test_snapshot_and_csv(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(core, "DATA_DIR", Path(temp)):
                data = core.du_lieu_demo()
                saved = core.luu_snapshot(data, demo=True)
                self.assertTrue(saved.exists())
                self.assertEqual(core.doc_snapshot(saved)["connections"], data)
                self.assertEqual(len(core.danh_sach_snapshot()), 1)
                csv_file = Path(temp) / "test.csv"
                core.xuat_csv(data, csv_file)
                self.assertIn("process", csv_file.read_text(encoding="utf-8-sig"))

    def test_live_fields(self):
        data = core.quet_port()
        if data:
            self.assertEqual(set(data[0]), {
                "process", "pid", "protocol", "local_ip", "local_port",
                "remote_ip", "remote_port", "status",
            })


if __name__ == "__main__":
    unittest.main()
