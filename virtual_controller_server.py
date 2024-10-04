import pyvjoy
import asyncio
import json
import websockets


def to_axis_value(float_value):
    return int(float_value * 16384 + 16384)


async def handle_client(websocket, path):
    joystick = pyvjoy.VJoyDevice(1)
    joystick.set_axis(pyvjoy.HID_USAGE_X, 16384)  # Center position for X axis
    joystick.set_axis(pyvjoy.HID_USAGE_Y, 16384)  # Center position for Y axis

    async for message in websocket:
        controller_input = json.loads(message)
        x_value = to_axis_value(controller_input["axisX"])
        y_value = to_axis_value(controller_input["axisY"])
        joystick.set_axis(pyvjoy.HID_USAGE_X, x_value)
        joystick.set_axis(pyvjoy.HID_USAGE_Y, y_value)
        joystick.set_button(1, controller_input["btnX"])
        joystick.set_button(6, controller_input["btnR1"])


async def main():
    async with websockets.serve(handle_client, "localhost", 1337):
        print("WebSocket server started on ws://localhost:1337")
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())
