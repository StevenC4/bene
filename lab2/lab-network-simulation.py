import sys
import os
sys.path.append('..')

from src.sim import Sim
from src import packet

from src.tcp import TCP

from networks.network import Network

if not os.path.exists("out/lab2"):
    os.makedirs("out/lab2")

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
    net = Network('networks/one-hop.txt')

    # setup routes
    n1 = net.get_node('n1')
    n2 = net.get_node('n2')
    n1.add_forwarding_entry(address=n2.get_address('n1'),link=n1.links[0])
    n2.add_forwarding_entry(address=n1.get_address('n2'),link=n2.links[0])

    # setup app
    filename = "out/lab2/out.txt"
    description = "2 Nodes - 1 packet\n1Mbps, 1s, 1 packet, 1000 bytes\n\n"
    t1 = TransmitApp(n1, filename, description)
    t2 = TransmitApp(n2, filename, description)
    n2.add_protocol(protocol="delay", handler=t2)
    n2.add_protocol(protocol="delay", handler=t2)

    # send one packet
    c1 = TCP(t1,n1.get_address('n2'),1,n2.get_address('n1'),1,a,window=3000)
    c2 = TCP(t2,n2.get_address('n1'),1,n1.get_address('n2'),1,a,window=3000)

    p = packet.Packet(destination_address=n2.get_address('n1'),ident=1,protocol='delay',length=1000)
    Sim.scheduler.add(delay=0, event=p, handler=n1.send_packet)

    # run the simulation
    Sim.scheduler.run()
