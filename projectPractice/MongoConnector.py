import pymongo


def insert_document(collection, data):
    """ Function to insert a document into a collection and
    return the document's id.
    """
    return collection.insert_one(data).inserted_id


client = pymongo.MongoClient('localhost', 27017)
db = client['TestDB']
series_collection = db['test']

test = {
    "test": 1,
}

print(insert_document(series_collection, test))