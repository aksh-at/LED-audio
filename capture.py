"""Create a JACK client that copies input audio directly to the outputs.

This is somewhat modeled after the "thru_client.c" example of JACK 2:
http://github.com/jackaudio/jack2/blob/master/example-clients/thru_client.c

If you have a microphone and loudspeakers connected, this might cause an
acoustical feedback!

"""
import sys
import signal
import os
import jack
from aubio import tempo, source
import threading
import numpy as np
import socket

HOST = '18.111.38.125'
PORT = 6000

rms_vals = []
RMS_Q_SZ = 3

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
signal.signal(signal.SIGINT, signal.SIG_DFL)

client = jack.Client("ledaudio")
client.inports.register("input_1")
event = threading.Event()
win_s = client.blocksize # fft size
hop_s =  win_s/8          # hop size
Sr    = client.samplerate
o = tempo("default", win_s, hop_s, int(Sr))


@client.set_process_callback
def process(frames):
    global rms_vals
    SIL_THRESH = 0.01

    assert frames == client.blocksize
    arr =  client.inports[0].get_array()
    rms = np.sum(np.square(arr))
    if(rms < SIL_THRESH):
        return
    rms_vals.append(rms)
    if(len(rms_vals) == RMS_Q_SZ):
        s.sendall(str(min(rms_vals)))
        print min(rms_vals), len(rms_vals)
        rms_vals = []

    N   = len(arr)
    for i in xrange(1,int(N/hop_s)+1):
        if o(arr[(i-1)*hop_s:i*hop_s]):
            print "BEAT "
            s.sendall("beat "+str(rms)+" ")

@client.set_shutdown_callback
def shutdown(status, reason):
    print("JACK shutdown!")
    print("status:", status)
    print("reason:", reason)
    event.set()

with client:
    capture = client.get_ports()
    print capture

    client.connect("system:capture_1", "ledaudio:input_1")

    print("Press Ctrl+C to stop")
    try:
        event.wait()
    except KeyboardInterrupt:
        s.close()
        print("\nInterrupted by user")
