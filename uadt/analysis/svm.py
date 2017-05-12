#!/usr/bin/python3

"""
SVM - train and evaluate support vector machine on a given dataset.

Usage:
  svm.py <dataset> (--optimize | -C=<value> --gamma=<value>) [--train=<fraction>]

Options:
  --optimize          Specify that SVM should find optimal parameters for C and gamma.
  -C=<value>          Manual value for C (must be used together with --gamma)
  --gamma=<value>     Manual value for gamma (must be used together with -C)
  --train=<fraction>  Specifies the portion of the data set that should be used for training [default: 0.7].

Examples:
$ python svm.py data1000.csv --optimize --train=0.8
$ python svm.py data1000.csv -C 512 --gamma 0.5
"""

import pandas
import numpy
from docopt import docopt
from sklearn import svm, model_selection, preprocessing
from joblib import Parallel, delayed

from uadt import config
from uadt.analysis.model import Model


class Machine(Model):

    scale_data = True

    def test_parameters(self, C, gamma):
        """
        Performs a 5-Fold cross validation of the given parameters on the
        training set.
        """

        fold_success_rates = []
        five_fold = model_selection.KFold(n_splits=5)

        for fold_train, fold_test in five_fold.split(self.X_train, self.y_train):
            X_train = self.X_train[fold_train]
            X_test  = self.X_train[fold_test]
            y_train = self.y_train[fold_train]
            y_test  = self.y_train[fold_test]

            classifier = svm.SVC(C=C, gamma=gamma, decision_function_shape='ovr')
            model = classifier.fit(X_train, y_train)
            rate = model.score(X_test, y_test)

            fold_success_rates.append(rate)

        success_rate = numpy.average(fold_success_rates)
        return (success_rate, C, gamma)

    def optimize_paramters(self):
        """
        Optimizes C and gamma parameters.
        """

        C_candidates = [2.0**(2*p-1) for p in range(-2, 9)]
        gamma_candidates = [2.0**(2*p-1) for p in range(-8, 3)]

        rates = Parallel(n_jobs=config.NUM_JOBS)(
            delayed(self.test_parameters)(C, gamma)
            for C in C_candidates
            for gamma in gamma_candidates
        )

        _, self.C, self.gamma = max(rates)

    def initialize_classifier(self):
        """
        Intializes the SVM with the determined hyperparameters.
        """

        self.classifier = svm.SVC(
            C=self.C,
            gamma=self.gamma,
            decision_function_shape='ovr'
        )


def main():
    arguments = docopt(__doc__)

    machine = Machine(arguments['<dataset>'],
                      train_size=float(arguments['--train']))
    machine.prepare_data()

    if arguments.get('--optimize'):
        print("Searching for optimal parameters..")
        machine.optimize_paramters()
    elif arguments.get('-C') and arguments.get('--gamma'):
        machine.C = float(arguments.get('-C'))
        machine.gamma = float(arguments.get('--gamma'))

    print("Used parameters: C={0}, gamma={1}".format(machine.C, machine.gamma))

    machine.initialize_classifier()

    print("Success rate: {0}".format(machine.evaluate()))


if __name__ == '__main__':
    main()
