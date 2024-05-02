#server.py

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
# org.bluetooth.characteristic.message
CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)
# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC = const(768)

# How frequently to send advertising beacons.
_ADV_INTERVAL_MS = 250_000


# Register GATT server.
service = aioble.Service(SERVICE_UUID)
characteristic = aioble.Characteristic(
    service, CHARACTERISTIC_UUID, read=True, notify=True
)
aioble.register_services(service)

def _encode_decimal(c):
    return struct.pack("<h", int(c * 100))

# This is the message sent to the other ESP32S3
async def sending_task():
    t = 24.5
    while True:
        characteristic.write(_encode_decimal(t))
        t += random.uniform(-0.5, 0.5)
        print(t)
        await asyncio.sleep_ms(1000)


# Serially wait for connections. Don't advertise while a central is
# connected.
async def peripheral_task():
    while True:
        async with await aioble.advertise(
            _ADV_INTERVAL_MS,
            name="Esp32-Test",
            services=[SERVICE_UUID],
            appearance=_ADV_APPEARANCE_GENERIC,
        ) as connection:
            print("Connection from", connection.device)
            await connection.disconnected()


# Run both tasks.
async def main():
    t1 = asyncio.create_task(sending_task())
    t2 = asyncio.create_task(peripheral_task())
    await asyncio.gather(t1, t2)


asyncio.run(main())