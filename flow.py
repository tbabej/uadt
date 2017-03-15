import os
import pyshark
import pandas
import pprint

from features import ForwardFeatures, BackwardFeatures, GlobalFeatures
from constants import CLASSES


class Flow(ForwardFeatures, BackwardFeatures, GlobalFeatures):
    """
    Represents one captured session flow, which should be classified.
    Generates necessary features that will be used as inputs during classification.
    """

    def __init__(self, path):
        self.path = path

        # Parse out pcap file using pyshark
        self.packets = list(pyshark.FileCapture(path))

        # Extract basic data from the flow
        packet_data = [self.parse_packet(p) for p in self.packets]
        self.data = pandas.DataFrame(packet_data)

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

    @staticmethod
    def compute_time_shifts(data):
        data['timeshift'] = data['timestamp'] - data['timestamp'].shift(1)
        return data

    @property
    def features(self):
        # Dynamically find all features
        feature_method_names = [k for k in dir(self)
                                if k.startswith('feature_')]

        # Generate a data dict with results of feature methods
        feature_data = {}
        for method_name in feature_method_names:
            method = getattr(self, method_name)
            key = method_name.split('feature_')[1]
            feature_data[key] = method()

        return feature_data

    def feature_class(self):
        """
        Detect the class of the pcap file from the naming conventions. Detects
        application using SNI extension in the SSL handshake.
        """

        # Get OS and browser from the filename
        filename = os.path.basename(self.path)
        parts = filename.split('_')
        pcap_os = parts[0]
        browser = parts[2]
        return CLASSES.get((pcap_os, browser))

    def get_sni(self):
        sni_packet = pyshark.FileCapture(path,
            display_filter='ssl.handshake.extensions_server_name')[0]
        return sni_packet.ssl.handshake_extensions_server_name
