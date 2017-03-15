class ForwardFeatures(object):
    """
    Provides implementation of features for forward packets.
    """

    @property
    def forward_packets(self):
        data = self.data[self.data['direction'] == 'forward'].copy()
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


class BackwardFeatures(object):
    """
    Provides implementation of features for backward packets.
    """

    @property
    def backward_packets(self):
        data = self.data[self.data['direction'] == 'backward'].copy()
        return self.compute_time_shifts(data)


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
