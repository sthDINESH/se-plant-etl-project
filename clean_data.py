import json
import re
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode


# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------

SPECIES_INPUT = "plants_101.species.json"
DETAIL_INPUT = "plants_101.species_detail.json"

SPECIES_OUTPUT = "plants_101.species_clean.json"
DETAIL_OUTPUT = "plants_101.species_detail_clean.json"
SEARCH_OUTPUT = "plants_101.semantic_search.json"


# --------------------------------------------------
# FIELDS THAT CONTAIN API SUBSCRIPTION MESSAGES
# --------------------------------------------------

SUBSCRIPTION_FIELDS = {
    "other_images",
    "xWateringQuality",
    "xWateringPeriod",
    "xWateringAvgVolumeRequirement",
    "xWateringDepthRequirement",
    "xWateringBasedTemperature",
    "xWateringPhLevel",
    "xSunlightDuration",
    "xTemperatureTolence",
    "xPlantSpacingRequirement",
}


# --------------------------------------------------
# CONTROLLED CATEGORICAL FIELDS
# These will be standardised to lowercase
# --------------------------------------------------

LOWERCASE_FIELDS = {
    "type",
    "cycle",
    "watering",
    "growth_rate",
    "maintenance",
    "care_level",
}


LOWERCASE_LIST_FIELDS = {
    "sunlight",
    "soil",
    "pest_susceptibility",
}


# --------------------------------------------------
# BASIC STRING CLEANING
# --------------------------------------------------

def clean_string(value):
    """
    Remove leading/trailing whitespace and collapse
    repeated spaces.

    Empty strings become None.
    """

    if not isinstance(value, str):
        return value

    value = value.strip()

    # Collapse repeated whitespace
    value = re.sub(r"\s+", " ", value)

    if value == "":
        return None

    return value


# --------------------------------------------------
# REMOVE DUPLICATES WHILE PRESERVING ORDER
# --------------------------------------------------

def remove_duplicates(values):
    cleaned = []
    seen = set()

    for value in values:
        if isinstance(value, str):
            comparison_value = value.lower()
        else:
            comparison_value = str(value)

        if comparison_value not in seen:
            cleaned.append(value)
            seen.add(comparison_value)

    return cleaned


# --------------------------------------------------
# CLEAN LIST
# --------------------------------------------------

def clean_list(values, lowercase=False):
    if not isinstance(values, list):
        return values

    cleaned = []

    for value in values:

        if isinstance(value, str):
            value = clean_string(value)

            if value is None:
                continue

            if lowercase:
                value = value.lower()

        elif isinstance(value, dict):
            value = clean_nested_dict(value)

        cleaned.append(value)

    return remove_duplicates(cleaned)


# --------------------------------------------------
# CLEAN NESTED DICTIONARIES
# --------------------------------------------------

def clean_nested_dict(data):
    if not isinstance(data, dict):
        return data

    cleaned = {}

    for key, value in data.items():

        if isinstance(value, str):
            cleaned[key] = clean_string(value)

        elif isinstance(value, list):
            cleaned[key] = clean_list(value)

        elif isinstance(value, dict):
            cleaned[key] = clean_nested_dict(value)

        else:
            cleaned[key] = value

    return cleaned


# --------------------------------------------------
# SAFE NUMBER CONVERSION
# --------------------------------------------------

def to_number(value):
    """
    Convert numeric strings into int or float.

    Invalid/missing values return None.
    """

    if value is None:
        return None

    if isinstance(value, (int, float)):
        return value

    if isinstance(value, str):
        value = value.strip()

        try:
            number = float(value)

            if number.is_integer():
                return int(number)

            return number

        except ValueError:
            return None

    return None


# --------------------------------------------------
# SANITISE URL
# --------------------------------------------------

