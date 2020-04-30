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
        #self.port = random.randint(1, 8887)
        self.bcast = '192.168.1.255'

    def check_route(self, sender_id):
        """Checks routing table to see if there is a route to the sender_id"""
        for route_idx in range(len(self.routing_table)):
            dest_id = self.routing_table[route_idx]['dest_id']
            if dest_id == sender_id:
                return True
        return False

    def save_routing_table(self):
            with open('routing_tables/{}_routing_table.json'.format(str(self.id)), 'w') as fp:
                   fp.write(json.dumps(self.routing_table, sort_keys=True, indent=4))

    def is_route(self, dest_id):
        """This function takes in a destination id and checks to see if there is a route
        for that id in the current routers routing table"""
        for route in self.routing_table:
            if route['dest_id'] == dest_id:
                return (route['dest_addr'], route['dest_port'])
            elif self.id == dest_id: 
                return 0 
        return None

    def update_routing_table(self, new_table, src):
        length = len(self.routing_table)
        for route_idx in range(length):
            for new_route in new_table:
                if new_route['dest_id'] == self.routing_table[route_idx]['dest_id'] or new_route['dest_id'] == self.id:
                    continue
                else:
                    dest_addr = self.is_route(src)
                    self.routing_table.append({'dest_id': new_route['dest_id'], 'dest_addr': dest_addr, 'dest_port': new_route['dest_port'], 'cost': 1+new_route['cost']}) 
        self.save_routing_table()

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
        broadcast_sock.bind(('', self.port))
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
       
                if contents[1] == 0 and contents[2] is not self.id:    
                    routes.append({'dest_id': contents[2], 'dest_addr': addr[0], 'dest_port': addr[1], 'cost': 1})

            except OSError:
                print('Timeout')
                break
        self.routing_table = routes
        self.save_routing_table()
        print(self.routing_table)
        print('{} finished booting'.format(self.id))
        broadcast_sock.close()

    def intf_listen(self):
        print('Listening on all interfaces')
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) #To send broadcasts using bcast addr for LS
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
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
                    self.routing_table.append({'dest_id': contents[2], 'dest_addr': addr[0], 'dest_port': addr[1], 'cost':1})
                    self.save_routing_table()

                elif contents[1] == 1 and self.check_route(contents[2]) == True:
                    packet = createHellopkt(0, self.id)
                    sock.sendto(packet, addr)    

                print('Sent: {}\tTo: {}'.format(packet, contents[2]))

            elif contents[0] == 1 and contents[2] is not self.id: #LS
                temp_routing_table = self.routing_table
                self.update_routing_table(contents[4], contents[2])

                if len(temp_routing_table) is not len(self.routing_table):
                    ls_packet = createLSpkt(self.id, self.routing_table)
                    sock.sendto(ls_packet, (self.bcast, self.port))
                    print('Sent: {}\tTo: {}'.format(ls_packet, (self.bcast, self.port)))

                else:
                    continue

            elif contents[0] == 3: #Data
                src, seq, dest = contents[2], contents[1], contents[5]
                dest_addr = self.is_route(dest)

                if dest_addr == 0: #pkt reached destination
                    ack_packet = createACKpkt(self.id, seq, src)
                    sock.sendto(ack_packet, addr)

                elif dest_addr is not None:
                    #Make and send ack back to sender
                    ack_packet = createACKpkt(self.id, seq, src)
                    sock.sendto(ack_packet, addr) 
                   
                    #Forward data packet to destination
                    sock.sendto(packet, dest_addr)

                elif dest_addr is None:
                    ls_packet = createLSpkt(self.id, self.routing_table)
                    sock.sendto(ls_packet, (self.bcast, self.port))
                    print('Sent: {}\tTo: {}'.format(ls_packet, (self.bcast, self.port)))

            elif contents[0] == 4: #ACK
                pass

            else:
                pass
            #print(self.routing_table)
        sock.close()

if __name__=='__main__':
    #Assuming that therouter knows the number of nodes in the network, this will be changed
    #nodes = 10

    router=Router()
    logging.basicConfig(filename='debug_logs/{}_debug.log'.format(router.id), level=logging.INFO)
    router.bootstrap()
    router.intf_listen()





