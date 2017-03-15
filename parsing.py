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

    @staticmethod
    def compute_time_shifts(data):
        data['timeshift'] = data['timestamp'] - data['timestamp'].shift(1)
        return data

    @property
    def forward_packets(self):
        data = self.data[self.data['direction'] == 'forward'].copy()
        return self.compute_time_shifts(data)

    @property
    def backward_packets(self):
        data = self.data[self.data['direction'] == 'backward'].copy()
        return self.compute_time_shifts(data)

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

    def feature_f_size_min(self):
        """
        Returns the size of the smallest forward packet.
        """
        return self.forward_packets['size'].min()

    def feature_f_size_max(self):
        """
        Returns the size of the biggest forward packet.
        """
        return self.forward_packets['size'].max()

    def feature_f_size_mean(self):
        """
        Returns the mean size of the forward packets.
        """
        return self.forward_packets['size'].mean()

    def feature_f_size_std(self):
        """
        Returns the mean size of the forward packets.
        """
        return self.forward_packets['size'].std()

    def feature_f_time_min(self):
        """
        Returns the smallest inter time difference among forward packets.
        """
        return self.forward_packets['timeshift'].min()

    def feature_f_time_max(self):
        """
        Returns the biggest inter time difference among forward packets.
        """
        return self.forward_packets['timeshift'].max()

    def feature_f_time_mean(self):
        """
        Returns the mean inter time difference among forward packets.
        """
        return self.forward_packets['timeshift'].mean()

    def feature_f_time_std(self):
        """
        Returns the std of inter time difference among forward packets.
        """
        return self.forward_packets['timeshift'].std()

    def feature_b_num(self):
        """
        Returns the number of backward packets.
        """
        return len(self.backward_packets)

    def feature_b_size_sum(self):
        """
        Returns the total size of all backward packets.
        """
        return self.backward_packets['size'].sum()

    def feature_b_size_min(self):
        """
        Returns the size of the smallest backward packet.
        """
        return self.backward_packets['size'].min()

    def feature_b_size_max(self):
        """
        Returns the size of the biggest backward packet.
        """
        return self.backward_packets['size'].max()

    def feature_b_size_mean(self):
        """
        Returns the mean size of the backward packets.
        """
        return self.backward_packets['size'].mean()

    def feature_b_size_std(self):
        """
        Returns the mean size of the backward packets.
        """
        return self.backward_packets['size'].std()

    def feature_b_time_min(self):
        """
        Returns the smallest inter time difference among backward packets.
        """
        return self.backward_packets['timeshift'].min()

    def feature_b_time_max(self):
        """
        Returns the biggest inter time difference among backward packets.
        """
        return self.backward_packets['timeshift'].max()

    def feature_b_time_mean(self):
        """
        Returns the mean inter time difference among backward packets.
        """
        return self.backward_packets['timeshift'].mean()

    def feature_b_time_std(self):
        """
        Returns the std of inter time difference among backward packets.
        """
        return self.backward_packets['timeshift'].std()


f = Flow(filename)
print(f.generate_features())
