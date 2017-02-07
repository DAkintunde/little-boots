import machine
from machine import Pin, I2C
import time, network
from umqtt.simple import MQTTClient

def getvalues():  #returns list with the xyz components
	out = []
	for i in range(0x28, 0x2d, 2): #cycles through memory with angle data
		data1 = i2c.readfrom_mem(24, i, 1) #memory access for LSBs
		data2 = i2c.readfrom_mem(24, i+1, 1) #memory acces for MSBs
		value = (int(data2[0]) << 2) + (int(data1[0]) >> 6) #concatinate data
		if (0x80 & data2[0] == 0x80): #check if negative and adjust value so int output is also negative
				value -= 1024
		out.append(value)
	return out

#x:\t<xval>\ty:\t<yval>\tz:\t<zval>	
def

	
def printvalues():
	fred = getvalues()
	axis = ['x','y','z']
	for i in range(0,3):
		print('{}\t{}'.format(axis[i],fred[i]))
	print()
	time.sleep(0.1)
	return
	

#setup i2c and tell accelerometer to be awake
i2c = I2C(scl = Pin(5), sda = Pin(4), freq = 100000)

i2c.writeto_mem(24,0x20,b'\x47')
time.sleep_ms(100)

#connect to network
sta_if = network.WLAN(network.STA_IF); sta_if.active(True)
sta_if.connect("EEERover","exhibition")
while sta_if.isconnected() == False:
	time.sleep_ms(10)
print("Connected to network")

#set up MQTT

client=MQTTClient(machine.unique_id(),"192.168.0.10")
client.connect()
while True:
	client.publish("esys/<team_little_boots>/hello",bytes(str(getvalues()[0]),'utf-8'))
	time.sleep(1)


#main running loop




"""  #memory dump code, do not delete, was v useful for debugging memory perhaps it should be turned into a functio
for i in range(0x07, 0x3f):
	data = str(hex(i)) + " " + str(i2c.readfrom_mem(24,i,1))
	print(data)
	#time.sleep(5)
"""
