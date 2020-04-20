
#!/usr/bin/python
#Topology for example network 2 from final project slides
#Author: Group 6
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.cli import CLI
from mininet.node import Node
from mininet.link import TCLink
from cleanup import cleanup
from bootstrap import bootstrap
import logging
from utility import generate_routing_table
import os

def example_network_2():
    #Create new mininet
    net = Mininet(link=TCLink, controller=None, cleanup=True)

    #Create nodes
    info("Creating nodes\n")
    r1 = net.addHost( 'r1', inNamespace=False )
    r2 = net.addHost( 'r2', inNamespace=False )
    r3 = net.addHost( 'r3', inNamespace=False )
    r4 = net.addHost( 'r4', inNamespace=False )
    r5 = net.addHost( 'r5', inNamespace=False )
    r6 = net.addHost( 'r6', inNamespace=False )
    s = net.addHost( 's', inNamespace=False )
    d1 = net.addHost( 'd1', inNamespace=False )
    d2 = net.addHost( 'd2', inNamespace=False )
    d3 = net.addHost( 'd3', inNamespace=False )

    #Establishing links
    info("Creating links\n")
    net.addLink( s, r1, intfName2='r1-eth0' )
    net.addLink( r1, r2, intfName1='r1-eth1', intfName2='r2-eth0' )
    net.addLink( r1, r4, intfName1='r1-eth2' )
    net.addLink( r2, r3, intfName1='r2-eth1', intfName2='r3-eth0' )
    net.addLink( r3, d1, intfName1='r3-eth1', intfName2='d1-eth0' )
    net.addLink( r4, r3, intfName1='r4-eth1', intfName2='r3-eth2' )
    net.addLink( r4, r5, intfName1='r4-eth2', intfName2='r5-eth0' )
    net.addLink( r5, r6, intfName1='r5-eth1', intfName2='r6-eth0' )
    net.addLink( r6, d2, intfName1='r6-eth1' )
    net.addLink( r6, d3, intfName1='r6-eth2' )

    #Setting interface ip addresses since params1 or params2 just will not work
    #router1 = net.get( 'r1' )
    #router1.setIP(

    #Set up forwarding on routers
    r1.cmd( 'sysctl net.ipv4.ip_forward=1' )
    r2.cmd( 'sysctl net.ipv4.ip_forward=1' )
    r3.cmd( 'sysctl net.ipv4.ip_forward=1' )
    r4.cmd( 'sysctl net.ipv4.ip_forward=1' )
    r5.cmd( 'sysctl net.ipv4.ip_forward=1' )
    r6.cmd( 'sysctl net.ipv4.ip_forward=1' )

    #Temp array to goes through all nodes until we find function that does it
    routers = [r1, r2, r3, r4, r5, r6]
    hosts = [s, d1, d2, d3]

    #Save ifconfig file
    with open('ifconfig.txt','w') as fp:
        fp.write(r1.cmd('ifconfig'))

    #Boostrap, starts scripts on each node
    info('Booting router scripts and generating routing tables')
    for router in routers:
        generate_routing_table(str(router), net.links, 'ifconfig.txt')
    	router.cmd( 'python router.py {}'.format(str(router)) ) 

    info('Booting Host Scripts')
    for host in hosts:
        host.cmd( 'python host.py {}'.format(str(host)) )

    #Build net
    info("Building network\n")
    net.build()

    CLI( net )

if __name__ == '__main__':
    logging.basicConfig(filename='debug_logs/network_debug.log', level=logging.INFO)
    example_network_2()
    cleanup()



