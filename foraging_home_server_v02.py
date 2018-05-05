

import socket, time

timeReceived = time.time()

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
    time_str = '{}'.format(int(1000000*timeReceived))
    conn.send(time_str.encode())
    print('Connection received from {}'.format(addr))

    
conn.close()
print('All done')
