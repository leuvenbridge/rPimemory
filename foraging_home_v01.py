
# load libraries
import os, sys, time, math, random, pygame, numpy
from pygame.locals import *

try:
    rPi = 1
    import RPi.GPIO as io
except ImportError:
    rPi = 0
    pass


# set parameters
screenWidth = 480
screenHeight = 480
refreshRate = 60

lambdaVal = 0.5
stimTau = 0.156       #
stimVar = 0.1
avail = 0
replSpeed = 0.5
deplSpeed = 0.5

colMin = -0.50*math.pi
colMax = 0
colvar = 0.1
speedChange = 20

sndFreq1 = 1000
sndFreq2 = 500
sndDur = 0.2
sndFadeDur = 0.01
sndSampFreq = 22050

motorStepsNum = 20
motorStepWait = 0.001
motorCurrStep = -1

quittime = 5


# define functions
def quitprogram():
    fidLog.close()
    fidData.close()
    pygame.mouse.set_visible(1)
    pygame.quit()
    sys.exit()
    if rPi:
        os.system("shutdown now -h")

def makePowerSpectrum(arraySize):
    u = numpy.vstack((numpy.array([numpy.arange(0,math.floor(arraySize[0]/2)+1)]).T,numpy.array([numpy.arange(-(math.ceil(arraySize[0]/2)-1),0)]).T))
    v = numpy.hstack((numpy.array([numpy.arange(0,math.floor(arraySize[1]/2)+1)]),numpy.array([numpy.arange(-(math.ceil(arraySize[1]/2)-1),0)])))

    u = numpy.tile(u/arraySize[0],(1,arraySize[1]))
    v = numpy.tile(v/arraySize[1],(arraySize[0],1))
    S = u**2 + v**2
    S = numpy.sqrt(numpy.power(S,-1,where=(S!=0)))
    return S

def makeComplexSpectrum(powerSpectrum):
    reSpec = numpy.random.normal(0,1,powerSpectrum.shape)
    imSpec = numpy.random.normal(0,1,powerSpectrum.shape)
    complexSpectrum = (reSpec+1j*imSpec) * powerSpectrum
    return complexSpectrum

def makeInvk(arraySize):
    u = numpy.vstack((numpy.array([numpy.arange(0,math.floor(arraySize[0]/2)+1)]).T,numpy.array([numpy.arange(-(math.ceil(arraySize[0]/2)-1),0)]).T))
    v = numpy.hstack((numpy.array([numpy.arange(0,math.floor(arraySize[1]/2)+1)]),numpy.array([numpy.arange(-(math.ceil(arraySize[1]/2)-1),0)])))
    u = numpy.tile(u/arraySize[0],(1,arraySize[1]))
    v = numpy.tile(v/arraySize[1],(arraySize[0],1))
    k = numpy.sqrt(u**2 + v**2)
    invk = numpy.exp(-k*speedChange)
    return invk

if rPi:
    rootPath = "/home/pi/Documents/stim"

    io.setmode(io.BCM)

    pinEnable = 2
    pinMotor = (13,19,4,3)
    pinButton = 26

    io.setup(pinEnable, io.OUT)
    for pin in range(4):
        io.setup(pinMotor[pin], io.OUT)

    io.setup(pinButton, io.IN)
    io.add_event_detect(pinButton, io.RISING)
    io.add_event_callback(pinButton, buttonCallback)

    def buttonCallback():
        logStr = "{time} - Button pressed\n".format(time=time.time()-startTime)
        fidLog.write(logStr)
        getTreats()
        snd1.play(loops=0)

    def motor_ck(step):
        stepSequence = numpy.array([[1,0,1,0],[1,0,0,1],[0,1,0,1],[0,1,1,0]])
        for coil in range(4):
            io.output(pinMotor[coil], stepSequence[step,coil])

    def motor_stop():
        # forces fast stop
        for pin in range(4):
            io.output(pinMotor[pin], True)
        # shut down coils
        for pin in range(4):
            io.output(pinMotor[pin], False)

    def getTreats():
        io.output(pinEnable, True)
        for step in range(motorStepsNum):
            motorCurrStep = motorCurrStep+1
            if (motorCurrStep>3):
                motorCurrStep = 0
            motor_ck(motorCurrStep)
            time.sleep(motorStepWait)
        motor_stop()
        io.output(pinEnable, False)

else:
    rootPath = "/Users/baptiste/Documents/python/rPi"


# start pygame
pygame.init()
win = pygame.display.set_mode((screenWidth,screenHeight), pygame.FULLSCREEN, 32)
pygame.mouse.set_visible(0)
winSize = (screenWidth,screenHeight)
winCenter = (screenWidth/2,screenHeight/2)


# makes sounds
sndBufferSize = int(sndSampFreq*sndDur)
sndFadeSize = int(sndSampFreq*sndFadeDur)
sndPlateauSize = int(sndBufferSize-2*sndFadeSize)

