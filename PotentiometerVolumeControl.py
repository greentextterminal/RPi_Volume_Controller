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
def get_voltage(pin):
    # converting ADC pin values to a 0 to ~3.3V range (accuracy may vary)
    # avg ADC max is around 64700
    # return (pin * 3.3) / 65535
    return (pin * 3.3) / 64700
    
    
def find_nearest_boundary(current_volt_val, error):
    for idx, array_val in enumerate(volume_boundary_array):
        if (array_val - error) <= current_volt_val and current_volt_val <= (array_val + error):
            print('Nearrest boundary is:', array_val)
            return idx


def up_or_down_determiner(current_position, last_position):
    # volume up 
    if current_position > last_position:
        print('vol up')
        print('CURRENT VOLT POSITION:', current_position)
        cc.send(ConsumerControlCode.VOLUME_INCREMENT)
        return True

    # volume down
    elif current_position < last_position:
        print('vol down')
        print('CURRENT VOLT POSITION:', current_position)
        cc.send(ConsumerControlCode.VOLUME_DECREMENT)
        return True


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

while True:
    analog_volume_pin_value = ANALOG_VOLUME_PIN.value
    current_volt = get_voltage(analog_volume_pin_value)
    current_position = find_nearest_boundary(current_volt, ERROR)
    if up_or_down_determiner(current_position, last_position):
        last_position = current_position
    # print("analog vol pin", analog_volume_pin_value)
    #print("voltage vol pin", current_volt)
    # make a fast sleep time for better accuracy 
    time.sleep(0.01)

