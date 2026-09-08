# Plant Dataset Cleaning and Semantic Search Preparation

## Overview

The approach was to keep the original API data unchanged, create cleaned versions of both datasets, and then create a separate dataset specifically prepared for downstream semantic search.

The overall pipeline is:

```text
Raw API datasets
        ↓
Cleaning and normalization
        ↓
Cleaned datasets
        ↓
Semantic-search preparation
        ↓
Embeddings
        ↓
Vector / semantic search
```

The main cleaning principle was:

> Preserve meaningful plant information, normalize inconsistent values, remove irrelevant noise, protect credentials, and retain structured data for filtering.

---

# 1. Raw Datasets

The original files are:

```text
plants_101.species.json
plants_101.species_detail.json
```

These files should remain unchanged.

This gives us a copy of the original data returned by the API in case:

- cleaning needs to be repeated
- a transformation is incorrect
- additional fields are needed later
- the source data needs to be compared with the cleaned data

---

# 2. `plants_101.species_clean.json`

## Purpose

This is the cleaned version of the basic species dataset.

The species dataset mainly answers:

> Who is the plant?

It contains identity and taxonomy information such as:

```text
id
common_name
scientific_name
other_name
family
genus
species_epithet
cultivar
species_detail_id
default_image
```

---

## Cleaning Approach

### Whitespace Cleaning

Leading and trailing whitespace was removed from string values.

Example:

```text
" Silver Fir "
```

becomes:

```text
"Silver Fir"
```

### Rationale

Whitespace differences can cause values that mean the same thing to be treated as different values.

---

## Duplicate List Values

Duplicate values in arrays were removed where appropriate.

Example:

```json
[
    "Silver Fir",
    "Silver Fir"
]
```

becomes:

```json
[
    "Silver Fir"
]
```

### Rationale

Repeated values do not add useful information and could unnecessarily influence downstream semantic processing.

---

## Numeric IDs

Plant IDs were preserved as numbers.

Example:

```json
"id": 3
```

rather than:

```json
"id": "3"
```

### Rationale

Numeric IDs are easier to validate, match and filter.

---

## Taxonomy Preserved

Fields such as:

```text
common_name
scientific_name
family
genus
other_name
```

were preserved.

### Rationale

These fields provide useful semantic information and allow searches such as:

```text
silver fir

Abies species

plants from the Pinaceae family
```

---

## MongoDB Reference Preserved

The field:

```text
species_detail_id
```

was kept.

It maintains the relationship between the species document and its detailed document.

Conceptually:

```text
species_clean
      |
      | species_detail_id
      ↓
species_detail_clean
```

The reference is useful for database relationships but should not later be included in embedding text.

---

# 3. `plants_101.species_detail_clean.json`

## Purpose

This file contains the cleaned detailed plant information.

The detailed dataset mainly answers:

> What is the plant like?

It contains information such as:

```text
origin
type
dimensions
cycle
hardiness
watering
sunlight
soil
growth_rate
maintenance
care_level
propagation
pest_susceptibility
drought_tolerant
indoor
medicinal
description
```

This dataset contains much of the information that will be useful for semantic search.

---

# 4. Whitespace Normalization

Some values contained unnecessary spaces.

For example:

```text
" Rocky "
" gravelly "
" dry"
" Well-drained"
```

These were cleaned to:

```text
"rocky"
"gravelly"
"dry"
"well-drained"
```

## Rationale

Without cleaning:

```text
"Rocky"
```

and:

```text
" Rocky "
```

could be treated as different values.

Normalizing whitespace improves:

- filtering
- consistency
- semantic text generation
- data quality

---

# 5. Category Normalization

Controlled categorical fields were standardized.

For example:

```text
"Full sun"
```

was standardized to:

```text
"full sun"
```

Other examples include:

```text
"Average" → "average"

"Moderate" → "moderate"

"Frequent" → "frequent"
```

Fields that can benefit from this include:

```text
sunlight
watering
soil
growth_rate
maintenance
care_level
pest_susceptibility
```

## Rationale

The following:

```text
Full sun
full sun
FULL SUN
```

all represent the same category.

Standardizing them makes later filtering easier.

Instead of searching for several variations:

