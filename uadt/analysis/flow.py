import os
import pyshark
import pandas
import pprint

from cached_property import cached_property

from uadt.analysis.features import ForwardFeatures, BackwardFeatures, GlobalFeatures
from uadt import constants
from uadt import config


class Flow(ForwardFeatures, BackwardFeatures, GlobalFeatures):
    """
    Represents one captured session flow, which should be classified.
    Generates necessary features that will be used as inputs during classification.
    """

    def __init__(self, packets, path=None):
        self.path = path

        # Dynamically find all parameters
        self.parameter_methods = [
            ('_'.join(k.split('_')[1:]), getattr(self, k))
            for k in dir(self)
            if k.startswith('parameter_')
        ]

        # Extract basic data from the flow
        packet_data = [self.parse_packet(p) for p in packets]
        self.data = pandas.DataFrame(packet_data)

    @classmethod
    def from_path(cls, path):
        # Parse out pcap file using pyshark
        packets = list(pyshark.FileCapture(path))
        return cls(packets, path=path)

    def parse_packet(self, packet):
        """
        Compute the parameters vector by applying each parameter method
        on the given packet. This parameter vector is then expanded to
        a feature vector by computing various statistics of parameters.
        """

        return {
            key: method(packet)
            for key, method in self.parameter_methods
        }

    @cached_property
    def forward_packets(self):
        data = self.data[self.data['direction'] == 'forward'].copy()
        return self.compute_time_shifts(data)

    @cached_property
    def backward_packets(self):
        data = self.data[self.data['direction'] == 'backward'].copy()
        return self.compute_time_shifts(data)

    @staticmethod
    def parameter_direction(packet):
        """
        Returns the direction of the packet.
        """
        try:
            if any([packet.ip.src.startswith(subnet)
                    for subnet in config.LOCAL_SUBNETS]):
                return 'forward'
        except AttributeError:
            pass

        return 'backward'

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

        if not self.path:
            return

        # Get OS and browser from the filename
        filename = os.path.basename(self.path)
        class_parts = filename.split('-')[0].split('_')
        if class_parts[-1] in ('delivered', 'undelivered'):
            class_parts = class_parts[:-1]

        class_name = '_'.join(class_parts)
        class_value = constants.CLASSES.get(class_name)
        if class_value is None:
            print("Unable to determine class value for: {}".format(class_name))

        return class_value

    def get_sni(self):
        sni_packet = pyshark.FileCapture(path,
            display_filter='ssl.handshake.extensions_server_name')[0]
        return sni_packet.ssl.handshake_extensions_server_name
