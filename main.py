import machine
from machine import Pin, I2C
import time, network
from umqtt.simple import MQTTClient
import ujson
import urequests



#Global Variables
GUARD_ON=False
AP_PASSWORD="earthquake"
AP_NAME="Francine"
myClient=machine.unique_id()
thingspeakURL="mqtt.thingspeak.com"
ts_channelId="227715"
ts_channelWriteAPI="0NRQOTAOFKJGP12Y"
tweet_channelWriteAPI="OTNM7ZQ5I6WYCYRE"


"""
TASKLIST
Deji
Do all the conversion stuff	
Adem
Do all the sensor interface stuff
"""



#setup clock
rtc=machine.RTC()
rtc.datetime((2017, 5, 1, 4, 13, 0, 0, 0))


#setup i2c
i2c = I2C(scl = Pin(5), sda = Pin(4), freq = 100000)
deviceList = i2c.scan() #deviceList[0] = accelerometer, deviceList[1] = ADC

#set up Accelerometer to coninuously output readings
i2c.writeto_mem(deviceList[0],0x20,b'\x17')
time.sleep_ms(100)

#function definitions
def connect_network():
	sta_if = network.WLAN(network.STA_IF); sta_if.active(True)
	sta_if.connect(AP_NAME,AP_PASSWORD)
	while sta_if.isconnected() == False:
		time.sleep_ms(10)
	print("Network Connected")
	

def tweet_alert(message,user_id):
	API_KEY=tweet_channelWriteAPI
	url="http://api.thingspeak.com/apps/thingtweet/1/statuses/update?api_key="
	fill="&status="
	url=url+API_KEY+fill
	tweet="@"+user_id+" "+message+" #bicicle"
	print("Tweet sent to "+user_id)
	url=url+tweet
	response=urequests.get(url)
	
def send_data_MQTT(data,field_id):
	connect_network()
	client=MQTTClient(myClient,thingspeakURL)
	client.connect()
	print("MQTT Connected")
	credentials="channels/{:s}/publish/{:s}".format(ts_channelId, ts_channelWriteAPI)
	payload="field"+str(field_id)+"={:d}".format(data)
	client.publish(credentials, payload)
	print("published")
	client.disconnect()
	
def measureLight(): #returns raw value from ADC input with LDR
	i2c.writeto_mem(deviceList[1],0x01,b'\xc1\x03')
	time.sleep(0.5)
	return convertADCtoValue(i2c.readfrom_mem(deviceList[1],0x00,2))
	
def measureTemp(): #returns raw value from ADC input with Thermistor
	i2c.writeto_mem(deviceList[1],0x01,b'\xd1\x03')
	time.sleep(0.5)
	return convertADCtoValue(i2c.readfrom_mem(deviceList[1],0x00,2))
	
def button_depress(): #Returns true if button press event detected
	i2c.writeto_mem(deviceList[1],0x01,b'\xe1\x03')
	time.sleep(0.5)
	if(convertADCtoValue(i2c.readfrom_mem(deviceList[1],0x00,2)) > 0x0100):
		return False
	else:
		return True
	
def button_release(): #Returns true if button release event detected
	i2c.writeto_mem(deviceList[1],0x01,b'\xe1\x03')
	time.sleep(0.5)
	if(convertADCtoValue(i2c.readfrom_mem(deviceList[1],0x00,2)) > 0x0100):
		return True
	else:
		return False
	
def convertADCtoValue(data):
	value = data[1] + ((0x7f & data[0])<<8)
	if (data[0] > 0x8000):
		value -= 0x8000
	return int(value)
	
def getaccelvalues():  #returns list with the xyz components
	out = []
	for i in range(0x28, 0x2d, 2): #cycles through memory with angle data
		data1 = i2c.readfrom_mem(deviceList[0], i, 1) #memory access for LSBs
		data2 = i2c.readfrom_mem(deviceList[0], i+1, 1) #memory acces for MSBs
		value = (int(data2[0]) << 2) + (int(data1[0]) >> 6) #concatinate data
		if (0x80 & data2[0] == 0x80): #check if negative and adjust value so int output is also negative
				value -= 1024
		out.append(value)
	return out
	
def sigAccelChange(prev):
	data = getaccelvalues()
	for i in range(0,3):
		if (abs(prev[i]-data[i]) > 10):
			return True
	prev = data
	return False

#button interface variables
PRESS_STATE = False
RELEASE_STATE = False	
previousXYZ = []
for i in range(0,3):
	previousXYZ.append(0) #filthy
timething = 0
	
	
while True:

	while PRESS_STATE == False:
		#IDLE mode normal
		print('IDLE MODE')
		
		PRESS_STATE = button_depress()
	PRESS_STATE = False
	
	while RELEASE_STATE == False:
		#IDLE mode button press
		RELEASE_STATE = button_release()
	RELEASE_STATE = False
	
	previousXYZ = getaccelvalues() #set the values for the 
	
	while PRESS_STATE == False:
		#GUARD mode normal
		"""
		#nominal guarding
		#loop exit upon unlock confirmation from user
		#pressing button can prempt tamper alert to poll broker for unlock confirmation
		"""
		
		if(rtc.datetime()[6]>=10): 
			#check temperature and light intensity
			#read the temperature and light intensity
			lightData=measureLight()
			tempData=measureTemp()
			accData = getaccelvalues()
			print(lightData,' ',tempData,' ',accData)
			#decode the ADC value into a real value
			#convert into JSON
			#sends it to broker
				#connect to the network
				#set up MQTT
				#send the packet
				#Disconnect from the network
			#Reset the timer
			rtc.datetime((2017, 5, 1, 4, 13, 0, 0, 0))
			timething = 0
			
			#Accelerometer
		if(rtc.datetime()[6]>=timething):
			timething += 1
			if(sigAccelChange(previousXYZ) == True):
				print('Alarm')
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
			
		PRESS_STATE = button_depress()
	PRESS_STATE = False
	
	while RELEASE_STATE == False:
		#GUARD mode button press
		RELEASE_STATE = button_release()
	RELEASE_STATE = False