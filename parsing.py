import pyshark
import pandas

filename = 'data/L_cyber_ff_09-17__11_37_53.pcap.TCP_10-0-0-9_59515_212-179-180-110_443.pcap'


class Flow(object):
    """
    Represents one captured session flow, which should be classified.
    Generates necessary features that will be used as inputs during classification.
    """

    def __init__(self, path):
        self.path = path

        # Parse out pcap file using pyshark
        self.packets = list(pyshark.FileCapture(path))

        # Extract basic data from the flow
        self.generate_data()

    @staticmethod
    def parse_packet(packet):
        packet_data = {
            'size': int(packet.captured_length),
            'timestamp': float(packet.sniff_timestamp),
            'ttl': int(packet.ip.ttl),
            'direction': 'forward' if packet.tcp.dstport == '443'
                         else 'backward'
        }
        return packet_data

    def generate_data(self):
        packet_data = [self.parse_packet(p) for p in self.packets]
        self.data = pandas.DataFrame(packet_data)
