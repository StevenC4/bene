from src.sim import Sim
from src import packet
from src import node

class DVRoutingApp(object):
    def __init__(self,node,delay=5):
        self.node = node
        self.distance_vector = {node.hostname: 0}
        self.dv_packet_ident = 0
        self.delay = delay
        Sim.scheduler.add(delay=0, event=None, handler=self.broadcast_dv_packet)

    def broadcast_dv_packet(self,event):
    	p = packet.Packet(source_address=0,destination_address=0,ident=self.dv_packet_ident,ttl=1,protocol='dvrouting',body=self.distance_vector)
    	self.node.send_packet(p)
        self.dv_packet_ident += 1
        if self.dv_packet_ident < 10:
			Sim.scheduler.add(delay=self.delay, event=None, handler=self.broadcast_dv_packet)        

    def receive_packet(self,packet):
        print Sim.scheduler.current_time(),self.node.hostname,packet.ident
        new_distance_vector = packet.body
        for node_name in new_distance_vector:
        	distance = int(new_distance_vector[node_name])
        	if (node_name not in self.distance_vector) or (distance + 1) < self.distance_vector[node_name]:
        		self.distance_vector[node_name] = distance + 1
        		# Update routing table
        		address = None
        		link = None
    			self.node.remove_forwarding_entry(address)
        		self.node.add_forwarding_entry(address,link)
        print self.distance_vector
        #print new_distance_vector
        print ""