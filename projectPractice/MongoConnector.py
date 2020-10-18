import pymongo


def insert_document(collection, data):
    """ Function to insert a document into a collection and
    return the document's id.
    """
    return collection.insert_one(data).inserted_id


# Create the client
client = pymongo.MongoClient('localhost', 27017)

# Connect to our database
db = client['SeriesDB']

# Fetch our series collection
series_collection = db['series']
