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


########## CONSTANTS ##########

# capacitive touch setup
TOUCH_PIN = touchio.TouchIn(board.A3)

# Initialize pins and func
RED_LED = digitalio.DigitalInOut(board.D8)
GREEN_LED = digitalio.DigitalInOut(board.D9)

# Declare pins to output
RED_LED.direction = digitalio.Direction.OUTPUT
GREEN_LED.direction = digitalio.Direction.OUTPUT

# analog input setup
ANALOG_VOLUME_PIN = analogio.AnalogIn(board.A0)

# total number of MAC volume divisions
MAC_TOTAL_VOLUME_DIVISIONS = 16
MAX_VOLTAGE = 3.3
ERROR = 0.25

# creating arr of volume boundaries 
volume_boundary_array = [0] # include a starting zero in the array in order to have mute option
vol_fraction = round((MAX_VOLTAGE / MAC_TOTAL_VOLUME_DIVISIONS), 1)
sum = vol_fraction
for i in range(MAC_TOTAL_VOLUME_DIVISIONS):
    volume_boundary_array.append(sum)
    sum += vol_fraction
    

    
########## FUNCTIONS ##########
### FOR POT VOLUME CONTROL ###
def get_voltage(pin):
    # converting ADC pin values to a 0 to ~3.3V range (accuracy may vary)
    # avg ADC max is around 64700
    # return (pin * 3.3) / 65535
    return (pin * 3.3) / 64700
    
    
def find_nearest_boundary(current_volt_val, error):
    for idx, array_val in enumerate(volume_boundary_array):
        if (array_val - error) <= current_volt_val and current_volt_val <= (array_val + error):
            #print('Nearrest boundary is:', array_val)
            return idx


def up_or_down_determiner(current_position, last_position):
    # volume up 
    if current_position > last_position:
        print('vol up')
        #print('CURRENT VOLT POSITION:', current_position)
        cc.send(ConsumerControlCode.VOLUME_INCREMENT)
        return True

    # volume down
    elif current_position < last_position:
        print('vol down')
        #print('CURRENT VOLT POSITION:', current_position)
        cc.send(ConsumerControlCode.VOLUME_DECREMENT)
        return True

### FOR MUTING AND LIGHTS ###
# controls (LED) pins with .value member by setting equal to Booleans
def initialize_press_and_lights():
    while True:
        RED_LED.value = 0
        GREEN_LED.value = 1
        # to break out of while loop touch or pot value
        if TOUCH_PIN.value or ANALOG_VOLUME_PIN.value:
            #print("INIT FUNC PRESS DETECTED")
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

########## GLOBAL VALS, INITIALIZATION, SETUP ##########
# determine current position of pot 
# decrementing by max divisions
for i in range(MAC_TOTAL_VOLUME_DIVISIONS):
    cc.send(ConsumerControlCode.VOLUME_DECREMENT)

### determining current pot position and corresponding array vol voltage idx ###
analog_volume_pin_value = ANALOG_VOLUME_PIN.value
#print(analog_volume_pin_value)
current_volt = get_voltage(analog_volume_pin_value)
#print(current_volt)
current_position = find_nearest_boundary(current_volt, ERROR) # get the closest idx to determine init position
#print(current_position)
last_position = current_position

# increment volume (idx) amount of times to set current pot and corresponding volume position
for i in range(current_position):
    cc.send(ConsumerControlCode.VOLUME_INCREMENT)
    
# initial run for lights
initialize_press_and_lights()
# flag variable for light press
cap_press = 0

while True:
    analog_volume_pin_value = ANALOG_VOLUME_PIN.value
    current_volt = get_voltage(analog_volume_pin_value)
    current_position = find_nearest_boundary(current_volt, ERROR)
    if up_or_down_determiner(current_position, last_position):
        last_position = current_position
    elif TOUCH_PIN.value:
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
        keyboard.release_all()
    # print("analog vol pin", analog_volume_pin_value)
    #print("voltage vol pin", current_volt)
    # make a fast sleep time for better accuracy 
    time.sleep(0.01)

