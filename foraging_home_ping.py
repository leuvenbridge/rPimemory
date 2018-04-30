

import socket, time

def serverConnect():
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    host = '192.168.0.10'
    port = 12345
    conn = sock.connect((host,port))
    print('Connection received from {}'.format(host))
    return sock,conn

def pingServer(sock,conn):
    tList = []
    tList.append(time.time())
    conn.send('0'.encode())
    msg = conn.recv(1)
    tList.append(time.time())
    conn.send('1'.encode())
    msg = conn.recv(1024)
    tList.append(int(msg))
    return tList

def closeConnection(sock,conn):
    conn.close()
    sock.close()
    print('Connection closed')
