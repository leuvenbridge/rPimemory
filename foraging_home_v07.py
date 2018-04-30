
# load libraries
import os, sys, time, math, random, pygame, numpy, imageio
from pygame.locals import *

try:
    rPi = 1
    import RPi.GPIO as io
    import ft5406
except ImportError:
    rPi = 0
    pass


# stim param
screenWidth = 800
screenHeight = 480
refreshRate = 60
movMax = 10
rewardsMax = 100
diskSize = int(100)

# color params
colMin = -0.50*math.pi
colMax = 0
colvar = 0.1
speedChange = 20

# feedback params
sndFreq1 = 1000
sndFreq2 = 500
sndDur = 0.2
sndFadeDur = 0.01
sndSampFreq = 22050

# motor params
motorStepsMax = 50
motorStepWait = 0.01
motorCurrStep = -1
motorStop = 0

# pins params
pinEnable = 2
pinMotor = (19,3,13,4)
pinButtonI = 17
pinButtonO = 26
pinLedI = 18
pinLedO = 23


# define functions
def quitprogram():
    fidLog.close()
    fidData.close()
    pygame.mouse.set_visible(1)
    pygame.quit()

    if rPi:
        io.output(pinEnable, False)
        io.output(pinButtonI, False)
        io.output(pinLedI, False)
        for pp in range(4):
            io.output(pinMotor[pp], False)
        io.cleanup()
        os.system("shutdown now -h")
    else:
        sys.exit()


if rPi:
    rootPath = "/home/pi/Documents/git/rPi"

    def motor_ck(step):
        stepSequence = numpy.array([[1,0,0,1],[1,0,0,0],[1,1,0,0],[0,1,0,0],[0,1,1,0],[0,0,1,0],[0,0,1,1],[0,0,0,1]])
        for coil in range(4):
            io.output(pinMotor[coil], int(stepSequence[step,coil]))

    def motor_stop():
        # forces fast stop
        for pin in range(4):
            io.output(pinMotor[pin], True)
        # shut down coils
        for pin in range(4):
            io.output(pinMotor[pin], False)

    def getTreats():
        global motorCurrStep, motorStop
        motorStop = 0
        io.output(pinEnable, True)
        for step in range(motorStepsMax):
            motorCurrStep = motorCurrStep+1
            if (motorCurrStep>7):
                motorCurrStep = 0
            motor_ck(motorCurrStep)
            time.sleep(motorStepWait)
            if motorStop:
                break
        motor_stop()
        io.output(pinEnable, False)

    def photoCallback(chan):
        global motorStop
        motorStop = 1
        logStr = "{time},2,1\n".format(time=time.time()-startTime)
        fidLog.write(logStr)

    # activate pins
    io.setmode(io.BCM)

    io.setup(pinEnable, io.OUT)
    for pin in range(4):
        io.setup(pinMotor[pin], io.OUT)

    io.setup(pinButtonI, io.OUT)
    io.output(pinButtonI, True)
    io.setup(pinButtonO, io.IN, pull_up_down=io.PUD_DOWN)

    io.setup(pinLedI, io.OUT)
    io.output(pinLedI, True)
    io.setup(pinLedO, io.IN, pull_up_down=io.PUD_DOWN)
    io.add_event_detect(pinLedO, io.FALLING, callback=photoCallback)


    # start touchscreen
    ts = ft5406.Touchscreen()

else:
    rootPath = "/Users/baptiste/Documents/python/rPi"


# start pygame
pygame.init()
win = pygame.display.set_mode((screenWidth,screenHeight), pygame.FULLSCREEN, 32)
##win = pygame.display.set_mode((screenWidth,screenHeight), 32)
clock = pygame.time.Clock()
pygame.font.init()
myfont = pygame.font.SysFont('Helvetica', 30)
pygame.mouse.set_visible(0)
winSize = (screenWidth,screenHeight)
winCenter = (int(screenWidth/2),int(screenHeight/2))


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


# select animal
monkeyList = ('Ody','Kraut','Hansel','Lysander','Achilles','Schodinger','Quigley')
textCenter = numpy.array([[150,80],[400,80],[650,80],[150,240],[400,240],[650,240],[150,400]])
rectSize = numpy.array([200,120])
textSurf = []
for mm in range(len(monkeyList)):
     textSurf.append(myfont.render(monkeyList[mm], False, (0, 0, 0)))

monkey = -1
while monkey<0:
    win.fill((128,128,128))
    for mm in range(len(monkeyList)):
        pygame.draw.rect(win, (0,0,0), numpy.append(textCenter[mm,:]-0.5*rectSize,rectSize), 4)
        win.blit(textSurf[mm],textCenter[mm,:]-0.5*numpy.array([textSurf[mm].get_rect().width,textSurf[mm].get_rect().height]))
    pygame.display.flip()
    clock.tick(refreshRate)

    click = 0
    if rPi:
        for touch in ts.poll():
            if not touch.valid:
                continue
            else:
                click = 1
                x, y = touch.position
    else:
        pygame.event.pump()
        pos = pygame.mouse.get_pos()
        x = pos[0]
        y = pos[1]
        if sum(pygame.mouse.get_pressed()):
            click = 1

    if click:
        for mm in range(len(monkeyList)):
            if (x>textCenter[mm,0]-0.5*rectSize[0]) and  (x<textCenter[mm,0]+0.5*rectSize[0]) and (y>textCenter[mm,1]-0.5*rectSize[1]) and (y<textCenter[mm,1]+0.5*rectSize[1]):
                monkey = mm
                break

win.fill((128,128,128))
pygame.display.flip()
time.sleep(0.25)


