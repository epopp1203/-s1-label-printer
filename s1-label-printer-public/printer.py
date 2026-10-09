import asyncio
import os

from bleak import BleakClient, BleakScanner

from label import make_label, raster_command

PRINTER_NAME = os.getenv("PRINTER_NAME", "").strip()
WRITE_UUID = "0000ff02-0000-1000-8000-00805f9b34fb"
ENABLE_COMMAND = bytes.fromhex("10 FF F1 03")
SET_DENSITY_COMMAND = bytes.fromhex("10 FF 10 00 01")
STOP_COMMAND = bytes.fromhex("10 FF F1 45")


async def send_chunks(client: BleakClient, payload: bytes) -> None:
    for offset in range(0, len(payload), 100):
        await client.write_gatt_char(
            WRITE_UUID, payload[offset : offset + 100], response=False
        )
        await asyncio.sleep(0.03)


async def print_label(value: str, printer_name: str | None = None) -> None:
    raster = raster_command(make_label(value))
    selected_name = PRINTER_NAME if printer_name is None else printer_name.strip()
    if not selected_name:
        raise RuntimeError("Set PRINTER_NAME to the printer's advertised BLE name")

    device = await BleakScanner.find_device_by_name(selected_name, timeout=10)
    if device is None:
        raise RuntimeError(f"Bluetooth printer {selected_name!r} was not found")

    async with BleakClient(device, timeout=20) as client:
        await client.write_gatt_char(WRITE_UUID, ENABLE_COMMAND, response=False)
        await asyncio.sleep(0.2)
        await client.write_gatt_char(WRITE_UUID, bytes(12), response=False)
        await asyncio.sleep(0.2)
        await client.write_gatt_char(WRITE_UUID, SET_DENSITY_COMMAND, response=False)
        await send_chunks(client, raster)
        await client.write_gatt_char(
            WRITE_UUID, bytes.fromhex("1B 4A 50"), response=False
        )
        await client.write_gatt_char(WRITE_UUID, STOP_COMMAND, response=False)
