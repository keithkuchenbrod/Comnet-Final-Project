import logging
from packets import *
from socket import socket, AF_INET, SOCK_DGRAM
from sys import argv

class Host:

	def __init__(self, *args):
		self.id = argv[1]
		self.gateway = '0.0.0.0'
		self.port = 3535
		self.buffer_size = 1024

	def logger(self, info):
		"""Saves info passed to a log file specific to the host"""
		file_path = 'debug_logs/{}_debug.log'.format(self.id)
		logging.basicConfig(filename=file_path, level=logging.INFO)
		logging.info(info)

	def run_source_host(self, k):
		sock = socket(AF_INET, SOCK_DGRAM)
		sock.bind((self.gateway,self.port))

		dest = 'r1' #Just here for testing

		packet = createDatapkt(self.id, dest, 'Hello')
		sock.sendto(packet, self.gateway)
		
		log_string = 'Sent packet: {}'.format(packet)
		logger(log_string)

		sock.close()
		self.run_host()


	def run_host(self):
		"""Sets up socket and waits to recieve a packet

		For the most part regular hosts that are not the main sender host only have to send/reply with
		ACK packets 

		*Note: stop and wait AQR not yet implented
		"""
		sock = socket(AF_INET, SOCK_DGRAM)
		sock.bind((self.gateway, self.port))

		while True:
			packet, addr = sock.recvfrom(self.buffer_size)
			header = read_header(packet) #returns a tuple, header(0) is always the packet type

			#String for logging
			log_string = 'Recieved packet: header: {}'.format(header)
			self.logger(log_string)

			#ACK packet (ack --> TYPE|SEQ|SRC|DEST
			if header[0] != 4:
				packet = createACKpkt(self.id, addr)
				sock.sendto(packet, self.gateway)

			#String for logging
			log_string = 'Sent packet: {}'.format(packet)
			self.logger(log_string)

		sock.close()

if __name__ == '__main__':
	host = Host()
	if host.id == 's': #hosts with the id of 's' are source hosts (the host sending k out of n)
		host.run_source_host(k=1)
	else: 
		host.run_host()
