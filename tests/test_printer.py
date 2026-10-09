import unittest
from unittest.mock import patch

from printer import print_label


class PrinterTests(unittest.IsolatedAsyncioTestCase):
    async def test_too_wide_label_is_rejected_before_bluetooth_scan(self):
        with patch("printer.BleakScanner.find_device_by_name") as find_device:
            with self.assertRaisesRegex(ValueError, "too wide"):
                await print_label("A" * 32)
        find_device.assert_not_awaited()

    async def test_missing_printer_name_is_reported_before_bluetooth_scan(self):
        with patch("printer.BleakScanner.find_device_by_name") as find_device:
            with self.assertRaisesRegex(RuntimeError, "Set PRINTER_NAME"):
                await print_label("ABC123", printer_name="")
        find_device.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
