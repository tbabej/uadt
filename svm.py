from sklearn import svm, model_selection, preprocessing
import pandas

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

        results = []
        for C in C_candidates:
            for gamma in gamma_candidates:
                print "Testing C: {0}, gamma: {1}".format(C, gamma)
                classifier = svm.SVC(C=C, gamma=gamma, decision_function_shape='ovo')
                model = classifier.fit(self.X_train, self.y_train)
                prediction = model.predict(self.X_test)
                compare_vector =  prediction - self.y_test

                rate = 100*len([p for p in compare_vector if p == 0])/float(len(compare_vector))
                results.append((rate, C, gamma))
                print rate, '% success'

        _, self.C, self.gamma = max(results)


machine = Machine("dataset1000.csv", train_size=0.7)
machine.prepare_data()
machine.optimize_paramters()
print machine.C, machine.gamma
