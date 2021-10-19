import csv
import re
import unidecode
#from nltk.corpus import stopwords
from math import log


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
    document = re.sub(r'style font style (normal|italic)', '', document)
    document = ' '.join([word for word in document.split() if word not in stopWords])
    #print(document)
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
            if tfIdf <= 0:
                tfIdf = 0

            if term not in tfIdfDict:
                tfIdfDict[term] = {}
                tfIdfDict[term][int(key)] = tfIdf
            elif term in tfIdfDict:
                tfIdfDict[term][int(key)] = tfIdf

    return tfIdfDict


# main
if __name__ == "__main__":

    myStopWords = ['Navbox', 'navbox', 'Infobox', 'infobox', 'getArgs', 'args', 'listclass', '|listclass',
                   'br', 'hlist', 'autocollapse', 'imagesize', 'caption', '|hlist', 'hlist|', 'listclass|']
    #stopWords = stopwords.words("english")
    #stopWords.extend(myList)

    termDict = {}
    tfIdfDict = {}
    numOfDocs = 0

    with open(PATH + FILE_01, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)

        for row in csv_reader:
            document = row['title'] + row['text']
            document = removeStopWord(document, myStopWords)
            termDict = createTermDict(row['id'], document, termDict)
            numOfDocs += 1

    for key in termDict:
        tfIdfDict.update(calculateTfIdf(key, termDict[key], numOfDocs))

    # for key in tfIdfDict:
    #    print(key, tfIdfDict[key])

    # vyhladavanie
    while True:
        query = input("Search for: ")
        query = query.lower()

        avgTfIdf = []
        found = []
        shared = []

        if query == 'q':
            break
        else:
            try:
                for term in query.split():
                    if term.isalnum() and term in tfIdfDict:
                        found.append(tfIdfDict[term])

                for item in found:

                    if len(shared) == 0:
                        shared = list(item.keys())

                    temp = list(item.keys())
                    shared = (list(set(shared).intersection(temp)))

                for doc in shared:
                    temp = 0
                    for item in found:
                        temp += item[doc]
                    avgTfIdf.append((doc, temp/len(shared)))

                avgTfIdf.sort(key=lambda x:x[1])
                for doc in avgTfIdf:
                    print("Check out document", doc[0])

            except:
                print("Nothing relevant found ...")