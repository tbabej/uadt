#!/usr/bin/python3

import abc
import pandas
import numpy
import itertools
from matplotlib import pyplot as plt
from sklearn import model_selection, preprocessing
from sklearn import metrics
from joblib import Parallel, delayed

from uadt import config
from uadt import constants

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

    @abc.abstractmethod
    def initialize_classifier(self):
        """
        Initializes the classifier instance.
        """
        pass

    def plot_confusion_matrix(self, normalize=False):
        """
        This function plots the confusion matrix.
        Normalization can be applied by setting `normalize=True`.
        """

        # Obtain confusion matrix data
        cm = metrics.confusion_matrix(self.y_test, self.y_predicted)

        classes = list(
            [k for v, k in [(v, k) for k, v in constants.CLASSES.items()]]
        )

        # Preprocess the matrix data
        if normalize:
            cm = cm.astype('float') / cm.sum(axis=1)[:, numpy.newaxis]

        label_color_threshold = cm.max() / 2.

        # Plot the matrix
        plt.figure()
        plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
        plt.title("Confusion matrix")
        plt.colorbar()

        tick_marks = numpy.arange(len(classes))
        plt.xticks(tick_marks, classes, rotation=45)
        plt.yticks(tick_marks, classes)

        plt.tight_layout()
        plt.ylabel('True label')
        plt.xlabel('Predicted label')

        matrix_coordinates = itertools.product(
            range(cm.shape[0]),
            range(cm.shape[1])
        )

        for i, j in matrix_coordinates:
            plt.text(
                j, i, cm[i, j],
                horizontalalignment="center",
                color="white" if cm[i, j] > label_color_threshold else "black"
            )

        plt.show()

    def evaluate(self):
        """
        Evaluates the model on the training data set.
        """

        model = self.classifier.fit(self.X_train, self.y_train)
        self.y_predicted = model.predict(self.X_test)
        rate = metrics.accuracy_score(self.y_test, self.y_predicted)

        return rate
