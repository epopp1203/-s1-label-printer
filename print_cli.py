import argparse
import asyncio
import re
import sys

from bleak import BleakError

from printer import PRINTER_NAME, print_label

VALUE_PATTERN = re.compile(r"^[A-Za-z0-9]{1,32}$")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Print a Code 128 label on an iDPRT S1 over Bluetooth LE."
    )
    parser.add_argument("value", help="1 to 32 ASCII letters or digits")
    args = parser.parse_args()

    if not VALUE_PATTERN.fullmatch(args.value):
        parser.error("label value must be 1 to 32 ASCII letters or digits")
    if not PRINTER_NAME:
        parser.error("set PRINTER_NAME to the printer's advertised BLE name")

    try:
        asyncio.run(print_label(args.value))
    except (BleakError, OSError, RuntimeError, ValueError) as exc:
        print(f"Print failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
