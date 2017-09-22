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

class StripController:
    "Controller for neopixel things"

    def __init__(self, host, port, beatProcessor, valProcessor):
        self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recent_vals = []
        self.max_vol = 1
        self.floor_vol = 0
        self.host = host
        self.port = port
        self.beatProcessor = beatProcessor
        self.valProcessor = valProcessor

        #Constants
        self.NORMALIZE_SAMPLES = 1000

    def normalize(self, val):
        return val
        if len(self.recent_vals) == self.NORMALIZE_SAMPLES:
            self.recent_vals = self.recent_vals[1:]

        self.recent_vals.append(val)
        self.floor_vol = 0.5*np.median(self.recent_vals)
        self.max_vol = 2.5*np.mean(self.recent_vals) - self.floor_vol
        #print "max and floor are: ", self.max_vol, self.floor_vol

        return (val - self.floor_vol)/self.max_vol


    def run(self):
        self.strip.begin()
        self.s.bind((self.host, self.port))
        self.s.listen(1)
        conn, addr = self.s.accept()

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

                try:
                    val = self.normalize(float(data[-1]))
                except ValueError:
                    continue

                if data[0] == "beat":
                    self.beatProcessor.process(self.strip, val, -1)
                else:
                    self.valProcessor.process(self.strip, val, -1)

        except KeyboardInterrupt:
            conn.close()
