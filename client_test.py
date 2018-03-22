import socket
import sys
from time import sleep
import time
host='127.0.0.1'
port=8080
backlog=5
try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client.connect((host,port))
except socket.error():
    print("not possible to listen")
    sys.exit()
msg = "GET /index.html HTTP/1.1\r\nHost: localhost:"+str(port)+"\r\nConnection: Keep-alive\r\n\r\nGET / HTTP/1.1\r\nHost: localhost:"+str(port)+"\r\nConnection: keep-alive"
for i in range(0,2):
    client.send(msg.encode())
    while(True):
        data = client.recv(1024)
        if data:
            print(data.decode()) #SHOULD GET THE INDEX.HTML FILE 6 TIMES.