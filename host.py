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
		self.server = None
		self.buffer_size = 8000

	#Will probably delete this 
	def load_routing_table(self):
		"""Loads routing table for router from routing table json file"""
		for file in os.listdir('routing_tables'):
			if int(file.split('_')[0]) == self.id:
				with open('routing_tables/{}'.format(self.id),'r') as fp:
					self.routing_table = json.load(fp)

	def update_routing_table(self): 
		with open('routing_tables/{}_routing_table.json'.format(str(self.id)), 'w') as fp:
			json.dumps(self.routing_table, fp, sort_keys=True, indent=4)

	def bootstrap(self):
		broadcast_sock = socket(AF_INET, SOCK_DGRAM)
		broadcast_sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
		try:
			broadcast_sock.bind(('',8888))
		except Exception as e:
			print(e)
 
		packet, addr = broadcast_sock.recvfrom(self.buffer_size)
		self.server = addr
		contents = read_pkt(packet)
		print('Received: {}\tFrom: {}'.format(packet, contents[2]))
		logging.info('Received: {}\tFrom: {}'.format(packet, contents[2]))

		packet = createHellopkt(0, self.id)
		broadcast_sock.sendto(packet, addr)
		print('Sent: {}\tTo: {}'.format(packet, contents[2]))
		logging.info('Sent: {}\tTo: {}'.format(packet, contents[2]))

		broadcast_sock.close()

	def force_ls_update(self, rdest, data): #rdest is a temp parameter
		sock = socket(AF_INET, SOCK_DGRAM)
		#sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
		sock.bind(('',self.port))

		packet = createDatapkt(self.id, data, Rdest=int(rdest))
		sock.sendto(packet, self.server)

		print('Listening')
		packet, addr = sock.recvfrom(self.buffer_size)
		contents = read_pkt(packet)
		print('Received: {}\tFrom: {}'.format(packet, contents[2])) 
		sock.close()

	def send_to_k_dest(self, k, data): 
		sock = socket(AF_INET, SOCK_DGRAM)
		sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
		sock.bind(('',self.port))

		packet = createDatapkt(self.id, data, Ndest=int(k))
		sock.sendto(packet, self.server)

		print('Listening')
		packet, addr = sock.recvfrom(self.buffer_size)
		contents = read_pkt(packet)
		print('Received: {}\tFrom: {}'.format(packet, contents[2]))
		sock.close()

	def intf_listen(self):
		"""Sets up socket and waits to recieve a packet

		For the most part regular hosts that are not the main sender host only have to send/reply with
		ACK packets 

		*Note: stop and wait AQR not yet implented
		"""
		sock = socket(AF_INET, SOCK_DGRAM)
		sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		sock.bind(('', self.port))

		while True:
			packet, addr = sock.recvfrom(self.buffer_size)
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

		#Part of bootstrap to update routing tables with all nodes in network
		user_input = input('Enter start to give unkown destination to force routing update: ' )
		while True:
			if user_input == 'start':
				data = 'Hello'
				dest = input('Enter destination: ') #temp
				host.force_ls_update(dest, data)
				break
			else:
				print('Please input start')

		#Start the multicast process
		while True:
			user_input = input('Input send or stop: ')
			if user_input == 'send':
				data = 'Hello'
				k = input('Enter value of k (1, 2 or 3): ')
				host.send_to_k_dest(k, data)
			elif user_input == 'stop':
				break	
					
	
		print('Source host stopped')
		#host.intf_listen()

	elif 101 < host.id < 200: 
		host.bootstrap()
		host.intf_listen()

	else:
		logging.info('Incorrect host id value, must be between 1 and 51')
