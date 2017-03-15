#!/usr/bin/python2

"""
Dataset - generate the dataset out of directory with pcap files.

Usage:
  dataset.py <directory> [--outfile=<filename>] [--part=<spec>] [--max-size=<size>]

Options:
  --outfile=<name>  The name of output .csv file (defaults to <directory>.csv).
  --max-size=<size>  The maximum pcap file size (in MBs).
  --part=<num>  Specifies the part of the dataset to generate, see "Parts" section.

Parts:
Part 1 represents processing of files 1..100.
Part 2 represents processing of files 101..200.
part n represents processing of files -1+(n-1)*100..n*100.

If not first part is being processed, the outfile will be appended to.

Use this option to hackishly parallelize dataset generation, by running in multiple terminals:
$ for part in `seq 1 10`; do python dataset.py data --part $part; done
$ for part in `seq 11 20`; do python dataset.py data --part $part; done
$ for part in `seq 21 30`; do python dataset.py data --part $part; done
...

"""

from docopt import docopt

import os
import glob
import pandas

from flow import Flow


def main(arguments):
    search_string = os.path.join(arguments['<directory>'], '*.pcap')
    paths = list(sorted(glob.glob(search_string)))

    # If asked to, ignore files bigger than max-size
    size = arguments.get('--max-size')
    if size:
        size = int(size) * 1024 ** 2
        paths = list(filter(lambda p: os.path.getsize(p) < size, paths))

    files_count = len(paths)

    part = arguments.get('--part')

    # Determine the range of files to be processed
    if part:
        part = int(part) * 100
        start = max(part-100, 0)
        end = min(part, files_count)
    else:
        start = 0
        end = files_count

    # Extract features from selected files
    raw_data = []
    for counter, path in enumerate(paths[start:end]):
        print '[{1}/{2}] Processing: {0}'.format(path,
                                                 start+counter+1, files_count)

        f = Flow(path)
        raw_data.append(f.features)
        del f

    # Write data out to file
    data = pandas.DataFrame(raw_data)
    filename = arguments['--outfile'] or '{0}.csv'.format(arguments['<directory>'])

    print("Writing to " + filename)
    if start == 0:
        data.to_csv(filename, header=True, mode='w')
    else:
        data.to_csv(filename, header=False, mode='a')


if __name__ == '__main__':
    arguments = docopt(__doc__)
    main(arguments)
