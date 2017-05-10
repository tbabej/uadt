#!/usr/bin/python3

"""
splitter - split a session PCAP file using different methods

Usage:
  splitter.py --method=<method> [--parallel=TRUE] [--output-dir=<output_dir>] <file>...

Options:
  --method=<method>      Specify what method should be used to split the PCAP file.
  --output-dir=<value>   The directory where to create splitted PCAP file segments [default: data_split].
  --parallel=<value>     Whether use multiple processes to split files [default: TRUE].

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

import config
from plugins import PluginBase, PluginMount


class Splitter(PluginBase, metaclass=PluginMount):
    """
    An object that represents a mechanism for splitting a session PCAP file.
    """

    identifier = None

    def __init__(self, output_dir):
        if not self.identifier:
            raise ValueError("Method idenfitier must be specified")

        self.output_dir = output_dir

    def execute(self, pcap_filename):
        """
        Wraps the splitting method with common error handling and metadata
        loading.
        """

        self.info("Processing: '{}'".format(pcap_filename))

        if not pcap_filename.endswith('.pcap'):
            self.error('File "{}" is not a PCAP file. Skipping.'
                       .format(pcap_filename))
            return

        marks_path = '.'.join(pcap_filename.split('.')[:-1]) + '.marks'

        # Load the marks file
        with open(marks_path, 'r') as marks_file:
            self.metadata = json.loads(marks_file.read())

        # Convert timestamps into datetime objects
        for event in self.metadata:
            event['start'] = datetime.datetime.strptime(
                event['start'],
                "%Y-%m-%d %H:%M:%S.%f UTC"
            )
            event['end'] = datetime.datetime.strptime(
                event['end'],
                "%Y-%m-%d %H:%M:%S.%f UTC"
            )

        # Generate a separate file for each split interval
        for query, event_name, event_end in self.split_intervals(pcap_filename):

            # Generate the name for the output file
            output_filename = os.path.join(
                self.output_dir,
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
            else:
                self.debug('Splitting out "{}"'.format(output_filename))

            # Perform the extraction
            env = os.environ.copy()
            env['TZ'] = 'UTC'
            try:
                subprocess.run(
                    [
                        'tshark',
                        '-r', pcap_filename,
                        '-w', output_filename,
                        query
                    ],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    env=env
                )
            except subprocess.CalledProcessError:
                self.error(
                    "Extraction of '{0}' event from '{1}' unsuccessful. "
                    "Using query: {2}"
                    .format(event_name, pcap_filename, query)
                )

    def get_interval_allegiance(self, interval_start, interval_end):
        """
        Determines the most likely event associated with the given interval.
        Algorithm:
            - associate the event interval which has biggest overlap
        """

        def determine_overlap(e):
            return min(e['end'], interval_end) - max(e['start'], interval_start)

        return max(self.metadata, key=determine_overlap)['name']

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
                event['start'].strftime("%Y-%m-%d %H:%M:%S.%f"),
                event['end'].strftime("%Y-%m-%d %H:%M:%S.%f")
            )

            yield query, event['name'], event['end']


class AutoSplitter(Splitter):
    """
    Splits the session file according to smart heuristics that detect the
    beggining and end of a possible event in the PCAP session file.
    """

    identifier = 'auto'

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
                    self.debug(
                        "Identified interval split: {}".format(
                        previous.sniff_time.strftime("%Y-%m-%d %H:%M:%S.%f")
                    ))
                    interval_splits.append(previous.sniff_time)

            previous = current

        interval_splits.append(current.sniff_time)

        intervals = []
        for index in range(len(interval_splits) - 1):
            intervals.append((interval_splits[index], interval_splits[index+1]))

        for interval_start, interval_end in intervals:
            event_name = self.get_interval_allegiance(interval_start, interval_end)

            query = 'frame.time >= "{0}" and frame.time <= "{1}"'.format(
                interval_start.strftime('%Y-%m-%d %H:%M:%S.%f'),
                interval_end.strftime('%Y-%m-%d %H:%M:%S.%f')
            )

            yield query, event_name, interval_end


def process_file(cls, output_dir, path):
    splitter = cls(output_dir)
    splitter.execute(path)


def main(arguments):
    output_dir = arguments['--output-dir']
    method = arguments['--method']
    filepaths = arguments['<file>']
    parallel = arguments['--parallel']

    # Setup logging
    Splitter.setup_logging()

    # Obtain suitable splitter
    splitter_cls = Splitter.get_plugin(method)
    splitter = splitter_cls(output_dir)

    # Make sure target output dir exists
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    # Split each input file
    if parallel:
        Parallel(n_jobs=config.NUM_JOBS)(
            delayed(process_file)(splitter_cls, output_dir, path)
            for path in filepaths
        )
    else:
        for filepath in filepaths:
            splitter.execute(filepath)


if __name__ == '__main__':
    arguments = docopt.docopt(__doc__)
    main(arguments)
