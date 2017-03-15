from sklearn import svm
import pandas
import numpy

origdf = pandas.read_csv('dataset10000.csv').dropna()
origdf = origdf.sample(frac=1)

df = origdf.copy()
results = df['class']
df = df.drop('class', 1)

data = (df - df.mean()) / (df.max() - df.min())
splitpoint = int(len(data)*0.8)

X_train = data[:splitpoint].as_matrix()
Y_train = results[:splitpoint].as_matrix()

X_test = data[splitpoint:].as_matrix()
Y_test = results[splitpoint:].as_matrix()

C_candidates = [2.0**(2*p-1) for p in range(-2, 8)]
gamma_candidates = [2.0**(2*p-1) for p in range(-8, 2)]

results = []
for C in C_candidates:
    for gamma in gamma_candidates:
        print "Testing C: {0}, gamma: {1}".format(C, gamma)
        classifier = svm.SVC(C=C, gamma=gamma, decision_function_shape='ovo')
        model = classifier.fit(X_train, Y_train)
        prediction = model.predict(X_test)
        compare_vector =  prediction - Y_test
        #print prediction
        #print Y_test
        #print
        #print compare_vector

        rate = 100*len([p for p in compare_vector if p == 0])/float(len(compare_vector))
        results.append((rate, C, gamma))
        print rate, '% success'

print max(results)
