from rtmidi.midiconstants import *
from rtmidi.midiutil import open_midiport
from router import Router
import logging
import time
from config import ROUTER_IPS, DEBUG_LEVEL, MIDI_MAPPING

ROUTERS = [Router(ip).connect() for ip in ROUTER_IPS]

logging.basicConfig(level=DEBUG_LEVEL)

ROUTERS = [Router(ip).connect() for ip in ROUTER_IPS]


class MidiInputHandler(object):
    def __init__(self, port):
        self.port = port

    def __call__(self, event, data=None):
        message, deltatime = event

        status = message[0]

        if status & 0xF0 != 0x90 and status & 0xF0 != 0x80:
            return

        if status & 0xF0 == 0x90:
            note = message[1]
            on = message[2] != 0
        elif status & 0xF0 == 0x80:
            note = message[1]
            on = False

        if note in MIDI_MAPPING:
            router = MIDI_MAPPING[note]["router"]
            gpio = MIDI_MAPPING[note]["gpio"]
            # TODO: modulo!
            if router >= 0 and router < len(ROUTERS):
                ROUTERS[router].switch_light(gpio, on)
            else:
                logging.debug("Router {} not connected".format(router))
        else:
            logging.debug("Note {} not in mapping".format(note))


try:
    midiin, port_name = open_midiport(None)
except (EOFError, KeyboardInterrupt):
    sys.exit()

print("Attaching MIDI input callback handler.")
midiin.set_callback(MidiInputHandler(port_name))

print("Entering main loop. Press Control-C to exit.")
try:
    # just wait for keyboard interrupt in main thread
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print('')
finally:
    print("Exit.")
    midiin.close_port()
