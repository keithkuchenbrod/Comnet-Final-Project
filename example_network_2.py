
#!/usr/bin/python
#Topology for example network 2 from final project slides
#Author: Group 6
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.cli import CLI
from mininet.node import Node
from mininet.link import TCLink
from cleanup import cleanup
import logging
from utility import generate_routing_table
import os
import threading 

def example_network_2():
    #Create new mininet
    net = Mininet(link=TCLink, controller=None, cleanup=True)

    #Create nodes
    info("Creating nodes\n")
    r1 = net.addHost( 'r1', inNamespace=False, ip='192.168.1.0/24' )
    r2 = net.addHost( 'r2', inNamespace=False, ip='192.168.2.0/24' )
    r3 = net.addHost( 'r3', inNamespace=False, ip='192.168.3.0/24' )
    r4 = net.addHost( 'r4', inNamespace=False, ip='192.168.4.0/24' )
    r5 = net.addHost( 'r5', inNamespace=False, ip='192.168.5.0/24' )
    r6 = net.addHost( 'r6', inNamespace=False, ip='192.168.6.0/24' )
    s = net.addHost( 's', inNamespace=False, ip='192.168.7.0/24' )
    d1 = net.addHost( 'd1', inNamespace=False, ip='192.168.8.0/24' )
    d2 = net.addHost( 'd2', inNamespace=False, ip='192.168.9.0/24' )
    d3 = net.addHost( 'd3', inNamespace=False, ip='192.168.10.0/24' )

    #Establishing links
    info("Creating links\n")
    net.addLink( s, r1, intfName2='r1-eth0' )
    net.addLink( r1, r2, intfName1='r1-eth1', intfName2='r2-eth0', params1={'ip':'192.168.1.1'} )
    net.addLink( r1, r4, intfName1='r1-eth2' )
    net.addLink( r2, r3, intfName1='r2-eth1', intfName2='r3-eth0' )
    net.addLink( r3, d1, intfName1='r3-eth1', intfName2='d1-eth0' )
    net.addLink( r4, r3, intfName1='r4-eth1', intfName2='r3-eth2' )
    net.addLink( r4, r5, intfName1='r4-eth2', intfName2='r5-eth0' )
    net.addLink( r5, r6, intfName1='r5-eth1', intfName2='r6-eth0' )
    net.addLink( r6, d2, intfName1='r6-eth1' )
    net.addLink( r6, d3, intfName1='r6-eth2' )

    #Setting up interface ips
    source, host1, host2, host3 = net.get('s'), net.get('d1'), net.get('d2'), net.get('d3')
    router1 , router2, router3 = net.get('r1'), net.get('r2'), net.get('r3')
    router4, router5, router6 = net.get('r4'), net.get('r5'), net.get('r6')
    source.setIP('192.168.7.0')
    host1.setIP('192.168.8.0')
    host2.setIP('192.168.9.0')
    host3.setIP('192.168.10.0')
    router1.setIP('192.168.1.0', intf='r1-eth0')
    router1.setIP('192.168.1.1', intf='r1-eth1')
    router1.setIP('192.168.1.2', intf='r1-eth2')
    router2.setIP('192.168.2.0', intf='r2-eth0')
    router2.setIP('192.168.2.1', intf='r2-eth1')
    router3.setIP('192.168.3.0', intf='r3-eth0')
    router3.setIP('192.168.3.1', intf='r3-eth1')
    router3.setIP('192.168.3.2', intf='r3-eth2')
    router4.setIP('192.168.4.0', intf='r4-eth0')
    router4.setIP('192.168.4.1', intf='r4-eth1')
    router4.setIP('192.168.4.2', intf='r4-eth2')
    router5.setIP('192.168.5.0', intf='r5-eth0')
    router5.setIP('192.168.5.1', intf='r5-eth1')
    router6.setIP('192.168.6.0', intf='r6-eth0')
    router6.setIP('192.168.6.1', intf='r6-eth1')
    router6.setIP('192.168.6.2', intf='r6-eth2')

    #Set up forwarding on routers
    r1.cmd( 'sysctl net.ipv4.ip_forward=1' )
    r2.cmd( 'sysctl net.ipv4.ip_forward=1' )
    r3.cmd( 'sysctl net.ipv4.ip_forward=1' )
    r4.cmd( 'sysctl net.ipv4.ip_forward=1' )
    r5.cmd( 'sysctl net.ipv4.ip_forward=1' )
    r6.cmd( 'sysctl net.ipv4.ip_forward=1' )

    #Build network
    info('Building Network\n')
    net.build()

    #Temp array to goes through all nodes until we find function that does it
    routers = [r1, r2, r3, r4, r5, r6]
    hosts = [d1, d2, d3]

    #Save ifconfig file
    with open('ifconfig.txt','w') as fp:
        fp.write(r1.cmd('ifconfig'))

    #Boostrap, starts scripts on each node
    info('Booting router scripts and generating routing tables')
    threads = []
    for router in routers:
        #logging.info(str(router))
        #t = threading.Thread(router.cmd( 'python router.py {}'.format(str(router)) ) )
        #threads.append(t)
        #t.start()
        generate_routing_table(str(router), net.links, 'ifconfig.txt')
        #router.cmd( 'nohup python router.py {} &'.format(str(router)))

    info('Booting Host Scripts')
    #for host in hosts:
        #logging.info(str(host))
        #host.cmd( 'python host.py {}'.format(str(host)) )

    info('Booting Source Host')
    #logging.info(str(s))
    #s.cmd( 'python host.py {}'.format('s')

    CLI( net )

if __name__ == '__main__':
    logging.basicConfig(filename='debug_logs/network_debug.log', level=logging.INFO)
    example_network_2()
    cleanup()


