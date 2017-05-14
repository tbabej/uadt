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

    @staticmethod
    def parameter_tcp_window_size(packet):
        """
        Returns the window size of the TCP packet.
        """
        return int(packet.tcp.window_size)

    @staticmethod
    def parameter_tcp_window_scalefactor(packet):
        """
        Returns the window size scalefactor of the TCP packet.
        """
        return int(packet.tcp.window_size_scalefactor)

    def feature_tcp_window_size_min(self):
        return self.data['tcp_window_size'].min()

    def feature_tcp_window_size_max(self):
        return self.data['tcp_window_size'].max()

    def feature_tcp_window_size_mean(self):
        return self.data['tcp_window_size'].mean()

    def feature_tcp_window_size_std(self):
        return self.data['tcp_window_size'].std()

    def feature_tcp_window_scalefactor_min(self):
        return self.data['tcp_window_scalefactor'].min()

    def feature_tcp_window_scalefactor_max(self):
        return self.data['tcp_window_scalefactor'].max()

    def feature_tcp_window_scalefactor_mean(self):
        return self.data['tcp_window_scalefactor'].mean()

    def feature_tcp_window_scalefactor_std(self):
        return self.data['tcp_window_scalefactor'].std()


class SSLFeatures(object):
    """
    Provides implementation of features related to TCP metadata.
    """

    @staticmethod
    def parameter_ssl_session_id_length(packet):
        return int(packet.ssl.handshake_session_id_length)

    @staticmethod
    def parameter_ssl_compression_methods_length(packet):
        return int(packet.ssl.handshake_comp_methods_length)

    @staticmethod
    def parameter_ssl_extensions_length(packet):
        return int(packet.ssl.handshake_extensions_length)

    def feature_ssl_session_id_length_min(self):
        return self.data['ssl_session_id_length'].min()

    def feature_ssl_session_id_length_max(self):
        return self.data['ssl_session_id_length'].max()

    def feature_ssl_session_id_length_mean(self):
        return self.data['ssl_session_id_length'].mean()

    def feature_ssl_session_id_length_std(self):
        return self.data['ssl_session_id_length'].std()

    def feature_ssl_compression_methods_length_min(self):
        return self.data['ssl_compression_methods_length'].min()

    def feature_ssl_compression_methods_length_max(self):
        return self.data['ssl_compression_methods_length'].max()

    def feature_ssl_compression_methods_length_mean(self):
        return self.data['ssl_compression_methods_length'].mean()

    def feature_ssl_compression_methods_length_std(self):
        return self.data['ssl_compression_methods_length'].std()

    def feature_ssl_extensions_length_min(self):
        return self.data['ssl_extensions_length'].min()

    def feature_ssl_extensions_length_max(self):
        return self.data['ssl_extensions_length'].max()

    def feature_ssl_extensions_length_mean(self):
        return self.data['ssl_extensions_length'].mean()

    def feature_ssl_extensions_length_std(self):
        return self.data['ssl_extensions_length'].std()

    def feature_ssl_num_handshakes(self):
        counts = self.data['ssl_session_id_length'].notnull().value_counts()
        return counts[True]


class DNSFeatures(object):
    """
    Provides implementation of features related to DNS metadata.
    """

    @staticmethod
    def parameter_dns_request_type(packet):
        """
        Returns the type of the TCP packet.
        """
        return int(packet.dns.qry_type)

    def feature_num_dns_A_requests(self):
        return (self.data['dns_request_type'] == 1).value_counts()[True]

    def feature_num_dns_requests(self):
        return self.data['dns_request_type'].notnull().value_counts()[True]
