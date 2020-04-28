# ComNet2 Project
"""
File contains all create and read packet structures along with general readpkt() function
readpkt() should be called to read the packet no matter the type
"""

import struct
import random
import json

def createHellopkt(seq, SRC_ID):
	""" 
	Creates Hello packet with fields specified below
	Type(1)|SEQ(1)|SRC_ID(1)|ADDR_LEN|SRC_ADDR(1)|SRC_PORT(1)
	Type = 0, 1B (int)
	SEQ = 1 when receiver needs to send back, and 0 when sending back
	Inputs:
		SENDER_ID: Sender id, 1B 0-255 (int)
		SRC_ADDR: Source address, variable size, (String)
		SRC_PORT: Source port, 4B (int)
	Outputs:
		pkt
	"""
	#seq = random_randint(0, 254)
	return struct.pack('BBB', 0, seq, int(SRC_ID))

def readHello(pkt):
	"""
	Reads the Hello pkt and breaks down the contents to a single list
	Inputs:
		pkt: (bytes)
	Outputs:
		[pkttype, seq, src]: fields of Hello packet (list)
	"""
	pkttype, seq, SRC_ID = struct.unpack('BBB', pkt)
	return [pkttype, seq, SRC_ID]

def createLSpkt(src, webster):
	"""
	Takes in source addr and routing dict and formats it into Link State Packet
	Type(1)|SEQ(1)|LEN(2)|SRC(1)|Data(1-1495)
	Type = 1, 1B (int)
	Inputs:
		src: Source address 1B, 0-255 (int)
		webster: json formatted dictionary of a specific routing table(dictionary)
	Outputs:
		pkt: complete packet(bytes)
	"""
	seq = random.randint(0,254)
	data = json.dumps(webster) # json to string
	pktlen = len(data)
	header = struct.pack('BBHB', 1, seq, pktlen, src)
	return header + bytes(data, 'utf-8')


def readLSpkt(pkt):
	"""
	Takes in Links State Packet and outputs separated contents in list form
	Inputs:
		pkt: Link State Packet (bytes)
	Outputs:
		separated decoded LS packet contents (list)
	"""
	header = pkt[0:5]
	data = pkt[5:].decode('utf-8')
	webster = json.loads(data)
	pkttype, seq, pktlen, src = struct.unpack('BBHB', header)
	return [pkttype, seq, pktlen, src, webster]

def createDatapkt(src, Rdest, data, Ndest=1, dest1=0, dest2=0, dest3=0):
	"""
	Creates Data packet with the fields specified below
	Type(1)|SEQ(1)|LEN(2)|SRC(1)|NDEST(1)|RDEST(1)|DEST1(1)|DEST2(1)|DEST3(1)|DATA(1-1491)print(str(4).encode('utf-8'))
	Type = 3, 1B (int)
	SEQ generated randomly 0-254 (int)
	pktlen = length of data input (int)
	Inputs:
		src: Source ID (int)
		Rdest: Rendezvous router ID (int)
		data: data to be sent (str)
		Ndest: K, defaults to 1, possible values 1-3 (int)
		dest1: Destination 1 ID defaults to 0 (int)
		dest2: Destination 2 ID defaults to 0 (int)
		dest3: Destination 3 ID defaults to 0(int)
	Outputs:
		pkt: the packet with header and utf8 encoded data
	"""

	pktlen = len(data)
	seq = random.randint(0,254) # random integer between 0 and 254 inclusive
	header = struct.pack('BBHBBBBBB', 3, seq, pktlen, src, Ndest, Rdest, dest1, dest2, dest3)
	return header + bytes(data, 'utf-8')

def readDatapkt(pkt):
	"""
	Reads Data packet specified in createDatapkt() function
	Inputs:
		pkt: complete data packet (bytes)
	Outputs:
		contents: separated decoded packet with all contents as its own index (list)
	"""
	header = pkt[0:10]
	pkttype, seq, pktlen, src, Ndest, Rdest, dest1, dest2, dest3 = struct.unpack('BBHBBBBBB', header)
	data = pkt[10:].decode('utf-8')
	contents = [pkttype, seq, pktlen, src, Ndest, Rdest, dest1, dest2, dest3, data]
	return contents

def createACKpkt(src, seq, dest):
	"""
	Creates ACK packet with fields specified below
	Type(1)|SEQ(1)|SRC(1)|DEST(1)
	Type = 4, 1B (int)
	SEQ generated randomly, 1B 0-254 (int)
	Inputs: 
		src: source address 1B 0-255 (int)
		seq: Sequence number recived from previous packet 0-254 (int)
		dest: destination address 1B 0-255 (int)
	Outputs:
		complete packet (bytes)
	"""
	return struct.pack('BBBB', 4, seq, src, dest)

def readACK(pkt):
	"""
	Reads ACK packet and separates its fields into a list
	Inputs:
		pkt: ACK packet as specified in createACKpkt() (bytes)
	Outputs:
		Broken up field of ACK pkt (list)
	"""
	header = pkt[0:8]
	pkttype, seq, src, dest = struct.unpack('BBBB', header)
	return [pkttype, seq, src, dest]

def read_pkt(pkt):
	"""
	Takes in unknown packet and outputs the contents in a list format
	packettype can be determined from list size or pkt type at first index
	Inputs:
		pkt: unknown packet (bytes)
	Output:
		contents: broken down contents of packet (list)
	"""
	contents = None
	if pkt[0] == 0:
		contents = readHello(pkt)
	elif pkt[0] == 1:
		contents = readLS(pkt)
	elif pkt[0] == 3:
		contents = readDatapkt(pkt)
	elif pkt[0] == 4:
		contents = readACK(pkt)
	else:
		pkt = None # will never happen
	return contents
