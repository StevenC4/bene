import optparse
import sys

import matplotlib
from pylab import *

# Parses a file of rates and plot a sequence number graph. Black
# squares indicate a sequence number being sent and dots indicate a
# sequence number being ACKed.
class Plotter:
    def __init__(self,filename):
        """ Initialize plotter with a file name. """
        self.transmitted_data = []
        self.dropped_data = []
        self.acked_data = []
        self.multi_sequence_diagram_ids = []
        self.multi_transmitted_data = {}
        self.multi_dropped_data = {}
        self.multi_acked_data = {}
        self.receiver_rate = []
        self.multi_receiver_rate = {}
        self.queue_size = []
        self.queue_dropped = []
        self.window_size = []
        self.multi_window_size = {}
        self.min_time = {}
        self.max_time = {}
        self.filename = filename

    def add_data(self,t,data,event,identifier=None):
        t = float(t)
        sequence = int(data)

        min_max_key = event

        if  event == 'Transmitted':
            if identifier is None:
                self.transmitted_data.append((t,sequence))
                min_max_key = 'Sequence'
            else:
                if identifier not in self.multi_transmitted_data.keys():
                    self.multi_transmitted_data[identifier] = []
                self.multi_transmitted_data[identifier].append((t,data))
                if identifier not in self.multi_sequence_diagram_ids:
                    self.multi_sequence_diagram_ids.append(identifier)
                min_max_key = 'Sequence' + identifier 
        if  event == 'Dropped':
            if identifier is None:
                self.dropped_data.append((t,sequence))
                min_max_key = 'Sequence'
            else:
                if identifier not in self.multi_dropped_data.keys():
                    self.multi_dropped_data[identifier] = []
                self.multi_dropped_data[identifier].append((t,data))
                if identifier not in self.multi_sequence_diagram_ids:
                    self.multi_sequence_diagram_ids.append(identifier)
                min_max_key = 'Sequence' + identifier
        if  event == 'Acked':
            if identifier is None:
                self.acked_data.append((t,sequence))
                min_max_key = 'Sequence'
            else:
                if identifier not in self.multi_acked_data.keys():
                    self.multi_acked_data[identifier] = []
                self.multi_acked_data[identifier].append((t,data))
                if identifier not in self.multi_sequence_diagram_ids:
                    self.multi_sequence_diagram_ids.append(identifier)
                min_max_key = 'Sequence' + identifier
        if  event == 'ReceiverRate':
            if identifier is None:
                self.receiver_rate.append((t,data))
            else:
                if identifier not in self.multi_receiver_rate.keys():
                    self.multi_receiver_rate[identifier] = []
                self.multi_receiver_rate[identifier].append((t,data))
        if  event == 'QueueSize':
            self.queue_size.append((t,data))
            min_max_key = 'Queue'
        if event == 'QueueDrop':
            self.queue_dropped.append((t,data))
            min_max_key = 'Queue'
        if  event == 'WindowSize':
            if identifier is None:
                self.window_size.append((t,data))
            else:
                if identifier not in self.multi_receiver_rate.keys():
                    self.multi_window_size[identifier] = []
                self.multi_window_size[identifier].append((t,data))

        self.set_min_max_times(t,min_max_key)

    def set_min_max_times(self,t,event):
        if not event in self.min_time.keys() or t < self.min_time[event]:
            self.min_time[event] = t
        if not event in self.max_time.keys() or t > self.max_time[event]:
            self.max_time[event] = t


    def plot(self,filename):
        """ Create a sequence graph of the packets. """
        clf()
        figure(figsize=(15,10))

        if len(self.transmitted_data) != 0 and len(self.dropped_data) != 0 and len(self.acked_data) != 0:
            self.plotSequenceDiagram()
        if len(self.multi_sequence_diagram_ids) != 0:
            self.plotMultiSequenceDiagram()
        if len(self.receiver_rate) != 0:
            self.plotReceiverRate()
        if len(self.multi_receiver_rate.keys()) != 0:
            self.plotMultiReceiverRate()
        if len(self.queue_size) != 0 and len(self.queue_dropped) != 0:
            self.plotQueueSize()
        if len(self.window_size) != 0:
            self.plotWindowSize()
        if len(self.multi_window_size.keys()) != 0:
            self.plotMultiWindowSize()

    def plotSequenceDiagram(self):
        transmitted_x = []
        transmitted_y = []

        dropped_x = []
        dropped_y = []
        
        acked_x = []
        acked_y = []

        for (t,sequence) in self.transmitted_data:
            transmitted_x.append(t)
            transmitted_y.append((sequence / 1000) % 50)
            #transmitted_y.append(sequence)

        for (t,sequence) in self.dropped_data:
            dropped_x.append(t)
            dropped_y.append((sequence / 1000) % 50)
            #dropped_y.append(sequence)

        for (t,sequence) in self.acked_data:
            acked_x.append(t)
            acked_y.append((sequence / 1000) % 50)
            #acked_y.append(sequence)

        #scatter(transmitted_x,transmitted_y,marker='.',s=1,c="black")
        scatter(transmitted_x,transmitted_y,marker='s',s=15,c="black")
        scatter(dropped_x,dropped_y,marker='x',s=100,c="red")
        scatter(acked_x,acked_y,marker='o',s=15,c="blue")
        xlabel('Time (seconds)')
        ylabel('Sequence Number / 1000 % 50')
        xlim([self.min_time['Sequence'],self.max_time['Sequence']])
        savefig(self.filename + '-sequence-plot.png')
        clf()

    def plotMultiSequenceDiagram(self):
        for identifier in self.multi_sequence_diagram_ids:
            transmitted_x = []
            transmitted_y = []

            dropped_x = []
            dropped_y = []
        
            acked_x = []
            acked_y = []

            if identifier in self.multi_transmitted_data.keys():
                transmitted_list = self.multi_transmitted_data[identifier]
                for (t,sequence) in transmitted_list:
                    transmitted_x.append(t)
                    transmitted_y.append((sequence / 1000) % 50)
                scatter(transmitted_x,transmitted_y,marker='s',s=15,c="black")        

            if identifier in self.multi_dropped_data.keys():
                dropped_list = self.multi_dropped_data[identifier]
                for (t,sequence) in dropped_list:
                    dropped_x.append(t)
                    dropped_y.append((sequence / 1000) % 50)
                scatter(dropped_x,dropped_y,marker='x',s=100,c="red")

            if identifier in self.multi_acked_data.keys():
                acked_list = self.multi_acked_data[identifier]
                for (t,sequence) in acked_list:
                    acked_x.append(t)
                    acked_y.append((sequence / 1000) % 50)
                scatter(acked_x,acked_y,marker='o',s=15,c="blue")

            xlabel('Time (seconds)')
            ylabel('Sequence Number / 1000 % 50')
            min_max_key = 'Sequence' + identifier
            xlim([self.min_time[min_max_key],self.max_time[min_max_key]])
            savefig(self.filename + '-' + identifier + '-sequence-plot.png')
            clf()

    def plotReceiverRate(self):
        receiver_rate_x = []
        receiver_rate_y = []

        for (t,data) in self.receiver_rate:
            receiver_rate_x.append(t)
            receiver_rate_y.append(data)

        plot(receiver_rate_x,receiver_rate_y)
        xlabel('Time (seconds)')
        ylabel('Receiver Rate')
        xlim([self.min_time['ReceiverRate'],self.max_time['ReceiverRate']])
        savefig(self.filename + '-receiver-rate.png')
        clf()

    def plotMultiReceiverRate(self):
        multi_receiver_rate_x = []
        multi_receiver_rate_y = []

        for identifier in self.multi_receiver_rate.keys():
            data_list = self.multi_receiver_rate[identifier]
            multi_receiver_rate_x = []
            multi_receiver_rate_y = []
            for (t,data) in data_list:
                multi_receiver_rate_x.append(t)
                multi_receiver_rate_y.append(data)
            plot(multi_receiver_rate_x,multi_receiver_rate_y)
            
        xlabel('Time (seconds)')
        ylabel('Receiver Rate')
        xlim([self.min_time['ReceiverRate'],self.max_time['ReceiverRate']])
        savefig(self.filename + '-multi-receiver-rate.png')
        clf()    

    def plotQueueSize(self):
        queue_size_x = []
        queue_size_y = []

        queue_dropped_x = []
        queue_dropped_y = []

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
        savefig(self.filename + '-queue-size.png')
        clf()

    def plotWindowSize(self):
        window_size_x = []
        window_size_y = []

        for (t,data) in self.window_size:
            window_size_x.append(t)
            window_size_y.append(data)

        plot(window_size_x,window_size_y)
        xlabel('Time (seconds)')
        ylabel('Window Size')
        xlim([self.min_time['WindowSize'],self.max_time['WindowSize']])
        savefig(self.filename + '-window-size.png')
        clf()

    def plotMultiWindowSize(self):
        for identifier in self.multi_window_size.keys():
            data_list = self.multi_window_size[identifier]
            multi_window_size_x = []
            multi_window_size_y = []
            for (t,data) in data_list:
                multi_window_size_x.append(t)
                multi_window_size_y.append(data)
            plot(multi_window_size_x,multi_window_size_y)
            xlabel('Time (seconds)')
            ylabel('Window Size')
            xlim([self.min_time['WindowSize'],self.max_time['WindowSize']])
            savefig(self.filename + '-' + identifier + '-window_size.png')
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