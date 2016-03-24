from src.sim import Sim

import random

class Link(object):
    def __init__(self,address=0,startpoint=None,endpoint=None,queue_size=None,
                 bandwidth=1000000.0,propagation=0.001,loss=0,plotter=None):
        self.running = True
        self.address = address
        self.startpoint = startpoint
        self.endpoint = endpoint
        self.queue_size = queue_size
        self.bandwidth = bandwidth
        self.propagation = propagation
        self.loss = loss
        self.busy = False
        self.queue = []
        self.plotter = plotter

    def trace(self,message):
        Sim.trace("Link",message)

    ## Handling packets ##

    def send_packet(self,packet):
        # check if link is running
        if not self.running:
            return
        # drop packet if instructed to do so
        if packet.drop_packet:
            self.trace("%d packet dropped because I said so" % (self.address))
            return
        # drop packet due to queue overflow
        if self.queue_size and len(self.queue) == self.queue_size:
            self.plotter.add_data(Sim.scheduler.current_time(),self.queue_size + 1,'QueueDrop')
            self.trace("%d dropped packet due to queue overflow" % (self.address))
            return
        # drop packet due to random loss
        if self.loss > 0 and random.random() < self.loss:
            self.trace("%d dropped packet due to random loss" % (self.address))
            return
        packet.enter_queue = Sim.scheduler.current_time()
        self.plotter.add_data(Sim.scheduler.current_time(),self.queue_size,'QueueSize')
        if len(self.queue) == 0 and not self.busy:
            # packet can be sent immediately
            self.busy = True
            self.transmit(packet)
        else:
            # add packet to queue
            self.queue.append(packet)
        
    def transmit(self,packet):
        packet.queueing_delay += Sim.scheduler.current_time() - packet.enter_queue
        delay = (8.0*packet.length)/self.bandwidth
        packet.transmission_delay += delay
        packet.propagation_delay += self.propagation
        # schedule packet arrival at end of link
        Sim.scheduler.add(delay=delay+self.propagation,event=packet,handler=self.endpoint.receive_packet)
        # schedule next transmission
        Sim.scheduler.add(delay=delay,event='finish',handler=self.next)

    def next(self,event):
        if len(self.queue) > 0:
            packet = self.queue.pop(0)
            self.transmit(packet)
        else:
            self.busy = False

    def down(self,event):
        self.running = False

    def up(self,event):
        self.running = True
