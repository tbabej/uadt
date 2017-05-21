#!/usr/bin/python3

"""
timeline - given a session PCAP file, generate the timeline of events

Usage:
  uadt-timeline --model=<path> <session_file>
"""

import datetime
import glob
import json
import os
import pprint
import tempfile

import editdistance
import pandas
import joblib
from docopt import docopt

from uadt import config, constants
from uadt.automation.splitter import Splitter
from uadt.analysis.flow import Flow


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
               'start': event['start'].
               'end': event['end'],
               'name': event['name']
            }  for event in events
        ]
        self.events.sort(key=lambda e: e['start'])

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

        event_sequence = [event['name'] for event in self.events]
        other_sequence = [event['name'] for event in self.events]

        return editdistance.eval(event_sequence, other_sequence)


class TimelineExtractor(object):
    # Split the session PCAP files into several events
    # Generate feature vector for each event
    # Classify feature vectors
    # Output timeline
    # Compute distance metric

    def __init__(self, model_path):
        """
        Intialize the pipeline.
        """

        self.classifier = joblib.load(model_path)

    def main(self, session_file):
        # Generate temporary output dir to store the splitted PCAPs
        predictions = []

        with tempfile.TemporaryDirectory() as temp_output_dir:
            splitter = Splitter.get_plugin('auto')(temp_output_dir)
            splitter.execute(session_file)

            splitted_files = glob.glob(os.path.join(temp_output_dir, '*.pcap'))
            for splitted_file in splitted_files:
                flow = Flow.from_path(splitted_file)

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

        predictions.sort(key=lambda p: p['start'])
        pprint.pprint(predictions)

    def evaluate(self, X):
        """
        Evaluates the model on the unseen data.
        """

        return self.classifier.predict(X)[0]


def main():
    arguments = docopt(__doc__)
    session_file = arguments['<session_file>']
    model_path = arguments['--model']

    extractor = TimelineExtractor(model_path)
    print(extractor.main(session_file))


if __name__ == '__main__':
    main()
