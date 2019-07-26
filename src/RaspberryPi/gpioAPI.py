from statistics import mean
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO_TRIGGER = 5
GPIO_ECHO = 0
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

#BASED ON THE BOOLEAN VALUE ON status, IT TURNS ON OR OFF THE LED IN pin
def ledaccess(pin, status):
    GPIO.setup(pin, GPIO.OUT)
    if status:
        GPIO.output(pin, GPIO.HIGH)
    else:
        GPIO.output(pin, GPIO.LOW)

def waitPIR(pin):
    GPIO.setup(pin, GPIO.IN)
    while True:
        if GPIO.input(pin) == GPIO.HIGH:
            break

        time.sleep(0.1)

def get_raw_distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance

def get_distance():
    distances = []
    for i in range(0, 3):
        distances.append(get_raw_distance())
        time.sleep(0.3)

    return round(mean(distances), 1)

if __name__ == '__main__':

    while True:
        waitPIR(6)
        print("Done")
        time.sleep(0.01)
    
    print("exiting..")

    '''ledaccess(21, True)
    time.sleep(5)
    ledaccess(21, False)'''
