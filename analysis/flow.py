import os
import pyshark
import pandas
import pprint

from features import ForwardFeatures, BackwardFeatures, GlobalFeatures
from constants import CLASSES

LOCAL_IP = '10.42.0.71'


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
            'ttl': int(packet.ip.ttl if 'ip' in dir(packet) else 0),
            'direction': ('forward' if packet.ip.src == LOCAL_IP
                         else 'backward') if 'ip' in dir(packet) else 'forward'
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
        class_parts = filename.split('-')[0].split('_')
        if class_parts[-1] in ('delivered', 'undelivered'):
            class_parts = class_parts[:-1]

        class_name = '_'.join(class_parts)
        class_value = CLASSES.get(class_name)
        if class_value is None:
            print("Unable to determine class value for: {}".format(class_name))

        return class_value

    def get_sni(self):
        sni_packet = pyshark.FileCapture(path,
            display_filter='ssl.handshake.extensions_server_name')[0]
        return sni_packet.ssl.handshake_extensions_server_name
