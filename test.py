import paramiko
import getpass
import time


class SshConnection(object):
    def __init__(self, ip, username, password):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(ip, username=username, password=password)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.ssh.close()

    def __call__(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        stdin.close()

        return stdout.read(), stderr.read()

ip = '192.168.1.106'
username = 'bdejong'
password = getpass.getpass()

with SshConnection(ip, username, password) as ssh:
    num_calls = 1000
    start = time.time()
    latency = 0
    for _ in range(num_calls):
        lat_start = time.time()
        ssh("pwd")
        lat_end = time.time()
        latency += lat_end - lat_start

    end = time.time()
    print "We can call exec_command at:", (num_calls / (end - start)), "hz"
    print "Average latency is:", latency/num_calls*1000, "ms"
