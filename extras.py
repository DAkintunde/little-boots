#dump for extra code that we don't need but don't want to get rid of


#memory dump code, do not delete, was v useful for debugging memory perhaps it should be turned into a functio
for i in range(0x07, 0x3f):
	data = str(hex(i)) + " " + str(i2c.readfrom_mem(24,i,1))
	print(data)
	#time.sleep(5)

	
connectToNetwork("Drop It Like It's Hotspot", "3wtpsgHVzty6") #testing connection to wifi at my house