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

    @property
    def forward_packets(self):
        return self.data[self.data['direction'] == 'forward']

    @property
    def backward_packets(self):
        return self.data[self.data['direction'] == 'backward']

    def feature_f_num(self):
        """
        Returns the number of forward packets.
        """
        return len(self.forward_packets)

    def feature_f_size_sum(self):
        """
        Returns the total size of all forward packets.
        """
        return self.forward_packets['size'].sum()

    def generate_features(self):
        # Dynamically find all features
        feature_method_names = [k for k in self.__class__.__dict__.keys()
                                if k.startswith('feature_')]

        # Generate a data dict with results of feature methods
        feature_data = {}
        for method_name in feature_method_names:
            method = getattr(self, method_name)
            key = method_name.split('feature_')[1]
            feature_data[key] = method()

        return feature_data

f = Flow(filename)
print(f.generate_features())
