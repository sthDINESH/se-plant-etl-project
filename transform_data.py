from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client["plants_101"]
species_details = db["species_detail"]


## Update notes ##

# Removed fields with lots of null values
# Changed fields with null to unknown
# Removed duplicate data from species detail
# Converted hardiness min and max values from strings to integers


# Remove unnecessary fields from each document
def remove_fields(collection, fields):
    for plant in collection.find():
        for field in fields:
            plant.pop(field, None)

        collection.replace_one(
            {"_id": plant["_id"]},
            plant
        )

# Change null values to unknown in each document
def update_missing(collection, fields):
    for plant in collection.find():
        for field in fields:
            if plant.get(field) is None:
                plant[field] = "Unknown"

            elif isinstance(plant[field], list) and plant[field] == []:
                plant[field] = ["Unknown"]

        collection.replace_one(
            {"_id": plant["_id"]},
            plant
        )


fields_to_remove = ["hybrid","authority","subspecies", "default_image", "hardiness_location"]
remove_fields(species_details, fields_to_remove)


unknown_detail_fields = ["pruning_count",
                         "attracts",
                         "pest_susceptibility",
                         "maintenance",
                         "family",
                         "other_name",
                         "cultivar",
                         "variety",
                         "soil",
                         "plant_anatomy"
                        ]
update_missing(species_details, unknown_detail_fields)


# Converted hardiness min and max values from strings to integers

for details in species_details.find():
    hardiness = details.get("hardiness")

    if hardiness:
        if hardiness.get("min") != "unknown":
            hardiness["min"] = int(hardiness["min"])

        if hardiness.get("max") != "unknown":
            hardiness["max"] = int(hardiness["max"])

        species_details.replace_one(
            {"_id": details["_id"]},
            details
        )
