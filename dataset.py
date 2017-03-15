"""
Generates the training / testing datasets.
"""

import glob
import pandas

from flow import Flow

import sys

paths = list(sorted(glob.glob('data10000/*.pcap')))
total_paths = len(paths)

part = int(sys.argv[1]) * 100
start = max(part-100, 0)
end = min(part, total_paths)

paths = paths[start:end]

counter = start + 1
raw_data = []
for path in paths:
    print '[{1}/{2}] Processing: {0}'.format(path, counter, total_paths)
    f = Flow(path)
    raw_data.append(f.features)
    del f
    counter = counter + 1

data = pandas.DataFrame(raw_data)

if start == 0:
    data.to_csv('dataset10000.csv', header=True, mode='w')
else:
    data.to_csv('dataset10000.csv', header=False, mode='a')
