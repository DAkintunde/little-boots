import machine
from machine import Pin, I2C
import time, network
from umqtt.simple import MQTTClient
import ujson
import urequests


#Global Variables
AP_PASSWORD="earthquake" 	#username and password for Francine's phone wifi hotspot
AP_NAME="Francine"			#we needed an extra hotspot so that internet connectivity funcitons like tweeting could take place.  This would ideally be done by imperial wifi in the finished product since it's designed for imperial students
BROKER_NAME="EEERover"					#EERover broker details
BROKER_PASSWORD="exhibition"
myClient=machine.unique_id() 			#set up MQTT unique id
thingspeakURL="mqtt.thingspeak.com"		#broker address and other details for online graphing tool
ts_channelId="227715"
ts_channelWriteAPI="0NRQOTAOFKJGP12Y"
tweet_channelWriteAPI="OTNM7ZQ5I6WYCYRE"
user_id="francinetarta"					#francine's twitter handle to receive bike status updates


#setup clock
rtc=machine.RTC()
rtc.datetime((2017, 5, 1, 4, 13, 0, 0, 0))


#setup i2c
i2c = I2C(scl = Pin(5), sda = Pin(4), freq = 100000)
deviceList = i2c.scan() #deviceList[0] = accelerometer, deviceList[1] = ADC

#set up Accelerometer to coninuously output readings at 1 Hz
i2c.writeto_mem(deviceList[0],0x20,b'\x17')
time.sleep_ms(100)

#function definitions

def thingtweet(event): #all encompassing function for sending tweets
	sta_if = network.WLAN(network.STA_IF); sta_if.active(True)
	sta_if.connect(AP_NAME,AP_PASSWORD)
	while sta_if.isconnected() == False:
		time.sleep_ms(10)
	print("Network Connected")
	tweet_alert(event,user_id)
	print("Now disconnect")
	sta_if.disconnect()

def event_to_message(event): #decodes event name to tweet string
	if event=="move_bike":
		return "Your bike has been moved, you might wanna check that out!"


def tweet_alert(message,user_id): #connects to twitter and tweets
	API_KEY=tweet_channelWriteAPI
	url="http://api.thingspeak.com/apps/thingtweet/1/statuses/update?api_key="
	fill="&status="
	url=url+API_KEY+fill
	tweet="@"+user_id+" "+message
	print("Tweet sent to "+user_id)
	url=url+tweet
	response=urequests.get(url)
	
def send_data_MQTT(light_data,temp_data): #sends light and temperature data to online graphing broker
	sta_if = network.WLAN(network.STA_IF); sta_if.active(True) #connects to phone hotspot
	sta_if.connect(AP_NAME,AP_PASSWORD)
	while sta_if.isconnected() == False: #wait for connection to establish
		time.sleep_ms(10)
	print("Network Connected")
	client=MQTTClient(myClient,thingspeakURL) #set up MQTT and connect to online graphing broker
	client.connect()
	print("MQTT Connected")
	credentials="channels/{:s}/publish/{:s}".format(ts_channelId, ts_channelWriteAPI)
	payload="field1={:d}&field2={:d}\n".format(light_data,temp_data)
	client.publish(credentials, payload)
	print("published")
	client.disconnect() #disconnect from MQTT and phone hotspot
	sta_if.disconnect()
	
def check_user_unlock(block): #connects to EERover broker and waits for a user responce with a code to disarm the device
	sta_if = network.WLAN(network.STA_IF); sta_if.active(True) #connect to EERover network
	sta_if.connect(BROKER_NAME,BROKER_PASSWORD)
	while sta_if.isconnected() == False: #wait for connectoin to be established
		time.sleep_ms(10)
	print("Broker Connected")
	client=MQTTClient(machine.unique_id(),"192.168.0.10")
	client.connect()
	client.set_callback(sub_cb)
	client.subscribe("esys/<team_little_boots>/unlock/1234") #subcribe to a topic with a specific code (here 1234) would be different for different units
	if(block):
		client.wait_msg() #blocking message receive function that waits until the topic is recieved
	else: #blocks operation but only for 1 minute
		rtc.datetime((2017, 5, 1, 4, 13, 0, 0, 0))
		while((rtc.datetime()[5] < 1) and (ALARM_RESET == False)):
			client.check_msg()
			time.sleep_ms(10)
	client.disconnect() #disconnect from broker and network
	sta_if.disconnect()
	
	
def data_to_broker(data): #used periodically to send data to the EERover broker (data already in JSON format)
	sta_if = network.WLAN(network.STA_IF); sta_if.active(True) #set up and connect to EERover network
	sta_if.connect(BROKER_NAME,BROKER_PASSWORD)
	while sta_if.isconnected() == False: #wait for connection to be established
		time.sleep_ms(10)
	print("Broker Connected")
	client=MQTTClient(machine.unique_id(),"192.168.0.10")
	client.connect()
	client.publish('esys/<team_little_boots>',data) #send JSON encoded data to broker
	client.disconnect() #disconect from broker and network
	sta_if.disconnect()

def sub_cb(topic,msg): #callback function that is triggered in wait_msg
	ALARM_RESET = True
	return

def measureLight(): #returns raw value from ADC input with LDR resistive divider
	i2c.writeto_mem(deviceList[1],0x01,b'\xc1\x03') #puts ADC into single shot mode with correct parameters
	time.sleep(0.5)
	return convertADCtoValue(i2c.readfrom_mem(deviceList[1],0x00,2)) #reads back 16-bit conversion
	
