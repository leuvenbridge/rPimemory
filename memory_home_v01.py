

# load libraries
import os, sys, time, math, random, pygame, numpy, imageio
from pygame.locals import *
from foraging_home_ping import *

try:
    rPi = 1
    import RPi.GPIO as io
    import ft5406
except ImportError:
    rPi = 0
    pass


# LOG ENTRIES
# 1st col: time
# 2nd col: event type (1=touch, 2=pellet, 3=quit options, 4=motor action)
# 3rd col: event value (touhes: avail=0/1; pellets=1; quit: 1=reward max,
#           2=button press, 3="q" press and 4=pellet failing to drop;
#           motor: 1=ck, 2=cck


# stim param
imagesFolder = '/home/pi/Pictures/png4/'
screenWidth = 800
screenHeight = 480
refreshRate = 60
rewardsMax = 200
timeMax = 1
timeOut = 1
stimScale = 2


# feedback params
sndFreq1 = 1000
sndFreq2 = 500
sndDur = 0.2
sndFadeDur = 0.01
sndSampFreq = 22050

# motor params
motorStepsMax = 100 # 50 steps for 1 drop
motorStepsWait = 0.01
motorStepsUnstick = 25
motorAttempts = 5
motorCurrStep = -1
pelletDropped = 0

# pins params
pinEnable = 4
pinMotor = (17,19,27,26)
pinButton = 21
pinLedI = 18
pinLedO = 23

# system param
pingInterval = 10


# define functions
def quitprogram(circ):
    logStr = "\n{time},3,circ".format(time=time.time()-startTime)
    fidLog.write(logStr)

    fidLog.close()
    fidData.close()
    if (monkey==7):
        os.remove(dataPath)
        os.remove(logPath)

    pygame.mouse.set_visible(1)
    pygame.quit()

    if rPi:
        io.output(pinEnable, False)
        io.output(pinLedI, False)
        for pp in range(4):
            io.output(pinMotor[pp], False)
        io.cleanup()
        if (monkey!=7):
            os.system("shutdown now -h")
        else:
            sys.exit()
    else:
        sys.exit()


if rPi:
    rootPath = "/home/pi/Documents/git/rPi"

    # rotate motor
    def motor_rotate(step):
        ## half steps - higher accuracy
        # stepSequence = numpy.array([[1,0,0,1],[1,0,0,0],[1,1,0,0],[0,1,0,0],[0,1,1,0],[0,0,1,0],[0,0,1,1],[0,0,0,1]])
        ## full steps - maximum torque
        stepSequence = numpy.array([[1,0,0,1],[1,1,0,0],[0,1,1,0],[0,0,1,1]])
        for coil in range(4):
            io.output(pinMotor[coil], int(stepSequence[step,coil]))

    # freezes motor in current state
    def motor_stop():
        # forces fast stop
        for pin in range(4):
            io.output(pinMotor[pin], True)
        # shut down coils
        for pin in range(4):
            io.output(pinMotor[pin], False)

    # rotate clockwise until drop
    def motor_ck(startingStep):
        global pelletDropped
        currStep = startingStep
        for ss in range(motorStepsMax):
            currStep = currStep+1
            if (currStep>3):
                currStep = 0
            motor_rotate(currStep)
            time.sleep(motorStepsWait)
            if pelletDropped:
                break
        return currStep

    # rotate counter-clockwise for half a turn
    def motor_cck(startingStep):
        currStep = startingStep
        for ss in range(motorStepsUnstick):
            currStep = currStep-1
            if (currStep<0):
                currStep = 3
            motor_rotate(currStep)
            time.sleep(motorStepsWait)
        return currStep

    # tries dropping 5 times, if fail shuts off
    def drop_pellet(startingStep):
        global pelletDropped
        pelletDropped = 0
        io.output(pinEnable, True)
        for aa in range(motorAttempts):
            logStr = "\n{time},4,1".format(time=time.time()-startTime)
            fidLog.write(logStr)
            startingStep = motor_ck(startingStep)
            if pelletDropped:
                break
            else:
                logStr = "\n{time},4,2".format(time=time.time()-startTime)
                fidLog.write(logStr)
                startingStep = motor_cck(startingStep)
                if pelletDropped:
                    break
        motor_stop()
        io.output(pinEnable, False)
        if not pelletDropped:
            if (monkey!=7):
                quitprogram(4)
        return startingStep

    # pellet dropping detected
    def photo_callback(chan):
        global pelletDropped
        pelletDropped = 1
        logStr = "\n{time},2,1".format(time=time.time()-startTime)
        fidLog.write(logStr)

    # activate pins
    io.setmode(io.BCM)

    io.setup(pinEnable, io.OUT)
    for pin in range(4):
        io.setup(pinMotor[pin], io.OUT)

    io.setup(pinButton, io.IN, pull_up_down=io.PUD_DOWN)

    io.setup(pinLedI, io.OUT)
    io.output(pinLedI, True)
    io.setup(pinLedO, io.IN, pull_up_down=io.PUD_DOWN)
    io.add_event_detect(pinLedO, io.FALLING, callback=photo_callback)

    # start touchscreen
    ts = ft5406.Touchscreen()

