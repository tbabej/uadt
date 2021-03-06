Usage
-----

First, make sure you have all the dependencies:

    $ pip install -r requirements.txt

Additionally, you will need to provide training data in the form of pcap files:

    $ ls ~/mypcaps/*.pcap
    one.pcap
    two.pcap
    ...

To generate the dataset of features extracted from the pcap files, use dataset.py:

    $ ./dataset.py ~/mypcaps/
    [1/3] Processing: /home/tbabej/mypcaps/one.pcap
    [2/3] Processing: /home/tbabej/mypcaps/two.pcap
    [3/3] Processing: /home/tbabej/mypcaps/three.pcap
    Writing to mypcaps.csv

To train and evaluate the SVM on this data, use svm.py:

    $ ./svm.py mypcaps.csv --optimize
    Searching for optimal parameters..
    Used parameters: C=2048.0, gamma=0.03125
    Success rate: 0.744769874477

The dataset and svm commands have more options, explore their documentation via:

    $ ./dataset.py -h
    $ ./svm.py -h


Useful
------

Pre-generated .csv training data sets are available in trainingsets/ directory.
