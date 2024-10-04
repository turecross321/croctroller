import RPi.GPIO as GPIO
import time

# Set up the GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)

left_pin = 17
right_pin = 27

# Set the pin as input with an internal pull-up resistor
GPIO.setup(left_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(right_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

left_last = False
right_last = False

try:
    while True:
        right = GPIO.input(left_pin) == GPIO.LOW
        left = GPIO.input(right_pin) == GPIO.LOW

        if left_last and not left:  # just left floor
            print("left UP!")
        elif left and not left_last:  # just touched floor
            print("left DOWN!")

        time.sleep(0.1)

except KeyboardInterrupt:
    GPIO.cleanup()
