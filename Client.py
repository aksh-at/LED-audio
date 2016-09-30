import socket
import time
from neopixel import *
import threading

# LED strip configuration:
LED_COUNT      = 150      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 200     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

HOST = ''
PORT = 6000

BRIG_THRESH = 50
BRIG_SLOPE  = 200
RMS_Q_SZ = 3
dif_Q_SZ = 3
TIME_SLOPE = 5000

rms_vals = [0]
dif_vals = [500]
running = True

def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

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

def _listenerFunction():
    global cur_dif, rms_vals, running
    while running:
        data = conn.recv(1024)
        if data:
            data = data.split()
            print data
            #for i in range(strip.numPixels()):
            #    strip.setPixelColor(i, Color(255,255,255))
            try:
                rms_vals.append(float(data[2]))
                if(len(rms_vals) == RMS_Q_SZ):
                    rms_vals.pop(0)
                dif_vals.append(int(data[1]))
                if(len(dif_vals) == dif_Q_SZ):
                    dif_vals.pop(0)
            except ValueError:
                pass
            #strip.show()
            #time.sleep(250/1000.0)
        time.sleep(50/1000.0)

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
# Intialize the library (must be called once before other functions).
strip.begin()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
j = 0

threadListener= threading.Thread(target=_listenerFunction,args=())
threadListener.start()

print 'Connected by', addr
try:
    while 1:
        init  = int(round(time.time() * 1000))
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
        delay = mean(dif_vals)
        incr = int(TIME_SLOPE/delay)
        brightness = int(BRIG_THRESH + BRIG_SLOPE*mean(rms_vals))
        j+= incr
        print delay, brightness, incr
        #strip.setBrightness(brightness)
        cur  = int(round(time.time() * 1000))
        strip.show()
        time.sleep((delay-(cur-init))/1000.0)

except KeyboardInterrupt:
    conn.close()
    running = False
