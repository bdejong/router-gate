from pythonosc import dispatcher
from pythonosc import osc_server
from router import Router

IPS = ['192.168.1.108', '192.168.1.109']
ROUTERS = [Router(ip).connect() for ip in IPS]


def handle_light(unused_addr, value):
    # print("handle_light", unused_addr, value)

    parts = unused_addr.strip("/").split("/")
    if len(parts) != 4:
        print("failed split")
        return

    router_num = int(parts[1])
    light_num = int(parts[3])

    if router_num >= len(ROUTERS):
        print("router out of bounds")
        return

    ROUTERS[router_num].switch_light(light_num, value > 0.5)

if __name__ == "__main__":
    dispatcher = dispatcher.Dispatcher()

    dispatcher.set_default_handler(print)

    for index, ip in enumerate(IPS):
        address = "/router/*/light/*".format(index + 1)
        dispatcher.map(address, handle_light)

    server = osc_server.ThreadingOSCUDPServer(
        ("127.0.0.1", 8000),
        dispatcher
    )

    server.serve_forever()