# select task, 1=always on, 2=alternate on/off
textList = ('Training 1', 'Training 2', 'Training 3','Training 4')
textCenter = numpy.array([[250,140],[550,140],[250,340],[550,340]])
rectSize = numpy.array([200,120])
textSurf = []
for tt in range(len(textList)):
     textSurf.append(myfont.render(textList[tt], False, (0, 0, 0)))

task = -1
while task<0:
    win.fill((128,128,128))
    for tt in range(len(textList)):
        pygame.draw.rect(win, (0,0,0), numpy.append(textCenter[tt,:]-0.5*rectSize,rectSize), 4)
        win.blit(textSurf[tt],textCenter[tt,:]-0.5*numpy.array([textSurf[tt].get_rect().width,textSurf[tt].get_rect().height]))
    pygame.display.flip()
    clock.tick(refreshRate)

    click = 0
    if rPi:
        for touch in ts.poll():
            if not touch.valid:
                continue
            else:
                click = 1
                x, y = touch.position
    else:
        pygame.event.pump()
        pos = pygame.mouse.get_pos()
        x = pos[0]
        y = pos[1]
        if sum(pygame.mouse.get_pressed()):
            click = 1

    if click:
        for tt in range(len(textList)):
            if (x>textCenter[tt,0]-0.5*rectSize[0]) and  (x<textCenter[tt,0]+0.5*rectSize[0]) and (y>textCenter[tt,1]-0.5*rectSize[1]) and (y<textCenter[tt,1]+0.5*rectSize[1]):
                task = tt
                break

win.fill((128,128,128))
pygame.display.flip()
time.sleep(0.25)


# process params
avail = 1
if (task==0):
    lambdaVal = 1.0
    replSpeed = 0.0
    deplSpeed = 0.0
    stimTau = 0.016
elif (task==1):
    lambdaVal = 0.8
    replSpeed = 0.0
    deplSpeed = 0.0
    stimTau = 2.0
elif (task==2):
    lambdaVal = 0.5
    replSpeed = 0.5
    deplSpeed = 0.5
    stimTau = 0.5
elif (task==3):
    lambdaVal = 0.5
    replSpeed = 0.5
    deplSpeed = 0.5
    stimTau = 2.0


# create and load files
currDate = time.localtime(time.time())
clutPath = rootPath + "/clut.txt"
dataPath = rootPath + "/data/monkey"+str(monkey+1)+ "_task"+str(task+1)+ "_{year}-{month}-{day}_{hours}-{minutes}-{seconds}.dat".format(year=currDate[0],month=currDate[1],day=currDate[2],hours=currDate[3],minutes=currDate[4],seconds=currDate[5])
logPath = rootPath + "/data/monkey"+str(monkey+1)+"_task"+str(task+1)+"_{year}-{month}-{day}_{hours}-{minutes}-{seconds}.log".format(year=currDate[0],month=currDate[1],day=currDate[2],hours=currDate[3],minutes=currDate[4],seconds=currDate[5])
fidData = open(dataPath,"w")
fidLog = open(logPath,"w")
dataStr = "time,lambda,tau,pup,pdown,avail,click\n"
fidData.write(dataStr)
logStr = "time,type,value\n"
fidLog.write(logStr)


# start main loop
startTime = time.time()

pygame.event.clear()

wasClicked = 0
wasAvail = 1
movNum = 0
playing = False
rewardsNum = 0

while True:

    pygame.event.pump()

    # check keyboard
    keys = pygame.key.get_pressed()
    if keys[K_q]:
        quitprogram()

    # check mouse
    if sum(pygame.mouse.get_pressed()):
        if not wasClicked:
            logStr = "{time},1,{avail}\n".format(time=time.time()-startTime,avail=avail)
            fidLog.write(logStr)
            if avail:
                avail = 0
                lambdaVal = lambdaVal*(1-deplSpeed)
                rewardsNum = rewardsNum+1
                if rPi:
                    getTreats()
                snd1.play(loops=0)

                if (rewardsNum==rewardsMax):
                    quitprogram()
            else:
                snd2.play(loops=0)
        wasClicked = 1
    else:
        wasClicked = 0


    # update stim parameters
    pup = 1/stimTau/refreshRate
    pdown = pup*(1-lambdaVal)/lambdaVal
    lambdaVal = lambdaVal + replSpeed*(1-lambdaVal)/refreshRate

    if (avail==0) & (numpy.random.rand()<pup):
        avail = 1
    elif (avail==1) & (numpy.random.rand()<pdown):
        avail = 0

    # write in data files
    dataStr = "{time},{lamb},{tau},{pup},{pdown},{avail:b},{click:b}\n".format(time=time.time()-startTime,lamb=lambdaVal,tau=stimTau,pup=pup,pdown=pdown,avail=avail,click=wasClicked)
    fidData.write(dataStr)

    # load movie
    if (playing==0) or (wasAvail!=avail):
        movNum = int(numpy.ceil(numpy.random.rand()*10))
        if avail:
            filename = './stim/brownian_mu1.000_k0.020_'+str(movNum)+'.mp4'
        else:
            filename = './stim/brownian_mu0.000_k0.020_'+str(movNum)+'.mp4'
        vid = imageio.get_reader(filename,  'ffmpeg')
        nFrames = vid.get_length()/3
        currFrame = 0
        playing = 1

    wasAvail = avail

    # read next frame
    if currFrame==nFrames:
        playing = 0

    currFrame = currFrame+1
    I = vid.get_data(currFrame)

    # display frame
    pygame.surfarray.blit_array(win,I)
    if avail:
        pygame.draw.circle(win,(0,0,0),winCenter,diskSize)
    pygame.display.flip()
    clock.tick(refreshRate)

    if rPi and io.input(pinButtonO):
        quitprogram()
