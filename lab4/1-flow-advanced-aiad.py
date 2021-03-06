import sys
sys.path.append('..')

from src.sim import Sim
from src.transport import Transport
from tcpaiad import TCP

from network import Network

from plotter import Plotter

import optparse
import os
import subprocess

import threading

original_size = 0
received_size = {}

plotter = Plotter('out/1-flow-advanced-aiad')

decisecondEvent = None

tcps = []

class AppHandler(object):
    def __init__(self,inputfile,plot=False,identifier=None):
        self.inputfile = inputfile
        self.directory = 'received'
        self.plot = plot
        self.identifier = identifier

        global received_size
        received_size[identifier] = 0

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        self.f = open("%s/%s" % (self.directory,self.inputfile),'wb')


    def receive_data(self,data):
        if self.plot:
            global original_size
            global received_size
            Sim.trace('AppHandler',"application got %d bytes" % (len(data)))
            self.f.write(data)
            received_size[self.identifier] += len(data)
            self.f.flush()
            turn_timer_off = True
            for identifier in received_size.keys():
                if received_size[identifier] != original_size:
                    turn_timer_off = False
                    break
            if turn_timer_off:
                global decisecondEvent
                Sim.scheduler.cancel(decisecondEvent)

    def add_plot_data(self,t,data,event):
        plotter.add_data(t,data,event,self.identifier)


class Main(object):
    def __init__(self):
        self.directory = 'received'
        self.parse_options()
        self.run()

        self.diff()

    def parse_options(self):
        parser = optparse.OptionParser(usage = "%prog [options]",
                                       version = "%prog 0.1")

        parser.add_option("-f","--inputfile",type="str",dest="inputfile",
                          default='internet-architecture.pdf',
                          help="filename to send")

        parser.add_option("-l","--loss",type="float",dest="loss",
                          default=0.0,
                          help="random loss rate")

        parser.add_option("-w","--window",type="int",dest="window",
                          default=1000,
                          help="window size");

        parser.add_option("-d","--debug",type="str",dest="debug",
                          default="",
                          help="debug statements")

        parser.add_option("-t","--type",type="str",dest="type",
                          default="Tahoe",
                          help="Type of TCP implementation (Tahoe or Reno)")

        parser.add_option("-s","--sequencefile",type="str",dest="sequencefile",
                          default="out/default",
                          help="Destination for sequence plot")

        (options,args) = parser.parse_args()
        self.inputfile = options.inputfile
        self.loss = options.loss
        self.window = options.window
        self.debug = options.debug
        self.type = options.type
        self.sequencefile = options.sequencefile

    def diff(self):
        args = ['diff','-u',self.inputfile,self.directory+'/'+self.inputfile]
        result = subprocess.Popen(args,stdout = subprocess.PIPE,shell=True).communicate()[0]
        print
        if not result:
            print "File transfer correct!"
        else:
            print "File transfer failed. Here is the diff:"
            print
            print result

    def decisecond(self,Sim):
        global decisecondEvent
        decisecondEvent = Sim.scheduler.add(delay=0.1, event=Sim, handler=self.decisecond)

        global tcps
        for tcp in tcps:
            tcp.spur_plot_data_submission()

    def run(self):
        # parameters
        Sim.scheduler.reset()

        if "a" in self.debug:
            Sim.set_debug('AppHandler')
        if "t" in self.debug:
            Sim.set_debug('TCP')

        # setup network
        networkPlotter = Plotter('out/1-flow-advanced-aiad')
        net = Network(config='networks/one-hop.txt',plotter=networkPlotter)
        net.loss(self.loss)

        # setup routes
        n1 = net.get_node('n1')
        n2 = net.get_node('n2')
        n1.add_forwarding_entry(address=n2.get_address('n1'),link=n1.links[0])
        n2.add_forwarding_entry(address=n1.get_address('n2'),link=n2.links[0])

        # setup transport
        t1 = Transport(n1)
        t2 = Transport(n2)

        c1 = TCP(t1,n1.get_address('n2'),1,n2.get_address('n1'),1,AppHandler(inputfile=self.inputfile,plot=True),window=self.window,type=self.type,receiver_flow_plot=True)
        c2 = TCP(t2,n2.get_address('n1'),1,n1.get_address('n2'),1,AppHandler(inputfile=self.inputfile),window=self.window,type=self.type,window_size_plot=True,sequence_plot=True)

        global tcps
        tcps = [c1, c2]

        global original_size
        f = open(self.inputfile, "rb")
        try:
            data = f.read(1000)
            while data != "":
                original_size += len(data)
                Sim.scheduler.add(delay=0, event=data, handler=c1.send)
                Sim.scheduler.add(delay=0, event=data, handler=c2.send)
                data = f.read(1000)
        finally:
            f.close()

        # run the simulation

        global decisecondEvent
        decisecondEvent = Sim.scheduler.add(delay=0.1, event=Sim, handler=self.decisecond)

        Sim.scheduler.run()

        networkPlotter.plot(self.sequencefile)
        plotter.plot(self.sequencefile);

if __name__ == '__main__':
    m = Main()
