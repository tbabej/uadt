#!/usr/bin/python2

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

from docopt import docopt
from sklearn import svm, model_selection, preprocessing
import pandas
import numpy


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

        data = pandas.read_csv(self.path).dropna()

        X = data.drop('class', 1)
        y = data['class']

        splitted = model_selection.train_test_split(X, y, train_size=self.train_size)

        # Convert to numpy arrays and scale inputs to [0,1] range
        self.X_train = self.scale_array(splitted[0].as_matrix())
        self.X_test  = self.scale_array(splitted[1].as_matrix())
        self.y_train = splitted[2].as_matrix()
        self.y_test  = splitted[3].as_matrix()

    @staticmethod
    def scale_array(array):
        """
        Scales given array to [0,1] range.
        """
        scaler = preprocessing.MinMaxScaler()
        return scaler.fit_transform(array)

    def optimize_paramters(self):
        """
        Optimizes C and gamma parameters.
        """

        C_candidates = [2.0**(2*p-1) for p in range(-2, 9)]
        gamma_candidates = [2.0**(2*p-1) for p in range(-8, 3)]

        rates = []
        for C in C_candidates:
            for gamma in gamma_candidates:
                fold_success_rates = []
                five_fold = model_selection.KFold(n_splits=5)

                for fold_train, fold_test in five_fold.split(self.X_train, self.y_train):
                    X_train = self.X_train[fold_train]
                    X_test  = self.X_train[fold_test]
                    y_train = self.y_train[fold_train]
                    y_test  = self.y_train[fold_test]

                    classifier = svm.SVC(C=C, gamma=gamma, decision_function_shape='ovo')
                    model = classifier.fit(X_train, y_train)
                    rate = model.score(X_test, y_test)

                    fold_success_rates.append(rate)

                success_rate = numpy.average(fold_success_rates)
                rates.append((success_rate, C, gamma))

        _, self.C, self.gamma = max(rates)

    def evaluate(self):
        """
        Evaluates the SVM on the training data set.
        """

        classifier = svm.SVC(C=self.C, gamma=self.gamma, decision_function_shape='ovo')
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

