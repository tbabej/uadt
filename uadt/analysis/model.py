#!/usr/bin/python3

import pandas
import numpy
from sklearn import svm, model_selection, preprocessing
from joblib import Parallel, delayed

from uadt import config


class Model(object):

    scale_data = False

    def __init__(self, path, train_size):
        """
        Initialize model giving it the dataset at path to crunch.
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

        scaler = preprocessing.StandardScaler()

        # Scaling of the test set has to be performed with the same scaling, as
        # the data set of the training set, but the training set must not be
        # taken into account
        if self.scale_data:
            self.X_train = scaler.fit_transform(splitted[0])
            self.X_test  = scaler.transform(splitted[1])
        else:
            self.X_train = splitted[0]
            self.X_test  = splitted[1]

        self.y_train = splitted[2]
        self.y_test  = splitted[3]

    def evaluate(self):
        """
        Evaluates the SVM on the training data set.
        """

        classifier = svm.SVC(C=self.C, gamma=self.gamma, decision_function_shape='ovr')
        model = classifier.fit(self.X_train, self.y_train)
        rate = model.score(self.X_test, self.y_test)

        return rate
