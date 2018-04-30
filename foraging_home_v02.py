
# load libraries
import os, sys, time, math, random, pygame, numpy, imageio
from pygame.locals import *

try:
    rPi = 1
    import RPi.GPIO as io
except ImportError:
    rPi = 0
    pass


# stim param
screenWidth = 800
screenHeight = 480
refreshRate = 60
movMax = 10
rewardsMax = 50
diskSize = int(50)

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
motorStepsNum = 20
motorStepWait = 0.001
motorCurrStep = -1

# pins params
pinEnable = 2
pinMotor = (13,19,4,3)
pinButton = 26


# others
quitTime = 5


# define functions
def quitprogram():
    fidLog.close()
    fidData.close()
    pygame.mouse.set_visible(1)
    pygame.quit()
    sys.exit()
    if rPi:
        os.system("shutdown now -h")

if rPi:
    rootPath = "/home/pi/Documents/git/rPi"

    io.setmode(io.BCM)

    io.setup(pinEnable, io.OUT)
    for pin in range(4):
        io.setup(pinMotor[pin], io.OUT)

    io.setup(pinButton, io.IN)
    io.add_event_detect(pinButton, io.RISING)
    #io.add_event_callback(pinButton, buttonCallback)

    def buttonCallback():
        logStr = "{time} - Button pressed\n".format(time=time.time()-startTime)
        fidLog.write(logStr)
        getTreats()
        snd1.play(loops=0)

    def motor_ck(step):
        stepSequence = numpy.array([[1,0,1,0],[1,0,0,1],[0,1,0,1],[0,1,1,0]])
        for coil in range(4):
            print(step, coil)
            print(pinMotor[coil])
            print(stepSequence[step,coil])
            io.output(pinMotor[coil], int(stepSequence[step,coil]))
            
    def motor_stop():
        # forces fast stop
        for pin in range(4):
            io.output(pinMotor[pin], True)
        # shut down coils
        for pin in range(4):
            io.output(pinMotor[pin], False)

    def getTreats():
        global motorCurrStep
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
#win = pygame.display.set_mode((screenWidth,screenHeight), 32)
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


# display menu
textSurf1 = myfont.render('Training 1', False, (0, 0, 0))
textSurf2 = myfont.render('Training 2', False, (0, 0, 0))
textSurf3 = myfont.render('Training 3', False, (0, 0, 0))
textSurf4 = myfont.render('Training 4', False, (0, 0, 0))

while True:
    mousePos = pygame.mouse.get_pos()
    pygame.mouse.set_pos(mousePos)
    
    win.fill((128,128,128))
    pygame.draw.rect(win, (0,0,0), (150,80,200,120), 4)
    pygame.draw.rect(win, (0,0,0), (450,80,200,120), 4)
    pygame.draw.rect(win, (0,0,0), (150,280,200,120), 4)
    pygame.draw.rect(win, (0,0,0), (450,280,200,120), 4)
    win.blit(textSurf1,(250-0.5*textSurf1.get_rect().width,140-0.5*textSurf1.get_rect().height))
    win.blit(textSurf2,(550-0.5*textSurf2.get_rect().width,140-0.5*textSurf2.get_rect().height))
    win.blit(textSurf3,(250-0.5*textSurf3.get_rect().width,340-0.5*textSurf3.get_rect().height))
    win.blit(textSurf4,(550-0.5*textSurf4.get_rect().width,340-0.5*textSurf4.get_rect().height))
    pygame.draw.circle(win, (255,0,0), mousePos, 4, 0)
    pygame.display.flip()
    clock.tick(refreshRate)

    if sum(pygame.mouse.get_pressed()):
        print(mousePos)
        row = -1
        col = -1
        if (mousePos[0]>150) and (mousePos[0]<350):
            col = 1
        elif (mousePos[0]>450) and (mousePos[0]<650):
            col = 2
        if (mousePos[1]>80) and (mousePos[1]<300):
            row = 1
        elif (mousePos[1]>280) and (mousePos[1]<400):
            row = 2
        if (col>0) and (row>0):
            task = col+2*(row-1)
            break
    pygame.event.pump()

while sum(pygame.mouse.get_pressed()):
    pygame.event.pump()
    pygame.time.wait(1)


# process params
lambdaVal = 1
stimTau = 0.1
replSpeed = 0.5
deplSpeed = 0.5
if (task!=4):
    stimTau = 0.1
else:
    stimTau = 0.01


# select animal
textSurf1 = myfont.render('Ody', False, (0, 0, 0))
textSurf2 = myfont.render('Kraut', False, (0, 0, 0))
textSurf3 = myfont.render('Hansel', False, (0, 0, 0))
textSurf4 = myfont.render('Lysander', False, (0, 0, 0))
textSurf5 = myfont.render('Achilles', False, (0, 0, 0))

