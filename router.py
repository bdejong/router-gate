import time
import telnetlib
import re


class TelnetConnection(object):
    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password
        self._tn = None

    def is_connected(self):
        return self._tn is not None

    def connect(self):
        if self.is_connected():
            self.disconnect()

        self._tn = telnetlib.Telnet(self.ip)
        self.read_until("login: ")
        self.write(self.username + "\n")
        self.read_until("Password: ")
        self.write(self.password + "\n")
        self.read_until("~# ")

        return self

    def disconnect(self):
        if self.is_connected():
            self._tn.close()

        return self

    def read_until(self, string):
        if not self.is_connected():
            return ""
        data = self._tn.read_until(string.encode("ascii"))
        return data.decode("ascii")

    def write(self, string):
        if self.is_connected():
            self._tn.write(string.encode("ascii"))

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

    def __call__(self, command):
        if not self.is_connected():
            return None

        self.write(command + "\n")
        data = self.read_until("~# ").split("\n")[1:-1]
        return "\n".join(data).strip()


class Router(TelnetConnection):
    def __init__(self, ip, username="root", password="d3c3ss10n"):
        super(Router, self).__init__(ip, username, password)

    def get_switch_light_command(self, gpio_num, turn_on):
        return "gpio %s %d" % (
            ("disable " if turn_on else "enable "),
            gpio_num
        )

    def switch_light(self, gpio_num, turn_on):
        self(self.get_switch_light_command(gpio_num, turn_on))

    def get_packets_command(self, interface_name):
        return "ifconfig " + interface_name

    def get_packets(self, interface_name):
        ifconfig = self(self.get_packets_command(interface_name))

        RX = TX = 0

        if ifconfig is None:
            return RX, TX

        for line in ifconfig.split("\n"):
            line = line.strip()
            if "RX packets" in line:
                RX = int(re.findall(r"[\w]+", line)[2])
            elif "TX packets" in line:
                TX = int(re.findall(r"[\w]+", line)[2])

        return RX, TX

    def test_speed(self, command):
        index = 0
        for _ in range(10):
            num_calls = 100
            latency = 0
            min_lat, max_lat = 100000, -1

            for _ in range(num_calls):
                lat_start = time.time()
                self(command[index])
                lat_end = time.time()

                index = (index + 1) % len(command)

                lat_diff = lat_end - lat_start
                latency += lat_diff
                min_lat = min(lat_diff, min_lat)
                max_lat = max(lat_diff, max_lat)

            print(
                "{}\t{}\t{}".format(
                    num_calls / latency,
                    min_lat*1000,
                    max_lat*1000
                )
            )


if __name__ == "__main__":
    ip = '192.168.1.107'

    with Router(ip) as router:
        router.test_speed(["gpio disable 2", "gpio enable 2"])
