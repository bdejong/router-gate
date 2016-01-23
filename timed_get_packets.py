from time import sleep
from router import Router
from threading import Lock, Thread, Event


DELAY = 1
INTERFACE = "vlan1"
IPS = ['192.168.1.107']


class StopableDeamon(Thread):
    def __init__(self, lock, ip, delay, interface):
        super(StopableDeamon, self).__init__()
        self.lock = lock
        self.delay = delay
        self.ip = ip
        self.interface = interface
        self.stop_event = Event()
        self.TX = 0
        self.RX = 0

        self.daemon = True

    def stop(self):
        self.stop_event.set()

    def run(self):
        with Router(self.ip) as router:
            while not self.stop_event.is_set():
                packets = router.get_packets(self.interface)
                self.deal_with_packets(router.ip, *packets)
                sleep(self.delay)

    def deal_with_packets(self, ip, RX, TX):
        with self.lock:
            print ip, RX - self.RX, TX - self.TX
            self.RX = RX
            self.TX = TX


def start_deamons(deamons):
    for deamon in deamons:
        deamon.start()


def stop_deamons(deamons):
    print "Stopping deamons"

    for deamon in deamons:
        deamon.stop()

    while any(deamon.is_alive() for demon in deamons):
        sleep(0.1)

    print "All done"


def main():
    lock = Lock()

    deamons = (StopableDeamon(lock, ip, DELAY, INTERFACE) for ip in IPS)

    start_deamons(deamons)

    try:
        sleep(60*60*24)
    except (KeyboardInterrupt, SystemExit):
        stop_deamons(deamons)


if __name__ == "__main__":
    main()