```python
{
    "sunlight": {
        "$in": [
            "Full sun",
            "full sun",
            "FULL SUN"
        ]
    }
}
```

the data can consistently use:

```python
{
    "sunlight": "full sun"
}
```

---

# 6. Numeric Normalization

Some numeric information was stored as text.

For example:

```json
{
    "hardiness": {
        "min": "3",
        "max": "3"
    }
}
```

was converted to:

```json
{
    "hardiness": {
        "min": 3,
        "max": 3
    }
}
```

## Rationale

Numbers should be stored as numbers when they represent measurable values.

This makes comparisons possible.

For example:

```python
{
    "hardiness.min": {
        "$lte": 5
    }
}
```

This could later be used to find plants suitable for particular hardiness conditions.

---

# 7. Watering Range Normalization

The raw data contained watering intervals in a format such as:

```json
{
    "value": "\"7-10\"",
    "unit": "days"
}
```

This was converted to a more structured format:

```json
{
    "min_days": 7,
    "max_days": 10
}
```

## Rationale

The original value is useful for humans but difficult to analyse.

The cleaned structure allows later queries such as:

```text
plants requiring watering every 7 days or less
```

using actual numeric values.

---

# 8. Subscription Messages Removed

Some API fields did not contain plant information.

Instead, they contained messages similar to:

```text
Upgrade Plan To Supreme For Access...
```

Examples included fields such as:

```text
xWateringQuality
xWateringPeriod
xWateringAvgVolumeRequirement
xWateringDepthRequirement
xWateringBasedTemperature
xWateringPhLevel
xSunlightDuration
xTemperatureTolence
xPlantSpacingRequirement
```

These fields were removed from the cleaned dataset.

## Rationale

These values describe the API subscription plan rather than the plant.

If this text were included in embeddings, concepts such as:

```text
upgrade
subscription
supreme
access
```

could influence semantic similarity.

This would add noise to the search system.

---

# 9. API Credentials and URLs

API keys and unnecessary signed URL parameters were removed or sanitized.

Long URLs and HTML iframe content were also excluded from semantic-search text.

## Rationale

These values:

```text
API keys
MongoDB ObjectIds
signed image URLs
HTML
iframe code
```

do not describe the plant.

They should not influence semantic similarity.

Removing credentials also reduces the risk of exposing secrets when the cleaned data is committed to Git.

---

# 10. Missing Values

Real missing values were kept as:

```json
null
```

They were not automatically changed to:

```text
"unknown"
"N/A"
0
""
```

## Rationale

A missing value means:

```text
No information is available
```

It does not mean:

```text
The value is zero
```

or:

```text
The actual value is "unknown"
```

Keeping `null` preserves the meaning of missing data.

When semantic text is generated, fields containing `null` are simply skipped.

---

# 11. Why Keep Two Cleaned Datasets?

The two original collections perform different roles.

```text
species_clean
= plant identity and taxonomy

species_detail_clean
= detailed plant characteristics
```

Keeping them separate preserves the MongoDB data model and the referencing relationship already created by the extraction process.

The data does not need to be permanently merged just to support semantic search.

Instead, the records can be logically combined using:

```text
species.id = species_detail.id
```

when preparing the semantic-search dataset.

---

# 12. `plants_101.semantic_search.json`

## Purpose

This file is different from the two cleaned datasets.

It is a derived dataset specifically prepared for search.

The process is:

```text
species_clean
       +
species_detail_clean
       ↓
match using plant ID
       ↓
semantic_search.json
```

Each plant has one search-preparation document.

---

# 13. `semantic_text`

The most important field in the search-preparation file is:

```text
semantic_text
```

This combines useful plant information into readable natural language.

Example:

```text
Name: White Fir.
Scientific name: Abies concolor.
Family: Pinaceae.
Plant type: tree.
Origin: Western United States; Mexico.
Sunlight: full sun; part shade.
Soil: acidic; rocky; gravelly; dry; well-drained.
Watering: average.
Growth rate: low.
Care level: moderate.
Trait: drought tolerant.
Trait: medicinal.
Description: ...
```

## Rationale

Embedding models work primarily with natural-language meaning.

