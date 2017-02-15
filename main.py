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

#function definitions
def button_press(): #Returns true if button press event detected

	return
	

#setup clock
rtc=machine.RTC()
rtc.datetime((2017, 5, 1, 4, 13, 0, 0, 0))

#setup i2c
i2c = I2C(scl = Pin(5), sda = Pin(4), freq = 100000)
deviceList = i2c.scan() #deviceList[0] = accelerometer, deviceList[1] = ADC

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
	return i2c.readfrom_mem(deviceList[1],0x00,2)

connect_network()
tweet_alert("Your bike is being stolen!","francinetarta")
light_level=20
while True:
	light_level=generate_light_level(light_level)
	send_data_MQTT(light_level,1)
	print(light_level)
	time.sleep(10)

	

while True:
	if GUARD_ON==True:
		if button_press()==True:
			GUARD_ON=False
		if(rtc.datetime()[5]>=10):
			#check temperature and light intensity
				#read the temperature and light intensity
				#lightData=measureLight()
				#tempData=measureTemp()
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
		
	
	
	
	
	
	
	
	
	
	
	
	
	
	