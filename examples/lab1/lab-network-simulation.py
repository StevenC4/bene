import sys
import os
sys.path.append('..')

from src.sim import Sim
from src import packet

from networks.network import Network

if not os.path.exists("../../out/lab1/2-nodes"):
    os.makedirs("../../out/lab1/2-nodes")
if not os.path.exists("../../out/lab1/3-nodes"):
    os.makedirs("../../out/lab1/3-nodes")

class TransmitApp(object):
    def __init__(self, node, filename, description):
        self.node = node
        self.filename = filename

        f = open(filename, "w")
        f.write(description)
        f.close()

    def receive_packet(self,packet):
        f = open(self.filename, "a")
        f.write("Node:\t\t\t\t{:s}\n".format(self.node.hostname))
        f.write("Packet Created:\t\t{:f}\n".format(packet.created))
        f.write("Packet Identifier:\t{:d}\n".format(packet.ident))
        f.write("Time Received:\t\t{:f}\n\n".format(Sim.scheduler.current_time()))
        f.close()

if __name__ == '__main__':
    # ------------------------- 2 nodes, 1Mbps, 1s, 1 packet, 1000 bytes ------------------------- #

    # parameters
    Sim.scheduler.reset()

    # setup network
    net = Network('../../networks/lab1/2-nodes/1Mbps-1s.txt')

    # setup routes
    n1 = net.get_node('n1')
    n2 = net.get_node('n2')
    n1.add_forwarding_entry(address=n2.get_address('n1'),link=n1.links[0])
    n2.add_forwarding_entry(address=n1.get_address('n2'),link=n2.links[0])

    # setup app
    filename = "../../out/lab1/2-nodes/1Mbps-1s-1packet-1000bytes.txt"
    description = "2 Nodes - 1 packet\n1Mbps, 1s, 1 packet, 1000 bytes\n\n"
    t = TransmitApp(n2, filename, description)
    n2.add_protocol(protocol="delay", handler=t)

    # send one packet
    p = packet.Packet(destination_address=n2.get_address('n1'),ident=1,protocol='delay',length=1000)
    Sim.scheduler.add(delay=0, event=p, handler=n1.send_packet)

    # run the simulation
    Sim.scheduler.run()


    # ------------------------- 2 nodes, 100bps, 10ms, 1 packets, 1000 bytes ------------------------- #

    # parameters
    Sim.scheduler.reset()

    # setup network
    net = Network('../../networks/lab1/2-nodes/100bps-10ms.txt')

    # setup routes
    n1 = net.get_node('n1')
    n2 = net.get_node('n2')
    n1.add_forwarding_entry(address=n2.get_address('n1'),link=n1.links[0])
    n2.add_forwarding_entry(address=n1.get_address('n2'),link=n2.links[0])

    # setup app
    filename = "../../out/lab1/2-nodes/100bps-10ms-1packet-1000bytes.txt"
    description = "2 Nodes - 1 packet\n100bps, 10ms, 1 packet, 1000 bytes\n\n"
    t = TransmitApp(n2, filename, description)
    n2.add_protocol(protocol="delay", handler=t)

    # send one packet
    p = packet.Packet(destination_address=n2.get_address('n1'),ident=1,protocol='delay',length=1000)
    Sim.scheduler.add(delay=0, event=p, handler=n1.send_packet)

    # run the simulation
    Sim.scheduler.run()


    # ------------------------- 2 nodes, 1Mbps, 10ms, 4 packets, 1000 bytes ------------------------- #

    # parameters
    Sim.scheduler.reset()

    # setup network
    net = Network('../../networks/lab1/2-nodes/1Mbps-10ms.txt')

    # setup routes
    n1 = net.get_node('n1')
    n2 = net.get_node('n2')
    n1.add_forwarding_entry(address=n2.get_address('n1'),link=n1.links[0])
    n2.add_forwarding_entry(address=n1.get_address('n2'),link=n2.links[0])

    # setup app
    filename = "../../out/lab1/2-nodes/1Mbps-10ms-4packets-1000bytes.txt"
    description = "2 Nodes - 1 packet\n1Mbps, 10ms, 4 packets, 1000 bytes\n\n"
    t = TransmitApp(n2, filename, description)
    n2.add_protocol(protocol="delay", handler=t)

    # send four packets
    p1 = packet.Packet(destination_address=n2.get_address('n1'),ident=1,protocol='delay',length=1000)
    p2 = packet.Packet(destination_address=n2.get_address('n1'),ident=2,protocol='delay',length=1000)
    p3 = packet.Packet(destination_address=n2.get_address('n1'),ident=3,protocol='delay',length=1000)
    p4 = packet.Packet(destination_address=n2.get_address('n1'),ident=4,protocol='delay',length=1000)
    Sim.scheduler.add(delay=0, event=p1, handler=n1.send_packet)
    Sim.scheduler.add(delay=0, event=p2, handler=n1.send_packet)
    Sim.scheduler.add(delay=0, event=p3, handler=n1.send_packet)
    Sim.scheduler.add(delay=2, event=p4, handler=n1.send_packet)

    # run the simulation
    Sim.scheduler.run()


    # ------------------------- 3 nodes, 2 fast links, 1000 packets, 1000 bytes ------------------------- #

    # parameters
    Sim.scheduler.reset()

    # setup network
    net = Network('../../networks/lab1/3-nodes/2-fast-links.txt')

    # setup routes
    n1 = net.get_node('n1')
    n2 = net.get_node('n2')
    n3 = net.get_node('n3')
    # n1 -> n2
    n1.add_forwarding_entry(address=n2.get_address('n1'),link=n1.links[0])
    # n1 -> n3
    n1.add_forwarding_entry(address=n3.get_address('n2'),link=n1.links[0])
    # n2 -> n1
    n2.add_forwarding_entry(address=n1.get_address('n2'),link=n2.links[0])
    # n2 -> n3
    n2.add_forwarding_entry(address=n3.get_address('n2'),link=n2.links[1])
    # n3 -> n2
    n3.add_forwarding_entry(address=n2.get_address('n3'),link=n3.links[0])
    # n3 -> n1
    n3.add_forwarding_entry(address=n1.get_address('n2'),link=n3.links[0])

    # setup app
    filename = "../../out/lab1/3-nodes/2-fast-links.txt"
    description = "3 Nodes - 2 fast links\n\n"
    t3 = TransmitApp(n3, filename, description)
    n3.add_protocol(protocol="transmit", handler=t3)

    # send one packet
    for x in range(0, 1000):
        p = packet.Packet(destination_address=n3.get_address('n2'),ident=x,protocol='transmit',length=1000)
        Sim.scheduler.add(delay=0, event=p, handler=n1.send_packet)

    # run the simulation
    Sim.scheduler.run()

    # ------------------------- 3 nodes, 2 fast links, 1000 packets, 1000 bytes ------------------------- #

    # parameters
    Sim.scheduler.reset()

    # setup network
    net = Network('../../networks/lab1/3-nodes/2-fast-links.txt')

    # setup routes
    n1 = net.get_node('n1')
    n2 = net.get_node('n2')
    n3 = net.get_node('n3')
    # n1 -> n2
    n1.add_forwarding_entry(address=n2.get_address('n1'),link=n1.links[0])
    # n1 -> n3
    n1.add_forwarding_entry(address=n3.get_address('n2'),link=n1.links[0])
    # n2 -> n1
    n2.add_forwarding_entry(address=n1.get_address('n2'),link=n2.links[0])
    # n2 -> n3
    n2.add_forwarding_entry(address=n3.get_address('n2'),link=n2.links[1])
    # n3 -> n2
    n3.add_forwarding_entry(address=n2.get_address('n3'),link=n3.links[0])
    # n3 -> n1
    n3.add_forwarding_entry(address=n1.get_address('n2'),link=n3.links[0])

    # setup app
    filename = "../../out/lab1/3-nodes/2-fast-links.txt"
    description = "3 Nodes - 2 fast links\n\n"
    t3 = TransmitApp(n3, filename, description)
    n3.add_protocol(protocol="transmit", handler=t3)

    # send one packet
    for x in range(0, 1000):
        p = packet.Packet(destination_address=n3.get_address('n2'),ident=x,protocol='transmit',length=1000)
        Sim.scheduler.add(delay=0, event=p, handler=n1.send_packet)

    # run the simulation
    Sim.scheduler.run()


    # ------------------------- 3 nodes, 2 fast links upgraded, 1000 packets, 1000 bytes ------------------------- #

    # parameters
    Sim.scheduler.reset()

    # setup network
    net = Network('../../networks/lab1/3-nodes/2-fast-links-upgraded.txt')

    # setup routes
    n1 = net.get_node('n1')
    n2 = net.get_node('n2')
    n3 = net.get_node('n3')
    # n1 -> n2
    n1.add_forwarding_entry(address=n2.get_address('n1'),link=n1.links[0])
    # n1 -> n3
    n1.add_forwarding_entry(address=n3.get_address('n2'),link=n1.links[0])
    # n2 -> n1
    n2.add_forwarding_entry(address=n1.get_address('n2'),link=n2.links[0])
    # n2 -> n3
    n2.add_forwarding_entry(address=n3.get_address('n2'),link=n2.links[1])
    # n3 -> n2
    n3.add_forwarding_entry(address=n2.get_address('n3'),link=n3.links[0])
    # n3 -> n1
    n3.add_forwarding_entry(address=n1.get_address('n2'),link=n3.links[0])

    # setup app
    filename = "../../out/lab1/3-nodes/2-fast-links-upgraded.txt"
    description = "3 Nodes - 2 fast links - upgraded\n\n"
    t3 = TransmitApp(n3, filename, description)
    n3.add_protocol(protocol="transmit", handler=t3)

    # send one packet
    for x in range(0, 1000):
        p = packet.Packet(destination_address=n3.get_address('n2'),ident=x,protocol='transmit',length=1000)
        Sim.scheduler.add(delay=0, event=p, handler=n1.send_packet)

    # run the simulation
    Sim.scheduler.run()


    # ------------------------- 3 nodes, 2 fast links upgraded, 1000 packets, 1000 bytes ------------------------- #

    # parameters
    Sim.scheduler.reset()

    # setup network
    net = Network('../../networks/lab1/3-nodes/1-fast-link-1-slow-link.txt')

    # setup routes
    n1 = net.get_node('n1')
    n2 = net.get_node('n2')
    n3 = net.get_node('n3')
    # n1 -> n2
    n1.add_forwarding_entry(address=n2.get_address('n1'),link=n1.links[0])
    # n1 -> n3
    n1.add_forwarding_entry(address=n3.get_address('n2'),link=n1.links[0])
    # n2 -> n1
    n2.add_forwarding_entry(address=n1.get_address('n2'),link=n2.links[0])
    # n2 -> n3
    n2.add_forwarding_entry(address=n3.get_address('n2'),link=n2.links[1])
    # n3 -> n2
    n3.add_forwarding_entry(address=n2.get_address('n3'),link=n3.links[0])
    # n3 -> n1
    n3.add_forwarding_entry(address=n1.get_address('n2'),link=n3.links[0])

    # setup app
    filename = "../../out/lab1/3-nodes/1-fast-link-1-slow-link.txt"
    description = "3 Nodes - 1 fast link, 1 slow link\n\n"
    t3 = TransmitApp(n3, filename, description)
    n3.add_protocol(protocol="transmit", handler=t3)

    # send one packet
    for x in range(0, 1000):
        p = packet.Packet(destination_address=n3.get_address('n2'),ident=x,protocol='transmit',length=1000)
        Sim.scheduler.add(delay=0, event=p, handler=n1.send_packet)

    # run the simulation
    Sim.scheduler.run()