else:
    rootPath = "/Users/baptiste/Documents/python/rPi"


# start pygame
pygame.init()
##win = pygame.display.set_mode((screenWidth,screenHeight), pygame.FULLSCREEN, 32)
win = pygame.display.set_mode((screenWidth,screenHeight), 32)
clock = pygame.time.Clock()
pygame.font.init()
myfont = pygame.font.SysFont('Helvetica', 30)
if rPi:
    pygame.mouse.set_visible(0)
winSize = (screenWidth,screenHeight)
winCenter = (int(screenWidth/2),int(screenHeight/2))


# # makes sounds
# sndBufferSize = int(sndSampFreq*sndDur)
# sndFadeSize = int(sndSampFreq*sndFadeDur)
# sndPlateauSize = int(sndBufferSize-2*sndFadeSize)
#
# fadeIn = numpy.expand_dims(numpy.sin(numpy.linspace(0,numpy.pi/2,sndFadeSize))**2,1)
# fadeOut = numpy.expand_dims(numpy.sin(numpy.linspace(numpy.pi/2,0,sndFadeSize))**2,1)
# plateau = numpy.ones((sndPlateauSize,1))
# window = numpy.vstack((fadeIn,plateau,fadeOut))
# sine1 = numpy.expand_dims(numpy.sin(numpy.linspace(0,2*numpy.pi*sndFreq1*sndDur,sndBufferSize)),1)
# sine2 = numpy.expand_dims(numpy.sin(numpy.linspace(0,2*numpy.pi*sndFreq2*sndDur,sndBufferSize)),1)
# sndVec1 = 32768*sine1*window
# sndVec2 = 32768*sine2*window
#
# pygame.mixer.init(frequency=sndSampFreq, size=-16, channels=1, buffer=sndBufferSize)
# snd1 = pygame.mixer.Sound(sndVec1.astype('int16'))
# snd2 = pygame.mixer.Sound(sndVec2.astype('int16'))


# select animal
monkeyList = ('Ody','Kraut','Hansel','Lysander','Achilles','Schodinger','Quigley','Test')
textCenter = numpy.array([[150,80],[400,80],[650,80],[150,240],[400,240],[650,240],[150,400],[650,400]])
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


### process params
##if (task==0):
##    
##elif (task==1):
##    
##elif (task==2):
##    
##elif (task==3):
    

