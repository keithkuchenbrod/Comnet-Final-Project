#!/usr/bin/python
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.cli import CLI
#from mininet.node import Node
#from mininet.link import TCLink
from cleanup import cleanup
import logging
from utility import *
import os

def example_network_2():
    #Create new mininet
    net = Mininet()

    #Create nodes All lie within same subnet
    info("Creating nodes\n")
    r1 = net.addHost( '201', inNamespace=True, ip='192.168.1.2/24' )
    r2 = net.addHost( '202', inNamespace=True, ip='192.168.1.5/24' )
    r3 = net.addHost( '203', inNamespace=True, ip='192.168.1.7/24' )
    r4 = net.addHost( '204', inNamespace=True, ip='192.168.1.11/24' )
    r5 = net.addHost( '205', inNamespace=True, ip='192.168.1.14/24' )
    r6 = net.addHost( '206', inNamespace=True, ip='192.168.1.16/24' )
    s = net.addHost( '101', inNamespace=True, ip='192.168.1.1/24' )
    d1 = net.addHost( '102', inNamespace=True, ip='192.168.1.9/24' )
    d2 = net.addHost( '103', inNamespace=True, ip='192.168.1.19/24' )
    d3 = net.addHost( '104', inNamespace=True, ip='192.168.1.20/24' )

    #Establishing links
    info("Creating links\n")
    net.addLink( s, r1, intfName1='101-eth0', intfName2='201-eth0' )
    net.addLink( r1, r2, intfName1='201-eth1', intfName2='202-eth0' )
    net.addLink( r1, r4, intfName1='201-eth2', intfName2='204-eth0' )
    net.addLink( r2, r3, intfName1='202-eth1', intfName2='203-eth0' )
    net.addLink( r3, d1, intfName1='203-eth1', intfName2='102-eth0' )
    net.addLink( r4, r3, intfName1='204-eth1', intfName2='203-eth2' )
    net.addLink( r4, r5, intfName1='204-eth2', intfName2='205-eth0' )
    net.addLink( r5, r6, intfName1='205-eth1', intfName2='206-eth0' )
    net.addLink( r6, d2, intfName1='206-eth1', intfName2='103-eth0' )
    net.addLink( r6, d3, intfName1='206-eth2', intfName2='104-eth0' )

    #Setting up interface ips
    source, host1, host2, host3 = net.get('101'), net.get('102'), net.get('103'), net.get('104')
    router1 , router2, router3 = net.get('201'), net.get('202'), net.get('203')
    router4, router5, router6 = net.get('204'), net.get('205'), net.get('206')
    source.setIP('192.168.1.1/24')
    host1.setIP('192.168.1.9/24')
    host2.setIP('192.168.1.19/24')
    host3.setIP('192.168.1.20/24')
    router1.setIP('192.168.1.2/24', intf='201-eth0')
    router1.setIP('192.168.1.3/24', intf='201-eth1')
    router1.setIP('192.168.1.4/24', intf='201-eth2')
    router2.setIP('192.168.1.5/24', intf='202-eth0')
    router2.setIP('192.168.1.6/24', intf='202-eth1')
    router3.setIP('192.168.1.7/24', intf='203-eth0')
    router3.setIP('192.168.1.8/24', intf='203-eth1')
    router3.setIP('192.168.1.10/24', intf='203-eth2')
    router4.setIP('192.168.1.11/24', intf='204-eth0')
    router4.setIP('192.168.1.12/24', intf='204-eth1')
    router4.setIP('192.168.1.13/24', intf='204-eth2')
    router5.setIP('192.168.1.14/24', intf='205-eth0')
    router5.setIP('192.168.1.15/24', intf='205-eth1')
    router6.setIP('192.168.1.16/24', intf='206-eth0')
    router6.setIP('192.168.1.17/24', intf='206-eth1')
    router6.setIP('192.168.1.18/24', intf='206-eth2')

    #Set up forwarding on routers
    r1.cmd( 'sysctl -w net.ipv4.ip_forward=1' )
    r2.cmd( 'sysctl -w net.ipv4.ip_forward=1' )
    r3.cmd( 'sysctl -w net.ipv4.ip_forward=1' )
    r4.cmd( 'sysctl -w net.ipv4.ip_forward=1' )
    r5.cmd( 'sysctl -w net.ipv4.ip_forward=1' )
    r6.cmd( 'sysctl -w net.ipv4.ip_forward=1' )

    #Set routes in each namespace will try to automate making these dictionaries later. Already have some code to kinda do this
    routers = [r1, r2, r3, r4, r5, r6]
    all_routes = {'201':[{'dest':'192.168.1.1' , 'intf':'201-eth0'},{'dest':'192.168.1.5' , 'intf':'201-eth1'},{'dest':'192.168.1.11' , 'intf':'201-eth2'}],  
             '202':[{'dest':'192.168.1.3' , 'intf':'202-eth0'},{'dest':'192.168.1.7' , 'intf':'202-eth1'}],
             '203':[{'dest':'192.168.1.6' , 'intf':'203-eth0'},{'dest':'192.168.1.9' , 'intf':'203-eth1'},{'dest':'192.168.1.12' , 'intf':'203-eth2'}],
             '204':[{'dest':'192.168.1.4' , 'intf':'204-eth0'},{'dest':'192.168.1.10' , 'intf':'204-eth1'},{'dest':'192.168.1.14' , 'intf':'204-eth2'}],
             '205':[{'dest':'192.168.1.13' , 'intf':'205-eth0'},{'dest':'192.168.1.16' , 'intf':'205-eth1'}],
             '206':[{'dest':'192.168.1.15' , 'intf':'206-eth0'},{'dest':'192.168.1.19' , 'intf':'206-eth1'},{'dest':'192.168.1.20' , 'intf':'206-eth2'}]}
    
    routers = [r1, r2, r3, r4, r5, r6]
    for router in routers:
        routes = all_routes[str(router)]
        for route in routes:
            router.cmd( 'ip route add {} dev {}'.format(route['dest'], route['intf']))
         
    #Build network
    info('Building Network\n')
    net.build()

    CLI( net )

if __name__ == '__main__':
    logging.basicConfig(filename='debug_logs/network_debug.log', level=logging.INFO)
    example_network_2()
    cleanup()


