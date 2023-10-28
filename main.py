import termios
import tty
import requests as rq
import threading
import time
import numpy
import urllib3
import keyboard
import os
import sys
import platform
from colorsys import hsv_to_rgb
from rgbxy import Converter
from rgbxy import GamutC
import light_specific_vars
import light_utils

converter = Converter(GamutC)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # Disable warning about insecure connection
header = light_specific_vars.header
light_url = light_specific_vars.light_url
break_from_function = False


def hsv2rgb(h, s, v):
    return tuple(round(i * 255) for i in hsv_to_rgb(h, s, v))


def hsv2xy(h):
    r, g, b = hsv2rgb(h, 1, 1)
    x, y = converter.rgb_to_xy(r, g, b)
    return x, y


def change_color(x, y):
    r = rq.put(light_url, headers=header,
               json={
                   "color": {
                       "xy": {
                           "x": x,
                           "y": y
                       }
                   }
               }, verify=False)
    # print(it)
    if (r.status_code == 200) or (r.status_code == 207):
        pass
    else:
        print(r.status_code)
    time.sleep(0.1)


def listen_for_break_key():
    global break_from_function
    if platform.system() == 'Linux':
        orig_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin)
        key = ''
        while key != 'q':
            key = sys.stdin.read(1)
        break_from_function = True
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)
    else:
        if keyboard.is_pressed('q'):
            break_from_function = True
    # "keyboard" library requires root access in Linux environment, so different method is used in the "if" block
    # source : https://copyprogramming.com/howto/python-detect-which-key-is-pressed-python-linux


def change_power():
    os.system('clear')
    light_utils.change_power()
    os.system('clear')


def set_brightness_level():
    os.system('clear')
    brightness_level = int(input('Enter brightness level: '))
    if brightness_level > 100:
        brightness_level = 100
    elif brightness_level < 0:
        brightness_level = 0
    light_utils.change_brightness(brightness_level)
    os.system('clear')


def cycle_colors():
    while True:
        for j in numpy.arange(0, 1.01, 0.01):
            if break_from_function:
                return
            x, y = hsv2xy(j)
            change_color(x, y)


def cycle_colors_option():
    os.system('clear')
    print('Cycling through colors...')
    print('Press q to quit to main menu!')

    cycle_colors_thread = threading.Thread(target=cycle_colors)
    listen_for_break_key_thread = threading.Thread(target=listen_for_break_key)
    cycle_colors_thread.start()
    listen_for_break_key_thread.start()
    cycle_colors_thread.join()
    listen_for_break_key_thread.join()

    cycle_colors()
    global break_from_function
    break_from_function = False
    os.system('clear')


def invalid_option():
    os.system('clear')
    print("Choose valid option!")
    time.sleep(1)
    os.system('clear')


def main():
    while True:
        print('1 - power on/off')
        print('2 - brightness level')
        print('3 - cycle through colors')
        print('4 - exit program')
        choice = input('Enter your choice: ')

        if choice == '':
            invalid_option()
        elif choice == '1':
            change_power()
        elif choice == '2':
            set_brightness_level()
        elif choice == '3':
            cycle_colors_option()
        elif choice == '4':
            sys.exit()
        else:
            invalid_option()


if __name__ == "__main__":
    main()
