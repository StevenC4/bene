import sys
sys.path.append('..')

from sim import Sim
from src.tcp import TCP
from networks.network import Network

import csv
import os
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
from operator import itemgetter

total_time = 0
num_transmissions = 0

times = {}

class Transport(object):
    def __init__(self,node):
        self.node = node
        self.binding = {}
        self.node.add_protocol(protocol="TCP",handler=self)

    def bind(self,connection,source_address,source_port,
             destination_address,destination_port):
        # setup binding so that packets we receive for this combination
        # are sent to the right socket
        tuple = (destination_address,destination_port,
                 source_address,source_port)
        self.binding[tuple] = connection

    def receive_packet(self,packet):
        # Add to average queueing delay
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
        Sim.trace('AppHandler',"application got %d bytes" % (len(data)))
        self.f.write(data)
        self.f.flush()


class Main(object):
    def __init__(self):
        global total_time
        global num_transmissions

        # losses = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        # losses = [0.7, 0.75, 0.8, 0.85, 0.9, 0.95]
        losses = [0.9, 0.925, 0.95, 0.975]

        for loss in losses:
            total_time = 0
            num_transmissions = 0
            for x in range(0,10):
                self.setup_and_run(loss, False)
            average_time = total_time / num_transmissions
            times[loss] = {"static": average_time}

            total_time = 0
            num_transmissions = 0
            for x in range(0,10):
                self.setup_and_run(loss, False)
            average_time = total_time / num_transmissions
            times[loss]["dynamic"] = average_time

        self.save_plot(times, "Loss", "Static Retransmission Timer", "Dynamic Retransmission Timer", "out/time-per-loss-zoomed.png")

    def save_plot(self, dict, x_col_name, y_col_name_1, y_col_name_2, save_file_path):
        with open('out/tmp/loss-times.csv', 'wb') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=[x_col_name, y_col_name_1, y_col_name_2])

            writer.writeheader()
            for key in sorted(dict.keys()):
                values = dict[key]
                writer.writerow({x_col_name: key, y_col_name_1: values["static"], y_col_name_2: values["dynamic"]})

        df = pd.read_csv("out/tmp/loss-times.csv")
        plt.figure()

        experimental = df.plot(x=x_col_name, y=[y_col_name_1, y_col_name_2])
        experimental.set_xlabel("Loss (% packets)")
        experimental.set_ylabel("Time (sec)")

        fig = experimental.get_figure()
        fig.savefig(save_file_path)

    def setup_and_run(self, loss, dyanmic_rto):
        self.directory = 'received'
        self.filename = 'internet-architecture.pdf'
        self.loss = loss
        self.dynamic_rto = dyanmic_rto

        self.run()

        global num_transmissions
        global total_time

        num_transmissions += 1

        time = Sim.scheduler.current_time()
        total_time += time

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
        t2 = Transport(n2)

        # setup application
        a = AppHandler(self.filename)

        # setup connection
        c1 = TCP(t1,n1.get_address('n2'),1,n2.get_address('n1'),1,a,dynamic_rto=self.dynamic_rto)
        c2 = TCP(t2,n2.get_address('n1'),1,n1.get_address('n2'),1,a,dynamic_rto=self.dynamic_rto)

        f = open(self.filename, "rb")
        try:
            data = f.read(1000)
            while data != "":
                Sim.scheduler.add(delay=0, event=data, handler=c1.send)
                data = f.read(1000)
        finally:
            f.close()

        # run the simulation
        Sim.scheduler.run()

if __name__ == '__main__':
    m = Main()
