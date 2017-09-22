import socket
import time
from neopixel import *
import numpy as np

# LED strip configuration:
LED_COUNT      = 150      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

# Network configuration
HOST = ''
PORT = 6000

# Beat configuration
DELAY_MULTIPLIER = 100
MAX_DELAY = 250
DELAY_THRESH = 50

# Other constants
NORMALIZE_SAMPLES = 1000 #How many samples to take before settling on a value
DECAY_CONSTANT = 0.5

# Global variables
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
led_offset = 0
recent_vals = []
max_vol = 1
prev_leds = 0

def wheel(pos): 
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

# Record NORMALIZE_SAMPLES and then recompute max volume
def normalize(val):
    global recent_vals, max_vol

    if len(recent_vals) == NORMALIZE_SAMPLES:
        recent_vals = recent_vals[1:]

    recent_vals.append(val)
    max_vol = 2*np.mean(recent_vals)
    print "Normalized max_volume to ", max_vol

def process_beat(data):
    global strip

    try:
        delay = min(float((data[1])) / max_vol * DELAY_MULTIPLIER, MAX_DELAY)
        if delay > DELAY_THRESH:
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, Color(255,255,255))
            strip.show()
            print "BEAT! Sleeping for ", delay
            time.sleep(delay/1000.0)
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, Color(0,0,0))
            strip.show()
            time.sleep(delay/2000.0)
        else:
            process_val(data[1:])

    except ValueError:
        pass

def process_val(data):
    global max_vol, prev_leds, led_offset, strip

    try:
        val = float(data[0])

        normalize(val)

        leds = strip.numPixels()*val/max_vol
        leds = leds + DECAY_CONSTANT * prev_leds
        leds = min(int(leds), LED_COUNT)
        prev_leds = leds

        #print "Setting LEDS: ", leds

        for i in range(leds):
                strip.setPixelColor(i, wheel((i+led_offset) & 255))

        for i in range(leds, strip.numPixels()):
                strip.setPixelColor(i, Color(0,0,0))

        strip.show()
        led_offset += 1

    except ValueError:
        pass

def run():
    strip.begin()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)
    conn, addr = s.accept()

    print('Connected by', addr)
    try:
        c = 0
        while 1:
            data = conn.recv(1024)
            if not data:
                c+=1
                if c == 50:
                    break
                continue
            data = data.split()
            if data[0] == "beat":
                process_beat(data)
            else:
                process_val(data)
    except KeyboardInterrupt:
        conn.close()

run()
