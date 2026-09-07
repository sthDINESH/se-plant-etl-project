from env import MONGODB_URI, SPECIES_API, SPECIES_DETAIL_API, CONFIG
from mongo_db_driver import get_db, get_collection
import api_requests as api

# Connect to MongoDB
db = get_db(MONGODB_URI, "plants_101")

# Get relevant collections within the database
species_collection = get_collection(db, "species")
species_detail_collection = get_collection(db, "species_detail")

if CONFIG['EXTRACT']:
    # Fetch plant species list from API and add it to database
    species = api.get(SPECIES_API)

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
        exit(1)

    # Fetch details for each species from API and add it to database
    for plant in species_collection.find():
        print(f"Fetching data for {plant['common_name']}")
        species_detail_url = SPECIES_DETAIL_API + str(plant["id"])
        species_detail = api.get(species_detail_url)
        if "error" in species_detail:
            print(
                f"✗ Could not fetch details for {plant['common_name']}: "
                f"{species_detail['error']}"
            )
            continue

        # Add species detail to mongodb to create the document
        species_detail_collection.replace_one(
            {"id": plant["id"]},
            species_detail,
            upsert=True,
        )

        # Get the created document
        detail_document = species_detail_collection.find_one(
            {"id": plant["id"]}
        )

        # Add reference to the document in species_collection documents
        species_collection.update_one(
            {"_id": plant["_id"]},
            {"$set": {"species_detail_id": detail_document["_id"]}},
        )
        print(f"✓ Saved details for {plant['common_name']}")
