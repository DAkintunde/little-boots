from machine import Pin, I2C
import time

def getvalues():  #returns list with the xyz components
	out = []
	for i in range(0x28, 0x2d, 2): #cycles through memory with data in
		data1 = i2c.readfrom_mem(24, i, 1) #memory access for LSBs
		data2 = i2c.readfrom_mem(24, i+1, 1) #memory acces for MSBs
		value = (int(data2[0]) << 2) + (int(data1[0]) >> 6) #concatinate data
		if (0x80 & data2[0] == 0x80): #check if negative and adjust value so int output is also negative
				value -= 1024
		out.append(value)
	return out

#setup i2c and tell accelerometer to be awake
i2c = I2C(scl = Pin(5), sda = Pin(4), freq = 100000) #set up i2c

i2c.writeto_mem(24,0x20,b'\x47')
time.sleep_ms(100)

#main running loop
while True:
	fred = getvalues()
	axis = ['x','y','z']
	for i in range(0,3):
		print('{}\t{}'.format(axis[i],fred[i]))
	print()
	time.sleep(0.1)

"""  #memory dump code, do not delete, was v useful for debugging memory perhaps it should be turned into a functio
for i in range(0x07, 0x3f):
	data = str(hex(i)) + " " + str(i2c.readfrom_mem(24,i,1))
	print(data)
	#time.sleep(5)

"""


