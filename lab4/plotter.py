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
        self.receiver_rate = []
        self.queue_size = []
        self.queue_dropped = []
        self.window_size = []
        self.min_time = None
        self.max_time = None

    def add_data(self,t,data,event):
        t = float(t)
        sequence = int(data)

        if  event == 'ReceiverRate':
            self.receiver_rate.append((t,data))
        if  event == 'QueueSize':
            self.queue_size.append((t,data))
        if event == 'QueueDrop'
            self.queue_dropped.append((t,data))
        if  event == 'WindowSize':
            self.window_size.append((t,data))

        if not self.min_time or t < self.min_time:
            self.min_time = t
        if not self.max_time or t > self.max_time:
            self.max_time = t

    def plot(self,filename):
        """ Create a sequence graph of the packets. """
        clf()
        figure(figsize=(15,10))
        
        receiver_rate_x = []
        receiver_rate_y = []

        queue_size_x = []
        queue_size_y = []
        
        queue_dropped_x = []
        queue_dropped_y = []

        window_size_x = []
        window_size_y = []

        for (t,data) in self.receiver_rate:
            receiver_rate_x.append(t)
            receiver_rate_y.append(data)

        line(receiver_rate_x,receiver_rate_y)
        xlabel('Time (seconds)')
        ylabel('Receiver Rate')
        xlim([self.min_time,self.max_time])
        savefig('receiver-rate-' + filename)

        for (t,data) in self.queue_size:
            queue_size_x.append(t)
            queue_size_y.append(data)

        for (t,data) in self.queue_dropped:
            queue_dropped_x.append(t)
            queue_dropped_y.append(data)

        line(queue_size_x,queue_size_y)
        scatter(queue_dropped_x,queue_dropped_y,marker='x',s=100,c="red")
        xlabel('Time (seconds)')
        ylabel('Queue Size')
        xlim([self.min_time,self.max_time])
        savefig('queue-size-' + filename)

        for (t,data) in self.window_size:
            window_size_x.append(t)
            window_size_y.append(data)

        line(window_size_x,window_size_y)
        xlabel('Time (seconds)')
        ylabel('Window Size')
        xlim([self.min_time,self.max_time])
        savefig('window-size-' + filename)

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