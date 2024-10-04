import RPi.GPIO as GPIO
import time

# Set up the GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)

left_pin = 27
right_pin = 17

# Set the pin as input with an internal pull-up resistor
GPIO.setup(left_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(right_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

left_last = False
right_last = False

steps = 0
def on_step():
    global steps
    steps = steps + 1
    print("Steps:", str(steps))

try:
    while True:
        right = GPIO.input(left_pin) == GPIO.LOW
        left = GPIO.input(right_pin) == GPIO.LOW

        if not left and not right:
            print("JUMP!")

        if left_last and not left:  # just left floor
            pass
        elif left and not left_last:  # just touched floor
            on_step()

        if right_last and not right:  # just left floor
            pass
        elif right and not right_last:  # just touched floor
            on_step()

        left_last = left
        right_last = right

        time.sleep(0.1)

except KeyboardInterrupt:
    GPIO.cleanup()
