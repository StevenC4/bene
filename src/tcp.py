import sys
sys.path.append('..')

from src.sim import Sim
from src.connection import Connection
from src.tcppacket import TCPPacket
from src.buffer import SendBuffer,ReceiveBuffer

default_mss = 1000

class TCP(Connection):
    ''' A TCP connection between two hosts.'''
    def __init__(self,transport,source_address,source_port,
                 destination_address,destination_port,app=None,window=1000,dynamic_rto=True):
        Connection.__init__(self,transport,source_address,source_port,
                            destination_address,destination_port,app)

        ### Sender functionality

        # send window; represents the total number of bytes that may
        # be outstanding at one time
        self.window = default_mss
        # send buffer
        self.send_buffer = SendBuffer()
        # maximum segment size, in bytes
        self.mss = default_mss
        # largest sequence number that has been ACKed so far; represents
        # the next sequence number the client expects to receive
        self.sequence = 0
        # retransmission timer
        self.timer = None
        # timeout duration in seconds
        self.timeout = 1

        # constants
        self.k = 4
        self.g = .1
        self.alpha = 1/8
        self.beta = 1/4

        self.dynamic_rto = dynamic_rto
        self.rto = 3
        self.srtt = None
        self.rttvar = None

        ### Receiver functionality

        # receive buffer
        self.receive_buffer = ReceiveBuffer()
        # ack number to send; represents the largest in-order sequence
        # number not yet received
        self.ack = 0

        self.threshold = 100000

    def trace(self,message):
        ''' Print debugging messages. '''
        Sim.trace("TCP",message)

    def receive_packet(self,packet):
        ''' Receive a packet from the network layer. '''
        if packet.ack_number > 0:
            # handle ACK
            self.handle_ack(packet)
        if packet.length > 0:
            # handle data
            self.handle_data(packet)

    ''' Sender '''

    def send(self,data):
        ''' Send data on the connection. Called by the application. This
            code currently sends all data immediately. '''
        self.send_buffer.put(data)
        self.send_packets_if_possible()

    def send_packets_if_possible(self):
        # if self.send_buffer.outstanding() < self.window:
        while self.send_buffer.outstanding() < self.window and self.send_buffer.available():
            data_length = min(self.window - self.send_buffer.outstanding(), self.mss)
            data_tuple = self.send_buffer.get(data_length)
            data = data_tuple[0]
            self.sequence = data_tuple[1]
            self.send_packet(data,self.sequence)

    def send_packet(self,data,sequence):
        packet = TCPPacket(source_address=self.source_address,
                           source_port=self.source_port,
                           destination_address=self.destination_address,
                           destination_port=self.destination_port,
                           body=data,
                           sequence=sequence,ack_number=self.ack)
        packet.created = Sim.scheduler.current_time()

        # send the packet
        self.trace("%s (%d) sending TCP segment to %d for %d" % (self.node.hostname,self.source_address,self.destination_address,packet.sequence))
        self.transport.send_packet(packet)

        # set a timer
        if not self.timer:
            self.timer = Sim.scheduler.add(delay=self.rto, event='retransmit', handler=self.retransmit)

    def handle_ack(self,packet):
        ''' Handle an incoming ACK. '''

        r = Sim.scheduler.current_time() - packet.created
        if not self.srtt and not self.rttvar:
            self.srtt = r
            self.rttvar = r / 2
        else:
            self.rttvar = (1 - self.beta) * self.rttvar + (self.beta * abs(self.srtt - r))
            self.srtt = (1 - self.alpha) * self.srtt + (self.alpha * r)
        self.rto = self.srtt + max(self.g, self.k * self.rttvar)

        print "Seqeunce Num: [%d] ACKed: [%d]" % (self.sequence, packet.ack_number)

        self.trace("%s (%d) receiving TCP ACK from %d for %d" % (self.node.hostname,self.source_address,self.destination_address,packet.ack_number))

        self.cancel_timer()

        # somehow increment the cwnd here

        self.send_buffer.slide(packet.ack_number)
        self.send_packets_if_possible()

        if self.send_buffer.outstanding() and not self.timer:
            self.timer = Sim.scheduler.add(delay=self.rto, event='retransmit', handler=self.retransmit)

    def retransmit(self,event):
        ''' Retransmit data. '''
        self.timer = None
        self.trace("%s (%d) retransmission timer fired" % (self.node.hostname,self.source_address))
        data_tuple = self.send_buffer.resend(self.mss)
        data = data_tuple[0]
        if data:
            self.sequence = data_tuple[1]
            if self.dynamic_rto:
                self.timer = Sim.scheduler.add(delay=self.rto, event='retransmit', handler=self.retransmit)
            else:
                self.timer = Sim.scheduler.add(delay=self.rto, event='retransmit', handler=self.retransmit)
            self.send_packet(data, self.sequence)

    def cancel_timer(self):
        ''' Cancel the timer. '''
        if not self.timer:
            return
        Sim.scheduler.cancel(self.timer)
        self.timer = None

    ''' Receiver '''

    def handle_data(self,packet):
        ''' Handle incoming data. This code currently gives all data to
            the application, regardless of whether it is in order, and sends
            an ACK.'''
        self.trace("%s (%d) received TCP segment from %d for %d" % (self.node.hostname,packet.destination_address,packet.source_address,packet.sequence))
        self.receive_buffer.put(packet.body, packet.sequence)

        data_tuple = self.receive_buffer.get()
        data = data_tuple[0]
        sequence = data_tuple[1]
        if data:
            self.app.receive_data(data)
            self.ack = sequence + len(data)

        self.send_ack(packet.created)

    def send_ack(self, created):
        ''' Send an ack. '''
        packet = TCPPacket(source_address=self.source_address,
                           source_port=self.source_port,
                           destination_address=self.destination_address,
                           destination_port=self.destination_port,
                           sequence=self.sequence,ack_number=self.ack)
        packet.created = created
        # send the packet
        self.trace("%s (%d) sending TCP ACK to %d for %d" % (self.node.hostname,self.source_address,self.destination_address,packet.ack_number))
        self.transport.send_packet(packet)