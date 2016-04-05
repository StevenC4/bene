import sys
sys.path.append('..')

from src.sim import Sim
from src import node
from src import link
from src import packet

from networks.network import Network

from DVRoutingApp import DVRoutingApp

import random

if __name__ == '__main__':
    # parameters
    Sim.scheduler.reset()
    Sim.set_debug(True)

    # setup network
    net = Network('networks/five-nodes.txt')

    # get nodes
    n1 = net.get_node('n1')
    n2 = net.get_node('n2')
    n3 = net.get_node('n3')
    n4 = net.get_node('n4')
    n5 = net.get_node('n5')

    # setup broadcast application
    rp1 = DVRoutingApp(n1)
    n1.add_protocol(protocol="dvrouting",handler=rp1)
    rp2 = DVRoutingApp(n2)
    n2.add_protocol(protocol="dvrouting",handler=rp2)
    rp3 = DVRoutingApp(n3)
    n3.add_protocol(protocol="dvrouting",handler=rp3)
    rp4 = DVRoutingApp(n4)
    n4.add_protocol(protocol="dvrouting",handler=rp4)
    rp5 = DVRoutingApp(n5)
    n5.add_protocol(protocol="dvrouting",handler=rp5)

    # send a broadcast packet from 1 with TTL 2, so everyone should get it
    #p = packet.Packet(source_address=n1.get_address('n2'),destination_address=0,ident=1,ttl=1,protocol='dvrouting',length=100)
    #Sim.scheduler.add(delay=0, event=p, handler=n1.send_packet)

    # send a broadcast packet from 1 with TTL 1, so just nodes 2 and 3
    # should get it
    #p = packet.Packet(source_address=n1.get_address('n2'),destination_address=0,ident=2,ttl=1,protocol='dvrouting',length=100)
    #Sim.scheduler.add(delay=1, event=p, handler=n1.send_packet)

    # send a broadcast packet from 3 with TTL 1, so just nodes 1, 4, and 5
    # should get it
    #p = packet.Packet(source_address=n3.get_address('n1'),destination_address=0,ident=3,ttl=1,protocol='dvrouting',length=100)
    #Sim.scheduler.add(delay=2, event=p, handler=n3.send_packet)

    # run the simulation
    Sim.scheduler.run()
