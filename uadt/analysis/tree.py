#!/usr/bin/python3

"""
Tree - train and evaluate support vector machine on a given dataset.

Usage:
  tree.py <dataset> [--train=<fraction>] [--confusion]

Options:
  --train=<fraction>  Specifies the portion of the data set that should be used for training [default: 0.7].
  --confusion         Displays the confusion matrix.

Examples:
$ python tree.py data1000.csv
$ python tree.py data1000.csv --train=0.8
"""

from docopt import docopt
from sklearn import tree

from uadt.analysis.model import Model


class Tree(Model):
    """
    Provides the decision tree classifier.
    """

    def initialize_classifier(self):
        """
        Initializes the classifier. Decision trees do not require any
        hyperparamters.
        """

        self.classifier = tree.DecisionTreeClassifier()


def main():
    arguments = docopt(__doc__)

    machine = Tree(arguments['<dataset>'],
                   train_size=float(arguments['--train']))
    machine.prepare_data()
    machine.initialize_classifier()

    print("Success rate: {0}".format(machine.evaluate()))

    if arguments.get('--confusion'):
        machine.plot_confusion_matrix()


if __name__ == '__main__':
    main()