# create and load files
currDate = time.localtime(time.time())
clutPath = rootPath + "/clut.txt"
dataPath = rootPath + "/data/monkey"+str(monkey+1)+ "_task"+str(task+1)+ "_{year}-{month}-{day}_{hours}-{minutes}-{seconds}.dat".format(year=currDate[0],month=currDate[1],day=currDate[2],hours=currDate[3],minutes=currDate[4],seconds=currDate[5])
logPath = rootPath + "/data/monkey"+str(monkey+1)+"_task"+str(task+1)+"_{year}-{month}-{day}_{hours}-{minutes}-{seconds}.log".format(year=currDate[0],month=currDate[1],day=currDate[2],hours=currDate[3],minutes=currDate[4],seconds=currDate[5])
pingPath = rootPath + "/data/monkey"+str(monkey+1)+"_task"+str(task+1)+"_{year}-{month}-{day}_{hours}-{minutes}-{seconds}.synch".format(year=currDate[0],month=currDate[1],day=currDate[2],hours=currDate[3],minutes=currDate[4],seconds=currDate[5])
fidData = open(dataPath,"w")
fidLog = open(logPath,"w")
fidSynch = open(logPath,"w")
dataStr = "time,lambda,tau,pup,pdown,avail,click,timeout"
fidData.write(dataStr)
logStr = "time,type,value"
fidLog.write(logStr)
synchStr = "client1,server,client2"
fidSynch.write(synchStr)

### open socket
##sock = serverConnect()


# start main loop
startTime = time.time()

pygame.event.clear()


target = 1
newStim = 0
inTimeOut = 0
rewardsNum = 0
lastTimeOut = -timeOut
lastSwitch = -time.time()
lastPing = -time.time()
giveReward = 0
I = numpy.zeros((screenWidth,screenHeight,3))

while True:

    pygame.event.pump()

    # check mouse
    if sum(pygame.mouse.get_pressed()):
        if not wasClicked:
##            logStr = "\n{time},1,{avail}".format(time=time.time()-startTime,avail=avail)
##            fidLog.write(logStr)
            if target:
                lastSwitch = time.time()
                rewardsNum = rewardsNum+1
                if rPi:
                    motorCurrStep = drop_pellet(motorCurrStep)
                # snd1.play(loops=0)
            else:
                lastTimeOut = time.time()
                # snd2.play(loops=0)
        wasClicked = 1
    else:
        wasClicked = 0

    # check if maxTime reached
    if ((time.time()-lastSwitch)>timeMax) and not inTimeOut:
        newStim = 1
        lastSwitch = time.time()
    elif inTimeOut and (time.time()-lastTimeOut)>timeOut:
        newstim = 1
        
    if newStim:
        target = int(numpy.ceil(numpy.random.rand()-0.5))
        newStim = 0
        stimNumber = int(numpy.ceil(numpy.random.rand()*1000))
        stimName = '{stimFolder:s}/{stimNumber:d}/{stimNumber:d}_r0.png'.format(stimFolder=imagesFolder,stimNumber=stimNumber)
        I = pygame.image.load(stimName)
        oldRect = I.get_rect()
        newRect = tuple(rr*stimScale for rr in oldRect)
        I = pygame.transform.scale(I,newRect[2:4])
        offsetRect = (int((screenWidth-newRect[2])/2),int((screenHeight-newRect[3])/2))


##    # write in data files
##    dataStr = "\n{time},{lamb},{tau},{pup},{pdown},{avail:b},{click:b},{out:b}".format(time=time.time()-startTime,lamb=lambdaVal,tau=stimTau,pup=pup,pdown=pdown,avail=avail,click=wasClicked,out=(time.time()-lastTimeOut)<timeOut)
##    fidData.write(dataStr)


    # display frame
    if not inTimeOut:
        win.fill((0,0,0))
        win.blit(I,offsetRect)
    else:
        win.fill((64,64,64))
    pygame.display.flip()
    clock.tick(refreshRate)


##    # ping server
##    if (time.time()-lastPing)>pingInterval:
##        tList = pingServer(sock)
##        lastPing = time.time()
##        synchStr = "\n{client1},{server},{client2}".format(client1=tList[0],server=tList[2],client2=tList[1])
##        fidSynch.write(synchStr)


    # quit if key press, button press or reward max
    keys = pygame.key.get_pressed()
    if keys[K_q]:
        quitprogram(3)
    if rPi and io.input(pinButton):
        quitprogram(2)
    if (rewardsNum==rewardsMax):
        quitprogram(1)

