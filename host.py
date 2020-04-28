import logging
from packets import *
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, SO_REUSEADDR, SO_REUSEPORT
from sys import argv
import random
import os

class Host:

	def __init__(self, *args):
		self.id = int(argv[1])
		self.port = 8888
		self.routing_table = []

	#Will probably delete this 
	def load_routing_table(self):
		"""Loads routing table for router from routing table json file"""
		for file in os.listdir('routing_tables'):
			if int(file.split('_')[0]) == self.id:
				with open('routing_tables/{}'.format(self.id),'r') as fp:
					self.routing_table = json.load(fp)

	def bootstrap(self):
		#sock = socket(AF_INET, SOCK_DGRAM)
		#sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
		#gateway = self.routing_table[0]['gateway']
		#sock.bind((gateway, self.port))

		broadcast_sock = socket(AF_INET, SOCK_DGRAM)
		broadcast_sock.bind(('',8888))
 
		packet, addr = broadcast_sock.recvfrom(1024)
		contents = read_pkt(packet)
		print('Received: {}\tFrom: {}'.format(packet, contents[2]))
		logging.info('Received: {}\tFrom: {}'.format(packet, contents[2]))

		packet = createHellopkt(0, self.id)
		broadcast_sock.sendto(packet, addr)
		print('Sent: {}\tTo: {}'.format(packet, contents[2]))
		logging.info('Sent: {}\tTo: {}'.format(packet, contents[2]))

		broadcast_sock.close()

	def intf_listen(self):
		"""Sets up socket and waits to recieve a packet

		For the most part regular hosts that are not the main sender host only have to send/reply with
		ACK packets 

		*Note: stop and wait AQR not yet implented
		"""
		sock = socket(AF_INET, SOCK_DGRAM)
		sock.bind(('', self.port))

		while True:
			packet, addr = sock.recvfrom(1024)
			contents = read_pkt(packet)
			print('Receive: {}\tFrom: {}'.format(packet, contents[2]))
			logging.info('Received: {}\tFrom: {}'.format(packet, contents[2]))

			#Idk if we should do handle the hellos like below for hosts 
			if contents[0] == 0: #Hello
				pass
				#if contents[1] == 0:
					#pass
				#elif contents[1] == 1 and self.check_route(contents[2]) == False:
					#packet = createHellopkt(0, self.id)
					#sock.sendto(packet, addr)
					#self.routing_table.append({'dest_id': contents[2], 'dest_addr': addr[0], 'dest_port': addr[1]})
				#elif contents[1] == 1 and self.check_route(contents[2]) == True:
					#packet = createHellopkt(0, self.id)
					#sock.sendto(packet, addr)
				#print('Sent: {}\tTo: {}'.format(packet, contents[2]))				
			elif contents[0] == 1: #LS
				pass
			elif contents[0] == 3: #Data
				pass
			elif contents[0] == 4: #ACK
				pass
			#print(self.routing_table)
		sock.close()

if __name__ == '__main__':
	host = Host()
	logging.basicConfig(filename='debug_logs/{}_debug.log'.format(host.id), level=logging.INFO)
	if host.id == 101:
		host.bootstrap()
		host.intf_listen()
	elif 101 < host.id < 200: 
		host.bootstrap()
		host.intf_listen()
	else:
		logging.info('Incorrect host id value, must be between 1 and 51')
