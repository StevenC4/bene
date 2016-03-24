import optparse
import sys

import matplotlib
from pylab import *

# Parses a file of rates and plot a sequence number graph. Black
# squares indicate a sequence number being sent and dots indicate a
# sequence number being ACKed.
class Plotter:
    def __init__(self):
        """ Initialize plotter with a file name. """
        self.transmitted_data = []
        self.dropped_data = []
        self.acked_data = []
        self.min_time = None
        self.max_time = None

    def add_data(self,t,sequence,event):
        t = float(t)
        sequence = int(sequence)

        if  event == 'Transmitted':
            self.transmitted_data.append((t,sequence))
        if  event == 'Dropped':
            self.dropped_data.append((t,sequence))
        if  event == 'Acked':
            self.acked_data.append((t,sequence))

        if not self.min_time or t < self.min_time:
            self.min_time = t
        if not self.max_time or t > self.max_time:
            self.max_time = t

    def plot(self,filename):
        """ Create a sequence graph of the packets. """
        clf()
        figure(figsize=(15,10))
        
        transmitted_x = []
        transmitted_y = []

        dropped_x = []
        dropped_y = []
        
        acked_x = []
        acked_y = []

        for (t,sequence) in self.transmitted_data:
            transmitted_x.append(t)
            #transmitted_y.append((sequence / 1000) % 50)
            transmitted_y.append(sequence)

        for (t,sequence) in self.dropped_data:
            dropped_x.append(t)
            #dropped_y.append((sequence / 1000) % 50)
            dropped_y.append(sequence)

        for (t,sequence) in self.acked_data:
            acked_x.append(t)
            #acked_y.append((sequence / 1000) % 50)
            acked_y.append(sequence)

        #scatter(transmitted_x,transmitted_y,marker='.',s=1,c="black")
        scatter(transmitted_x,transmitted_y,marker='s',s=15,c="black")
        scatter(dropped_x,dropped_y,marker='x',s=100,c="red")
        scatter(acked_x,acked_y,marker='o',s=15,c="blue")
        xlabel('Time (seconds)')
        ylabel('Sequence Number / 1000 % 50')
        xlim([self.min_time,self.max_time])
        savefig(filename)

def parse_options():
        # parse options
        parser = optparse.OptionParser(usage = "%prog [options]",
                                       version = "%prog 0.1")

        (options,args) = parser.parse_args()
        return (options,args)


if __name__ == '__main__':
    (options,args) = parse_options()
    if options.file == None:
        print "plot.py -f file"
        sys.exit()
    p = Plotter(options.file)
    p.parse()
    p.plot()