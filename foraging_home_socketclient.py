import socket, time, math

nPings = 10
timeBuff = []
timeReceived = []
diffPre = []
diffPost = []

sock = socket.socket()
host = '192.168.0.10'
port = 12345
sock.connect((host,port))

timeBuff.append(time.time())
for pp in range(nPings):
    sock.send('1'.encode())
    sock.recv(1)
    timeBuff.append(time.time())

for pp in range(nPings):
    sock.send('1'.encode())
    tmp = sock.recv(1024)
    tmp = int(tmp.decode())/1000000
    timeReceived.append(tmp)
    
    diffPre.append(timeBuff[pp]-timeReceived[pp])
    diffPost.append(timeBuff[pp+1]-timeReceived[pp])


meanPre = 0
meanPost = 0
for pp in range(nPings):
    meanPre = meanPre+diffPre[pp]
    meanPost = meanPost+diffPost[pp]

meanPre = meanPre/nPings
meanPost = meanPost/nPings

print('Pre: {}, Post: {}, Diff: {}'.format(meanPre,meanPost,meanPre-meanPost))
sock.close()
