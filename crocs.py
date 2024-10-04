import json

import RPi.GPIO as GPIO
import time
import websocket

LEFT_PIN = 27
RIGHT_PIN = 17
JUMP_THRESHOLD = 0.2  # Time required for both feet to be in the air for it to be recognized as a jump
MAX_SECONDS_BETWEEN_STEPS = 0.75
STEPS_PER_SECOND_TO_RUN_FULL_SPEED = 3.0
SERVER_URL = "ws://192.168.1.134:1337/crocs"
KEEP_ALIVE_INTERVAL = 10.0

# Set up the GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)

# Set the pin as input with an internal pull-up resistor
GPIO.setup(LEFT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RIGHT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

last_left = False
last_right = False
last_neither_on_floor = False

last_step_time = time.time()
last_start_jump_time = time.time()

current_steps_per_second = 0.0

steps = 0


def on_step():
    time_now = time.time()

    global steps, last_step_time, current_steps_per_second

    steps = steps + 1

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

    if last_left and not left_on_floor:  # just left floor
        on_step()
    elif left_on_floor and not last_left:  # just touched floor
        pass

    if last_right and not right_on_floor:  # just left floor
        on_step()
    elif right_on_floor and not last_right:  # just touched floor
        pass

    if now - last_step_time <= MAX_SECONDS_BETWEEN_STEPS:
        speed = min(current_steps_per_second / STEPS_PER_SECOND_TO_RUN_FULL_SPEED, 1.0)

    last_left = left_on_floor
    last_right = right_on_floor
    last_neither_on_floor = neither_on_floor

    return speed, jump


try:
    last_ping_time = time.time()
    ws = websocket.WebSocket()
    ws.connect(SERVER_URL)

    while True:
        move_speed, is_jumping = input_process()
        message = {"speed": move_speed, "jump": is_jumping}
        ws.send(json.dumps(message))

        time.sleep(0.1)

except KeyboardInterrupt:
    GPIO.cleanup()
