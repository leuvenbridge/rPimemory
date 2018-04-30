

# load libraries
try:
    rPi = 1
    import RPi.GPIO as io
    import ft5406
except ImportError:
    rPi = 0
    # pass

import os, sys, time, logging, math, random, pygame, numpy, imageio
from pygame.locals import *
from foraging_home_sqlite import *
from foraging_home_tools import *


logger = logging.getLogger('foraging_home_v13')
hdlr = logging.FileHandler('/var/tmp/foraging_home_v13.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)



# LOG ENTRIES
# 1st col: time
# 2nd col: event type (0=start, 1=touch, 2=pellet, 3=quit options, 4=motor)
# 3rd col: event value (start=1; touhes: avail=0/1; pellets=1; quit: 1=reward max,
#           2=button press, 3='q' press and 4=pellet failing to drop;
#           motor: 1=ck, 2=cck


# stim param
screenWidth = 800
screenHeight = 480
refreshRate = 60
movMax = 10
rewardsMax = 200
diskSize = int(100)
timeOut = 4
timeMin = 2
timeMax = 20

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

# database param
dbName = 'foraging.db'
boxmac = getMAC(rPi)
timeStart = 0


# define functions
def quit_program(circ):
    curs.execute('''INSERT INTO logTable(id,recording,boxmac,timesession,type,value)
            VALUES(NULL,?,?,?,?,?)''', (recordNum, boxmac, time.time()-timeStart, 3, circ))
    conn.commit()
    conn.close()

    pygame.mouse.set_visible(1)
    pygame.quit()

    if rPi:
        io.output(pinEnable, False)
        io.output(pinLedI, False)
        for pp in range(4):
            io.output(pinMotor[pp], False)
        if (monkey!=7):
            io.cleanup()
        else:
            sys.exit()
        os.system('shutdown now -h')
    else:
        sys.exit()


if rPi:
    rootPath = '/home/pi/Documents/git/rPi'
    dbPath = '/home/pi/Documents/'

    ## rotate motor
    def motor_rotate(step):
        ## half steps - higher accuracy
        # stepSequence = numpy.array([[1,0,0,1],[1,0,0,0],[1,1,0,0],[0,1,0,0],[0,1,1,0],[0,0,1,0],[0,0,1,1],[0,0,0,1]])
        ## full steps - maximum torque
        stepSequence = numpy.array([[1,0,0,1],[1,1,0,0],[0,1,1,0],[0,0,1,1]])
        for coil in range(4):
            io.output(pinMotor[coil], int(stepSequence[step,coil]))

    ## freezes motor in current state
    def motor_stop():
        ## forces fast stop
        for pin in range(4):
            io.output(pinMotor[pin], True)
        ## shut down coils
        for pin in range(4):
            io.output(pinMotor[pin], False)

    ## rotate clockwise until drop
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

    ## rotate counter-clockwise for half a turn
    def motor_cck(startingStep):
        currStep = startingStep
        for ss in range(motorStepsUnstick):
            currStep = currStep-1
            if (currStep<0):
                currStep = 3
            motor_rotate(currStep)
            time.sleep(motorStepsWait)
        return currStep

    ## tries dropping 5 times, if fail shuts off
    def drop_pellet(startingStep):
        global pelletDropped
        pelletDropped = 0
        io.output(pinEnable, True)
        for aa in range(motorAttempts):
            curs.execute('''INSERT INTO logTable(id,recording,boxmac,timesession,type,value)
                    VALUES(NULL,?,?,?,?,?)''', (recordNum, boxmac, time.time()-timeStart, 4, 1))
            conn.commit()
            startingStep = motor_ck(startingStep)
            if pelletDropped:
                break
            else:
                curs.execute('''INSERT INTO logTable(id,recording,boxmac,timesession,type,value)
                        VALUES(NULL,?,?,?,?,?)''', (recordNum, boxmac, time.time()-timeStart, 4, 2))
                conn.commit()
                startingStep = motor_cck(startingStep)
                if pelletDropped:
                    break
        motor_stop()
        io.output(pinEnable, False)
        if not pelletDropped and (monkey!=7):
            quit_program(4)
        return startingStep

    ## pellet dropping detected
    def photo_callback(chan):
        global pelletDropped
        pelletDropped = 1
        curs.execute('''INSERT INTO logTable(id,recording,boxmac,timesession,type,value)
                VALUES(NULL,?,?,?,?,?)''', (recordNum, boxmac, time.time()-timeStart, 2, 1))
        conn.commit()

    ## activate pins
    io.setmode(io.BCM)

    io.setup(pinEnable, io.OUT)
    for pin in range(4):
        io.setup(pinMotor[pin], io.OUT)

    io.setup(pinButton, io.IN, pull_up_down=io.PUD_DOWN)

    io.setup(pinLedI, io.OUT)
    io.output(pinLedI, True)
    io.setup(pinLedO, io.IN, pull_up_down=io.PUD_DOWN)
    io.add_event_detect(pinLedO, io.FALLING, callback=photo_callback)

    ## start touchscreen library
    ts = ft5406.Touchscreen()

else:
    rootPath = '/Users/baptiste/Documents/python/rPi'
    dbPath = '/Users/baptiste/Documents/python/'

## start pygame
pygame.init()
win = pygame.display.set_mode((screenWidth,screenHeight), pygame.FULLSCREEN, 32)
# win = pygame.display.set_mode((screenWidth,screenHeight), 32)
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


## select animal
monkeyList = ('Ody','Kraut','Hansel','Lysander','Achilles','Schodinger','Quigley','test')
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


## select task, 1=always on, 2=alternate on/off
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


## process params
if (task==0):
    lambdaVal = 1.0
    replSpeed = 0.0
    deplSpeed = 0.0
    stimTau = 0.016
elif (task==1):
    lambdaVal = 0.5
    replSpeed = 0.0
    deplSpeed = 0.0
    stimTau = 10.0
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


## open database
conn = create_database(dbPath+dbName)
curs = conn.cursor()
curs.execute('''INSERT INTO recordingTable(id,boxmac,monkey,task,timestart)
        VALUES(NULL,?,?,?,?)''', (boxmac, monkey+1, task+1, time.time()))
conn.commit()

curs.execute('''SELECT MAX(id) FROM recordingTable''')
recordNum = curs.fetchone()[0]



## start main loop
timeStart = time.time()
curs.execute('''INSERT INTO logTable(id,recording,boxmac,timesession,type,value)
        VALUES(NULL,?,?,?,?,?)''', (recordNum, boxmac, time.time()-timeStart, 0, 1))
conn.commit()

pygame.event.clear()

avail = 1
wasAvail = 1
wasClicked = 0
movNum = 0
playing = False
rewardsNum = 0
lastTimeOut = -timeOut
lastSwitch = time.time()
giveReward = 0

while True:

    pygame.event.pump()

    ## check mouse
    if sum(pygame.mouse.get_pressed()):
        if not wasClicked:
            curs.execute('''INSERT INTO logTable(id,recording,boxmac,timesession,type,value)
                    VALUES(NULL,?,?,?,?,?)''', (recordNum, boxmac, time.time()-timeStart, 1, avail))
            conn.commit()

            if avail:
                avail = 0
                lastSwitch = time.time()
                lambdaVal = lambdaVal*(1-deplSpeed)
                rewardsNum = rewardsNum+1
                if rPi:
                    motorCurrStep = drop_pellet(motorCurrStep)
                # snd1.play(loops=0)

            else:
                # snd2.play(loops=0)
                if (task==1):
                    lastTimeOut = time.time()
        wasClicked = 1
    else:
        wasClicked = 0


    ## update stim parameters
    pup = 1/stimTau/refreshRate
    pdown = pup*(1-lambdaVal)/lambdaVal
    lambdaVal = lambdaVal + replSpeed*(1-lambdaVal)/refreshRate

    ## check if max duration reached to force switch
    if ((time.time()-max(lastSwitch,lastTimeOut+timeOut))>timeMax):
        forceSwitch = 1
    else:
        forceSwitch = 0

    ## switch if not timeout
    if (time.time()-lastTimeOut)>timeOut:
        if (time.time()-max(lastSwitch,lastTimeOut+timeOut))>timeMin:
            if (avail==0) & ((numpy.random.rand()<pup) | forceSwitch):
                avail = 1
                lastSwitch = time.time()
            elif (avail==1) & ((numpy.random.rand()<pdown) | forceSwitch):
                avail = 0
                lastSwitch = time.time()
    else:
        avail = 0

    ## set to 1 if train 1
    if (task==0):
        avail = 1


    ## write in data file
    preCommit = time.time()
    curs.execute('''INSERT INTO dataTable(id,recording,boxmac,timesession,lambda,tau,pup,pdown,avail,click,timeout)
            VALUES(NULL,?,?,?,?,?,?,?,?,?,?)''', (recordNum, boxmac, time.time()-timeStart, lambdaVal, stimTau, pup, pdown, avail, wasClicked, (time.time()-lastTimeOut)<timeOut))
    conn.commit()
    print(1000*(time.time()-preCommit))

    ## load movie
    if (playing==0) or (wasAvail!=avail):
        movNum = int(numpy.ceil(numpy.random.rand()*10))
        if avail:
            filename = rootPath + '/stim/brownian_mu1.000_k0.050.mp4'
        else:
            filename = rootPath + '/stim/brownian_mu0.000_k0.050.mp4'
        vid = imageio.get_reader(filename,  'ffmpeg')
        nFrames = vid.get_length()/3
        currFrame = 0
        playing = 1

    wasAvail = avail

    ## read next frame
    if (currFrame==nFrames):
        playing = 0
    currFrame = currFrame+1
    I = vid.get_data(currFrame)

    ## display frame
    pygame.surfarray.blit_array(win,I)
    if (time.time()-lastTimeOut)<timeOut:
        win.fill((64,64,64))
    pygame.display.flip()
    clock.tick(refreshRate)

    # quit if key press, button press or reward max
    keys = pygame.key.get_pressed()
    if keys[K_q]:
        quit_program(3)
    if rPi and io.input(pinButton):
        quit_program(2)
    if (rewardsNum==rewardsMax):
        quit_program(1)
