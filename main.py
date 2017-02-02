from machine import Pin, I2C
import time

#  b'\xac' -> ac     function needs work, perhaps accepting strings is not idea :P
def bufferExtract(buff):
	return buff[4:5]

i2c = I2C(scl = Pin(5), sda = Pin(4), freq = 100000) #set up i2c crap

i2c.writeto_mem(24,0x20,b'\x47') #tell the device to do something (i hate u so much)
time.sleep_ms(100)

while True:  #print a feed with all the measurements
	data = ''
	for i in range(0x28, 0x2e):
		data += str(i2c.readfrom_mem(24,i,1)) + '\t'

	print(data)
	time.sleep(0.1)

"""  #memory dump code, do not delete, was v useful for debugging memory perhaps it should be turned into a function
for i in range(0x07, 0x3f):
	data = str(hex(i)) + " " + str(i2c.readfrom_mem(24,i,1))
	print(data)
	#time.sleep(5)

"""


