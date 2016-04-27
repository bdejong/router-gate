from pythonosc import dispatcher
from pythonosc import osc_server
from router import Router
import logging
from config import ROUTER_IPS, INCOMING_OSC, DEBUG_LEVEL

ROUTERS = [Router(ip).connect() for ip in ROUTER_IPS]

logging.basicConfig(level=DEBUG_LEVEL)


def handle_light(unused_addr, value):
    logging.debug("{} {}".format(unused_addr, value))

    parts = unused_addr.strip("/").split("/")

    if len(parts) != 4:
        logging.debug("Cound't split message: {}".format(unused_addr))
        return

    router_num = int(parts[1])
    light_num = int(parts[3])

    if router_num >= len(ROUTERS):
        logging.debug("OUT OF BOUNDS: index:{} num_routers:{}".format(
                router_num, len(ROUTERS)
            )
        )
        return

    ROUTERS[router_num].switch_light(light_num, float(value) > 0.5)


def start_server():
    mapping = dispatcher.Dispatcher()

    if DEBUG_LEVEL == logging.DEBUG:
        mapping.set_default_handler(print)

    mapping.map("/router/*/light/*", handle_light)

    server = osc_server.ThreadingOSCUDPServer(INCOMING_OSC, mapping)

    server.serve_forever()


if __name__ == "__main__":
    start_server()
