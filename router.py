import time
import telnetlib
import re


class TelnetConnection(object):
    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password
        self.tn = None

    def __enter__(self):
        self.tn = telnetlib.Telnet(self.ip)
        self.tn.read_until("login: ")
        self.tn.write(self.username + "\n")
        self.tn.read_until("Password: ")
        self.tn.write(self.password + "\n")
        self.tn.read_until("~# ")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.tn.close()

    def __call__(self, command):
        if not self.tn:
            return None

        self.tn.write(command + "\n")
        data = self.tn.read_until("~# ").split("\n")[1:-1]
        return "\n".join(data).strip()


class Router(TelnetConnection):
    def __init__(self, ip, username, password):
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

            print (num_calls / latency), "\t", min_lat*1000, "\t", max_lat*1000


if __name__ == "__main__":
    ip = '192.168.1.107'
    username = 'root'
    password = 'admin'

    with Router(ip, username, password) as router:
        router.test_speed(["gpio disable 2", "gpio enable 2"])
