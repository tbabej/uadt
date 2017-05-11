#!/usr/bin/python3

"""
Tree - train and evaluate support vector machine on a given dataset.

Usage:
  tree.py <dataset> [--train=<fraction>]

Options:
  --train=<fraction>  Specifies the portion of the data set that should be used for training [default: 0.7].

Examples:
$ python tree.py data1000.csv
$ python tree.py data1000.csv --train=0.8
"""

import pandas
from docopt import docopt
from sklearn import tree, model_selection


class Tree(object):

    def __init__(self, path, train_size):
        """
        Initialize decision tree machinery giving it the dataset at path to crunch.
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

        # Convert to numpy arrays and split in the wanted ratio
        splitted = model_selection.train_test_split(
                X.as_matrix(),
                y.as_matrix(),
                train_size=self.train_size
        )

        self.X_train = splitted[0]
        self.X_test  = splitted[1]
        self.y_train = splitted[2]
        self.y_test  = splitted[3]

    def evaluate(self):
        """
        Evaluates the decision tree on the training data set.
        """

        classifier = tree.DecisionTreeClassifier()
        model = classifier.fit(self.X_train, self.y_train)
        rate = model.score(self.X_test, self.y_test)

        return rate


def main():
    arguments = docopt(__doc__)

    machine = Tree(arguments['<dataset>'],
                   train_size=float(arguments['--train']))
    machine.prepare_data()

    print("Success rate: {0}".format(machine.evaluate()))


if __name__ == '__main__':
    main()
