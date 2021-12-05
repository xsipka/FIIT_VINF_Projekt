import csv
from elasticsearch import Elasticsearch, helpers


IN_PATH = './datasets/'
WIKI_FILE = 'spark_output/wiki_complete.csv'
TEST_FILE = 'output_wiki_11.csv'


LOCALHOST = 'http://localhost'
PORT_NUM = 9200


# creates elastic index if needed
def create_index(elastic, index):
    res = elastic.indices.create(index=index)
    
    # make sure index was created
    if not res['acknowledged']:
        print('Error: Index was not created ...')
        print(res)
        exit(1)
    else:
        print('OK: Index was successfully created')



# process of indexing every document in csv file
def index_data(elastic, index):
    print('OK: Indexing data started')

    with open(IN_PATH + TEST_FILE) as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            row['title'] = row['title'].replace(':', ' ')
            text = {'text': row['title'] + ' | ' + row['text']}
            elastic.index(index=index, id=row['id'], document=text)

    print('OK: Indexing data finished')



# search in indexed data
def search(elastic, index, query):
    body = {"multi_match": {
                     "query": query,
                     "fields": ["text"]
                 }
             }

    resp = elastic.search(index=index, query=body)
    print(resp)
    return resp



# process found documents and prints them in a nice way
def process_resluts(results):
    pass



# main
if __name__ == "__main__":
    elastic = Elasticsearch(HOST=LOCALHOST, PORT=PORT_NUM)
    elastic = Elasticsearch()

    index = "test_index"
    #elastic.indices.delete(index=index)
    
    # creation of index
    if not elastic.indices.exists(index=index):
        create_index(elastic, index)
        index_data(elastic, index)

    # searching stuff
    while True:
        query = input("Search for: ")

        if query == 'q':
            print("Exiting program ...")
            break
        
        elif query:
            result = search(elastic, index, query)