import struct
import RPi.GPIO as GPIO
import signal
import sys
import math
import time
from threading import Timer

# Open the js0 device as if it were a file in read mode.
pipe = open('/dev/input/js0', 'r')

# Define GPIO to use on Pi
GPIO_TRIGGER = 24
GPIO_ECHO = 23


leftMotorPowerPin = 4
leftMotorDirectionPin = 17

rightMotorPowerPin = 27
rightMotorDirectionPin = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(leftMotorDirectionPin, GPIO.OUT)
GPIO.setup(rightMotorDirectionPin, GPIO.OUT)
GPIO.setup(leftMotorPowerPin, GPIO.OUT)
GPIO.setup(rightMotorPowerPin, GPIO.OUT)

# Set pins as output and input
GPIO.setup(GPIO_TRIGGER,GPIO.OUT)  # Trigger
GPIO.setup(GPIO_ECHO,GPIO.IN)      # Echo

# Set trigger to False (Low)
GPIO.output(GPIO_TRIGGER, False)

GPIO.output(leftMotorDirectionPin, GPIO.LOW)
GPIO.output(rightMotorDirectionPin, GPIO.LOW)
GPIO.output(leftMotorPowerPin, GPIO.LOW)
GPIO.output(rightMotorPowerPin, GPIO.LOW)


def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        GPIO.cleanup()  # cleanup all GPIO
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGABRT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


# pwnPin = 18
# GPIO.setup(pwnPin, GPIO.OUT)
# pwm = GPIO.PWM(pwnPin, 50)
# dc = 95
# pwm.start(dc)

# Boutons dessus
BTN_Y = 3
BTN_X = 2
BTN_A = 0
BTN_B = 1
BTN_START = 7
BTN_BACK = 6

# boutons avant
BTN_LB = 4
BTN_RB = 5

# Bouton croix gauche
BTN_CROSS_X_AXIS = 6
BTN_CROSS_Y_AXIS = 7

# Mini joystick gauche
STICK_LEFT_X_AXIS = 0
STICK_LEFT_Y_AXIS = 1

# Mini joystick droite
STICK_RIGHT_X_AXIS = 3
STICK_RIGHT_Y_AXIS = 4

# Gachettes
FIRE_LEFT = 2
FIRE_RIGHT = 5


'''The Joystick class is a GObject that sends signals that represent 
Joystick events''' 
EVENT_BUTTON = 0x01  # button pressed/released 
EVENT_AXIS = 0x02  # axis moved  
EVENT_INIT = 0x80  # button/axis initialized  
# see http://docs.python.org/library/struct.html for the format determination 
EVENT_FORMAT = "IhBB" 
EVENT_SIZE = struct.calcsize(EVENT_FORMAT) 

# 0 => OFF
# +1 => GO AHEAD
# -1 => GO BACK
rightMotorStatus = 0
leftMotorStatus = 0
AXIS_ERROR = 3

def buttonPressed(buttonNumber, isUp):
    print 'Button pressed ', buttonNumber, " UP", isUp
    global dc
    
    if buttonNumber == BTN_B:
        if isUp == False:
            goOnMotor('right')
        else:
            stopMotor('right')
    elif buttonNumber == BTN_X:
        if isUp == False:
            goOnMotor('left')
        else:
            stopMotor('left')

    if buttonNumber == BTN_Y:
        if isUp == False:
            goOnMotors()
        else:
            stopMotors()
    elif buttonNumber == BTN_A:
        if isUp == False:
            goBackMotors()
        else:
            stopMotors()

    
def crossPressed(buttonNumber, value):
    print 'Cross pressed ', buttonNumber, " UP", value
    global dc
    
    if value == 0:
        stopMotors()
    else:    
        if buttonNumber == BTN_CROSS_X_AXIS:
            if value > 0:
                goBackMotor('right')
                goOnMotor('left')
            else:
                goBackMotor('left')
                goOnMotor('right')
        elif buttonNumber == BTN_CROSS_Y_AXIS:
            if value > 0:
                goOnMotors()
            else :
                goBackMotors()

#     if buttonNumber == BTN_Y:
#         dc = dc + 5
#         print 'Faster'
#     elif buttonNumber == BTN_A:
#         dc = dc - 5
#         print 'Slower'
#     
#     if (dc > 100): dc = 100
#     if (dc < 0): dc = 0
#     
#     pwm.ChangeDutyCycle(dc)
    
    
def axisChange(axisNumber, axisValue):
    # print 'Axis changed ', axisNumber, axisValue
    
    if (axisNumber == STICK_RIGHT_Y_AXIS):
        # print "Right motor " + str(axisValue) + " prev=" + str(rightMotorStatus)
        if math.fabs(axisValue) < AXIS_ERROR and rightMotorStatus != 0:
            updateMotorState ('right', 0)
        elif axisValue > AXIS_ERROR and rightMotorStatus <= AXIS_ERROR:
            updateMotorState ('right', 1)
        elif axisValue < -AXIS_ERROR and rightMotorStatus >= AXIS_ERROR:
            updateMotorState ('right', -1)
    
    if (axisNumber == STICK_LEFT_Y_AXIS):
        # print "Left motor " + str(axisValue) + " prev=" + str(leftMotorStatus)
        if (math.fabs(axisValue) < AXIS_ERROR) and (leftMotorStatus != 0):
            updateMotorState ('left', 0)
        elif (axisValue > AXIS_ERROR) and (leftMotorStatus <= AXIS_ERROR):
            updateMotorState ('left', 1)
        elif (axisValue < -AXIS_ERROR) and (leftMotorStatus >= AXIS_ERROR):
            updateMotorState ('left', -1)    
                                    
