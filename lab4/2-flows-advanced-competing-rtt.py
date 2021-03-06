import sys
sys.path.append('..')

from src.sim import Sim
from src.transport import Transport
from tcp import TCP

from network import Network

from plotter import Plotter

import optparse
import os
import subprocess

import threading

original_size = 0
received_size = {}

plotter = Plotter('out/2-flows-advanced-competing-rtt')

decisecondEvent = None

tcps = []
plotting = {}

class AppHandler(object):
    def __init__(self,inputfile,plot=False,identifier=None):
        self.inputfile = inputfile
        self.directory = 'received'
        self.plot = plot
        self.identifier = identifier

        global plotting
        plotting[identifier] = plot

        global received_size
        received_size[identifier] = 0
        
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        self.f = open("%s/%s" % (self.directory,self.inputfile),'wb')

    def receive_data(self,data):
        if self.plot:
            global original_size
            global received_size
            global plotting
            Sim.trace('AppHandler',"application got %d bytes" % (len(data)))
            self.f.write(data)
            received_size[self.identifier] += len(data)
            self.f.flush()
            turn_timer_off = True
            for identifier in received_size.keys():
                if received_size[identifier] != original_size and plotting[identifier]:
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
        networkPlotter = Plotter('out/2-flows-advanced-competing-rtt')
        net = Network(config='networks/competing-rtt.txt',plotter=networkPlotter)
        net.loss(self.loss)

        # setup routes
        A = net.get_node('A')
        B = net.get_node('B')
        C = net.get_node('C')
        D = net.get_node('D')

        # A forwarding entries
        A.add_forwarding_entry(address=B.get_address('C'),link=A.links[0])
        A.add_forwarding_entry(address=C.get_address('A'),link=A.links[0])
        A.add_forwarding_entry(address=D.get_address('C'),link=A.links[0])

        # B forwarding entries
        B.add_forwarding_entry(address=A.get_address('C'),link=B.links[0])
        B.add_forwarding_entry(address=C.get_address('B'),link=B.links[0])
        B.add_forwarding_entry(address=D.get_address('C'),link=B.links[0])

        # C forwarding entries
        C.add_forwarding_entry(address=A.get_address('C'),link=C.links[0])
        C.add_forwarding_entry(address=B.get_address('C'),link=C.links[1])
        C.add_forwarding_entry(address=D.get_address('C'),link=C.links[2])

        # D forwarding entries
        D.add_forwarding_entry(address=A.get_address('C'),link=D.links[0])
        D.add_forwarding_entry(address=B.get_address('C'),link=D.links[0])
        D.add_forwarding_entry(address=C.get_address('D'),link=D.links[0])

        # setup transport
        t1 = Transport(A)
        t2 = Transport(B)
        t4 = Transport(D)

        # setup connection
        c1 = TCP(t1,A.get_address('C'),1,D.get_address('C'),1,AppHandler(inputfile=self.inputfile,identifier="c1"),window=self.window,type=self.type,window_size_plot=True,sequence_plot=True)
        c2 = TCP(t4,D.get_address('C'),1,A.get_address('C'),1,AppHandler(inputfile=self.inputfile,plot=True,identifier="c2"),window=self.window,type=self.type,receiver_flow_plot=True)
        
        c3 = TCP(t2,B.get_address('C'),2,D.get_address('C'),2,AppHandler(inputfile=self.inputfile,identifier="c3"),window=self.window,type=self.type,window_size_plot=True,sequence_plot=True)
        c4 = TCP(t4,D.get_address('C'),2,B.get_address('C'),2,AppHandler(inputfile=self.inputfile,plot=True,identifier="c4"),window=self.window,type=self.type,receiver_flow_plot=True)

        global tcps
        tcps = [c1, c2, c3, c4]

        global original_size
        f = open(self.inputfile, "rb")
        try:
            data = f.read(1000)
            while data != "":
                original_size += len(data)
                Sim.scheduler.add(delay=0, event=data, handler=c1.send)
                Sim.scheduler.add(delay=0, event=data, handler=c3.send)
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
