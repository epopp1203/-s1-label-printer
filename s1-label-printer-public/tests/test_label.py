import unittest

from PIL import Image, ImageChops

from label import PRINT_WIDTH, TEAR_OFF_PADDING, make_label, raster_command


class LabelTests(unittest.TestCase):
    def test_label_uses_printer_width_and_contains_black_pixels(self):
        image = make_label("SAMPLE123")
        self.assertEqual(image.size[0], PRINT_WIDTH)
        self.assertGreater(image.size[1], 250)
        self.assertEqual(image.mode, "1")
        self.assertLess(image.convert("L").getextrema()[0], 255)
        barcode_region = image.crop((0, 0, image.width, 231)).convert("L")
        ink = ImageChops.difference(
            barcode_region, Image.new("L", barcode_region.size, 255)
        )
        left, top, right, bottom = ink.getbbox()
        self.assertGreaterEqual(right - left, 320)
        self.assertGreaterEqual(bottom - top, 200)

    def test_short_barcode_is_widened_and_label_has_blank_tear_off_tail(self):
        self.assertEqual(TEAR_OFF_PADDING, 48)
        image = make_label("DEMO99")
        barcode_region = image.crop((0, 0, image.width, 231)).convert("L")
        ink = ImageChops.difference(
            barcode_region, Image.new("L", barcode_region.size, 255)
        )
        left, _, right, _ = ink.getbbox()
        self.assertGreaterEqual(right - left, 320)
        tail = image.crop(
            (0, image.height - TEAR_OFF_PADDING, image.width, image.height)
        )
        self.assertEqual(tail.convert("L").getextrema(), (255, 255))

    def test_raster_header_encodes_width_and_height(self):
        image = make_label("SAMPLE42")
        command = raster_command(image)
        self.assertEqual(command[:8], bytes((0x1D, 0x76, 0x30, 0, 48, 0, image.height & 255, image.height >> 8)))
        self.assertEqual(len(command), 8 + image.height * (PRINT_WIDTH // 8))

    def test_lowercase_value_prints_identically_to_uppercase(self):
        self.assertEqual(
            raster_command(make_label("sample42")),
            raster_command(make_label("SAMPLE42")),
        )

    def test_long_barcode_is_rejected_instead_of_cropped(self):
        with self.assertRaisesRegex(ValueError, "too wide"):
            make_label("A" * 32)


if __name__ == "__main__":
    unittest.main()
