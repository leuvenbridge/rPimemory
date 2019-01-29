

import socket, time

def serverConnect():
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    host = '192.168.0.10'
    port = 12345
    return sock


def pingServer(sock):
    tList = []
    tList.append(time.time())
    sock.connect((host,port))
    msg = sock.recv(1024)
    tList.append(int(msg.decode())/1000000)

    tList.append(time.time())
    sock.send('1'.encode())

    return tList

def closeConnection(sock):
    sock.send('2'.encode())
    sock.close()
    print('Connection closed')
