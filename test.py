import paramiko
import time
import telnetlib
import re


class TelnetConnection(object):
    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password

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
        self.tn.write(command + "\n")
        data = self.tn.read_until("~# ").split("\n")[1:-1]
        return "\n".join(data).strip()


class SshConnection(object):
    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def __enter__(self):
        self.ssh.connect(
            self.ip,
            username=self.username,
            password=self.password
        )
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.ssh.close()

    def __call__(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        stdin.close()

        return stdout.read(), stderr.read()


def test_speed(ip, username, password, command=["pwd"]):
    index = 0
    with TelnetConnection(ip, username, password) as ssh:
        for _ in range(10):
            num_calls = 100
            latency = 0
            min_lat, max_lat = 100000, -1

            for _ in range(num_calls):
                lat_start = time.time()
                ssh(command[index])
                lat_end = time.time()

                index = (index + 1) % len(command)

                lat_diff = lat_end - lat_start
                latency += lat_diff
                min_lat = min(lat_diff, min_lat)
                max_lat = max(lat_diff, max_lat)

            print (num_calls / latency), "\t", min_lat*1000, "\t", max_lat*1000


def parse_ifconfig_output(telnet, interface_name):
    ifconfig = telnet("ifconfig " + interface_name)

    RX = TX = 0

    for line in ifconfig.split("\n"):
        line = line.strip()
        if "RX packets" in line:
            RX = int(re.findall(r"[\w]+", line)[2])
        elif "TX packets" in line:
            TX = int(re.findall(r"[\w]+", line)[2])

    return RX, TX


def switch_light(telnet, gpio_num, turn_on):
    command = "gpio %s %d" % (
        ("disable " if turn_on else "enable "),
        gpio_num
    )
    telnet(command)


ip = '192.168.1.1'
username = 'root'
password = 'admin'

"""
test_speed(ip, username, password, command=["gpio disable 2", "gpio enable 2"])
"""
