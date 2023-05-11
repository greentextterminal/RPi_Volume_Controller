import time
import board
import touchio
import digitalio
import analogio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

# keyboard setup
keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)

# setup for consumer control use
cc = ConsumerControl(usb_hid.devices)

# capacitive touch setup
TOUCH_PIN = touchio.TouchIn(board.A3)

# analog input setup
ANALOG_VOLUME_PIN = analogio.AnalogIn(board.A0)

# Initialize pins and func
RED_LED = digitalio.DigitalInOut(board.D8)
GREEN_LED = digitalio.DigitalInOut(board.D9)

# Declare pins to output
RED_LED.direction = digitalio.Direction.OUTPUT
GREEN_LED.direction = digitalio.Direction.OUTPUT


# controls (LED) pins with .value member by setting equal to Booleans

def initialize_press_and_lights():
    while True:
        RED_LED.value = 0
        GREEN_LED.value = 1
        if TOUCH_PIN.value:
            print("INIT FUNC PRESS DETECTED")
            break

def volume_on_lights():
    while True:
        RED_LED.value = 0
        GREEN_LED.value = 1
        if TOUCH_PIN.value:
            break


def volume_off_lights():
    while True:
        RED_LED.value = 1
        GREEN_LED.value = 0
        if TOUCH_PIN.value:
            break


def cap_button_check(cap_press_val):
    if cap_press_val == 0:
        print('unmuted')
        volume_on_lights()
    elif cap_press_val == 1:
        print('muted')
        volume_off_lights()


# initial run 
initialize_press_and_lights()

# flag variables
cap_press = 0

while True:
    if TOUCH_PIN.value:
        #print(TOUCH_PIN.value)
        print("Pin touched!")
        if cap_press == 0:
            cap_press = 1
        elif cap_press == 1:
            cap_press = 0
        cap_button_check(cap_press)
        # keyboard.press(Keycode.A)
        cc.send(ConsumerControlCode.MUTE)
        # this while block prevent repeated "presses" when holding down touch
        while TOUCH_PIN.value:
            pass
    #else:
        keyboard.release_all()
    time.sleep(0.1)
