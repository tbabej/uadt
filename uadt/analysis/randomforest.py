#!/usr/bin/python3

"""
Forest - train and evaluate support vector machine on a given dataset.

Usage:
  forest.py <dataset> [--train=<fraction>] [--confusion] [--outfile=<path>]

Options:
  --train=<fraction>  Specifies the portion of the data set that should be used for training [default: 0.7].
  --confusion         Displays the confusion matrix.
  --outfile=<path>    Save the trained model at the given path.

Examples:
$ python tree.py data1000.csv
$ python tree.py data1000.csv --train=0.8
"""

from docopt import docopt
from sklearn import ensemble

from uadt.analysis.model import Model


class Forest(Model):
    """
    Provides the random forest classifier.
    """

    def initialize_classifier(self):
        """
        Initializes the classifier. Decision trees do not require any
        hyperparamters.
        """

        self.classifier = ensemble.RandomForestClassifier(n_estimators=20)


def main():
    arguments = docopt(__doc__)

    machine = Forest(arguments['<dataset>'],
                   train_size=float(arguments['--train']))
    machine.prepare_data()
    machine.initialize_classifier()

    print("Success rate: {0}".format(machine.evaluate()))

    if arguments.get('--confusion'):
        machine.plot_confusion_matrix()

    outfile_path = arguments.get('--outfile')
    if outfile_path:
        machine.save(outfile_path)


if __name__ == '__main__':
    main()