def sanitise_url(url):
    """
    Remove API keys and signed URL query parameters.

    The URL itself is kept as metadata but is not
    included in semantic_text.
    """

    if not isinstance(url, str):
        return url

    url = clean_string(url)

    if not url:
        return None

    try:
        parts = urlsplit(url)

        query_params = parse_qsl(
            parts.query,
            keep_blank_values=True
        )

        safe_params = []

        for key, value in query_params:

            key_lower = key.lower()

            # Remove API credentials
            if key_lower in {
                "key",
                "api_key",
                "apikey",
            }:
                continue

            # Remove AWS signed URL parameters
            if key_lower.startswith("x-amz-"):
                continue

            safe_params.append((key, value))

        safe_query = urlencode(safe_params)

        return urlunsplit(
            (
                parts.scheme,
                parts.netloc,
                parts.path,
                safe_query,
                parts.fragment,
            )
        )

    except ValueError:
        return None


# --------------------------------------------------
# CLEAN IMAGE OBJECT
# --------------------------------------------------

def clean_default_image(image):
    if not isinstance(image, dict):
        return image

    cleaned = {}

    for key, value in image.items():

        if key.endswith("_url") or key == "thumbnail":
            cleaned[key] = sanitise_url(value)

        elif isinstance(value, str):
            cleaned[key] = clean_string(value)

        else:
            cleaned[key] = value

    return cleaned


# --------------------------------------------------
# CLEAN HARDINESS
# --------------------------------------------------

def clean_hardiness(hardiness):
    if not isinstance(hardiness, dict):
        return hardiness

    return {
        "min": to_number(hardiness.get("min")),
        "max": to_number(hardiness.get("max")),
    }


# --------------------------------------------------
# CLEAN WATERING RANGE
# --------------------------------------------------

def clean_watering_benchmark(benchmark):
    """
    Example:

    Raw:
        value = '"7-10"'
        unit = 'days'

    Clean:
        min_days = 7
        max_days = 10
    """

    if not isinstance(benchmark, dict):
        return benchmark

    raw_value = benchmark.get("value")
    unit = clean_string(benchmark.get("unit"))

    if raw_value is None:
        return benchmark

    value = clean_string(str(raw_value))

    if value is None:
        return benchmark

    # Remove extra quotation marks
    value = value.replace('"', "").replace("'", "")

    # Match range such as 7-10
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)",
        value
    )

    if match:
        minimum = to_number(match.group(1))
        maximum = to_number(match.group(2))

        if unit and unit.lower() == "days":
            return {
                "min_days": minimum,
                "max_days": maximum,
            }

        return {
            "min_value": minimum,
            "max_value": maximum,
            "unit": unit,
        }

    # Match a single number
    single_number = to_number(value)

    if single_number is not None:

        if unit and unit.lower() == "days":
            return {
                "min_days": single_number,
                "max_days": single_number,
            }

        return {
            "min_value": single_number,
            "max_value": single_number,
            "unit": unit,
        }

    # If parsing fails, preserve cleaned value
    return {
        "value": value,
        "unit": unit,
    }


# --------------------------------------------------
# CLEAN DIMENSIONS
# --------------------------------------------------

def clean_dimensions(dimensions):
    if not isinstance(dimensions, list):
        return dimensions

    cleaned = []

    for dimension in dimensions:

        if not isinstance(dimension, dict):
            continue

        cleaned_dimension = {
            "type": clean_string(
                dimension.get("type")
            ),
            "min_value": to_number(
                dimension.get("min_value")
            ),
            "max_value": to_number(
                dimension.get("max_value")
            ),
            "unit": clean_string(
                dimension.get("unit")
            ),
        }

        cleaned.append(cleaned_dimension)

    return cleaned


# --------------------------------------------------
# CLEAN PLANT ANATOMY
# --------------------------------------------------

def clean_plant_anatomy(anatomy):
    if not isinstance(anatomy, list):
        return anatomy

    cleaned = []

    for item in anatomy:

        if not isinstance(item, dict):
            continue

        clean_item = {}

        for key, value in item.items():

            if key == "part" and isinstance(value, str):
                clean_item[key] = clean_string(value).lower()

            elif key == "color":
                clean_item[key] = clean_list(
                    value,
                    lowercase=True
                )

            else:
                clean_item[key] = value

        cleaned.append(clean_item)

    return cleaned


