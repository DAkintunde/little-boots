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
BROKER_NAME="EEERover"
BROKER_PASSWORD="exhibition"
myClient=machine.unique_id()
thingspeakURL="mqtt.thingspeak.com"
ts_channelId="227715"
ts_channelWriteAPI="0NRQOTAOFKJGP12Y"
tweet_channelWriteAPI="OTNM7ZQ5I6WYCYRE"



#function definitions


#setup clock
rtc=machine.RTC()
rtc.datetime((2017, 5, 1, 4, 13, 0, 0, 0))

#setup i2c
i2c = I2C(scl = Pin(5), sda = Pin(4), freq = 100000)
deviceList = i2c.scan() #deviceList[0] = accelerometer, deviceList[1] = ADC

def thingtweet(event):
	sta_if = network.WLAN(network.STA_IF); sta_if.active(True)
	sta_if.connect(AP_NAME,AP_PASSWORD)
	while sta_if.isconnected() == False:
		time.sleep_ms(10)
	print("Network Connected")
	tweet_alert(event_to_message(event),user_id)
	sta_if.disconnect()

def event_to_message(event):
	if event="light_low":
		return "Your bike is not in a well lit area"
	if event=="move_bike":
		return "Your bike has been moved"

	
def tweet_alert(message,user_id):
	API_KEY=tweet_channelWriteAPI
	url="http://api.thingspeak.com/apps/thingtweet/1/statuses/update?api_key="
	fill="&status="
	url=url+API_KEY+fill
	tweet="@"+user_id+" "+message
	print("Tweet sent to "+user_id)
	url=url+tweet
	response=urequests.get(url)
	
def send_data_MQTT(data1,data2):
	sta_if = network.WLAN(network.STA_IF); sta_if.active(True)
	sta_if.connect(AP_NAME,AP_PASSWORD)
	while sta_if.isconnected() == False:
		time.sleep_ms(10)
	print("Network Connected")
	client=MQTTClient(myClient,thingspeakURL)
	client.connect()
	print("MQTT Connected")
	credentials="channels/{:s}/publish/{:s}".format(ts_channelId, ts_channelWriteAPI)
	payload="field1"={:d}&field2\n"={:d}".format(data1,data2)
	client.publish(credentials, payload)
	print("published")
	client.disconnect()
	sta_if.disconnect()
	
def broker_interaction():
	sta_if = network.WLAN(network.STA_IF); sta_if.active(True)
	sta_if.connect(BROKER_NAME,BROKER_PASSWORD)
	while sta_if.isconnected() == False:
		time.sleep_ms(10)
	print("Broker Connected")
	client=MQTTClient(machine.unique_id(),"192.168.0.10")
	client.connect()
	client.set_callback(sub_cb)
	client.subscribe("esys/<team_little_boots>/unlock/1234")
	client.wait_msg()
	print("Alarm Disabled")
	client.disconnect()
	sta_if.disconnect()
		
	
def sub_cb(topic,msg):
	return


while True:
	thingtweet("move_bike")
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
		
	
	
	
	
	
	
	
	
	
	
	
	
	
	