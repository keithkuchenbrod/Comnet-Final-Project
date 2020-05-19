from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, SO_REUSEADDR, SO_REUSEPORT
import logging
import IN
from sys import argv
import os
import json
from packets import *
import random
import time
import numpy as np

class Router:

    def __init__(self, *args):
        self.id = int(argv[1])
        self.routing_table = []
        self.port = 8888
        self.buffer_size = 8000

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

    def pick_k_closest_hosts(self, k):
        """ 
        Picks the k closest host routing destinations, copies data packet and sends out to 
        those k closests hosts
        """
        hosts = []
        for route in self.routing_table:
            if route['dest_id'] is not '-':
                if 101 < int(route['dest_id']) < 200:
                    hosts.append(route)
        print(hosts)
        hosts = np.asarray(hosts)
        host_costs = np.asarray([route['cost'] for route in hosts])
        host_cost_idx = host_costs.argsort()[:k]
        print(host_cost_idx)
        return np.asarray(hosts[host_cost_idx])
         
    def update_routing_table(self, new_table, src, src_addr):
        """ 
        Adds new unknown routes to routing table and then calls save_routing_table 
        to overwrite old routing table file
        """
        for new_route in new_table:
            found_neighbor, found_dest = False, False
            for route in self.routing_table:
                if new_route['dest_id'] == route['dest_id'] or new_route['dest_id'] == self.id or src == self.id:
                    found_dest = True
                if route['dest_id'] == src or new_route['dest_id'] == self.id or src == self.id:
                    found_neighbor = True          
             
            if found_dest == False:
                dest_addr = self.is_route(src)
                self.routing_table.append({"dest_id": new_route['dest_id'], "dest_addr": dest_addr[0], "dest_port": new_route['dest_port'], "gateway": "-", "iface":"-", "bcast": "-", "cost": 1+new_route['cost']})

            if found_neighbor == False:
                self.routing_table.append({"dest_id": src, "dest_addr": src_addr[0], "dest_port": src_addr[1], "gateway": "-", "iface": "-", "bcast":"-", "cost": 1})

        self.save_routing_table()

    def bootstrap_update_routing_table(self, iface, dest_id, dest_addr, dest_port):
        for route_idx in range(len(self.routing_table)):
            if self.routing_table[route_idx]['iface'] == iface:
                self.routing_table[route_idx]['dest_id'] = dest_id
                self.routing_table[route_idx]['dest_addr'] = dest_addr
                self.routing_table[route_idx]['dest_port'] = dest_port

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
        broadcast_sock.bind(('',self.port))
        initial_rt_length = len(self.routing_table)
        for x in range(initial_rt_length):
            try:
                broadcast_sock.setsockopt(SOL_SOCKET, 25, self.routing_table[x]['iface'].encode('utf-8'))

                packet = createHellopkt(1, self.id)
                broadcast_sock.sendto(packet, (self.routing_table[x]['bcast'], self.port))
                print('Iface: {}\tSent: {}\tTo: {}'.format(self.routing_table[x]['iface'], packet, '{}, 8888'.format(self.routing_table[x]['bcast'])))

                
                packet, addr = broadcast_sock.recvfrom(self.buffer_size)
                contents = read_pkt(packet)
                
                #If recv from self then try again until socket times out
                while contents[2] == self.id:
                    packet, addr = broadcast_sock.recvfrom(self.buffer_size)
                    contents = read_pkt(packet)

                print('Received: {}\tFrom: {}'.format(packet, contents[2]))
       
                if contents[1] == 0 and contents[2] is not self.id:    
                    self.bootstrap_update_routing_table(self.routing_table[x]['iface'], contents[2], addr[0], addr[1])

            except OSError as e:
                print('Timeout')
                continue

        self.save_routing_table()
        print('{} finished booting'.format(self.id))
        broadcast_sock.close()

    def ls_broadcast(self):
        #Sends out a broadcast with a Hello packet to all neighbors via a broadcast adress
        temp_routing_table = self.routing_table

        broadcast_sock = socket(AF_INET, SOCK_DGRAM)
        broadcast_sock.setsockopt(SOL_SOCKET, SO_BROADCAST,1)
        broadcast_sock.settimeout(0.5)
        broadcast_sock.bind(('', self.port))

        #Get number of interfaces since routing table has probably changed since bootstrap
        initial_rt_length = sum([1 for route in self.routing_table if route['iface'] is not '-'])
        for x in range(initial_rt_length):
            try:
                #25 is int code for SO_BINDTODEVICE
                broadcast_sock.setsockopt(SOL_SOCKET, 25, self.routing_table[x]['iface'].encode('utf-8'))
                packet = createLSpkt(self.id, self.routing_table)
                broadcast_sock.sendto(packet, (self.routing_table[x]['bcast'], self.port))
                print('Iface: {}\tTo: {}'.format(self.routing_table[x]['iface'], '{}, 8888'.format(self.routing_table[x]['bcast'])))

            except OSError as e:
                continue

        broadcast_sock.close()
        self.intf_listen()

    def intf_listen(self):
        #Listens on all interfaces and handles all incoming packets based on their packet type
        print('Listening on all interfaces')
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) #To send broadcasts using bcast addr for LS
        sock.bind(('',self.port))

        contents = None
        while True:
            packet, addr = sock.recvfrom(self.buffer_size)
            contents = read_pkt(packet)
            print('Received: {}\tFrom: {}'.format(packet, contents[2]))

            if contents[0] == 0:   #Hello
                if contents[1] == 0:
                    pass

                elif contents[1] == 1 and self.check_route(contents[2]) == False:
                    packet = createHellopkt(0, self.id)
                    sock.sendto(packet, addr)
                    self.routing_table.append({"dest_id": contents[2], "dest_addr": addr[0], "dest_port": addr[1], "gateway": "-", "iface":"-", "bcast":"-", "cost": 1})
                    self.save_routing_table()

                elif contents[1] == 1 and self.check_route(contents[2]) == True:
                    packet = createHellopkt(0, self.id)
                    sock.sendto(packet, addr)    

                print('Sent: {}\tTo: {}'.format(packet, contents[2]))

            elif contents[0] == 1 and contents[2] is not self.id: #LS
                temp_routing_table = len(self.routing_table)
                self.update_routing_table(contents[4], contents[2], addr) #received table, src

                #Random delay before ls_broadcasting
                time.sleep(random.random())

                if temp_routing_table is not len(self.routing_table):
                    #If something gets updated it triggers a routing update
                    sock.close()
                    self.ls_broadcast()

            elif contents[0] == 3: #Data
                src, seq, dest, Ndest = contents[2], contents[1], contents[5], contents[4]
                if dest != 0: 
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
                        #Forces routing update
                        sock.close()
                        self.ls_broadcast()
                elif dest == 0:
                    #Make and send ack back to sender
                    ack_packet = createACKpkt(self.id, seq, src)
                    sock.sendto(ack_packet, addr)

                    #Copy and send packet to k lowest destinations only hosts
                    dest_routes = self.pick_k_closest_hosts(Ndest)
                    data = contents[9]
                    print(dest_routes)
                    for route in dest_routes:
                        packet = createDatapkt(src, data, Rdest=route['dest_id'])
                        sock.sendto(packet, (route['dest_addr'],route['dest_port']))
                        print('Sent: {}\t To: {}'.format(packet, route['dest_id']))

                        #Wait to recv ack
                        packet, addr = sock.recvfrom(self.buffer_size)
                        contents = read_pkt(packet)
                        print('Received: {}\tFrom: {}'.format(packet, contents[2]))

            elif contents[0] == 4: #ACK
                pass

            else:
                pass
            #print(self.routing_table)
        sock.close()

if __name__=='__main__':
    router=Router()
    logging.basicConfig(filename='debug_logs/{}_debug.log'.format(router.id), level=logging.INFO)
    
    with open('routing_tables/{}_routing_table.json'.format(router.id), 'r') as fp:
        router.routing_table = json.load(fp)

    router.bootstrap()
    router.intf_listen()





