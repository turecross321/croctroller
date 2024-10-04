import json
from typing import Optional

import RPi.GPIO as GPIO
import time
import websocket
import threading

LEFT_PIN = 27
RIGHT_PIN = 17
JUMP_THRESHOLD = 0.2  # Time required for both feet to be in the air for it to be recognized as a jump
MAX_SECONDS_BETWEEN_STEPS = 0.75
STEPS_PER_SECOND_TO_RUN_FULL_SPEED = 3.0
SERVER_URL = "ws://192.168.1.134:1337/crocs"
KEEP_ALIVE_INTERVAL = 10.0  # Keep-alive interval in seconds

# Set up the GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)
GPIO.setup(LEFT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RIGHT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

last_left = False
last_right = False
last_neither_on_floor = False
last_step_time = time.time()
last_start_jump_time = time.time()
current_steps_per_second = 0.0
steps = 0

ws: Optional[websocket.WebSocket] = None


def on_step():
    time_now = time.time()
    global steps, last_step_time, current_steps_per_second
    steps += 1
    current_steps_per_second = 1 / (time_now - last_step_time)
    last_step_time = time_now
    print("Steps:", str(steps))


def input_process():
    global last_left, last_right, last_neither_on_floor, last_step_time, last_start_jump_time

    right_on_floor = GPIO.input(LEFT_PIN) == GPIO.LOW
    left_on_floor = GPIO.input(RIGHT_PIN) == GPIO.LOW
    neither_on_floor = not left_on_floor and not right_on_floor
    now = time.time()

    speed: float = 0.0
    jump: bool = False

    if not last_neither_on_floor and neither_on_floor:
        last_start_jump_time = now

    if neither_on_floor and now - last_start_jump_time > JUMP_THRESHOLD:
        jump = True

    if last_left and not left_on_floor:
        on_step()
    if last_right and not right_on_floor:
        on_step()

    if now - last_step_time <= MAX_SECONDS_BETWEEN_STEPS:
        speed = min(current_steps_per_second / STEPS_PER_SECOND_TO_RUN_FULL_SPEED, 1.0)

    last_left = left_on_floor
    last_right = right_on_floor
    last_neither_on_floor = neither_on_floor

    return speed, jump


def send_ping():
    while True:
        time.sleep(KEEP_ALIVE_INTERVAL)
        if ws:
            try:
                ws.ping()
            except Exception as e:
                print(f"Failed to send ping: {e}")


def websocket_connect():
    global ws
    try:
        ws = websocket.WebSocket()
        ws.connect(SERVER_URL)
        print("WebSocket connected")
    except Exception as e:
        print(f"Failed to connect to WebSocket: {e}")
        ws = None


def run():
    global ws
    while True:
        if ws is None or not ws.connected:
            websocket_connect()

        try:
            move_speed, is_jumping = input_process()
            message = {"speed": move_speed, "jump": is_jumping}
            ws.send(json.dumps(message))
        except (websocket.WebSocketConnectionClosedException, ConnectionResetError) as e:
            print(f"Connection error: {e}")
            ws = None
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(0.1)


if __name__ == "__main__":
    try:
        threading.Thread(target=send_ping, daemon=True).start()
        run()
    except KeyboardInterrupt:
        GPIO.cleanup()
