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
    classifier_cls = None

    def __init__(self, path, train_size):
        """
        Initialize model giving it the dataset at path to crunch.
        """

        self.path = path
        self.train_size = train_size

        # Set empty hyperparameters initially (some models do not have any)
        self.hyperparameters = {}

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

        # Remember the columns for later usage
        self.columns = list(X.columns)

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

    def initialize_classifier(self):
        """
        Intializes the classifier with the determined hyperparameters.
        """

        print("Initializing classifier with hyperparameters: {0}"
              .format(self.hyperparameters))
        self.classifier = self.classifier_cls(**self.hyperparameters)

    def test_parameters(self, **hyperparameters):
        """
        Performs a 5-Fold cross validation of the given hyperparameters on the
        training set.
        """

        fold_success_rates = []
        five_fold = model_selection.KFold(n_splits=5)

        for fold_train, fold_test in five_fold.split(self.X_train, self.y_train):
            X_train = self.X_train[fold_train]
            X_test  = self.X_train[fold_test]
            y_train = self.y_train[fold_train]
            y_test  = self.y_train[fold_test]

            fold_classifier = self.classifier_cls(**hyperparameters)
            model = fold_classifier.fit(X_train, y_train)
            rate = model.score(X_test, y_test)

            fold_success_rates.append(rate)

        success_rate = numpy.average(fold_success_rates)
        return (success_rate, hyperparameters)

    def plot_confusion_matrix(self, normalize=False):
        """
        This function plots the confusion matrix.
        Normalization can be applied by setting `normalize=True`.
        """

        # Obtain confusion matrix data
        cm = metrics.confusion_matrix(self.y_test, self.y_predicted)

        importances = list(sorted(zip(self.classifier.feature_importances_, self.columns)))

        for importance, column_name in importances:
            print("{0}: {1}".format(column_name, importance))

        classes = list(
            [k for v, k in
                sorted([(v, k) for k, v in constants.CLASSES.items()])]
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

    def save(self, path):
        """
        Save the model at the given path.
        """

        joblib.dump(self.classifier, path)
