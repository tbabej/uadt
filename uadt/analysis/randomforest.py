#!/usr/bin/python3

"""
Forest - train and evaluate support vector machine on a given dataset.

Usage:
  forest.py <dataset> [--optimize] [--train=<fraction>] [--confusion] [--outfile=<path>]

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
from joblib import Parallel, delayed

from uadt import config
from uadt.analysis.model import Model


class Forest(Model):
    """
    Provides the random forest classifier.
    """

    classifier_cls = ensemble.RandomForestClassifier

    def optimize_paramters(self):
        """
        Optimizes parameters of the random forest.
        """

        n_estimators_candidates = [10*2**n for n in range(8,10)]
        max_features_candidates = [0.05 * n for n in range(1, 21)]
        min_samples_leaf_candidates = [
            1,2,3,4,6,8,10,12,15,18,21,25,30,35,40,45,50
        ]

        rates = Parallel(n_jobs=config.NUM_JOBS)(
            delayed(self.test_parameters)(n_estimators=n_estimators, max_features=max_features, min_samples_leaf=min_samples_leaf)
            for n_estimators in n_estimators_candidates
            for max_features in max_features_candidates
            for min_samples_leaf in min_samples_leaf_candidates
        )

        _, self.hyperparameters = max(rates, key=lambda x: x[0])


def main():
    arguments = docopt(__doc__)

    machine = Forest(arguments['<dataset>'],
                   train_size=float(arguments['--train']))
    machine.prepare_data()

    if arguments.get('--optimize'):
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
