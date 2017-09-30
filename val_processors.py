from color_funcs import Color

def val_proc_by_name(name, color_func):
    if name == 'histogram':
        return Histogram(0.7, color_func)
    elif name == 'flat':
        return Flat(color_func)
    elif name == 'flat_table':
        return FlatTable(color_func)

class FlatTable:
    """
    FOR INFINITY TABLE
    """
    def __init__(self, color_func):
        self.color_func = color_func

    def process(self, strip, val, beat_freq):
        strip[0].set_color(self.color_func.process(0, val, beat_freq))
        strip[1].set_color(self.color_func.process(1, val, beat_freq))

class Flat:
    def __init__(self, color_func):
        self.color_func = color_func

    def process(self, strip, val, beat_freq):
        for i in range(strip.numPixels()):
                strip.setPixelColor(i, self.color_func.process(i, val, beat_freq))

        strip.show()
        
class Histogram:
    """
    Classic histogram-looking(?) visualizer
    """
    def __init__(self, decay_constant, color_func):
        self.decay_constant = decay_constant
        self.color_func = color_func
        self.prev_leds = 0

    def process(self, strip, val, beat_freq):
        leds = strip.numPixels()*val
        leds = leds + self.decay_constant * self.prev_leds
        leds = min(int(leds), strip.numPixels())
        self.prev_leds = leds

        #print "Setting LEDS: ", leds

        for i in range(leds):
                strip.setPixelColor(i, self.color_func.process(i, val, beat_freq))

        for i in range(leds, strip.numPixels()):
                strip.setPixelColor(i, Color(0,0,0))

        strip.show()
