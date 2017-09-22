from neopixel import Color
import random

def color_func_by_name(name):
    if name == 'color_wheel':
        return ColorWheel()
    elif name == 'random_walk':
        return RandomWalk(0.5, 0.5, 0, 0.001, get_color_rgb)
    elif name == 'random':
        return RandomWalk(0, 0, 0, 0, get_color_rgb)
    elif name == 'random_light':
        return RandomWalk(0.5, 0.5, 0, 0.001, bias_rgb(0,0,0, alpha = 0.5 ))
    elif name == 'random_dark':
        return RandomWalk(0.5, 0.5, 0, 0.001, bias_rgb(0,0,0, alpha = 0.1 ))
    elif name == 'random_aqua':
        return RandomWalk(0.5, 0.5, 0, 0.001, bias_rgb(20,255,232))
    elif name == 'random_blue':
        return RandomWalk(0.5, 0.5, 0, 0.001, bias_rgb(0,0,255))
    elif name == 'aqua':
        return Flat(20,255,232)
    elif name == 'purple':
        return Flat(112,56,255)
    elif name == 'blue':
        return Flat(0, 0, 255)
    elif name == 'white':
        return Flat(255, 255, 255)
    elif name[0] == 'x':
        return Flat(int(name[1:3], 16), int(name[3:5], 16), int(name[5:7], 16))

def clamp(v, lim = 255): # clamps from 0 to lim, reversing in the appropriate ranges
    ret = v % lim
    if int(v / lim) % 2 == 1:
        ret = lim - ret
    return int(ret)

def get_color_rgb(r, g, b):
    return Color(clamp(g), clamp(r), clamp(b))

def bias_rgb(dr, dg, db, alpha = 0.5):
    def f(r, g, b):
        r = (alpha * clamp(r)) + (1 - alpha) * dr
        g = (alpha * clamp(g)) + (1 - alpha) * dg
        b = (alpha * clamp(b)) + (1 - alpha) * db
        return Color(int(g), int(r), int(b))
    return f

class Flat:
    """
    Plain color
    """
    def __init__(self, r, g, b):
        self.color = Color(g, r, b)

    def process(self, i, val, beat_freq):
        return self.color

class RandomWalk:
    """
    Random walk from starting color
    """
    def __init__(self, mu, sigma, vmu, vsigma, conv_fn):
        self.r = random.randint(0,255)
        self.g = random.randint(0,255)
        self.b = random.randint(0,255)

        self.vr = random.random() / 5
        self.vg = random.random() / 5
        self.vb = random.random() / 5

        self.mu = mu
        self.sigma = sigma
        self.vmu = vmu
        self.vsigma = vsigma

        self.conv_fn = conv_fn
        

    def process(self, i, val, beat_freq):
        if i == 0:
            # Perform random walk
            self.r += random.gauss(self.mu, self.vsigma)
            self.g += random.gauss(self.mu, self.vsigma)
            self.b += random.gauss(self.mu, self.vsigma)

            self.vr += random.gauss(self.vmu, self.vsigma)
            self.vg += random.gauss(self.vmu, self.vsigma)
            self.vb += random.gauss(self.vmu, self.vsigma)

        return self.conv_fn(self.r + i*self.vr, self.g + i*self.vg, self.b + i*self.vb)

class ColorWheel:
    """
    Simple pretty color wheel
    """
    def __init__(self):
        self.led_offset = 0.0

    def wheel(self, pos): 
        if pos < 85:
            return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3)
    
    def process(self, i, val, beat_freq):
        self.led_offset += 0.003
        return self.wheel((i+int(self.led_offset)) & 255)