fadeIn = numpy.expand_dims(numpy.sin(numpy.linspace(0,numpy.pi/2,sndFadeSize))**2,1)
fadeOut = numpy.expand_dims(numpy.sin(numpy.linspace(numpy.pi/2,0,sndFadeSize))**2,1)
plateau = numpy.ones((sndPlateauSize,1))
window = numpy.vstack((fadeIn,plateau,fadeOut))
sine1 = numpy.expand_dims(numpy.sin(numpy.linspace(0,2*numpy.pi*sndFreq1*sndDur,sndBufferSize)),1)
sine2 = numpy.expand_dims(numpy.sin(numpy.linspace(0,2*numpy.pi*sndFreq2*sndDur,sndBufferSize)),1)
sndVec1 = 32768*sine1*window
sndVec2 = 32768*sine2*window

pygame.mixer.init(frequency=sndSampFreq, size=-16, channels=1, buffer=sndBufferSize)
snd1 = pygame.mixer.Sound(sndVec1.astype('int16'))
snd2 = pygame.mixer.Sound(sndVec2.astype('int16'))

# create and load files
currDate = time.localtime(time.time())
clutPath = rootPath + "/clut.txt"
dataPath = rootPath + "/data/data_{year}-{month}-{day}_{hours}:{minutes}:{seconds}".format(year=currDate[0],month=currDate[1],day=currDate[2],hours=currDate[3],minutes=currDate[4],seconds=currDate[5])
# logPath = rootPath + "/data/log_{year}-{month}-{day}_{hours}:{minutes}:{seconds}".format(year=currDate[0],month=currDate[1],day=currDate[2],hours=currDate[3],minutes=currDate[4],seconds=currDate[5])
fidData = open(dataPath,"w")
# fidLog = open(logPath,"w")
dataStr = "time,lambda,tau,pup,pdown,avail,click\n"
fidData.write(dataStr)


startTime = time.time()


powerSpectrum = makePowerSpectrum(winSize)
Cold = makeComplexSpectrum(powerSpectrum)
inversePower = makeInvk(winSize)
clut = numpy.loadtxt(clutPath,dtype='int',delimiter=',')
nclutpoints = clut.shape[0]

keyWasDown = 0
wasClicked = 0

while True:

    # check keyboard
    keys = pygame.key.get_pressed()
    if keys[K_UP]:
        colvar = math.exp(math.log(colvar)-0.1)
    if keys[K_DOWN]:
        colvar = math.exp(math.log(colvar)+0.1)
    if keys[K_RIGHT]:
        colmean = colmean+0.1
    if keys[K_LEFT]:
        colmean = colmean-0.1
    if keys[K_q]:
        quitprogram()

    # check mouse
    if sum(pygame.mouse.get_pressed()):
        if not wasClicked:
            startClick = time.time()
            if avail:
                avail = 0
                lambdaVal = lambdaVal*(1-deplSpeed)
                if rPi:
                    getTreats()
                snd1.play(loops=0)
                # logStr = "{time} - Click reward\n".format(time=time.time()-startTime)
            else:
                snd2.play(loops=0)
                # logStr = "{time} - Click wrong\n".format(time=time.time()-startTime)
            # fidLog.write(logStr)
        elif (time.time()-startClick)>quittime:
            quitprogram()
        wasClicked = 1
    else:
        wasClicked = 0

    pygame.event.pump()

    # update stim parameters
    lambdaVal = lambdaVal + replSpeed*(1-lambdaVal)/refreshRate

    pup = 1/stimTau
    pdown = pup*(1-lambdaVal)/lambdaVal

    if (avail==0) & (numpy.random.rand()<(pup/refreshRate)):
        avail = 1
    elif (avail==1) & (numpy.random.rand()<(pdown/refreshRate)):
        avail = 0

    # write in data files
    dataStr = "{time},{lamb},{tau},{pup},{pdown},{avail},{click}\n".format(time=time.time()-startTime,lamb=lambdaVal,tau=stimTau,pup=pup,pdown=pdown,avail=avail,click=wasClicked)
    fidData.write(dataStr)

    # generate stimulus
    Ctemp = makeComplexSpectrum(powerSpectrum)
    Cnew = inversePower*Cold + numpy.sqrt(1-inversePower**2)*Ctemp
    Cold = Cnew

    stimMean = colMin+(colMax-colMin)*lambdaVal

    I = numpy.fft.ifft2(Cnew)

    I = numpy.angle(I+stimVar*numpy.exp(1j*stimMean))
    I = 0.5*I/math.pi
    I = (I<=0)*(I+1) + (I>0)*I
    I = clut[numpy.asarray(numpy.floor(nclutpoints*I), dtype=int)]

    pygame.surfarray.blit_array(win,I)

    pygame.draw.circle(win,((1-avail)*255,(1-avail)*255,(1-avail)*255),winCenter,50)

    pygame.display.flip()