# --------------------------------------------------
# CLEAN SPECIES
# --------------------------------------------------

def clean_species(plant):
    cleaned = {}

    for key, value in plant.items():

        # Keep MongoDB _id and species_detail_id.
        # They are useful metadata for linking records.

        if key == "default_image":
            cleaned[key] = clean_default_image(value)

        elif isinstance(value, str):
            cleaned[key] = clean_string(value)

        elif isinstance(value, list):
            cleaned[key] = clean_list(value)

        elif isinstance(value, dict):
            cleaned[key] = clean_nested_dict(value)

        else:
            cleaned[key] = value

    # ID should be numeric
    cleaned["id"] = to_number(cleaned.get("id"))

    return cleaned


# --------------------------------------------------
# CLEAN SPECIES DETAIL
# --------------------------------------------------

def clean_species_detail(plant):
    cleaned = {}

    for key, value in plant.items():

        # Remove subscription-only fields
        if key in SUBSCRIPTION_FIELDS:
            continue

        # Remove HTML iframe
        if key == "hardiness_location":
            if isinstance(value, dict):

                cleaned[key] = {
                    "full_url": sanitise_url(
                        value.get("full_url")
                    )
                }

            continue

        # API URL
        if key == "care_guides":
            cleaned[key] = sanitise_url(value)
            continue

        # Images
        if key == "default_image":
            cleaned[key] = clean_default_image(value)
            continue

        # Controlled category
        if key in LOWERCASE_FIELDS:

            if isinstance(value, str):
                value = clean_string(value)

                if value:
                    value = value.lower()

            cleaned[key] = value
            continue

        # Controlled category lists
        if key in LOWERCASE_LIST_FIELDS:

            cleaned[key] = clean_list(
                value,
                lowercase=True
            )

            continue

        # Hardiness
        if key == "hardiness":
            cleaned[key] = clean_hardiness(value)
            continue

        # Watering benchmark
        if key == "watering_general_benchmark":

            cleaned[key] = clean_watering_benchmark(
                value
            )

            continue

        # Dimensions
        if key == "dimensions":

            cleaned[key] = clean_dimensions(value)
            continue

        # Plant anatomy
        if key == "plant_anatomy":

            cleaned[key] = clean_plant_anatomy(value)
            continue

        # General string
        if isinstance(value, str):
            cleaned[key] = clean_string(value)

        # General list
        elif isinstance(value, list):
            cleaned[key] = clean_list(value)

        # Nested document
        elif isinstance(value, dict):
            cleaned[key] = clean_nested_dict(value)

        else:
            cleaned[key] = value

    cleaned["id"] = to_number(cleaned.get("id"))

    return cleaned


# --------------------------------------------------
# SEMANTIC TEXT HELPERS
# --------------------------------------------------

def list_to_text(value):
    if not value:
        return None

    if isinstance(value, list):

        text_values = []

        for item in value:

            if isinstance(item, str):
                text_values.append(item)

        if text_values:
            return "; ".join(text_values)

    return None


def add_semantic_part(parts, label, value):
    if value is None:
        return

    if isinstance(value, str):
        value = value.strip()

        if value:
            parts.append(f"{label}: {value}.")

    elif isinstance(value, list):

        text = list_to_text(value)

        if text:
            parts.append(f"{label}: {text}.")

    elif isinstance(value, bool):

        if value:
            parts.append(f"{label}: yes.")


# --------------------------------------------------
# BUILD SEMANTIC TEXT
# --------------------------------------------------

