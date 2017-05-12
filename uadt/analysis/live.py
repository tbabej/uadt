#!/usr/bin/python3

"""
Live - detect user actions in the live captured traffic

Usage:
  live.py --model=<path>

Options:
  --model=<path>  Specifies the path to the saved model.

Examples:
$ python live.py --model tree.model
"""

import pandas
import joblib
import pyshark
from docopt import docopt
from sklearn import tree, model_selection

from uadt.analysis.flow import Flow
from uadt import config, constants

class Live(object):

    def __init__(self, model_path):
        """
        Initialize decision tree machinery giving it the dataset at path to crunch.
        """

        self.classifier = joblib.load(model_path)

    def capture(self):
        captured = []

        current = None
        previous = None

        for current in pyshark.LiveCapture(config.CAPTURE_INTERFACE):
            if previous is not None:
                time_gap = current.sniff_time - previous.sniff_time
                if time_gap.total_seconds() > 2:
                    self.process(captured)
                    captured = []

            captured.append(current)
            previous = current

    def process(self, packet_list):
        flow = Flow(packet_list)
        data = pandas.DataFrame([flow.features]).fillna(0).as_matrix()

        event_id = self.evaluate(data)
        for key, value in constants.CLASSES.items():
            if value == event_id:
                print("Action detected: {0}".format(key))

    def evaluate(self, X):
        """
        Evaluates the decision tree on the training data set.
        """

        return self.classifier.predict(X)[0]


def main():
    arguments = docopt(__doc__)
    analyzer = Live(arguments['--model'])
    analyzer.capture()


if __name__ == '__main__':
    main()
