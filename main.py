import machine
from machine import Pin, I2C
import time, network
from umqtt.simple import MQTTClient
import ujson

#Global Variables
GUARD_ON=False
AP_PASSWORD="exhibition"
AP_NAME="EEERover"

"""
TASKLIST
Deji
Do all the conversion stuff	
Adem
Do all the sensor interface stuff
Fran
Do all the broker stuff
"""

#function definitions
def button_press(): #Returns true if button press event detected

	return

def measureLight(): #returns raw value from ADC input with LDR
	i2c.writeto_mem(deviceList[1],0x01,b'\xc1\x03')
	return i2c.readfrom_mem(deviceList[1],0x00,2)



#setup clock
rtc=machine.RTC()
rtc.datetime((2017, 5, 1, 4, 13, 0, 0, 0))




#setup i2c
i2c = I2C(scl = Pin(5), sda = Pin(4), freq = 100000)
deviceList = i2c.scan() #deviceList[0] = accelerometer, deviceList[1] = ADC


while True:
	if GUARD_ON=True:
		if button_press()==True:
			GUARD_ON=False
		if(rtc.datetime()[5]>=10):
			#check temperature and light intensity
				#read the temperature and light intensity
				#lightData = measureLight()
				#tempData = measureTemp()
				#decode the ADC value into a real value
				#convert into JSON
			#sends it to broker
				#connect to the network
				#set up MQTT
				#send the packet
				#Disconnect from the network
			#Reset the timer
			rtc.datetime((2017, 5, 1, 4, 13, 0, 0, 0))	
			
			
		#Accelerometer
		#function that returns a bool if the accel value has significantly changed then do IF
			#Sound alarm
				#Piezoelectric transducer
			#send it to broker
				#connect to the network
				#set up MQTT
				#send the packet to alert user
				#Wait for user response
					#subscribe to team_little_boots\disarm
				#Disconnect from the network
	else:
		if button_press()==True:
			GUARD_ON=True
		
	
	
	
	
	
	
	
	
	
	
	