def build_semantic_text(species, detail):
    """
    Create one deterministic text representation
    per plant for future embedding generation.
    """

    parts = []

    add_semantic_part(
        parts,
        "Name",
        species.get("common_name")
    )

    add_semantic_part(
        parts,
        "Scientific name",
        species.get("scientific_name")
    )

    add_semantic_part(
        parts,
        "Other names",
        species.get("other_name")
    )

    add_semantic_part(
        parts,
        "Family",
        species.get("family")
    )

    add_semantic_part(
        parts,
        "Genus",
        species.get("genus")
    )

    add_semantic_part(
        parts,
        "Plant type",
        detail.get("type")
    )

    add_semantic_part(
        parts,
        "Life cycle",
        detail.get("cycle")
    )

    add_semantic_part(
        parts,
        "Origin",
        detail.get("origin")
    )

    add_semantic_part(
        parts,
        "Watering",
        detail.get("watering")
    )

    add_semantic_part(
        parts,
        "Sunlight",
        detail.get("sunlight")
    )

    add_semantic_part(
        parts,
        "Soil",
        detail.get("soil")
    )

    add_semantic_part(
        parts,
        "Growth rate",
        detail.get("growth_rate")
    )

    add_semantic_part(
        parts,
        "Maintenance",
        detail.get("maintenance")
    )

    add_semantic_part(
        parts,
        "Care level",
        detail.get("care_level")
    )

    add_semantic_part(
        parts,
        "Propagation",
        detail.get("propagation")
    )

    add_semantic_part(
        parts,
        "Attracts",
        detail.get("attracts")
    )

    add_semantic_part(
        parts,
        "Pest susceptibility",
        detail.get("pest_susceptibility")
    )

    add_semantic_part(
        parts,
        "Flowering season",
        detail.get("flowering_season")
    )

    # Add useful boolean traits only when True
    trait_fields = {
        "drought_tolerant": "Drought tolerant",
        "salt_tolerant": "Salt tolerant",
        "thorny": "Thorny",
        "invasive": "Invasive",
        "tropical": "Tropical",
        "indoor": "Suitable for indoor growing",
        "flowers": "Produces flowers",
        "cones": "Produces cones",
        "fruits": "Produces fruit",
        "edible_fruit": "Edible fruit",
        "edible_leaf": "Edible leaves",
        "medicinal": "Medicinal",
        "poisonous_to_humans": "Poisonous to humans",
        "poisonous_to_pets": "Poisonous to pets",
    }

    for field, description in trait_fields.items():

        if detail.get(field) is True:
            parts.append(f"Trait: {description}.")

    # Description is especially valuable for semantic search
    description = detail.get("description")

    if description:
        parts.append(
            f"Description: {description}"
        )

    return " ".join(parts)


# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

def check_unique_ids(records, dataset_name):
    ids = [
        record.get("id")
        for record in records
    ]

    duplicates = {
        plant_id
        for plant_id in ids
        if ids.count(plant_id) > 1
    }

    if duplicates:
        print(
            f"WARNING: Duplicate IDs in "
            f"{dataset_name}: {duplicates}"
        )
    else:
        print(
            f"✓ No duplicate IDs in {dataset_name}"
        )


def validate_cleaning(species_clean, detail_clean, semantic_records):
    print("\nValidation checks:")

    # 1. Record counts
    print(
        "Species records:",
        len(species_clean)
    )

    print(
        "Detail records:",
        len(detail_clean)
    )

    print(
        "Semantic search records:",
        len(semantic_records)
    )

    # 2. Check for subscription messages
    subscription_text_found = False

    for plant in detail_clean:
        plant_text = json.dumps(plant)

        if "Upgrade Plan To Supreme" in plant_text:
            subscription_text_found = True
            break

    print(
        "Subscription messages removed:",
        not subscription_text_found
    )

    # 3. Check for API key parameters
    api_key_found = False

    for plant in detail_clean:
        plant_text = json.dumps(plant)

        if "key=" in plant_text:
            api_key_found = True
            break

    print(
        "API keys removed from cleaned detail:",
        not api_key_found
    )

    # 4. Check semantic text exists
    missing_semantic_text = 0

    for plant in semantic_records:
        if not plant.get("semantic_text"):
            missing_semantic_text += 1

    print(
        "Records missing semantic_text:",
        missing_semantic_text
    )


