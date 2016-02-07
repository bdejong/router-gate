from time import sleep
from router import Router
import logging
import threading
from pythonosc import osc_message_builder
from pythonosc import udp_client
from config import (
    ROUTER_IPS, OUTGOING_OSC, ROUTER_DELAY, ROUTER_INTERFACE, DEBUG_LEVEL
)

logging.basicConfig(level=DEBUG_LEVEL)

osc_client = udp_client.UDPClient(*OUTGOING_OSC)


class StopableDeamon():
    def __init__(self, osc_address, ip, delay, interface):
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.stop_event = threading.Event()
        self.delay = delay
        self.ip = ip
        self.interface = interface
        self.TX = 0
        self.RX = 0
        self.osc_address = osc_address

    def stop(self):
        self.stop_event.set()

    def run(self):
        with Router(self.ip) as router:
            while not self.stop_event.is_set():
                packets = router.get_packets(self.interface)
                self.deal_with_packets(router.ip, *packets)
                sleep(self.delay)

    def start(self):
        self.thread.start()

    def join(self):
        self.thread.join()

    def deal_with_packets(self, ip, RX, TX):
        if self.RX:
            d_TX = TX - self.TX
            d_RX = RX - self.RX

            logging.debug("{} {} {}".format(ip, d_RX, d_TX))

            msg = osc_message_builder.OscMessageBuilder(
                address=self.osc_address + "/TX"
            )
            msg.add_arg(d_TX)
            msg = msg.build()
            osc_client.send(msg)

            msg = osc_message_builder.OscMessageBuilder(
                address=self.osc_address + "/RX"
            )
            msg.add_arg(d_RX)
            msg = msg.build()
            osc_client.send(msg)

        self.RX = RX
        self.TX = TX


def main():
    deamons = []
    for index, ip in enumerate(ROUTER_IPS):
        osc_adress = "/router/{}".format(index)
        deamons.append(
            StopableDeamon(
                osc_adress, ip, ROUTER_DELAY, ROUTER_INTERFACE
            )
        )

    logging.info("Starting deamons")

    for deamon in deamons:
        deamon.start()

    try:
        sleep(60*60*24)
    except (KeyboardInterrupt, SystemExit):
        logging.info("Stopping deamons")

        for deamon in deamons:
            deamon.stop()

        for deamon in deamons:
            deamon.join()

        logging.info("All done")


if __name__ == "__main__":
    main()
