import socket, time

TCP_IP = '192.168.0.105'  # pi IP
TCP_PORT = 1234
BUFFER_SIZE = 24

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

conn, addr = s.accept()
print(time.time())
print('Connected to:', addr)
while 1:
    data = conn.recv(BUFFER_SIZE)
    if not data: break
    print ("received data:", data)
    conn.send(data)    # echo
    print(time.time())
conn.close()