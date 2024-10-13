import pyvjoy
import asyncio
import json
import websockets

LISTEN_IP = "192.168.1.134"
PORT = 1337

DIRECTION_UP = 0
DIRECTION_RIGHT = 1
DIRECTION_DOWN = 2
DIRECTION_LEFT = 3

joystick = pyvjoy.VJoyDevice(1)
joystick.set_axis(pyvjoy.HID_USAGE_X, 16384)  # Center position for X axis
joystick.set_axis(pyvjoy.HID_USAGE_Y, 16384)  # Center position for Y axis

azimuth = 0.0
move_speed = 0.0
jump = False


def to_axis_value(float_value):
    return int(float_value * 16384 + 16384)


def get_cardinal_direction(angle):
    # Normalize the angle to be within 0-360
    angle = angle % 360

    # Determine the direction based on the angle
    if angle >= 315 or angle < 45:
        print("UP")
        return DIRECTION_UP
    elif 45 <= angle < 135:
        print("RIGHT")
        return DIRECTION_RIGHT
    elif 135 <= angle < 225:
        print("DOWN")
        return DIRECTION_DOWN
    elif 225 <= angle < 315:
        print("LEFT")
        return DIRECTION_LEFT

def update_controller():
    global joystick, azimuth, move_speed, jump

    direction = get_cardinal_direction(azimuth)
    joystick_x_value = 0
    joystick_y_value = 0

    if direction == DIRECTION_UP:
        joystick_y_value = move_speed
    elif direction == DIRECTION_DOWN:
        joystick_y_value = -move_speed
    elif direction == DIRECTION_RIGHT:
        joystick_x_value = move_speed
    elif direction == DIRECTION_LEFT:
        joystick_x_value = -move_speed

    joystick.set_axis(pyvjoy.HID_USAGE_X, to_axis_value(joystick_x_value))
    joystick.set_axis(pyvjoy.HID_USAGE_Y, to_axis_value(joystick_y_value))


    joystick.set_button(3, jump)  # jump
    # todo: grab
    # todo: menu navigation stuff


async def controller_loop():
    while True:
        update_controller()
        await asyncio.sleep(1 / 30)  # Wait for 1/30th of a second


async def handle_client(websocket, path):
    print("New connection at", path)
    async for message in websocket:
        print(message)
        parsed = json.loads(message)

        if path == "/crocs":
            global move_speed, jump
            move_speed = parsed["speed"]
            jump = parsed["jump"]

        elif path == "/compass":
            global azimuth
            azimuth = parsed["azimuth"]


async def main():
    async with websockets.serve(handle_client, LISTEN_IP, PORT, ping_interval=None):
        print("WebSocket server started on", "ws://" + LISTEN_IP + ":" + str(PORT))
        # Start the controller loop in the background
        await asyncio.create_task(controller_loop())
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())
