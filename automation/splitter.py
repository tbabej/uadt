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
import datetime
import glob
import json
import subprocess
import os

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

    def execute(self, pcap_filename):
        """
        Wraps the splitting method with common error handling and metadata
        loading.
        """

        if not pcap_filename.endswith('.pcap'):
            self.error('File "{}" is not a PCAP file. Skipping.'
                       .format(pcap_filename))
            return

        marks_path = '.'.join(pcap_filename.split('.')[:-1]) + '.marks'

        # Load the marks file
        with open(marks_path, 'r') as marks_file:
            self.metadata = json.loads(marks_file.read())

        # Generate a separate file for each split interval
        for query, event_name, event_end in self.split_intervals(pcap_filename):

            # Generate the name for the output file
            output_filename = os.path.join(
                'data_split',
                ''.join([
                    event_name,
                    '-',
                    event_end.strftime('%Y%m%d_%H%M%S') + '.pcap'
                ])
            )

            # Skip already generated files
            if os.path.exists(output_filename):
                self.warning('File "{}" already exists. Skipping.'
                          .format(output_filename))
                continue

            # Perform the extraction
            retcode = subprocess.call([
                'tshark',
                '-r', pcap_filename,
                '-w', output_filename,
                query
            ])

            if retcode != 0:
                print("Extraction of {0} unsuccessful".format(event_name))

    @abc.abstractmethod
    def split_intervals(self, filename):
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

    def split_intervals(self, pcap_filename):
        # Process each event separately
        for event in self.metadata:
            query = 'frame.time >= "{0}" and frame.time <= "{1}"'.format(
                event['start'],
                event['end']
            )

            end_timestamp = datetime.datetime.strptime(
                event['end'],
                "%Y-%m-%d %H:%M:%S.%f"
            )

            yield query, event['name'], end_timestamp


class AutoSplitter(Splitter):
    """
    Splits the session file according to smart heuristics that detect the
    beggining and end of a possible event in the PCAP session file.
    """

    identifier = 'auto'

    def get_interval_allegiance(self, a,b,c):
        return 'random'

    def split_intervals(self, pcap_filename):
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

            yield query, event_name, interval_end


def main(arguments):
    output_dir = arguments['--output-dir']
    method = arguments['--method']
    filepaths = arguments['<file>']

    # Setup logging
    Splitter.setup_logging()

    # Obtain suitable splitter
    splitter_cls = Splitter.get_plugin(method)
    splitter = splitter_cls()

    # Make sure target output dir exists
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    # Split each input file
    for filepath in filepaths:
        splitter.execute(filepath)


if __name__ == '__main__':
    arguments = docopt.docopt(__doc__)
    main(arguments)
