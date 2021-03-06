# -*- coding: utf-8 -*-
"""NLP.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1LLCx_xH0NmdM3Rcq7EOixQmdHfYYan4r
"""

import os
import sys
import collections
import re
import math
import copy
import codecs
import csv
import itertools 

# Stores emails as dictionaries. email_file_name : Document (class defined below)
training_set = dict()
test_set = dict()

# Filtered sets without stop words
filtered_training_set = dict()
filtered_test_set = dict()

# list of Stop words
stop_words = []
classes = ["V", "N"]

# Conditional probability from the training data
conditional_probability = dict()
filtered_conditional_probability = dict()
# Prior for the classifications using the training data
prior = dict()
filtered_prior = dict()


# Read all text files in the given directory and construct the data set, D
def makeDataSet(storage_dict, directory, name):
    if os.path.isfile(directory):
        with open(directory, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1 
                if row["Class_label"] == "N":
                    text = (f'\t{row[name]}')
                    storage_dict.update({line_count: Document(text, bagOfWords(text), "N")})
                    line_count += 1
                else :
                    text = (f'\t{row[name]}')
                    storage_dict.update({line_count: Document(text, bagOfWords(text), "V")})
                    line_count += 1       
               


# counts frequency of each word in the text files and order of sequence doesn't matter
def bagOfWords(text):
    bagsofwords = collections.Counter(re.findall(r'\w+', text))
    return dict(bagsofwords)




# Preprocess all the text in a data set
def extractVocab(data_set):
    all_text = ""
    v = []
    for x in data_set:
        all_text += data_set[x].getText()
    for y in bagOfWords(all_text):
        v.append(y)
    return v


def sortSecond(val):
    return val[1] 

# Training
def trainMultinomialNB(training, priors, cond):
    # v is the vocabulary of the training set
    v = extractVocab(training)
    # n is the number of documents
    n = len(training)
    # for each class in classes (i.e. N and V)
    for c in classes:
        # n_c is number of documents with true class c
        n_c = 0.0
        # text_c = concatenation of text of all docs in class (D, c)
        text_c = ""
        for i in training:
            if training[i].getTrueClass() == c:
                n_c += 1
                text_c += training[i].getText()
        priors[c] = float(n_c) / float(n)
        # Count frequencies/tokens of each term in text_c in dictionary form (i.e. token : frequency)
        token_freqs = bagOfWords(text_c)
        

        #Unique Words
        print("Unique for class %s : \t %s" % (c,len(token_freqs)))
        

        #print top 10 words from N & V classes respectively
        sorted_age = dict(sorted(token_freqs.items(), key = lambda kv: kv[1], reverse=True))
        print(dict(itertools.islice(sorted_age.items(), 10)))

        # Calculate conditional probabilities for each token and sum using laplace smoothing and log-scale
        for t in v:
            if t in token_freqs:
                cond.update({t + "_" + c: (float((token_freqs[t] + 1.0)) / float((len(text_c) + len(token_freqs))))})
            else:
                cond.update({t + "_" + c: (float(1.0) / float((len(text_c) + len(token_freqs))))})

        



# Testing. Data instance is a Document
# Returns classification guess
def applyMultinomialNB(data_instance, priors, cond):
    score = {}
    for c in classes:
        score[c] = math.log10(float(priors[c]))
        for t in data_instance.getWordFreqs():
            if (t + "_" + c) in cond:
                score[c] += float(math.log10(cond[t + "_" + c]))
    if score["V"] > score["N"]:
        return "V"
    else:
        return "N"




# Document class to store email instances easier
class Document:
    text = ""
    word_freqs = {}

    # N or V
    true_class = ""
    learned_class = ""

    # Constructor
    def __init__(self, text, counter, true_class):
        self.text = text
        self.word_freqs = counter
        self.true_class = true_class

    def getText(self):
        return self.text

    def getWordFreqs(self):
        return self.word_freqs

    def getTrueClass(self):
        return self.true_class

    def getLearnedClass(self):
        return self.learned_class

    def setLearnedClass(self, guess):
        self.learned_class = guess


# takes directories holding the data text files as paramters. "N/V" for example
def main(training_dir, test_dir):
    # Set up data sets. Dictionaries containing the text, word frequencies, and true/learned classifications
    makeDataSet(training_set, training_dir,"Verb")
    makeDataSet(test_set, test_dir,"Verb")
    
    
    #count Number of words[value counts]
    print("Count : \t %s" % (len(training_set)))
    #print("Count : \t %s" % (len(test_set)))


    # Train using the training data
    trainMultinomialNB(training_set, prior, conditional_probability)
    #trainMultinomialNB(test_set, prior, conditional_probability)
    # Test using the testing data - unfiltered
    correct_guesses = 0
    for i in test_set:
        test_set[i].setLearnedClass(applyMultinomialNB(test_set[i], prior, conditional_probability))
        if test_set[i].getLearnedClass() == test_set[i].getTrueClass():
            correct_guesses += 1


    print ("Correct guesses:\t %d/%s" % (correct_guesses, len(test_set)))
    print ("Accuracy :\t\t\t %.2f%%" % (100.0 * float(correct_guesses) / float(len(test_set))))
  
if __name__ == '__main__':
    main("train.csv", "test.csv")