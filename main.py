from machine import Pin, I2C
import time

#  b'\xac' -> ac     function needs work, perhaps accepting strings is not idea :P
def bufferExtract(buff):
	return buff[4:5]

i2c = I2C(scl = Pin(5), sda = Pin(4), freq = 100000) #set up i2c

i2c.writeto_mem(24,0x20,b'\x47') #tell the device to do something (i hate u so much)
time.sleep_ms(100)

while True:  #print a feed with all the measurements
	for i in range(0x28, 0x2d, 2):
		data1 = i2c.readfrom_mem(24, i, 1)
		data2 = i2c.readfrom_mem(24, i+1, 1)
		value = (int(data2[0] & 0x7f) << 2) + (int(data1[0]) >> 6)
		#if (0x80 & data2[0] == 0x80):
		#	value = int(0xfe00 | value) #mmmmMMmMMmm
		print(bin(value))
	print()
	time.sleep(0.1)

"""  #memory dump code, do not delete, was v useful for debugging memory perhaps it should be turned into a functio
for i in range(0x07, 0x3f):
	data = str(hex(i)) + " " + str(i2c.readfrom_mem(24,i,1))
	print(data)
	#time.sleep(5)

"""


