#!/usr/bin/python3

"""
timeline - given a session PCAP file, generate the timeline of events

Usage:
  uadt-timeline --model=<path> [--threshold=<value>] <session_file>...

Options:
  --threshold=<value>  The edit distance above which timeline should notify about the session [default: 0.5].
"""

import datetime
import glob
import json
import os
import pprint
import tempfile

import editdistance
import pandas
import numpy
import joblib
from docopt import docopt

from uadt import config, constants
from uadt.analysis.splitter import Splitter
from uadt.analysis.flow import Flow


NOISE = [
    k for k, v in constants.CLASSES.items()
    if v == 0
]


class Timeline(object):
    """
    Represents a series of events.
    """

    def __init__(self, events):
        """
        Initialize timeline from a list of event dictionaries.
        """

        self.events = [
            {
               'start': event['start'],
               'end': event['end'],
               'name': event['name']
            }  for event in events
        ]
        self.events.sort(key=lambda e: e['start'])

    def __len__(self):
        return len(self.events)

    @classmethod
    def from_marks_file(cls, path):
        """
        Creates a timeline out of a given marks file.
        """

        with open(path, 'r') as marks_file:
            events = json.loads(marks_file.read())['events']

        for event in events:
            event['start'] = datetime.datetime.strptime(
                    event['start'],
                    constants.MARKS_TIMESTAMP
            )
            event['end'] = datetime.datetime.strptime(
                    event['end'],
                    constants.MARKS_TIMESTAMP
            )

        return cls(events)

    def distance(self, other):
        """
        Computes distance from this timeline to the other.
        """

        event_sequence = [
            event['name'] for event in self.events
            if event['name'] not in NOISE
        ]
        other_sequence = [
            event['name'] for event in other.events
            if event['name'] not in NOISE
        ]

        return editdistance.eval(event_sequence, other_sequence)


class TimelineExtractor(object):
    # Split the session PCAP files into several events
    # Generate feature vector for each event
    # Classify feature vectors
    # Output timeline
    # Compute distance metric

    def __init__(self, model_path, threshold):
        """
        Intialize the pipeline.
        """

        self.classifier = joblib.load(model_path)
        self.threshold = threshold

    def main(self, session_file):
        print("Extracting timeline from: {0}".format(session_file))

        predictions = []

        # First check if the marks file is available
        try:
            marks_filepath = '.'.join(session_file.split('.')[:-1]) + '.marks'
            ground_truth = Timeline.from_marks_file(marks_filepath)
        except FileNotFoundError:
            return None

        # Generate temporary output dir to store the splitted PCAPs
        with tempfile.TemporaryDirectory() as temp_output_dir:
            splitter = Splitter.get_plugin('auto')(temp_output_dir)
            splitter.execute(session_file)

            splitted_files = glob.glob(os.path.join(temp_output_dir, '*.pcap'))
            for splitted_file in splitted_files:
                flow = Flow.from_path(splitted_file)

                # If the flow contains no data, let's skip
                if flow.empty:
                    continue

                event = {
                    'start': flow.interval[0],
                    'end': flow.interval[1]
                }

                features = flow.features
                features.pop('class')
                data = pandas.DataFrame([features]).fillna(0).as_matrix()

                event_id = self.evaluate(data)
                for key, value in constants.CLASSES.items():
                    if value == event_id:
                        event['name'] = key

                predictions.append(event)


        predicted = Timeline(predictions)

        distance = ground_truth.distance(predicted)
        if distance > self.threshold * len(ground_truth):
            print("Warning: {2}: Distance from ground truth above "
                    "threshold (distance {0}, threshold {1:2})"
                  .format(distance, self.threshold * len(ground_truth),
                          session_file))

        return distance

    def evaluate(self, X):
        """
        Evaluates the model on the unseen data.
        """

        return self.classifier.predict(X)[0]


def main():
    arguments = docopt(__doc__)
    session_files = arguments['<session_file>']
    threshold = float(arguments['--threshold'])
    model_path = arguments['--model']

    extractor = TimelineExtractor(model_path, threshold)

    distances = joblib.Parallel(n_jobs=config.NUM_JOBS)(
        joblib.delayed(extractor.main)(path)
        for path in session_files
    )

    # Filter out unsuccessful computations
    distances = [d for d in distances if d is not None]

    print("Distances: {0}".format(distances))
    print("Min distance: {0}".format(numpy.min(distances)))
    print("Max distance: {0}".format(numpy.max(distances)))
    print("Average distance: {0}".format(numpy.mean(distances)))
    print("Med distance: {0}".format(numpy.median(distances)))


if __name__ == '__main__':
    main()
