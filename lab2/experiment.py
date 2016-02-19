import sys
sys.path.append('..')

from src.sim import Sim
from src.tcp import TCP
from networks.network import Network
from operator import itemgetter

import pandas as pd
import matplotlib.pyplot as plt
import os
import subprocess

original_size = 0
received_size = 0

experimental_throughput = {}
experimental_queueing_delay = {}

total_queueing_delay = 0
total_packets_received = 0

class Transport(object):
    def __init__(self,node,add_to_queueing_delay=False):
        self.node = node
        self.binding = {}
        self.node.add_protocol(protocol="TCP",handler=self)
        self.add_to_queueing_delay = add_to_queueing_delay

    def bind(self,connection,source_address,source_port,
             destination_address,destination_port):
        # setup binding so that packets we receive for this combination
        # are sent to the right socket
        tuple = (destination_address,destination_port,
                 source_address,source_port)
        self.binding[tuple] = connection

    def receive_packet(self,packet):
        # Add to average queueing delay
        if self.add_to_queueing_delay:
            global total_packets_received
            global total_queueing_delay
            total_packets_received += 1
            total_queueing_delay += packet.queueing_delay

        tuple = (packet.source_address,packet.source_port,
                 packet.destination_address,packet.destination_port)
        self.binding[tuple].receive_packet(packet)

    def send_packet(self,packet):
        Sim.scheduler.add(delay=0, event=packet, handler=self.node.send_packet)


class AppHandler(object):
    def __init__(self,filename):
        self.filename = filename
        self.directory = 'received'
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        self.f = open("%s/%s" % (self.directory,self.filename),'wb')

    def receive_data(self,data):
        global original_size
        global received_size
        Sim.trace('AppHandler',"application got %d bytes" % (len(data)))
        self.f.write(data)
        received_size += len(data)
        self.f.flush()
        # if received_size == original_size:


class Main(object):
    def __init__(self):
        window_sizes = [
            1000,
            2000,
            5000,
            10000,
            15000,
            20000
        ]
        for window_size in window_sizes:
            self.setup_and_run(window_size)

        global experimental_throughput
        global experimental_queueing_delay

        self.save_plot(experimental_throughput, "Window Size (bytes)", "Throughput (bps)", "out/throughput.png")
        self.save_plot(experimental_queueing_delay, "Window Size (bytes)", "Average Queueing Delay (sec)", "out/average-queueing-delay.png")

    def save_plot(self, dict, x_col_name, y_col_name, save_file_path):
        df = pd.DataFrame(sorted([[key,value] for key,value in dict.items()], key=itemgetter(0)), columns=[x_col_name,y_col_name])
        plt.figure()

        experimental = df.plot(x=x_col_name, y=y_col_name)
        experimental.set_xlabel(x_col_name)
        experimental.set_ylabel(y_col_name)

        fig = experimental.get_figure()
        fig.savefig(save_file_path)

    def setup_and_run(self, window_size):
        global total_queueing_delay
        total_queueing_delay = 0

        global total_packets_received
        total_packets_received = 0

        self.directory = 'received'
        self.filename = 'internet-architecture.pdf'
        self.loss = 0
        self.window = window_size

        self.run()

        time = Sim.scheduler.current_time()
        throughput = (original_size * 8) / time

        average_queueing_delay = total_queueing_delay / total_packets_received

        print "Throughput: ",throughput
        print "Average Queueing Delay: ",average_queueing_delay

        global experimental_throughput
        global experimental_queueing_delay
        experimental_throughput[self.window] = throughput
        experimental_queueing_delay[self.window] = average_queueing_delay

        self.diff()

    def diff(self):
        args = ['diff','-u',self.filename,self.directory+'/'+self.filename]
        result = subprocess.Popen(args,stdout = subprocess.PIPE,shell=True).communicate()[0]
        print
        if not result:
            print "File transfer correct!"
        else:
            print "File transfer failed. Here is the diff:"
            print
            print result

    def run(self):
        # parameters
        Sim.scheduler.reset()

        if hasattr(self, 'debug') and "a" in self.debug:
            Sim.set_debug('AppHandler')
        if hasattr(self, 'debug') and "t" in self.debug:
            Sim.set_debug('TCP')

        # setup network
        net = Network('networks/one-hop.txt')
        net.loss(self.loss)

        # setup routes
        n1 = net.get_node('n1')
        n2 = net.get_node('n2')
        n1.add_forwarding_entry(address=n2.get_address('n1'),link=n1.links[0])
        n2.add_forwarding_entry(address=n1.get_address('n2'),link=n2.links[0])

        # setup transport
        t1 = Transport(n1)
        t2 = Transport(n2, True)

        # setup application
        a = AppHandler(self.filename)

        # setup connection
        c1 = TCP(t1,n1.get_address('n2'),1,n2.get_address('n1'),1,a,window=self.window)
        c2 = TCP(t2,n2.get_address('n1'),1,n1.get_address('n2'),1,a,window=self.window)

        global original_size
        f = open(self.filename, "rb")
        try:
            data = f.read(1000)
            while data != "":
                original_size += len(data)
                Sim.scheduler.add(delay=0, event=data, handler=c1.send)
                data = f.read(1000)
        finally:
            f.close()

        # run the simulation
        Sim.scheduler.run()

if __name__ == '__main__':
    m = Main()
