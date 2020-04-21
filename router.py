import socket
import logging
from sys import argv
import os
import json
from _thread import *
from threading import Thread
from jsonmerge import merge
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
        self.latest_ls = {}  #stores sequence numbers of last recieved LS packets from each node
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

    def createACKpkt(src, seq, dest): #can be removed once packets.py is imported
	    seq = random.randint(0,254)
	    return struct.pack('ACK', 4, seq, src, dest)

    def readLSpkt(pkt): #can be removed once packets.py is imported
	header = pkt[0:5]
	data = pkt[5:].decode('utf-8')
	webster = json.loads(data)
	pkttype, seq, pktlen, src = struct.unpack('BBHB', header)
	return [pkttype, seq, pktlen, src, webster]

    def write_json(data, filename='routing_table.json'): 
    with open(filename,'w') as f: 
        json.dump(data, f, indent=4) 

    class receive_thread(Thread):
        def __init__(self,ip,interface):
            Thread.__init__(self)
            self.ip=ip
            self.interface=interface
            self.port=random.randint(1,1001)

        def run(self):
            sock=socket(AF_INET,SOCK_DGRAM)        
            sock.bind((self.ip,port))
            while True:#listen for packets at the socket
                packet,addr=sock.recvfrom(self.buffer_size)
                header=read_header(packet)
                if header(0) == 'Hello':#ignore Hello Packets
                    continue
                if header(0) == 'ACK':#no response to ACK Packets
                    continue
                pkt_info=self.readLSpkt(packet)#it is an LS packet
                if pkt_info(3) == self.ip: #packet ignored if sent from current router
                    continue
                if pkt_info(3) in latest_lsu:#sending node has been heard from before
                    if latest_lsu[pkt_info(3)] == pkt_info(1):#this packet has been recieved before from same sender
                        continue
                else:#sending node not heard from before
                    self.latest_ls.update(pkt.info(3),pkt.info(1))#updating the dictionary with new node
                #updating JSON dictionary
                new_data=pkt_info(4)
                with open('routing_tables.json','r+') as g:
                    old_data=json.load(g)
                    temp=old_data[self.id+'routing_table']
                    temp.append(new_data)
                write_json(old_data)
                sock.send(self.createACKpkt(self.ip, pkt_info(1), addr))#send ack packet


    def start_receiving():
        recv_threads=[]
        interfaces=[]
        f=open('routing_tables.json',)
        data=json.load(f)
        for d in data:
            if 'Iface' in d:
                interfaces.append(d['Iface'])
        for i in interfaces:
            t=recv_thread(self.ip,i)
            t.start()
            recv_threads.append(t)
       
    if __name__=='__main__':
        router=Router()
        router.load_routing_table()
        router.get_router_information
        router.start_receiving()
