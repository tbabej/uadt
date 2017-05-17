#!/usr/bin/python3

"""
Tree - train and evaluate support vector machine on a given dataset.

Usage:
  tree.py <dataset> [--train=<fraction>] [--optimize] [--confusion] [--outfile=<path>]

Options:
  --train=<fraction>  Specifies the portion of the data set that should be used for training [default: 0.7].
  --confusion         Displays the confusion matrix.
  --outfile=<path>    Save the trained model at the given path.

Examples:
$ python tree.py data1000.csv
$ python tree.py data1000.csv --train=0.8
"""

from docopt import docopt
from sklearn import tree
from joblib import Parallel, delayed

from uadt import config
from uadt.analysis.model import Model


class Tree(Model):
    """
    Provides the decision tree classifier.
    """

    classifier_cls = tree.DecisionTreeClassifier

    def optimize_paramters(self):
        """
        Optimizes tree depth.
        """

        max_depth_candidates = range(3, 20)

        rates = Parallel(n_jobs=config.NUM_JOBS)(
            delayed(self.test_parameters)(max_depth=depth)
            for max_depth in max_depth_candidates
        )

        _, self.hyperparameters = max(rates, key=lambda x: x[0])

def main():
    arguments = docopt(__doc__)

    machine = Tree(arguments['<dataset>'],
                   train_size=float(arguments['--train']))
    machine.prepare_data()

    if arguments.get('--optimize'):
        print("Searching for optimal parameters..")
        machine.optimize_paramters()

    machine.initialize_classifier()

    print("Success rate: {0}".format(machine.evaluate()))

    if arguments.get('--confusion'):
        machine.plot_confusion_matrix()

    outfile_path = arguments.get('--outfile')
    if outfile_path:
        machine.save(outfile_path)


if __name__ == '__main__':
    main()
