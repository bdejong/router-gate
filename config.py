import logging

ROUTER_IPS = ['192.168.100.101',
              '192.168.100.102',
              '192.168.100.103',
              '192.168.100.104',
              '192.168.100.105',
              '192.168.100.106']

INCOMING_OSC = ("127.0.0.1", 8000)
OUTGOING_OSC = ("127.0.0.1", 8001)

# For getting TX/RX
ROUTER_DELAY = 1
ROUTER_INTERFACE = "eth1"

DEBUG_LEVEL = logging.ERROR

MIDI_MAPPING = {
    48: dict(router=0, gpio=2),
    49: dict(router=0, gpio=3),
    50: dict(router=1, gpio=2),
    51: dict(router=1, gpio=3),
    52: dict(router=2, gpio=2),
    53: dict(router=2, gpio=3),
    54: dict(router=3, gpio=2),
    55: dict(router=3, gpio=3),
    56: dict(router=4, gpio=2),
    57: dict(router=4, gpio=3),
    58: dict(router=5, gpio=2),
    59: dict(router=5, gpio=3),
}

# MIDI_MAPPING = {}
