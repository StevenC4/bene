from __future__ import division
import random
import csv
import sys
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append('..')

from src.sim import Sim
from src import packet
from networks.network import Network

results = {}

class Generator(object):
    def __init__(self,node,destination,load,duration):
        self.node = node
        self.load = load
        self.duration = duration
        self.start = 0
        self.ident = 1

    def handle(self,event):
        # quit if done
        now = Sim.scheduler.current_time()
        if (now - self.start) > self.duration:
            return

        # generate a packet
        self.ident += 1
        p = packet.Packet(destination_address=destination,ident=self.ident,protocol='delay',length=1000)
        Sim.scheduler.add(delay=0, event=p, handler=self.node.send_packet)
        # schedule the next time we should generate a packet
        Sim.scheduler.add(delay=random.expovariate(self.load), event='generate', handler=self.handle)

class DelayHandler(object):
    def __init__(self, percentage):
        self.percentage = percentage

    def receive_packet(self,packet):
        if self.percentage not in results:
            results[self.percentage] = []
        results[self.percentage].append(packet.queueing_delay)

if __name__ == '__main__':
    # parameters

    percentages = [.1, .2, .3, .4, .5, .6, .7, .75, .8, .9, .95, .98]

    max_rate = 1000000/(1000*8)

    for percentage in percentages:
        for x in range (0, 3):
            Sim.scheduler.reset()

            # setup network
            net = Network('networks/one-hop.txt')

            # setup routes
            n1 = net.get_node('n1')
            n2 = net.get_node('n2')
            n1.add_forwarding_entry(address=n2.get_address('n1'),link=n1.links[0])
            n2.add_forwarding_entry(address=n1.get_address('n2'),link=n2.links[0])

            # setup app
            d = DelayHandler(percentage=percentage)
            net.nodes['n2'].add_protocol(protocol="delay",handler=d)

            # setup packet generator
            destination = n2.get_address('n1')
            load = percentage*max_rate
            g = Generator(node=n1,destination=destination,load=load,duration=10)
            Sim.scheduler.add(delay=0, event='generate', handler=g.handle)
    
            # run the simulation
            Sim.scheduler.run()

    with open('out/lab1/percentages.csv', 'wb') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['Utilization', 'Queueing Delay', 'Queueing Delay Theoretical'])


        writer.writeheader()
        for percentage in percentages:
            average = sum(results[percentage]) / len(results[percentage])
            delay_theoretical = (1 / (2 * 125)) * (percentage / (1 - percentage))
            writer.writerow({'Utilization': percentage, 'Queueing Delay': average, 'Queueing Delay Theoretical': delay_theoretical})

    df = pd.read_csv("out/lab1/percentages.csv")
    plt.figure()

    experimental = df.plot(x='Utilization', y=['Queueing Delay', 'Queueing Delay Theoretical'])
    experimental.set_xlabel("Utilization")
    experimental.set_ylabel("Queueing Delay")

    fig = experimental.get_figure()
    fig.savefig('out/lab1/line.png')