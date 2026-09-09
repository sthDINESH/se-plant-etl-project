from pathlib import Path

from bson.json_util import dumps
import boto3

from env import (
    MONGODB_URI,
    SPECIES_API,
    SPECIES_DETAIL_API,
    CONFIG,
    AWS_PROFILE,
    S3_BUCKET,
    OUTPUT_DIR,
    S3_ETL_JSON_KEY,
)
from mongo_db_driver import get_db, get_collection
import api_requests as api
from clean_data import clean_species_detail
from transform_data import remove_fields, update_missing, fields_to_remove, unknown_detail_fields

# Connect to MongoDB
db = get_db(MONGODB_URI, "plants_101")

# Get relevant collections within the database
metadata = get_collection(db, "_database_metadata")
species_collection = get_collection(db, "species")
species_detail_collection = get_collection(db, "species_detail")
species_search_collection = get_collection(db, "species_search")

if CONFIG['EXTRACT']:
    # Resume extraction from the page after the last successfully saved page.
    # Loop continues until limit for api calls/day is hit

    # Load saved extraction data from metadata in db
    metadata_document = metadata.find_one()
    extracted_page = metadata_document.get("extracted_page", 0)
    extracted_plant_id = metadata_document.get("extracted_plant_id", 0)

    next_page = extracted_page + 1

    error = False

    while not error:
        print(f"Fetching species data from page {next_page}...")
        species = api.get(SPECIES_API, page=next_page)

        # Check if response is an error
        if "error" in species:
            print(
                f"✗ Could not fetch species page {next_page}: "
                f"{species['error']}"
            )
            error = True
            break

        # Check if all pages have been fetched
        # or if there is error from previous fetches
        if next_page >= species.get("last_page", next_page):
            break

        # Check if the data field is empty in response
        plants = species.get("data", [])
        if not plants:
            print(f"✓ No more species found after page {next_page}.")
            break

        # Save the list in mongoDB into species collection
        for plant in plants:
            species_collection.replace_one(
                {"id": plant["id"]},
                plant,
                upsert=True,
            )
        print(
                f"✓ Added {len(plants)} species from page {next_page}."
            )

        # Fetch details for each species and add it to database
        for plant in plants:
            plant_id = plant["id"]

            # Document already available in database, so
            # Skip the loop for plant details already added
            if plant_id <= extracted_plant_id:
                continue

            print(f"Fetching details for {plant['common_name']}")
            species_detail_url = SPECIES_DETAIL_API + str(plant_id)
            species_detail = api.get(species_detail_url)
            if "error" in species_detail:
                print(
                    f"✗ Could not fetch details for {plant['common_name']}: "
                    f"{species_detail['error']}"
                )
                error = True
                break

            # Add species detail to mongodb to create the document
            detail_result = species_detail_collection.insert_one(
                species_detail
            )

            # Add reference to the document in species_collection documents
            species_collection.update_one(
                {"id": plant_id},
                {"$set": {"species_detail_id": detail_result.inserted_id}},
            )
            print(f"✓ Saved details for {plant['common_name']}")
            extracted_plant_id = plant_id

        # Save extraction history to metadata
        metadata.update_one(
            {"_id": metadata_document["_id"]},
            {
                "$set": {
                    "extracted_page": next_page,
                    "extracted_plant_id": extracted_plant_id,
                }
            },
        )
        if error:
            break
        next_page += 1

if CONFIG['TRANSFORM']:
    # Clean the species detail record and store in separate collection
    # for search and downstream processing
    for species_detail in species_detail_collection.find():

        cleaned_species_detail = clean_species_detail(species_detail)

        cleaned_species_detail = remove_fields(
            document=cleaned_species_detail,
            fields=fields_to_remove
        )

        cleaned_species_detail = update_missing(
            document=cleaned_species_detail,
            fields=unknown_detail_fields)

        species_search_collection.replace_one(
            {"_id": species_detail["_id"]},
            cleaned_species_detail,
            upsert=True,
        )
        print(f"✓ Transformed and saved species {species_detail.get('id')}")


if CONFIG['LOAD']:
    print("Dumping MongoDB collections to outputs as json")
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    collection_to_dump = {
        'metadata': metadata.find(),
        'species': species_collection.find(),
        'species_detail': species_detail_collection.find(),
        'species_search': species_search_collection.find(),
    }

    for key in collection_to_dump.keys():
        documents_list = list(collection_to_dump[key])

        with open(f"{OUTPUT_DIR}/{key}.json", "w", encoding="utf-8") as file:
            file.write(dumps(documents_list, indent=4))
            print(f"✓ Saved outputs/{key}.json")

    # Save to S3
    print("Saving species_search to S3")
    # Create client and resource objects
    session = boto3.Session(profile_name=AWS_PROFILE)
    s3_client = session.client("s3")

    s3_client.upload_file(
        Filename=f"{OUTPUT_DIR}/species_search.json",
        Bucket=S3_BUCKET,
        Key=S3_ETL_JSON_KEY,
    )
    print(f"✓ {S3_ETL_JSON_KEY} saved to {S3_BUCKET}")
