"""

BITalino API

Created on Tue Jun 25 2013
@author: Priscila Alves

Adapted on Wed 18 Dec 2013 for Raspberry Pi
@author: Jose Guerreiro

"""

import BITalinoPi

try:
	#example
	device = BITalinoPi.BITalino()
	SamplingRate = 10
	nSamples = 10
	device.open(SamplingRate)
	
	BITversion = device.version()
	print "version: ", BITversion
	
	device.start([0,1,2,3,4,5])
	device.trigger([1,1,1,1])
	#read samples
	dataAcquired = device.read(nSamples)
	device.trigger([0,0,0,0])
	device.stop()
	device.close()
	
	SeqN = dataAcquired[0,:]
	D0 = dataAcquired[1,:]
	D1 = dataAcquired[2,:]
	D2 = dataAcquired[3,:]
	D3 = dataAcquired[4,:]
	A0 = dataAcquired[5,:]
	A1 = dataAcquired[6,:]
	A2 = dataAcquired[7,:]
	A3 = dataAcquired[8,:]
	A4 = dataAcquired[9,:]
	A5 = dataAcquired[10,:]
	print SeqN
	print A0
	print A1
	print A2
	print A3
	print A4
	print A5

	
except KeyboardInterrupt:
	device.stop()
	device.close()
	
