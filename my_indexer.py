import csv
import re
import unidecode
from nltk.corpus import stopwords
from math import log
from nltk.stem import PorterStemmer
from nltk.tokenize import TweetTokenizer
import string

FILE_00 =  'output_wiki_13.csv'
FILE_01 = 'output_wiki_11.csv'
FILE_02 = 'output_wiki_conrad.csv'
FILE_03 = 'output_wiki_war_and_peace.csv'
PATH = 'datasets/'
BASE = 10


# removes stop words and most of nonalphanumeric characters
def removeStopWord(document, stopWords):
    document = unidecode.unidecode(document)
    document = document.lower()
    document = re.sub(r'[^a-z0-9|()*]+', ' ', document)
    document = ' '.join([word for word in document.split() if word not in stopWords])
    return document


# creates dictionary of terms and list of documents where they occur
def createTermDict(id, document, termDict):

    for index, word in enumerate(document.split()):
        if word.isalnum() and word not in termDict:
            termDict[word] = {}
            termDict[word]['docFreq'] = 1
            termDict[word][id] = {}
            termDict[word][id]['posList'] = []
            termDict[word][id]['posList'].append(index)
            termDict[word][id]['termFreq'] = len(termDict[word][id]['posList'])

        elif word.isalnum() and word in termDict:
            if id not in termDict[word]:
                termDict[word]['docFreq'] += 1
                termDict[word][id] = {}
                termDict[word][id]['posList'] = []
                termDict[word][id]['posList'].append(index)
                termDict[word][id]['termFreq'] = len(termDict[word][id]['posList'])

            elif id in termDict[word]:
                termDict[word][id]['posList'].append(index)
                termDict[word][id]['termFreq'] = len(termDict[word][id]['posList'])

    return termDict


# calculates tf-idf for every term
def calculateTfIdf(term, termDict, numOfDocs):

    docFreq = termDict['docFreq']
    idf = log(numOfDocs/docFreq, BASE)
    tfIdfDict = {}

    for key in termDict:
        if isinstance(termDict[key], int) == False:
            tf = termDict[key]['termFreq']
            tfIdf = tf * idf
            tfIdfDict[term, key] = tfIdf

    return tfIdfDict


# main
if __name__ == "__main__":

    myList = ['Navbox', 'navbox', 'Infobox', 'infobox', 'getArgs','args']
    stopWords = stopwords.words("english")
    stopWords.extend(myList)

    termDict = {}
    tfIdfDict = {}
    numOfDocs = 0

    with open(PATH + FILE_02, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)

        for row in csv_reader:
            document = row['title'] + row['text']
            document = removeStopWord(document, stopWords)
            termDict = createTermDict(row['id'], document, termDict)
            numOfDocs += 1

    for key in termDict:
        tfIdfDict.update(calculateTfIdf(key, termDict[key], numOfDocs))