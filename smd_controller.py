import socket
import time
import pigpio
import numpy as np

class SMDStrip:

    def __init__(self, r_pin, g_pin, b_pin):
        self.pi = pigpio.pi()
        self.r_pin = r_pin
        self.g_pin = g_pin
        self.b_pin = b_pin
    
    def set_color(color):
        b = color % (1 << 8)
        color = color >> 8
        g = color % (1 << 8)
        color = color >> 8
        r = color % (1 << 8)

        self.pi.set_PWM_dutycycle(self.r_pin, r)
        self.pi.set_PWM_dutycycle(self.g_pin, g)
        self.pi.set_PWM_dutycycle(self.b_pin, b)

class StripController:
    "Controller for SMD 5050"

    def __init__(self, host, port, beatProcessor, valProcessor):
        self.strip = [SMDStrip(0, 0, 0), SMDStrip(0,0,0)]

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port

        self.recent_vals = []
        self.max_vol = 1
        self.floor_vol = 0

        self.beatProcessor = beatProcessor
        self.valProcessor = valProcessor

        #Constants
        self.NORMALIZE_SAMPLES = 1000

    def normalize(self, val):
        if len(self.recent_vals) == self.NORMALIZE_SAMPLES:
            self.recent_vals = self.recent_vals[1:]

        self.recent_vals.append(val)
        self.floor_vol = 0.5*np.median(self.recent_vals)
        self.max_vol = 2.5*np.mean(self.recent_vals) - self.floor_vol

        return max((val - self.floor_vol)/self.max_vol, 0.01)


    def run(self):
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
