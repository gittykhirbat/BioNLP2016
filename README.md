# BioNLP2016 - SeeDev Task
University of Melbourne's SeeDev binary event extraction system for BioNLP-Shared Task 2016.

Authors: Nagesh PC, Gitansh Khirbat <br>
Date: 20th June 2016 <br>
Project: SeeDev binary event extraction of BioNLP-Shared Task 2016.<br>
Paper: {Link goes here when the paper is up on ACL-web}

## PROJECT INFORMATION

This is the public release of the University of Melbourne's system for SeeDev binary event extraction of BioNLP-Shared Task 2016. This task addresses the extraction of genetic and molecular mechanisms that regulate plant seed development from the natural language text of the published literature. This system makes use of support vector machine classifier with linear kernel powered by a rich set of features and achieved second-best results.

More details about the task can be obtained from: http://2016.bionlp-st.org/tasks/seedev

## GETTING THE CODE UP
### Prerequisites
This code requires Python to be installed on your system. It is compatible with Python2 and Python3. If you do not have Python, it can be downloaded from https://www.python.org/downloads/

### Installing 
The archive contains 3 python files. They are:
1. classifier.py - Contains main() function, classifier and feature information
2. preprocess.py - Code to preprocess data using corenlpparse.py and produces data points (entity pairs).
3. corenlpparse.py - Contains methods to read data from files using Stanford's CoreNLP.

### Running the code 
The code can be run by following these steps -
1. DATA - Create a sub-directory "data" within the directory of this code.
  a) Store the training data in a sub-directory named "training_data" within this directory like this: "/data/training_data/"
  b) Store the test data in a sub-directory named "test_data" within this directory like this: "/data/test_data/"
  
2. 

It is essential that your data is present in the same directory as this code is.
The data should be saved in this format:
  a) Training data: 



Installation
------------


TODO: Describe the installation process

Usage

TODO: Write usage instructions

Contributing

Fork it!
Create your feature branch: git checkout -b my-new-feature
Commit your changes: git commit -am 'Add some feature'
Push to the branch: git push origin my-new-feature
Submit a pull request :D
History

TODO: Write history

Credits

TODO: Write credits

License

TODO: Write license
