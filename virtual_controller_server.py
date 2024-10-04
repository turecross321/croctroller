import pyvjoy
import asyncio
import json
import websockets

LISTEN_IP = "192.168.1.134"
PORT = 1337

joystick = pyvjoy.VJoyDevice(1)
joystick.set_axis(pyvjoy.HID_USAGE_X, 16384)  # Center position for X axis
joystick.set_axis(pyvjoy.HID_USAGE_Y, 16384)  # Center position for Y axis

move_direction = 1
move_speed = 0.0
jump = False


def to_axis_value(float_value):
    return int(float_value * 16384 + 16384)


def update_controller():
    global joystick, move_direction, move_speed, jump
    joystick.set_axis(pyvjoy.HID_USAGE_X, to_axis_value(move_speed * move_direction))  # move
    joystick.set_button(1, jump)  # jump
    # todo: grab
    # todo: layer change
    # todo: menu navigation stuff


async def controller_loop():
    while True:
        update_controller()
        await asyncio.sleep(1 / 30)  # Wait for 1/30th of a second


async def handle_client(websocket, path):
    async for message in websocket:
        parsed = json.loads(message)

        if path == "crocs":
            global move_speed, jump
            move_speed = parsed["speed"]
            jump = parsed["jump"]


async def main():
    async with websockets.serve(handle_client, LISTEN_IP, PORT):
        print("WebSocket server started on", "ws://" + LISTEN_IP + ":" + str(PORT))
        # Start the controller loop in the background
        await asyncio.create_task(controller_loop())
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())
