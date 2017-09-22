from neopixel import Color

def color_func_by_name(name):
    if name == 'color_wheel':
        return ColorWheel()
    elif name == 'aqua':
        return Flat(20,255,232)
    elif name == 'white':
        return Flat(255, 255, 255)

class Flat:
    """
    Plain color
    """
    def __init__(self, r, g, b):
        self.color = Color(g, r, b)

    def process(self, i, val, beat_freq):
        return self.color

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
