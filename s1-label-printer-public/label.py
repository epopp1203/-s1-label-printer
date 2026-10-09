from io import BytesIO

from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont

PRINT_WIDTH = 384
MAX_BARCODE_WIDTH = 360
TEAR_OFF_PADDING = 48


def make_label(value: str) -> Image.Image:
    value = value.upper()
    barcode = None
    for module_width in (0.40, 0.30):
        output = BytesIO()
        Code128(value, writer=ImageWriter()).write(
            output,
            options={
                "dpi": 203,
                "module_width": module_width,
                "module_height": 27,
                "quiet_zone": 2,
                "write_text": False,
            },
        )
        candidate = Image.open(output).convert("1")
        if candidate.width <= MAX_BARCODE_WIDTH:
            barcode = candidate
            break

    if barcode is None:
        raise ValueError("This value makes a barcode too wide; use fewer characters")

    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22
    )
    while font.getlength(value) > MAX_BARCODE_WIDTH and font.size > 12:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font.size - 1
        )

    text_height = font.getbbox(value)[3] - font.getbbox(value)[1]
    image = Image.new(
        "1",
        (
            PRINT_WIDTH,
            barcode.height + text_height + 18 + TEAR_OFF_PADDING,
        ),
        1,
    )
    image.paste(barcode, ((PRINT_WIDTH - barcode.width) // 2, 0))
    draw = ImageDraw.Draw(image)
    draw.text(
        ((PRINT_WIDTH - font.getlength(value)) / 2, barcode.height + 7),
        value,
        font=font,
        fill=0,
    )
    return image


def raster_command(image: Image.Image) -> bytes:
    monochrome = image.convert("1")
    width, height = monochrome.size
    if width != PRINT_WIDTH:
        raise ValueError(f"Expected {PRINT_WIDTH}-dot image, got {width} dots")

    row_bytes = width // 8
    raster = bytearray()
    pixels = monochrome.load()
    for y in range(height):
        for byte_index in range(row_bytes):
            packed = 0
            for bit in range(8):
                if pixels[byte_index * 8 + bit, y] == 0:
                    packed |= 0x80 >> bit
            raster.append(packed)

    header = bytes(
        (
            0x1D,
            0x76,
            0x30,
            0x00,
            row_bytes & 0xFF,
            (row_bytes >> 8) & 0xFF,
            height & 0xFF,
            (height >> 8) & 0xFF,
        )
    )
    return header + raster