if __name__ == "__main__":
    # --------------------------------------------------
    # LOAD RAW JSON
    # --------------------------------------------------

    with open(
        SPECIES_INPUT,
        "r",
        encoding="utf-8"
    ) as file:

        species_raw = json.load(file)


    with open(
        DETAIL_INPUT,
        "r",
        encoding="utf-8"
    ) as file:

        detail_raw = json.load(file)


    print(
        f"Loaded {len(species_raw)} species records."
    )

    print(
        f"Loaded {len(detail_raw)} detail records."
    )


    # --------------------------------------------------
    # TRANSFORM
    # --------------------------------------------------

    species_clean = [
        clean_species(plant)
        for plant in species_raw
    ]


    detail_clean = [
        clean_species_detail(plant)
        for plant in detail_raw
    ]


    # --------------------------------------------------
    # VALIDATE IDS
    # --------------------------------------------------

    check_unique_ids(
        species_clean,
        "species"
    )

    check_unique_ids(
        detail_clean,
        "species_detail"
    )


    species_ids = {
        plant["id"]
        for plant in species_clean
    }

    detail_ids = {
        plant["id"]
        for plant in detail_clean
    }


    missing_details = species_ids - detail_ids

    if missing_details:
        print(
            f"WARNING: {len(missing_details)} species "
            "do not have detail records."
        )
    else:
        print(
            "✓ Every species has a matching detail record."
        )


    # --------------------------------------------------
    # CREATE LOOKUP BY PLANT ID
    # --------------------------------------------------

    detail_by_id = {
        plant["id"]: plant
        for plant in detail_clean
    }


    # --------------------------------------------------
    # BUILD SEARCH-READY RECORDS
    # --------------------------------------------------

    semantic_search_records = []


    for plant in species_clean:

        plant_id = plant["id"]

        detail = detail_by_id.get(
            plant_id,
            {}
        )

        semantic_text = build_semantic_text(
            plant,
            detail
        )

        search_record = {
            "id": plant_id,
            "common_name": plant.get(
                "common_name"
            ),
            "scientific_name": plant.get(
                "scientific_name"
            ),
            "semantic_text": semantic_text,

            # Structured metadata for later filtering
            "metadata": {
                "family": plant.get("family"),
                "genus": plant.get("genus"),
                "type": detail.get("type"),
                "cycle": detail.get("cycle"),
                "watering": detail.get("watering"),
                "sunlight": detail.get("sunlight"),
                "soil": detail.get("soil"),
                "growth_rate": detail.get(
                    "growth_rate"
                ),
                "care_level": detail.get(
                    "care_level"
                ),
                "hardiness": detail.get(
                    "hardiness"
                ),
                "drought_tolerant": detail.get(
                    "drought_tolerant"
                ),
                "indoor": detail.get("indoor"),
                "medicinal": detail.get(
                    "medicinal"
                ),
                "poisonous_to_humans": detail.get(
                    "poisonous_to_humans"
                ),
                "poisonous_to_pets": detail.get(
                    "poisonous_to_pets"
                ),
            }
        }

        semantic_search_records.append(
            search_record
        )


    # --------------------------------------------------
    # SAVE CLEANED FILES
    # --------------------------------------------------

    with open(
        SPECIES_OUTPUT,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            species_clean,
            file,
            indent=2,
            ensure_ascii=False
        )


    with open(
        DETAIL_OUTPUT,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            detail_clean,
            file,
            indent=2,
            ensure_ascii=False
        )


    with open(
        SEARCH_OUTPUT,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            semantic_search_records,
            file,
            indent=2,
            ensure_ascii=False
        )



    validate_cleaning(
        species_clean,
        detail_clean,
        semantic_search_records
    )


    print()
    print("Cleaning complete.")

    print(
        f"✓ Created {SPECIES_OUTPUT}"
    )

    print(
        f"✓ Created {DETAIL_OUTPUT}"
    )

    print(
        f"✓ Created {SEARCH_OUTPUT}"
    )
