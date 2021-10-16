import xml.sax
import csv
import os
import time
import re

FILE_00 =  'en_wiki_13.xml'
FILE_01 = 'en_wiki_11.xml-p6899367p7054859'
FILE_02 = 'conrad_wiki.xml'
FILE_03 = 'war_and_peace_wiki.xml'
PATH = 'datasets/'
MAX_LIST_LENGTH = 100000


# format elapsed time into h:mm:ss
def timeFormater(elapsedTime):
    hour = int(elapsedTime / (60 * 60))
    mins = int((elapsedTime % (60 * 60)) / 60)
    secs = elapsedTime % 60
    return "{}:{:>02}:{:>05.2f}".format(hour, mins, secs)

# class used for parsing XML file page by page
class PageHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        xml.sax.handler.ContentHandler.__init__(self)
        self.buffer = None
        self.values = {}
        self.element = None
        self.pageCounter = 0
        self.pageList = []
        self.contentParser = False
        self.contentHelper = False
        self.pageSaver = False

    # add retrieved content into buffer
    def characters(self, content):
        if self.element == 'title':
            self.buffer.append(content)

        if self.element == 'text' and self.findUsefulData(content):
            self.buffer.append(content)

    # check if starting tag of element whose content we want to retrieve (title or text)
    def startElement(self, element, attrs):
        if element in ('title', 'text'):
            self.element = element
            self.buffer = []

    # check if ending tag of element, save retrieved content
    def endElement(self, element):
        if element == self.element:
            value = ' '.join(self.buffer).replace('\n', ' ')
            self.values[element] = value

        if element == 'page' and self.pageSaver:
            self.pageList.append((self.values['title'], self.values['text']))
            self.pageCounter += 1
            self.pageSaver = False

        if len(self.pageList) > MAX_LIST_LENGTH:
            self.saveListAsCSV()
            self.pageList = []
            print("100k hotovo :)")

    # parse Infoboxes and Navboxes using regular expressions
    def findUsefulData(self, content):
        if re.search('(?i){{Infobox (book|manuscript|short story|writer|film)', content) or re.search('(?i){{Navbox', content):
            self.contentParser = True
            self.pageSaver = True
            return True

        if self.contentParser and re.search('{{', content):
            self.contentHelper = True

        if self.contentHelper and re.search('}}', content):
            self.contentHelper = False
            return True

        if self.contentParser and self.contentHelper == False and re.search('}}', content):
            self.contentParser = False
            self.contentHelper = False
            return True

        if self.contentParser:
             return True

        return False

    # save found data in file in CSV format
    def saveListAsCSV(self):
        header = ['id', 'title', 'text']

        with open(PATH + 'output.csv', 'a', encoding='utf-8') as file:
            writer = csv.writer(file)

            if os.path.getsize(PATH + 'output.csv') == 0:
                writer.writerow(header)

            for index, page in enumerate(self.pageList):
                row = [index, page[0], page[1]]
                writer.writerow(row)


# main
if __name__ == "__main__":
    start = time.time()
    handler = PageHandler()
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)

    with open(PATH + FILE_03, encoding='utf-8') as file:
        for line in file:
            parser.feed(line)

    if len(handler.pageList) > 0:
        handler.saveListAsCSV()

    end = time.time()
    print('Found pages: ', handler.pageCounter)
    print('Elapsed time: ', timeFormater(end - start))