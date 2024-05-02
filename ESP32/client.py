#client.py

import sys

sys.path.append("")

from micropython import const

import uasyncio as asyncio
import aioble
import bluetooth

import random
import struct

# org.bluetooth.service.environmental_messaging
SERVICE_UUID = bluetooth.UUID(0x181A)
# org.bluetooth.characteristic
CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)


async def find_device():
    # Scan for 5 seconds, in active mode, with very low interval/window (to
    # maximise detection rate).
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            # See if it matches our name and the environmental messaging service.
            if result.name() == "Esp32-Test" and SERVICE_UUID in result.services():
                return result.device
    return None

def _decode_decimal(data):
    return struct.unpack("<h", data)[0] / 100

async def main():
    device = await find_device()
    if not device:
        print("Device not found")
        return

    try:
        print("Connecting to", device)
        connection = await device.connect()
    except asyncio.TimeoutError:
        print("Timeout during connection")
        return

    async with connection:
        try:
            service = await connection.service(SERVICE_UUID)
            characteristic = await service.characteristic(CHARACTERISTIC_UUID)
        except asyncio.TimeoutError:
            print("Timeout discovering services/characteristics")
            return

        while True:
            c = _decode_decimal(await characteristic.read())
            print("Number: {:.2f}".format(c))
            await asyncio.sleep_ms(1000)


asyncio.run(main())