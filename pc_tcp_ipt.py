import socket, time
TCP_IP = '192.168.0.102'  # Pi IP
TCP_PORT = 1234
BUFFER_SIZE = 24
MESSAGE = "START!"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
connTime = time.time()
print("Connection time", time.time())
s.send((MESSAGE).encode())
data = s.recv(BUFFER_SIZE)
s.close()
print("Received data:", data)
monkey = "kraut"
pcrecpiTime = time.time()
print("Received time:", time.time())

# change to client listening to Pi stopping command
TCP_IP = '192.168.0.106'   # laptop IP
TCP_PORT = 1234
BUFFER_SIZE = 24
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
conn, addr = s.accept()

while 1:
    data = conn.recv(BUFFER_SIZE)
    if not data: break
    print("Received data:", data)
    pistopTime = time.time()
    print("Pi stopped time:", time.time())
conn.close()

rootPath = "C:/Users/Hannah/Documents/github/rPimemory/data/"
currDate = time.localtime(time.time())
dataPath = rootPath + monkey + "_synctime" + "_{year}-{month}-{day}_{hours}-{minutes}-{seconds}.txt".format(year=currDate[0],month=currDate[1],day=currDate[2],hours=currDate[3],minutes=currDate[4],seconds=currDate[5])
fidData  = open(dataPath, 'w')
dataStr  = "connTime, pcrecpiTime, pistopTime"
fidData.write(dataStr)
dataStr  = "\n{ct},{prpt},{pst}".format(ct=connTime,prpt=pcrecpiTime,pst=pistopTime)
fidData.write(dataStr)
fidData.close()