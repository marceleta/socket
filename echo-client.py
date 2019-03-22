#!/usr/bin/env python3

import socket
import json

HOST = '127.0.0.1'
PORT = 5000

json_string = b'{"fist_name":"Guido", "last_name":"Rossum"}'

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST,PORT))
    s.sendall(json_string)
    data = s.recv(1024)

print('Received', repr(data))