def updateMotorState (motorName, newState):
    if newState == 0:
        stopMotor(motorName)        
    elif newState == 1:
        goOnMotor(motorName)
    elif newState == -1:
        goBackMotor(motorName)

def stopMotor(motorName):
    # set default motor direction front
    # powerOff motor
    print motorName + ' motor STOPPED'
    global leftMotorStatus, rightMotorStatus
    
    if motorName == 'left':
        leftMotorStatus = 0
        GPIO.output(leftMotorPowerPin, GPIO.LOW)
        GPIO.output(leftMotorDirectionPin, GPIO.LOW)
    else:
        rightMotorStatus = 0
        GPIO.output(rightMotorPowerPin, GPIO.LOW)
        GPIO.output(rightMotorDirectionPin, GPIO.LOW)
        
def stopMotors():
    # set default motor direction front
    # powerOff motor
    print 'left+right motors STOPPED'
    global leftMotorStatus, rightMotorStatus
    
    leftMotorStatus = 0
    GPIO.output(leftMotorPowerPin, GPIO.LOW)
    GPIO.output(leftMotorDirectionPin, GPIO.LOW)

    rightMotorStatus = 0
    GPIO.output(rightMotorPowerPin, GPIO.LOW)
    GPIO.output(rightMotorDirectionPin, GPIO.LOW)

def goOnMotors():
    # set  motor direction front
    # powerON motor
    print 'left+right motor AHEAD'
    global leftMotorStatus, rightMotorStatus
    GPIO.output(leftMotorPowerPin, GPIO.HIGH)
    GPIO.output(leftMotorDirectionPin, GPIO.LOW)
    leftMotorStatus = 1
    GPIO.output(rightMotorPowerPin, GPIO.HIGH)
    GPIO.output(rightMotorDirectionPin, GPIO.LOW)
    rightMotorStatus = 1

def goOnMotor(motorName):
    # set  motor direction front
    # powerON motor
    print motorName + ' motor AHEAD'
    global leftMotorStatus, rightMotorStatus
    
    if motorName == 'left':
        GPIO.output(leftMotorPowerPin, GPIO.HIGH)
        GPIO.output(leftMotorDirectionPin, GPIO.LOW)
        leftMotorStatus = 1
    else:
        GPIO.output(rightMotorPowerPin, GPIO.HIGH)
        GPIO.output(rightMotorDirectionPin, GPIO.LOW)
        rightMotorStatus = 1
        
def goBackMotor(motorName):
    # set  motor direction back
    # powerON motor
    print motorName + ' motor BACK'
    global leftMotorStatus, rightMotorStatus


    if motorName == 'left':
        GPIO.output(leftMotorPowerPin, GPIO.HIGH)
        GPIO.output(leftMotorDirectionPin, GPIO.HIGH)
        leftMotorStatus = -1
    else:
        GPIO.output(rightMotorPowerPin, GPIO.HIGH)
        GPIO.output(rightMotorDirectionPin, GPIO.HIGH)
        rightMotorStatus = -1

def goBackMotors():
    # set  motor direction back
    # powerON motor
    print 'left+right motors BACK'
    global leftMotorStatus, rightMotorStatus
    GPIO.output(leftMotorPowerPin, GPIO.HIGH)
    GPIO.output(leftMotorDirectionPin, GPIO.HIGH)
    leftMotorStatus = -1

    GPIO.output(rightMotorPowerPin, GPIO.HIGH)
    GPIO.output(rightMotorDirectionPin, GPIO.HIGH)
    rightMotorStatus = -1

def getDistrance():
    print "Distance acquisition"
    
    # Set trigger to False (Low)
    GPIO.output(GPIO_TRIGGER, False)
    
    # Allow module to settle
    time.sleep(0.5)
    
    # Send 10us pulse to trigger
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    start = time.time()
    while GPIO.input(GPIO_ECHO)==0:
        start = time.time()
    
    while GPIO.input(GPIO_ECHO)==1:
        stop = time.time()
    
    # Calculate pulse length
    elapsed = stop-start
    
    # Distance pulse travelled in that time is time
    # multiplied by the speed of sound (cm/s)
    distance = elapsed * 34000
    
    # That was the distance there and back so halve the value
    distance = distance / 2
    
    print "Distance : %.1f" % distance
    return distance


def testCollision():
    if getDistrance() < 5.0:
        print "Collision detected !"
        stopMotors()
        
    Timer(2, testCollision, ()).start()
        
try:
    print "Ready"

    Timer(2, testCollision, ()).start()
    
    # Loop forever.
    while 1:

        # For each character read from the /dev/input/js0 pipe...
        read_event = pipe.read(EVENT_SIZE)
 
        evtTime, value, evt_type, number = struct.unpack(EVENT_FORMAT, read_event)
 
        # append the integer representation of the unicode character read to the msg list.
        # msg += [ord(char)
        
                    
        # Button event if 6th byte is 1
        if evt_type == EVENT_BUTTON:
#                 btnIsUp = True
            if value == 1:
                btnIsUp = False
            else:
                btnIsUp = True

            buttonPressed(number, btnIsUp)
         
        # Axis event if 6th byte is 2
        elif evt_type == EVENT_AXIS:
            # get the event structure values from  the read event  
            axisChange(number, value)


except (KeyboardInterrupt, SystemExit):  # If CTRL+C is pressed, exit cleanly:
    GPIO.cleanup()  # cleanup all GPIO