while True:
    mousePos = pygame.mouse.get_pos()

    win.fill((128,128,128))
    pygame.draw.rect(win, (0,0,0), (50,80,200,120), 4)
    pygame.draw.rect(win, (0,0,0), (300,80,200,120), 4)
    pygame.draw.rect(win, (0,0,0), (550,80,200,120), 4)
    pygame.draw.rect(win, (0,0,0), (50,280,200,120), 4)
    pygame.draw.rect(win, (0,0,0), (300,280,200,120), 4)
    win.blit(textSurf1,(150-0.5*textSurf1.get_rect().width,140-0.5*textSurf1.get_rect().height))
    win.blit(textSurf2,(400-0.5*textSurf2.get_rect().width,140-0.5*textSurf2.get_rect().height))
    win.blit(textSurf3,(650-0.5*textSurf3.get_rect().width,140-0.5*textSurf3.get_rect().height))
    win.blit(textSurf4,(150-0.5*textSurf4.get_rect().width,340-0.5*textSurf4.get_rect().height))
    win.blit(textSurf5,(400-0.5*textSurf5.get_rect().width,340-0.5*textSurf5.get_rect().height))
    pygame.draw.circle(win, (255,0,0), mousePos, 4, 0)
    pygame.display.flip()
    clock.tick(refreshRate)

    if sum(pygame.mouse.get_pressed()):
        row = -1
        col = -1
        if (mousePos[0]>50) and (mousePos[0]<250):
            col = 1
        elif (mousePos[0]>300) and (mousePos[0]<500):
            col = 2
        elif (mousePos[0]>550) and (mousePos[0]<750):
            col = 3
        if (mousePos[1]>80) and (mousePos[1]<300):
            row = 1
        elif (mousePos[1]>280) and (mousePos[1]<400):
            row = 2
        if (col>0) and (row>0):
            monkey = col+3*(row-1)-1
            break
    pygame.event.pump()

while sum(pygame.mouse.get_pressed()):
    pygame.event.pump()
    pygame.time.wait(1)


# create and load files
monkeyList = ('ody','kraut','hansel','lysander','achilles')
currDate = time.localtime(time.time())
clutPath = rootPath + "/clut.txt"
dataPath = rootPath + "/data/"+monkeyList[monkey]+"_task"+str(task)+"_data_{year}-{month}-{day}_{hours}:{minutes}:{seconds}".format(year=currDate[0],month=currDate[1],day=currDate[2],hours=currDate[3],minutes=currDate[4],seconds=currDate[5])
logPath = rootPath + "/data/"+monkeyList[monkey]+"_task"+str(task)+"_log_{year}-{month}-{day}_{hours}:{minutes}:{seconds}".format(year=currDate[0],month=currDate[1],day=currDate[2],hours=currDate[3],minutes=currDate[4],seconds=currDate[5])
fidData = open(dataPath,"w")
fidLog = open(logPath,"w")
dataStr = "time,lambda,tau,pup,pdown,avail,click\n"
fidData.write(dataStr)


# start main loop
startTime = time.time()
lastFrame = time.time()

keyWasDown = 0
wasClicked = 0
movNum = 0
playing = False
lambdaVal = 0.5
avail = 1
rewardsNum = 0

while True:

    switch = 0

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
                if (task==3) or (task==4):
                    avail = 0
                    lambdaVal = lambdaVal*(1-deplSpeed)
                    switch = 1
                rewardsNum = rewardsNum+1
                if rPi:
                    getTreats()
                snd1.play(loops=0)
                logStr = "{time} - Correct\n".format(time=time.time()-startTime)
                if (rewardsNum==rewardsMax):
                    quitprogram()
            else:
                snd2.play(loops=0)
                logStr = "{time} - Wrong\n".format(time=time.time()-startTime)
            fidLog.write(logStr)
        elif (time.time()-startClick)>quitTime:
            quitprogram()
        wasClicked = 1
    else:
        wasClicked = 0

    pygame.event.pump()


    # update stim parameters
    if (task==1):
        pup = refreshRate
        pdown = 0
    elif (task==2) or (task==3):
        pup = 0.1
        pdown = 0.1
    else:
        pup = 1/stimTau
        pdown = pup*(1-lambdaVal)/lambdaVal
        lambdaVal = lambdaVal + replSpeed*(1-lambdaVal)/refreshRate

    if (avail==0) & (numpy.random.rand()<(pup/refreshRate)):
        avail = 1
        switch = 1
    elif (avail==1) & (numpy.random.rand()<(pdown/refreshRate)):
        avail = 0
        switch = 1

    # write in data files
    dataStr = "{time},{lamb},{tau},{pup},{pdown},{avail},{click}\n".format(time=time.time()-startTime,lamb=lambdaVal,tau=stimTau,pup=pup,pdown=pdown,avail=avail,click=wasClicked)
    fidData.write(dataStr)


    # load movie
    if (playing==0) or (switch==1):
        movNum = int(numpy.ceil(numpy.random.rand()*10))
        if avail:
            filename = './stim/brownian_mu1.000_k0.020_'+str(movNum)+'.mp4'
        else:
            filename = './stim/brownian_mu0.000_k0.020_'+str(movNum)+'.mp4'
        vid = imageio.get_reader(filename,  'ffmpeg')
        nFrames = vid.get_length()/3
        currFrame = 0
        playing = 1

    # read next frame
    if not currFrame<(nFrames-1):
        playing = 0
    currFrame = currFrame+1
    I = vid.get_data(currFrame)


    # display frame
    pygame.surfarray.blit_array(win,I)
    if avail:
        pygame.draw.circle(win,(0,0,0),winCenter,diskSize)
    pygame.display.flip()
    clock.tick(refreshRate)
