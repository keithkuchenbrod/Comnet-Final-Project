import socket
import logging
from sys import argv
import os
import json

class Router:

	def __init__(self, *args):
		#ARGS[1:] --> id ip, argv[0] is the name of python file   
		self.id = argv[1]
		#self.ip = argv[2] Do we need this??
		self.routing_table = None

	def get_router_information(self):
		"""Logs routing information in debug.log file"""
		logging.basicConfig(filename='debug.log',level=logging.INFO)
		logging.info('Node id: {}\tNode ip: {}\tRouting table: {}'.format(self.id, self.ip, self.routing_table))

	def load_routing_table(self):
		"""Loads routing table for router from routing table json file"""
		logging.basicConfig(filename='debug.log',level=logging.INFO)
		for file in os.listdir('routing_tables'):
			if file.split('_')[0] == self.id:
				with open('routing_tables/{}'.format(file), 'r') as fp:
					self.routing_table = json.load(fp)

	def bootstrap(self, network):
		raise NotImplmentedError


if __name__ == '__main__':
	router = Router()
	router.load_routing_table()
	router.get_router_information()
