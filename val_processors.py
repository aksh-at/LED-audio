from neopixel import Color

def val_proc_by_name(name, color_func):
    if name == 'histogram':
        return Histogram(0.55, color_func)
        
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
