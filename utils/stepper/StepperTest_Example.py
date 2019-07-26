from Adafruit_MotorShield import Adafruit_MotorShield
from Adafruit_StepperMotor import Adafruit_StepperMotor
import time

# Create the motor shield object with the default I2C address
AFMS = Adafruit_MotorShield()
# Or, create it with a different I2C address (say for stacking)
# AFMS = Adafruit_MotorShield(0x61); 

# Connect a stepper motor with 200 steps per revolution (1.8 degree)
# to motor port #2 (M3 and M4)
myMotor = AFMS.getStepper(200, 1)

AFMS.begin() # create with the default frequency 1.6KHz
#AFMS.begin(1100);  #// OR with a different frequency, say 1KHz

myMotor.setSpeed(4000);  # 10 rpm

try:
	steps = 0
	start = time.time()
	while (True):
		steps += 50
		myMotor.step(50, Adafruit_StepperMotor.FORWARD, Adafruit_StepperMotor.DOUBLE)

		if steps % 200 == 0:
			print("Revolutions: %d" % int(steps / 200))

except KeyboardInterrupt:
	myMotor.release() #remove current flow accross motor
	print ("Total steps: %d " % steps)
	print ("Revolutions: %d" % int(steps / 200))
	print ("Total time: %.2f" % round(time.time() - start, 2))