The `semantic_text` field provides one consistent representation containing the most useful information about the plant.

The future process will be:

```text
semantic_text
      ↓
embedding model
      ↓
vector
```

A user could then search:

```text
evergreen tree that grows well in dry rocky soil
```

The search system does not have to find those exact words.

Instead, it compares semantic meaning.

---

# 14. Information Excluded from `semantic_text`

Not every database field should be sent to an embedding model.

The following are useful for the application or database but not for semantic meaning:

```text
MongoDB _id
species_detail_id
API URLs
image URLs
signed URL parameters
license URLs
iframe HTML
API credentials
subscription messages
```

For example:

```text
ObjectId("6a9...")
```

does not provide useful information about the characteristics of a plant.

Including this information would add unnecessary noise.

---

# 15. Metadata

The semantic-search dataset also contains:

```text
metadata
```

Example:

```json
{
    "metadata": {
        "family": "Pinaceae",
        "genus": "Abies",
        "type": "tree",
        "watering": "average",
        "sunlight": [
            "full sun",
            "part shade"
        ],
        "soil": [
            "acidic",
            "rocky",
            "dry"
        ],
        "hardiness": {
            "min": 3,
            "max": 3
        },
        "drought_tolerant": true,
        "indoor": false
    }
}
```

## Rationale

Metadata is useful for exact filtering rather than semantic similarity.

This allows the search system to use both:

```text
meaning
```

and:

```text
exact conditions
```

---

# 16. Semantic Search

The `semantic_text` field will later support queries such as:

```text
low maintenance evergreen for dry conditions
```

The query will eventually be converted into an embedding:

```text
User query
     ↓
Embedding model
     ↓
Query vector
     ↓
Compare against plant vectors
     ↓
Most semantically similar plants
```

---

# 17. Metadata Filtering

Metadata can provide exact constraints.

For example:

```text
drought_tolerant = true
```

or:

```text
indoor = false
```

or:

```text
hardiness.min <= 5
```

This is different from semantic similarity because these are exact values.

---

# 18. Hybrid Search

A future search system can combine semantic similarity and metadata filtering.

For example, the user searches:

```text
low maintenance evergreen for a dry sunny garden
```

The semantic component searches for concepts such as:

```text
low maintenance
evergreen
dry conditions
sunny garden
```

Metadata could then filter results using:

```text
drought_tolerant = true

sunlight contains "full sun"

indoor = false
```

The overall approach becomes:

```text
Semantic similarity
        +
Metadata filtering
        =
Hybrid search
```

This provides more accurate search results than relying only on keyword matching.

---

# 19. Purpose of Each File

| File | Purpose |
|---|---|
| `plants_101.species.json` | Original basic API data |
| `plants_101.species_detail.json` | Original detailed API data |
| `plants_101.species_clean.json` | Cleaned plant identity and taxonomy |
| `plants_101.species_detail_clean.json` | Cleaned detailed plant characteristics |
| `plants_101.semantic_search.json` | Combined representation prepared for semantic search |

---

# 20. Difference Between Clean Data and Search-Prepared Data

The cleaned datasets are still general-purpose datasets.

```text
species_clean
species_detail_clean
```

They can be used for:

```text
MongoDB queries
analytics
filtering
applications
data validation
future transformations
```

The semantic-search dataset has a more specific purpose:

```text
plants_101.semantic_search.json
```

It prepares the plant information for:

```text
embedding generation
vector similarity search
metadata filtering
hybrid search
```

Therefore:

```text
Cleaned datasets
= cleaned source data

Semantic-search dataset
= data redesigned for retrieval
```

---

# 21. Current Pipeline

The project currently reaches this stage:

```text
API
 ↓
Raw JSON
 ↓
Cleaning and normalization
 ↓
species_clean.json
species_detail_clean.json
 ↓
Logical join using plant ID
 ↓
semantic_text + metadata
 ↓
semantic_search.json
 ↓
Generate embeddings
 ↓
Create vector index
 ↓
Semantic / hybrid search
```

The cleaning and semantic-search preparation stages are complete.

The next downstream stage is:

```text
Generate embeddings
```

followed by:

```text
Store/index vectors
```

and finally:

```text
Run semantic and hybrid searches
```

