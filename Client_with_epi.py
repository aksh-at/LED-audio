import socket
import time
from neopixel import *

# LED strip configuration:
LED_COUNT      = 150      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

HOST = ''
PORT = 6000

def wheel(pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
                return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
                pos -= 85
                return Color(255 - pos * 3, 0, pos * 3)
        else:
                pos -= 170
                return Color(0, pos * 3, 255 - pos * 3)

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
# Intialize the library (must be called once before other functions).
strip.begin()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
c = 0
j = 0

print('Connected by', addr)
try:
    while 1:
        data = conn.recv(1024)
        if not data:
            c+=1
            if c == 50:
                break
            continue
        data = data.split()
        if data[0] == "beat":
            print(data)
            try:
                delay = min(float(data[1]) * 200,500)
                if delay <60:
                    continue
                for i in range(strip.numPixels()):
                        strip.setPixelColor(i, Color(255,255,255))
                strip.show()
                time.sleep(delay/1000.0)
            except ValueError:
                pass
        else:
            try:
                val = float(data[0])
                lim = int(strip.numPixels()*val/20) + 30
		print(lim)
                for i in range(lim):
                        strip.setPixelColor(i, wheel((i+j) & 255))
                for i in range(lim, strip.numPixels()):
                        strip.setPixelColor(i, Color(0,0,0))
                j+=1
                strip.show()
            except ValueError:
                pass
except KeyboardInterrupt:
    conn.close()
