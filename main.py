import api_requests as api
import pprint as pp
from env import SPECIES_API
from mongo_db_driver import get_db, get_collection


MONGODB_URI = 'mongodb://localhost:27017/'
# Connect to database
db = get_db(MONGODB_URI, "plants_101")
species_collection = get_collection(db, "species")

# Fetch the list first so the detail endpoint receives a numeric species ID.
species = api.get(SPECIES_API)
print("SPECIES DICT")
pp.pprint(species)

if "data" in species:
    for plant in species["data"]:
        species_collection.replace_one(
            {"id": plant["id"]},
            plant,
            upsert=True,
        )
    print(f"✓ Added {len(species['data'])} species to the collection.")
else:
    print(f"✗ Could not add species data: {species}")






