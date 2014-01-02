"""

BITalino API

Created on Tue Jun 25 2013
@author: Priscila Alves

Adapted on Wed 18 Dec 2013 for Raspberry Pi
@author: Jose Guerreiro

"""

import RPi.GPIO as GPIO
from time import sleep
import serial
import numpy
import math
import traceback

class BITalino:
	
	def __init__(self):
		self.analogChannels=[]
		self.nChannels = None
		self.number_bytes = None
		self.uart = None
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(16, GPIO.OUT) # One RPi.GPIO must be connected to the STAT pin of the BITalino board
		GPIO.output(16, GPIO.HIGH) # must be output high
	
	# This function sets the UART Pi peripheral to serial communication and also sets the sampling rate
	def open(self, SamplingRate = 1000, dev ="/dev/ttyAMA0"):
		# Configure sampling rate
		if SamplingRate == 1000:
			variableToSend = 0x03
		elif SamplingRate == 100:
			variableToSend = 0x02
		elif SamplingRate == 10:
			variableToSend = 0x01
		elif SamplingRate == 1:
			variableToSend = 0x00
		else:
			print traceback.format_exc()
			raise TypeError, "The Sampling Rate %s cannot be set in BITalino. Choose 1000, 100, 10 or 1."%SamplingRate
			return -1
			
		#create and open UART connectivity
		try:
			self.uart = serial.Serial(dev,115200,timeout=2)
			self.uart.open()
			self.uart.flushInput()
			self.uart.flushOutput()
			variableToSend = int((variableToSend<<6)|0x03)
			self.write(variableToSend)
		except Exception:
			self.uart.close()
			self.uart = None
			print traceback.format_exc()
			raise TypeError, " Problems within UART_Pi peripheral."
			return -1		
		return 1
		
	# This function starts the Acquisition mode in the analog channels set
	def start(self, analogChannels = [0,1,2,3,4,5]):
		if self.uart is None:
			print traceback.format_exc()
			raise TypeError, "An input connection is needed."
			return -1
		elif len(analogChannels) == 0 or len(analogChannels)>6 or sum(i > 5 or i < 0 for i in analogChannels)> 0 or len(list(set(analogChannels))) != len(analogChannels):
			print traceback.format_exc()
			raise TypeError, "Analog channels set not valid."
			return -1
		else:
			# save global variables
			self.analogChannels = analogChannels
			self.nChannels = len(analogChannels)
			if self.nChannels <=4:
				self.number_bytes = int(math.ceil((12.+10.*self.nChannels)/8.))
			else:
				self.number_bytes = int(math.ceil((52.+6.*(self.nChannels-4))/8.))
					
			bit = 1
			# setting channels mask
			for i in analogChannels:
				bit = bit | 1<<(2+i)
			# start acquisition
			self.write(bit)
			return 1
	
	# This function stops the Acquisition mode	
	def stop(self):
		if self.uart is None:
			print traceback.format_exc()
			raise TypeError, "An input connection is needed."
			return -1
		else:
			# send stop command
			self.write(0)
			self.uart.flushInput()
			return 1
	
	# This function closes the UART Pi communication	
	def close(self):
		if self.uart is None:
			print traceback.format_exc()
			raise TypeError, "An input connection is needed."
			return -1
		else:
			self.uart.close()
			return 1
	
	# This function sets the battery threshold. It works only in idle mode		
	def battery(self, value = 0):
		if self.uart is None:
			print traceback.format_exc()
			raise TypeError, "An input connection is needed."
			return -1
		else:
			if 0 <= value <= 63:
				Mode = value << 2
				self.write(Mode)
				return 1
			else:
				raise TypeError, "The threshold value must be between 0 and 63."
				return -1
	# This function gets BITalino version. It works only in idle mode
	def version(self):
		if self.uart is None:
			print traceback.format_exc()
			raise TypeError, "An input connection is needed."
			return -1
		else:
			self.write(7)
			version = ' '
			while version[-1] != '\n':
				version += self.uart.read(1)
			else:
				return version[:-1]
				
	# This function sets on digital output channels. It works only during acquisition mode
	def trigger(self,digitalArray = [0,0,0,0]):
		if self.uart is None:
			print traceback.format_exc()
			raise TypeError, "An input connection is needed."
			return -1
		elif len(digitalArray)!=4 or sum(i>1 or i<0 for i in digitalArray)>0:
			print traceback.format_exc()
			raise TypeError, "Digital channels set not valid."
			return -1
		else:
			data = 3
			for i,j in enumerate(digitalArray):
				data = data | j<<(2+i)
			self.write(data)			
			return 1
	
	def write(self, data = 0):
		if self.uart is None:
			print traceback.format_exc()
			raise TypeError, "An input connection is needed."
			return -1
		else:
			self.uart.write(chr(data))
			sleep(1)
			return 1
	
	# This function gets number of samples from UART Pi	
	def read(self, nSamples = 100):
		# get Data according to the value nSamples set
		dataAcquired = numpy.zeros((5+self.nChannels, nSamples))
		Data = ''
		sampleIndex = 0
		while sampleIndex < nSamples:
			while len(Data) < self.number_bytes:
				Data += self.uart.read(1) # it reads 1 bytes from UART_Pi
			else:
				decoded = self.decode(Data)
			if len(decoded)!=0:
				dataAcquired[:,sampleIndex] = decoded.T
				Data = ''
				sampleIndex+=1
			else:
				Data += self.uart.read(1)
				Data = Data[1:]
				print "ERROR READING"
		else:
			return dataAcquired
		
	# This function unpacks data
	def decode(self, data):
		nSamples = len(data)/self.number_bytes
		res = numpy.zeros(((5 + self.nChannels,nSamples)))
		j,x0,x1,x2,x3,out,inp,col,line = 0,0,0,0,0,0,0,0,0
		encode0F = int('\x0F'.encode("hex"),16)
		encode01 = int('\x01'.encode("hex"),16)
		encode03 = int('\x03'.encode("hex"),16)
		encodeFC = int('\xFC'.encode("hex"),16)
		encodeFF = int('\xFF'.encode("hex"),16)
		encodeC0 = int('\xC0'.encode("hex"),16)
		encode3F = int('\x3F'.encode("hex"),16)
		encodeF0 = int('\xF0'.encode("hex"),16)
		#CRC check
		CRC = int(data[j+self.number_bytes-1].encode("hex"),16) & encode0F
		for byte in range(self.number_bytes):
			for bit in range (7,-1,-1):
				inp = int(data[byte].encode("hex"),16)>>bit & encode01
				if byte == (self.number_bytes -1) and bit<4:
					inp = 0
				out=x3
				x3=x2
				x2=x1
				x1=out^x0
				x0=inp^out
		if CRC == int((x3<<3)|(x2<<2)|(x1<<1)|x0):
			try:
				#Seq Number
				SeqN = int(data[j+self.number_bytes-1].encode("hex"),16)>>4 & encode0F
				res[line,col] = SeqN
				line+=1
				#Digital 0
				Digital = int(data[j+self.number_bytes-2].encode("hex"),16)>>7 & encode01
				res[line,col] = Digital
				line+=1
				#Digital 1
				Digital = int(data[j+self.number_bytes-2].encode("hex"),16)>>6 & encode01
				res[line,col] = Digital
				line+=1
				#Digital 2
				Digital = int(data[j+self.number_bytes-2].encode("hex"),16)>>5 & encode01
				res[line,col] = Digital
				line+=1
				#Digital 3
				Digital = int(data[j+self.number_bytes-2].encode("hex"),16)>>4 & encode01
				res[line,col] = Digital
				line+=1
				if self.number_bytes>=3:
					#Analog 0
					Analog = (int(data[j+self.number_bytes-2].encode("hex"),16) & encode0F)<<6 | (int(data[j+self.number_bytes-3].encode("hex"),16) & encodeFC)>>2
					res[line,col] = Analog
					line+=1
				if self.number_bytes>=4:
					#Analog 1
					Analog = (int(data[j+self.number_bytes-3].encode("hex"),16) & encode03)<<8 | (int(data[j+self.number_bytes-4].encode("hex"),16) & encodeFF)
					res[line,col] = Analog
					line+=1
				if self.number_bytes>=6:
					#Analog 2
					Analog = (int(data[j+self.number_bytes-5].encode("hex"),16) & encodeFF)<<2 | (int(data[j+self.number_bytes-6].encode("hex"),16) & encodeC0)>>6
					res[line,col] = Analog
					line+=1
				if self.number_bytes>=7:
					#Analog 3
					Analog = (int(data[j+self.number_bytes-6].encode("hex"),16) & encode3F)<<4 | (int(data[j+self.number_bytes-7].encode("hex"),16) & encodeF0)>>4
					res[line,col] = Analog
					line+=1
				if self.number_bytes>=8:
					#Analog 4
					Analog = (int(data[j+self.number_bytes-7].encode("hex"),16) & encode0F)<<2 | (int(data[j+self.number_bytes-8].encode("hex"),16) & encodeC0)>>6
					res[line,col] = Analog
					line+=1
				if numpy.shape(res)[0]==11:
					#Analog 5
					Analog = int(data[j+self.number_bytes-8].encode("hex"),16) & encode3F
					res[line,col] = Analog
				return res
			except Exception:
				print traceback.format_exc()
		else:
			print "ERROR DECODING"
			return []
					

######################### main #################################

def main():
	
	try:
		#example
		device = BITalino()
		SamplingRate = 10
		nSamples = 10
		device.open(SamplingRate)
		
		#BITversion = device.version()
		#print "version: ", BITversion
		
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
		GPIO.cleanup()

		
	except KeyboardInterrupt:
		device.stop()
		device.close()
		GPIO.cleanup()


if __name__=="__main__":
	main()
	
