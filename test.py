import paramiko
import time
import re

server_ip = ''
username = ''
password = ''

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(server_ip, username=username, password=password)

channel = ssh.invoke_shell()

channel.send("pwd\n")

while not channel.recv_ready():
    time.sleep(1)

output_buffer = ''
while True:
    tmp = channel.recv(1024)
    if not tmp:
        break
    output_buffer += tmp


print output_buffer
