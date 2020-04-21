import socket
import logging
from sys import argv
import os
import json
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI

class Router:

	def __init__(self, *args):
		#ARGS[1:] --> id ip, argv[0] is the name of python file   
		self.id = argv[1]
		#self.ip = argv[2] Do we need this??
		self.routing_table = None
        #To enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )
        self.cmd( 'sysctl net.ipv4.icmp_echo_ignore_broadcasts=0' )
        self.cmd( 'sysctl net.ipv4.conf.r0-eth1.force_igmp_version=2' )
        self.cmd( 'sysctl net.ipv4.conf.r0-eth2.force_igmp_version=2' )
        self.cmd( 'sysctl net.ipv4.conf.r0-eth3.force_igmp_version=2' )
        self.cmd( '/opt/smcroute/sbin/smcrouted -l debug -I smcroute-r0' )
        self.cmd( 'sleep 1')
        self.cmd( '/opt/smcroute/sbin/smcroutectl -I smcroute-r0 '
                  'add r0-eth1 239.0.0.1 r0-eth2 r0-eth3' )
        self.cmd( '/opt/smcroute/sbin/smcroutectl -I smcroute-r0 '
                  'add r0-eth2 239.0.0.2 r0-eth1 r0-eth3' )
        self.cmd( '/opt/smcroute/sbin/smcroutectl -I smcroute-r0 '
                  'add r0-eth3 239.0.0.3 r0-eth1 r0-eth2' )

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

    def terminate(self):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        self.cmd( '/opt/smcroute/sbin/smcroutectl -I smcroute-r0 kill' )

	def bootstrap(self, network):
		raise NotImplementedError

    def createACKpkt(src, dest): #can be removed once packets.py is imported
	    seq = random.randint(0,254)
	    return struct.pack('BBBB', 4, seq, src, dest)

    def run(self):
        sock=socket(AF_INET,SOCK_DGRAM)
        sock.bind((self.ip,self.id))
        while True:
            packet,addr=sock.recvfrom(self.buffer_size)
            header=read_header(packet)
            if header(0) == 'Hello':#ignore Hello Packets
                continue
            elif header(0) == 'LSU':
                if header(2)==self.ip: #drop packet if sent from same router
                    continue
            sock.send(self.createACKpkt(self.ip, addr))#send ack packet
                    


    if __name__=='__main__':
        router=Router()
        router.load_routing_table()
        router.get_router_information
        router.run()