def measureTemp(): #returns raw value from ADC input with Thermistor
	i2c.writeto_mem(deviceList[1],0x01,b'\xd1\x03') #puts ADC into single shot mode with correct parameters
	time.sleep(0.5)
	return convertADCtoValue(i2c.readfrom_mem(deviceList[1],0x00,2)) #reads back 16-bit conversion
	
def button_depress(): #Returns true if button press event detected
	i2c.writeto_mem(deviceList[1],0x01,b'\xe1\x03') #puts ADC into single shot mode with correct parameters
	time.sleep(0.5)
	if(convertADCtoValue(i2c.readfrom_mem(deviceList[1],0x00,2)) > 0x0100): #checks ADC value with a threshold and returns 1 bit comparison
		return False
	else:
		return True
	
def button_release(): #Returns true if button release event detected
	i2c.writeto_mem(deviceList[1],0x01,b'\xe1\x03')  #puts ADC into single shot mode with correct parameters
	time.sleep(0.5)
	if(convertADCtoValue(i2c.readfrom_mem(deviceList[1],0x00,2)) > 0x0100): #checks ADC value with a threshold and returns 1 bit comparison
		return True
	else:
		return False
	
def convertADCtoValue(data): #takes in a byte array and converts it to a signed integer
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
	
def sigAccelChange(prev): #compare current Accelerometer value to previous value and return true if more change than a threshold
	data = getaccelvalues()
	for i in range(0,3):
		if (abs(prev[i]-data[i]) > 10):
			return True
	prev = data
	return False

def lightConvert(data): #maps raw ADC output to user accesible range of intensities
	intensities = ['Dark','Low light','Well lit', 'Bright']
	if(data < 5000):
		return intensities[0]
	if((data >= 5000) and (data < 8000)):
		return intensities[1]
	if((data >= 8000) and (data < 12000)):
		return intensities[2]
	else:
		return intensities[3]
		
def tempConvert(data): #maps raw ADC output to user accessible range of temperatures
	intensities = ['Cold', 'Mild', 'Warm', 'Hot']
	if(data < 5000):
		return intensities[0]
	if((data >= 5000) and (data < 8000)):
		return intensities[1]
	if((data >= 8000) and (data < 12000)):
		return intensities[2]
	else:
		return intensities[3]
		
def accConvert(data): #normalise accelerometer XYZ readings.  Gives the proportion of g in each direction
	out = []
	for item in data:
		out.append(float(item)/255)
	return out
	
#ops JSON formatted data
def outputToJSON(light,temp,acc):
	 output = ujson.dumps({'Light intensity':light,'Temp_celcius':temp,'x_g':acc[0],'y_g':acc[1],'z_g':acc[2]})
	 return output
	
#global variables specific to main while loop
PRESS_STATE = False
RELEASE_STATE = False
ALARM_RESET = False
previousXYZ = []
for i in range(0,3):
	previousXYZ.append(0)
second_counter = 0
	
	
while True:
	#button must be pressed than released to change mode in order to avoid long button presses being mistaken for mulitiple presses
	while PRESS_STATE == False:
		#IDLE mode normal
		print('IDLE MODE')
		
		PRESS_STATE = button_depress()
	PRESS_STATE = False
	
	while RELEASE_STATE == False:
		#IDLE mode button press
		RELEASE_STATE = button_release()
	
	RELEASE_STATE = False
	ALARM_RESET = False
	previousXYZ = getaccelvalues() #save orientation of bike
	while ALARM_RESET == False:
		while PRESS_STATE == False:
			#GUARD mode normal
			if(rtc.datetime()[5]>=10): #send data about the ambient light intensity and temperature and orientation of the bike
				#collect raw values
				lightData=measureLight()
				tempData=measureTemp()
				accData = getaccelvalues()
				
				#convert raw values to useable data
				lightValue = lightConvert(lightData)
				tempValue = tempConvert(tempData)
				accValues = accConvert(accData)
				
				#print(lightValue,' ',tempValue,' ',accValues) #left in for debugging in case of network problems
				
				send_data_MQTT(lightData,tempData) #send raw light and temp data to online graphing broker

				JSONoutput = outputToJSON(lightValue,tempValue,accValues) #convert usable data to JSON
				data_to_broker(JSONoutput) #send JSON encoded packet to EERover broker

				rtc.datetime((2017, 5, 1, 4, 13, 0, 0, 0)) #Reset time (only needed the rtc for timing purposes so actual value can stay wrong)
			
			if(rtc.datetime()[5] == 0): #can only have one real time clock so for the following conditional to be executed every second an additional counter must be reset
				second_counter = 0
			
				#Accelerometer
			if(rtc.datetime()[6]>=second_counter): #read data from the accelerometer ever second to check if the bike has been moved
				second_counter += 1
				if(sigAccelChange(previousXYZ) == True): #if bike has been moved...
					print('Alarm') #sound an alarm, external driver would be used to run a speaker
					thingtweet("move_bike") #tweet @ user to notify them
					check_user_unlock(True) #subscribe EERover and wait for user to send disarm code
					print('Alarm disabled by user') 
					ALARM_RESET = True
				
			PRESS_STATE = button_depress()
		PRESS_STATE = False
	
		while RELEASE_STATE == False:
			#GUARD mode button press
			RELEASE_STATE = button_release()
		RELEASE_STATE = False
		
		if ALARM_RESET == False:
			check_user_unlock(False)
			