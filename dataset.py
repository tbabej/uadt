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

from docopt import docopt

from flow import Flow

def process_pcap(path, path_index, files_count):
    print('[{1}/{2}] Processing: {0}'
          .format(path, path_index, files_count))
    f = Flow(path)
    if not f.data.empty:
        return f.features

def main(arguments):
    search_string = os.path.join(arguments['<directory>'], '*.pcap')
    paths = list(sorted(glob.glob(search_string)))

    # If asked to, ignore files bigger than max-size
    size = arguments.get('--max-size')
    if size:
        size = int(size) * 1024 ** 2
        paths = list(filter(lambda p: os.path.getsize(p) < size, paths))

    # Determine the range of files to be processed
    pool = multiprocessing.Pool(8)
    results = []

    for counter, path in enumerate(paths):
        path_index = start + counter + 1
        result = pool.apply_async(process_pcap, (path, path_index, files_count))
        results.append(result)

    raw_data = list([r.get() for r in results if r.get() is not None])

    pool.close()
    pool.join()

    # Determining filename can be complicated
    directory_name = os.path.basename(arguments['<directory>'])
    if not directory_name:
        directory_name = os.path.dirname(arguments['<directory>'])
        directory_name = os.path.basename(directory_name)
    filename = arguments['--outfile'] or '{0}.csv'.format(directory_name)

    # Write data out to file
    print("Writing to " + filename)
    data = pandas.DataFrame(raw_data)
    data.to_csv(filename, header=True, mode='w')


if __name__ == '__main__':
    arguments = docopt(__doc__)
    main(arguments)
