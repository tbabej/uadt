#!/usr/bin/python3

"""
Dataset - generate the dataset out of directory with pcap files.

Usage:
  dataset.py <directory> [--parallel=TRUE] [--outfile=<filename>] [--max-size=<size>]

Options:
  --outfile=<name>  The name of output .csv file (defaults to <directory>.csv).
  --max-size=<size>  The maximum pcap file size (in MBs).
  --parallel=<value> Specify if dataset generation should leverage multiple processes [default: TRUE].

"""


import os
import glob
import multiprocessing

import pandas
import pebble
from concurrent.futures import TimeoutError
from docopt import docopt

from uadt import config
from uadt.analysis.flow import Flow


class DatasetProcessor(object):
    """
    A tool to for creation of data matrix from the annotated PCAP files.
    """

    def __init__(self, input_directory, output_file=None, max_size=None, parallel=True):
        self.file_queue = self.paths_to_process(input_directory, max_size)
        self.output = self.output_filename(input_directory, output_file)
        self.parallel = parallel

    @staticmethod
    def paths_to_process(input_directory, max_size):
        """
        Returns a list of files that are to be processed. By default it
        searches for all the PCAP files in the given input directory, that do
        not exceed given maximum filesize.
        """

        search_string = os.path.join(input_directory, '*.pcap')
        paths = list(sorted(glob.glob(search_string)))

        # If asked to, ignore files bigger than max-size
        if max_size:
            size = int(max_size) * 1024 ** 2
            paths = list(filter(lambda p: os.path.getsize(p) < max_size, paths))

        return paths

    @staticmethod
    def output_filename(input_directory, output_file):
        """
        Determines the filename of the output file. If no particular name was
        specified at initialization, the output filename is derived from the
        source folder.
        """

        if output_file:
            return output_file
        else:
            directory_name = os.path.basename(input_directory)
            if not directory_name:
                directory_name = os.path.dirname(input_directory)
                directory_name = os.path.basename(directory_name)
            return '{0}.csv'.format(directory_name)

    @staticmethod
    def process_pcap(path, path_index, files_count):
        """
        Extracts feature vector for one particular PCAP file.
        """

        print('[{1}/{2}] Processing: {0}'.format(path, path_index, files_count))

        try:
            f = Flow(path)
            if not f.data.empty:
                return f.features
            else:
                print("Warning: Flow '{0}' is empty".format(path))
        except (Exception, AttributeError):
            print("Data extraction from '{0}' failed".format(path))

    def process(self):
        """
        Processes the splitted PCAP files, extracting feature vector from each.
        The implementation leverages a pool of processes provided my the
        multiprocess module.
        """

        # Determine the range of files to be processed
        futures = []

        queue_length = len(self.file_queue)

        with pebble.ProcessPool(max_workers=config.NUM_JOBS) as pool:
            for counter, path in enumerate(self.file_queue):
                future = pool.schedule(
                    self.process_pcap,
                    (path, counter + 1, queue_length),
                    timeout=1800,
                )
                futures.append(future)

        raw_data = []
        for future in futures:
            try:
                raw_data.append(future.result())
            except TimeoutError:
                pass

        pool.close()
        pool.join()

        data = pandas.DataFrame(raw_data)
        data.to_csv(self.output, header=True, mode='w')


def main():
    arguments = docopt(__doc__)
    processor = DatasetProcessor(
        arguments['<directory>'],
        arguments['--outfile'],
        arguments['--max-size'],
        arguments['--parallel']
    )
    processor.process()


if __name__ == '__main__':
    main()
