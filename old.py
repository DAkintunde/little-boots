import machine
from machine import Pin, I2C
import time, network
from umqtt.simple import MQTTClient
import ujson

def printADCvalues(): #for debugging purposes only
	i2c.writeto(deviceList[1],b'\x00') #only need this if it's the first time
	data = i2c.readfrom(deviceList[1],2)
	print(convertADCtoVoltage(data))
	print()
	return

def convertADCtoVoltage(data): #needs work, currently not functioning quite right
	value = data[1] + ((0x7f & data[0])<<8)
	if (data[0] > 0x8000):
		value -= 0x8000
	truevalue = 6.144*float(value)/0x8000
	return truevalue
	
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

#ops JSON formatted data
def outputXYZtoJSON(data):
	 output = ujson.dumps({'x':data[0],'y':data[1],'z':data[2]})
	 return output
	
def printaccelvalues():
	fred = getaccelvalues()
	axis = ['x','y','z']
	for i in range(0,3):
		print('{}\t{}'.format(axis[i],fred[i]))
	print()
	time.sleep(0.1)
	return

#since this function doesn't D/C it should not be used in the final code
#use this function to make others where they D/C after they're done
def connectToNetwork(name, password):
	sta_if = network.WLAN(network.STA_IF); sta_if.active(True)
	sta_if.connect(name,password)
	while sta_if.isconnected() == False:
		time.sleep_ms(10)
	print("Connected to {}".format(name))
	return

#setup i2c
i2c = I2C(scl = Pin(5), sda = Pin(4), freq = 100000)
deviceList = i2c.scan() #deviceList[0] = accelerometer, deviceList[1] = ADC

"""
#tell accelerometer to be awake
i2c.writeto_mem(deviceList[0],0x20,b'\x47')
time.sleep_ms(100)
"""

#tell ADC to go into single shot mode
i2c.writeto_mem(deviceList[1],0x01,b'\xc0\x03') #sets up the ADC
i2c.writeto(deviceList[1],b'\x00') 

#accelerometer interrupt
#i2c.writeto_mem(deviceList[0],0x21,b'\  #sets up the interrupt




#connectToNetwork("EEERover","exhibition")
#set up MQTT
client=MQTTClient(machine.unique_id(),"192.168.0.10")
client.connect()

"""	client.publish("esys/<team_little_boots>/hello",str(outputXYZtoJSON(getvalues()),'utf-8'))
"""


while True:
	#printADCvalues()
	#time.sleep(1)


	
	