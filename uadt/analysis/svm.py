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


class Machine(object):

    def __init__(self, path, train_size):
        """
        Initialize SVM machinery giving it the dataset at path to crunch.
        """

        self.path = path
        self.train_size = train_size

    def prepare_data(self):
        """
        Reads, randomizes data from the given dataset and splits it into test
        and training sets. Test data set is not used during training or
        parameter optimization.
        """

        data = pandas.read_csv(self.path).fillna(0)
        print("The size of data {0}".format(data.shape))

        X = data.drop('class', 1)
        y = data['class']

        # Convert to numpy arrays and scale inputs
        splitted = model_selection.train_test_split(
                X.as_matrix(),
                y.as_matrix(),
                train_size=self.train_size
        )

        # Scaling of the test set has to be performed with the same scaling, as
        # the data set of the training set, but the training set must not be
        # taken into account
        scaler = preprocessing.StandardScaler()
        self.X_train = scaler.fit_transform(splitted[0])
        self.X_test  = scaler.transform(splitted[1])
        self.y_train = splitted[2]
        self.y_test  = splitted[3]

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

    def evaluate(self):
        """
        Evaluates the SVM on the training data set.
        """

        classifier = svm.SVC(C=self.C, gamma=self.gamma, decision_function_shape='ovr')
        model = classifier.fit(self.X_train, self.y_train)
        rate = model.score(self.X_test, self.y_test)

        return rate


def main(arguments):
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
    print("Success rate: {0}".format(machine.evaluate()))


if __name__ == '__main__':
    arguments = docopt(__doc__)
    main(arguments)

