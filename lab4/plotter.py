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
        self.min_time = {}
        self.max_time = {}

    def add_data(self,t,data,event):
        t = float(t)
        sequence = int(data)

        if  event == 'ReceiverRate':
            self.receiver_rate.append((t,data))
            self.set_min_max_times(t,event)
        if  event == 'QueueSize':
            self.queue_size.append((t,data))
            self.set_min_max_times(t,'Queue')
        if event == 'QueueDrop':
            self.queue_dropped.append((t,data))
            self.set_min_max_times(t,'Queue')
        if  event == 'WindowSize':
            self.window_size.append((t,data))
            self.set_min_max_times(t,event)

    def set_min_max_times(self,t,event):
        if not event in self.min_time.keys() or t < self.min_time[event]:
            self.min_time[event] = t
        if not event in self.max_time.keys() or t > self.max_time[event]:
            self.max_time[event] = t


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

        plot(receiver_rate_x,receiver_rate_y)
        xlabel('Time (seconds)')
        ylabel('Receiver Rate')
        xlim([self.min_time['ReceiverRate'],self.max_time['ReceiverRate']])
        savefig(filename + '-receiver-rate.png')
        clf()

        for (t,data) in self.queue_size:
            queue_size_x.append(t)
            queue_size_y.append(data)

        for (t,data) in self.queue_dropped:
            queue_dropped_x.append(t)
            queue_dropped_y.append(data)

        plot(queue_size_x,queue_size_y)
        scatter(queue_dropped_x,queue_dropped_y,marker='x',s=100,c="red")
        xlabel('Time (seconds)')
        ylabel('Queue Size')
        xlim([self.min_time['Queue'],self.max_time['Queue']])
        savefig(filename + '-queue-size.png')
        clf()

        for (t,data) in self.window_size:
            window_size_x.append(t)
            window_size_y.append(data)

        plot(window_size_x,window_size_y)
        xlabel('Time (seconds)')
        ylabel('Window Size')
        xlim([self.min_time['WindowSize'],self.max_time['WindowSize']])
        savefig(filename + '-window-size.png')
        clf()

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