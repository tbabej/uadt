#!/usr/bin/python3

"""
splitter - split a session PCAP file using different methods

Usage:
  splitter.py --method=<method> [--output-dir=<output_dir>] <file>...

Options:
  --method=<method>      Specify what method should be used to split the PCAP file.
  --output-dir=<value>   The directory where to create splitted PCAP file segments [default: data_split].

Examples:
$ ./splitter.py --method marks data/*.pcap
$ ./splitter.py --method auto --output-dir data_split data/*.pcap
"""

import abc
import os
import glob
import subprocess

import docopt
import pyshark

from joblib import Parallel, delayed

from plugins import PluginBase, PluginMount


class Splitter(PluginBase, metaclass=PluginMount):
    """
    An object that represents a mechanism for splitting a session PCAP file.
    """

    identifier = None

    def __init__(self):
        if not self.identifier:
            raise ValueError("Method idenfitier must be specified")

    @abc.abstractmethod
    def split(self, filename):
        """
        Splits the session file into multiple segments.
        """
        pass


class MarkSplitter(Splitter):
    """
    Splits the session file according to the timestamps that denote the
    beggining and end of each particular event.
    """

    identifier = 'marks'

    def split(marks_filename):
        pcap_filename = marks_filename.split('.')[0] + '.pcap'

        print("Processing {}".format(pcap_filename))

        with open(marks_filename) as marks_f:
            marklines = list(marks_f.readlines())
            marks_num = len(marklines)

        if marks_num != 28:
            print("Invalid number of marks, skipping.")

        for mark_index in range(marks_num/2):
            start_line = marklines[2*mark_index]
            end_line = marklines[2*mark_index+1]

            start_line_parts = start_line.split(' ')
            end_line_parts = end_line.split(' ')

            start_timestamp = ' '.join(start_line_parts[:2])
            end_timestamp = ' '.join(end_line_parts[:2])

            event_name = '_'.join(start_line_parts[-1].strip().split('_')[1:])

            query = 'frame.time >= "{0}" and frame.time <= "{1}"'.format(
                start_timestamp,
                end_timestamp
            )

            # Generate the name for the output file
            time_suffix = end_timestamp.replace('-', '')
            time_suffix = time_suffix.replace(':', '')
            time_suffix = time_suffix.replace(' ', '_').split('.')[0]

            output_filename = os.path.join(
                'data_split',
                event_name + '_' + time_suffix + '.pcap'
            )

            if os.path.exists(output_filename):
                # This should not happen due to the fact that two events do not
                # happen at the same time
                output_filename = output_filename.split('.')[0] + '_1.pcap'

            retcode = subprocess.call([
                'tshark',
                '-r', pcap_filename,
                '-w', output_filename,
                query])

            if retcode != 0:
                print("Extraction of {0} unsuccessful".format(event_name))


class AutoSplitter(Splitter):
    """
    Splits the session file according to smart heuristics that detect the
    beggining and end of a possible event in the PCAP session file.
    """

    identifier = 'auto'

    def get_interval_allegiance(self, a,b,c):
        return 'random'

    def split(self, pcap_filename):
        # Ignore retrasmissions
        packets = pyshark.FileCapture(
            pcap_filename,
            display_filter='not tcp.analysis.retransmission and '
                           'not tcp.analysis.fast_retransmission and '
                           'not arp'
        )

        previous = None
        interval_splits = []
        for current in packets:
            if not interval_splits:
                interval_splits.append(current.sniff_time)

            try:
                sni = current.ssl.handshake_Extensions_server_name
            except AttributeError:
                sni = None

            try:
                dns = current.dns.qry_name if current.udp.dstport == 53 else None
            except AttributeError:
                dns = None

            if previous is not None:
                time_gap = current.sniff_time - previous.sniff_time
                if time_gap.total_seconds() > 2:
                    print(current.sniff_time.strftime('%H:%M:%S'))
                    interval_splits.append(previous.sniff_time)

            previous = current

        interval_splits.append(current.sniff_time)

        intervals = []
        for index in range(len(interval_splits) - 1):
            intervals.append((interval_splits[index], interval_splits[index+1]))

        for interval_start, interval_end in intervals:
            event_name = self.get_interval_allegiance(interval_start, interval_end, 'marksfile')

            query = 'frame.time >= "{0}" and frame.time <= "{1}"'.format(
                interval_start.strftime('%Y-%m-%d %H:%M:%S.%f'),
                interval_end.strftime('%Y-%m-%d %H:%M:%S.%f')
            )

            # Generate the name for the output file
            time_suffix = interval_end.strftime('%Y%m%d_%H%M%S')

            output_filename = os.path.join(
                'data_split',
                event_name + '_' + time_suffix + '.pcap'
            )

            if os.path.exists(output_filename):
                # This should not happen due to the fact that two events do not
                # happen at the same time
                output_filename = output_filename.split('.')[0] + '_1.pcap'

            retcode = subprocess.call([
                'tshark',
                '-r', pcap_filename,
                '-w', output_filename,
                query])


def main(arguments):
    output_dir = arguments['--output-dir']
    method = arguments['--method']
    filepaths = arguments['<file>']

    # Obtain suitable splitter
    splitter_cls = Splitter.get_plugin(method)
    splitter = splitter_cls()

    # Make sure target output dir exists
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    # Split each input file
    for filepath in filepaths:
        splitter.split(filepath)


if __name__ == '__main__':
    arguments = docopt.docopt(__doc__)
    main(arguments)
