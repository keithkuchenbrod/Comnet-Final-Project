
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
    net.addLink( s, r1 )
    net.addLink( r1, r2 )
    net.addLink( r1, r4 )
    net.addLink( r2, r3 )
    net.addLink( r3, d1 )
    net.addLink( r4, r3 )
    net.addLink( r4, r5 )
    net.addLink( r5, r6 )
    net.addLink( r6, d2 )
    net.addLink( r6, d3 )

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

    #Boostrap, starts scripts on each node
    info('Booting router scripts and generating routing tables')
    for router in routers:
        generate_routing_table(router.cmd('route -n').split(), str(router))
    	router.cmd( 'python router.py {}'.format(str(router)) ) 

    info('Booting Host Scripts')
    for host in hosts:
        host.cmd( 'python host.py {}'.format(str(host)) )

    #Build net
    info("Building network\n")
    net.build()

    CLI( net )

if __name__ == '__main__':
    example_network_2()
    cleanup()



