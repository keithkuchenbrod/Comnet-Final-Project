from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, SO_REUSEADDR, SO_REUSEPORT
import logging
from sys import argv
import os
import json
from packets import *
import random
import time

class Router:

    def __init__(self, *args):
        self.id = int(argv[1])
        self.routing_table = []
        self.port = 8888
        self.bcast = '192.168.1.255'

    def check_route(self, sender_id):
        """Checks routing table to see if there is a route to the sender_id"""
        for route_idx in range(len(self.routing_table)):
            dest_id = self.routing_table[route_idx]['dest_id']
            if dest_id == sender_id:
                return True
        return False

    def bootstrap(self):
        """Creates two sockets:
        sock: This is the main sock to be used on the intf
        broadcast_sock: This is used to send out a broadcast message to subnets. It allows
        for the current router to discover its neighbors addr and the port its socket is
        listening on
        param route_idx: Index in the routing table for a specific intf
        """ 
        broadcast_sock = socket(AF_INET, SOCK_DGRAM)
        broadcast_sock.setsockopt(SOL_SOCKET, SO_BROADCAST,1)
        broadcast_sock.settimeout(0.2)
        #broadcast_sock.bind(('192.168.1.8',8888))
        packet = createHellopkt(1, self.id)
        broadcast_sock.sendto(packet, (self.bcast, 8888))
       
        print('Sent: {}\tTo: {}'.format(packet, '{}, 8888'.format(self.bcast)))
        logging.info('Sent: {}\tTo: {}'.format(packet, '{}, 8888'.format(self.bcast)))
       
        routes = []
        while True:
            try:
                packet, addr = broadcast_sock.recvfrom(1024)
                contents = read_pkt(packet)
                
                print('Received: {}\tFrom: {}'.format(packet, contents[2]))
                logging.info('Recieved: {}\tFrom: {}'.format(packet, contents[2]))
       
                if contents[1] == 0:    
                    routes.append({'dest_id': contents[2], 'dest_addr': addr[0], 'dest_port': addr[1]})

            except OSError:
                print('Timeout')
                break
        self.routing_table = routes
        print(self.routing_table)
        print('{} finished booting'.format(self.id))
        broadcast_sock.close()

    def intf_listen(self):
        print('Listening on all interfaces')
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.bind(('',self.port))

        contents = None
        while True:
            packet, addr = sock.recvfrom(1024)
            contents = read_pkt(packet)
            print('Received: {}\tFrom: {}'.format(packet, contents[2]))
            logging.info('Received: {}\tFrom: {}'.format(packet, contents[2]))

            if contents[0] == 0:   #Hello
                if contents[1] == 0:
                    pass
                elif contents[1] == 1 and self.check_route(contents[2]) == False:
                    packet = createHellopkt(0, self.id)
                    sock.sendto(packet, addr)
                    self.routing_table.append({'dest_id': contents[2], 'dest_addr': addr[0], 'dest_port': addr[1]})
                elif contents[1] == 1 and self.check_route(contents[2]) == True:
                    packet = createHellopkt(0, self.id)
                    sock.sendto(packet, addr)    
                print('Sent: {}\tTo: {}'.format(packet, contents[2]))

            elif contents[0] == 1: #LS
                pass

            elif contents[0] == 3: #Data
                src, seq, dest = contents[3], contents[1], contents[5]
                dest_addr = self.get_addr(dest)
                if dest_addr is not -1:
                    packet = createACKpkt(src, seq, dest)
                    sock.sendto(packet, (dest_addr, 3535)) #port is dest ports number
                    logging.info('Sent: {}\tTo: {}'.format(packet, dest))
            elif contents[0] == 4: #ACK
                pass

            else:
                pass
            print(self.routing_table)
        sock.close()

if __name__=='__main__':
    router=Router()
    logging.basicConfig(filename='debug_logs/{}_debug.log'.format(router.id), level=logging.INFO)
    router.bootstrap()
    router.intf_listen()





