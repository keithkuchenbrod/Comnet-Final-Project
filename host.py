import logging
#from packet import *
from socket import socket, AF_INET, SOCK_DGRAM
from sys import argv

class Host:

	def __init__(self, *args):
		self.id = argv[1]
		#self.ip = None #Proabably dont need
		self.gateway = '0.0.0.0'
		self.port = 3535
		self.buffer_size = 1024

	def logger(self, info):
		"""Saves info passed to a log file specific to the host"""
		file_path = 'debug.logs/{}_debug.log'.format(self.id)
		logging.basicConfig(filename=file_path, level=logging.INFO)
		logging.info(info)

	def listen(self):
		"""Sets up socket and waits to recieve a packet

		For the most part regular hosts that are not the main sender host only have to send/reply with
		ACK packets 

		*Note: stop and wait AQR not yet implented
		"""
		sock = socket(AF_INET, SOCK_DGRAM)
		sock.bind((self.ip, self.id))

		while True:
			packet, addr = sock.recvfrom(self.buffer_size)
			header = read_header(packet) #returns a tuple, header(0) is always the packet type

			#String for logging
			log_string = 'Recieved packet: header: {}'.format(header)
			self.logger(log_string)

			#ACK packet (ack --> TYPE|SEQ|SRC|DEST
			#packet_ack = create_ack(seq, src, dest)
			sock.sendto(packet_ack, self.gateway)

			#String for logging
			log_string = 'Sent packet: {}'.format(packet_ack)
			self.logger(log_string)

		sock.close()

if __name__ == '__main__':
	host = Host()
	#host.listen()
