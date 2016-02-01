from time import sleep
from router import Router
import logging
import threading

DELAY = 1
INTERFACE = "vlan1"
IPS = ['192.168.1.108', '192.168.1.109']

logging.basicConfig(level=logging.DEBUG)


class StopableDeamon():
    def __init__(self, lock, ip, delay, interface):
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.lock = lock
        self.stop_event = threading.Event()
        self.delay = delay
        self.ip = ip
        self.interface = interface
        self.TX = 0
        self.RX = 0

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
            logging.debug("{} {} {}".format(ip, RX - self.RX, TX - self.TX))

        self.RX = RX
        self.TX = TX


def start_deamons(deamons):
    for deamon in deamons:
        deamon.start()


def stop_deamons(deamons):
    print "Stopping deamons"

    for deamon in deamons:
        deamon.stop()

    for deamon in deamons:
        deamon.join()

    print "All done"


def main():
    lock =  threading.Lock()

    deamons = (StopableDeamon(lock, ip, DELAY, INTERFACE) for ip in IPS)

    start_deamons(deamons)

    try:
        sleep(60*60*24)
    except (KeyboardInterrupt, SystemExit):
        stop_deamons(deamons)


if __name__ == "__main__":
    main()
