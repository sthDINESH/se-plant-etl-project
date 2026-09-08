from env import MONGODB_URI, SPECIES_API, SPECIES_DETAIL_API, CONFIG
from mongo_db_driver import get_db, get_collection
import api_requests as api


# Connect to MongoDB
db = get_db(MONGODB_URI, "plants_101")

# Get collections
species_collection = get_collection(db, "species")
species_detail_collection = get_collection(db, "species_detail")


if CONFIG["EXTRACT"]:

    # -------------------------
    # Get species from API
    # -------------------------

    all_species = []

    for page in range(1, 4):

        species = api.get(
            SPECIES_API,
            params={"page": page}
        )

        if "data" not in species:
            print(f"Could not fetch page {page}: {species}")
            exit(1)

        all_species.extend(species["data"])

    print(f"Fetched {len(all_species)} species")


    # -------------------------
    # Add species to MongoDB
    # -------------------------

    for plant in all_species:

        species_collection.replace_one(
            {"id": plant["id"]},
            plant,
            upsert=True
        )

    print(f"Added {len(all_species)} species to MongoDB")


    # -------------------------
    # Get details for species that don't have them
    # -------------------------

    for plant in all_species:

        saved_plant = species_collection.find_one(
            {"id": plant["id"]}
        )

        # Skip species that already have details
        if saved_plant.get("species_detail_id"):
            continue

        print(f"Fetching data for {plant['common_name']}")

        species_detail_url = SPECIES_DETAIL_API + str(plant["id"])

        species_detail = api.get(species_detail_url)

        if "error" in species_detail:
            print(
                f"Could not fetch details for "
                f"{plant['common_name']}: {species_detail['error']}"
            )
            continue


        # -------------------------
        # Save details to MongoDB
        # -------------------------

        species_detail_collection.replace_one(
            {"id": plant["id"]},
            species_detail,
            upsert=True
        )


        # Get the detail document so we can get its MongoDB _id
        detail_document = species_detail_collection.find_one(
            {"id": plant["id"]}
        )


        # -------------------------
        # Create reference
        # -------------------------

        species_collection.update_one(
            {"_id": saved_plant["_id"]},
            {"$set": {"species_detail_id": detail_document["_id"]}}
        )

        print(f"Saved details for {plant['common_name']}")