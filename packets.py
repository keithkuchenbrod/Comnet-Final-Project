# ComNet2 Project


import time
from socket import socket, AF_INET, SOCK_DGRAM
import struct
import select
import random
import asyncore
import numpy as np

def createHellopkt(src):
	"""
	Type(1)|SEQ(1)|SRC(1)
	Type = 0 (1 Byte)
	SEQ generated randomly, 1B 0-254
	Inputs:
		src: source address, 1B, 0-255
	Outputs:

	"""



def createACKpkt(src, dest):
	"""
	Type(1) SEQ(1) SRC(1) DEST(1)
	Type = 4 (1B)
	SEQ generated randomly, 1B 0-254
	Inputs: 
		src: source address 1B 0-255
		dest: destination address 1B 0-255
	Outputs:
		total packet as described in line 14 (in decimal not utf-8)
	"""
	seq = random.randint(0,254)
	#why do we need this as a function.  Do we convert to utf-8?
	return struct.pack('BBBB', 4, seq, src, dest)

def readACK(pkt):
	"""

	Inputs:
		pkt
	"""
	header = pkt[0:8]
	pkttype, seq, src, dest = struct.unpack('BBBB', header)
	return [pkttype, seq, src, dest]

def createDatapkt(src, Ndest, Rdest, dest1, dest2, dest3, data):
	"""
	Type(1)|SEQ(1)|LEN(2)|SRC(1)|NDEST(1)|RDEST(1)|DEST1(1)|DEST2(1)|DEST3(1)|DATA(1-1491)print(str(4).encode('utf-8'))
	Type = 3, 1B
	SEQ generated randomly
	pktlen = length of data input
	Inputs:
		src:
		Ndest: K, 1-3
		Rdest:
		dest1:
		dest2:
		dest3:
		data:
	Outputs:
		pkt:
	"""

	pktlen = len(data)
	seq = random.randint(0,254) # random integer between 0 and 254 inclusive
	header = struct.pack('BBHBBBBBB', 3, seq, pktlen, src, Ndest, Rdest, dest1, dest2, dest3)
	return header + bytes(data, 'utf-8')

def readDATApkt(pkt):
	"""

	Inputs:
		pkt:
	Outputs:
		contents:
	"""
	header = pkt[0:10]
	pkttype, seq, pktlen, src, Ndest, Rdest, dest1, dest2, dest3 = struct.unpack('BBHBBBBB', header)
	data = pkt[10:].decode("utf-8")
	contents = [pkttype, seq, pktlen, src, Ndest, Rdest, dest1, dest2, dest3, data]
	return contents


def read_pkt(pkt):
	"""

	Inputs:
		pkt:
	Output:
		contents
	"""

	if pkt[0] == 4: 
		contents = readACK(pkt)
	elif pkt[0] == 3:
		contents = readDatapkt(pkt)
	else:
		contents = print("Get Fucked")
	return contents