from uadt import config

class SizeFeatures(object):
    """
    Provides implementation of size-related features.
    """

    @staticmethod
    def parameter_size(packet):
        """
        Returns the size of the packet.
        """
        return int(packet.captured_length)

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

    def feature_t_num(self):
        """
        Returns the number of packets.
        """
        return len(self.data)

    def feature_t_size_min(self):
        """
        Returns the size of the smallest packet.
        """
        return self.data['size'].min()

    def feature_t_size_max(self):
        """
        Returns the size of the biggest packet.
        """
        return self.data['size'].max()

    def feature_t_size_mean(self):
        """
        Returns the mean of size of all the packets.
        """
        return self.data['size'].mean()

    def feature_t_size_var(self):
        """
        Returns the variance of size of all the packets.
        """
        return self.data['size'].var()


class TimeGapFeatures(object):
    """
    Provides implementation of features for backward packets.
    """

    @staticmethod
    def parameter_timestamp(packet):
        """
        Returns the time when the packet was captured.
        """
        return float(packet.sniff_timestamp)

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


class IPFeatures(object):
    """
    Provides implementation of features derived from various IP header values.
    """

    @staticmethod
    def parameter_ttl(packet):
        """
        Returns the time-to-live value of the packet.
        """

        return int(packet.ip.ttl)

    def feature_f_ttl_mean(self):
        """
        Returns the mean of TTL values in forward packets.
        """
        return self.forward_packets['ttl'].mean()

class TCPFeatures(object):
    """
    Provides implementation of features related to TCP metadata.
    """

    def feature_tcp_window_size(self):
        first_packet = self.packets[0]
        return int(first_packet.tcp.window_size)

    def feature_tcp_window_scale(self):
        first_packet = self.packets[0]
        return int(first_packet.tcp.window_size)
