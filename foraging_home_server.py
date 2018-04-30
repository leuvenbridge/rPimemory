

import socket, time

timeReceived = time.time()

sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host = '192.168.0.10'
port = 12345
sock.bind((host,port))

sock.listen(5)

conn, addr = sock.accept()
print('Connection received from {}'.format(addr))

while True:
    msg = conn.recv(1)
    if (int(msg.decode())==0):
        timeReceived = time.time()
        conn.send('1'.encode())
    elif (int(msg.decode())==1):
        time_str = '{}'.format(int(1000000*timeReceived))
        conn.send(time_str.encode())
    elif (int(msg.decode())==2):
        break

conn.close()
print('All done')
