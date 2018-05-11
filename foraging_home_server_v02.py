

import socket, time

timeReceived = time.time()
keepRunning = 1

sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host = '192.168.0.10'
port = 12345
sock.bind((host,port))
print('Server started')


sock.listen(5)


while True:
    conn, addr = sock.accept()
    timeReceived = time.time()
    sock.send((keepRunning).to_bytes(1,'big'))

    time_str = '{}'.format(int(1000000*timeReceived))
    conn.send(time_str.encode())
    print('Connection received from {}'.format(addr))


conn.close()
print('All done')
