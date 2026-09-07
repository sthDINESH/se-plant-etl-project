from pymongo import MongoClient


def get_db(uri, database):
    """
    Connect to MongoDB and return a database object.
    Args:
        uri (str): MongoDB connection URI (e.g., 'mongodb://localhost:27017/')
        database (str): Name of the database to connect to
    Returns:
        Database: MongoDB database object if connection successful,
        exits otherwise
    Raises:
        Prints error messages to console on connection failure
    """
    client = MongoClient(uri)

    try:
        # Verify connection
        client.admin.command('ping')
        print("✓ Successfully connected to MongoDB")

        # MongoDB creates a database only after its first collection write.
        available_dbs = client.list_database_names()

        if database in available_dbs:
            print(f"✓ Database '{database}' found.")
            return client.get_database(database)
        else:
            db = client.get_database(database)
            metadata = db.get_collection("_database_metadata")
            metadata.insert_one({"_id": "initialized"})
            print(f"✓ Database '{database}' created.")
            return db

    except Exception as e:
        print(f"✗ Error connecting to MongoDB: {e}")
        exit(1)


def get_collection(db, collection):
    """
    Get a collection from a MongoDB database.
    Args:
        db: MongoDB database object
        collection (str): Name of the collection to retrieve
    Returns:
        Collection: MongoDB collection object if it exists, exits otherwise
    """
    try:
        # Check if collection exists
        available_collections = db.list_collection_names()
        if collection in available_collections:
            print(f"✓ Collection '{collection}' found.")
            return db.get_collection(collection)
        else:
            created_collection = db.create_collection(collection)
            print(f"✓ Collection '{collection}' created.")
            return created_collection
    except Exception as e:
        print(f"✗ Error retrieving collection: {e}")
        exit(1)
