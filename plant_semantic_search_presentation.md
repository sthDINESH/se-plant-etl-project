# Plant Semantic Search
## Data Preparation and Search Approach

---

## 1. From Raw Data to Semantic Search

```text
Raw API data
      ↓
Data cleaning
      ↓
Combine useful information
      ↓
Semantic-search dataset
      ↓
Embeddings
      ↓
FAISS vector search
      ↓
Plant results
```

**Main goal:** prepare clean, meaningful plant data that can be searched by meaning.

---

## 2. Starting Data

We began with two JSON datasets:

```text
plants_101.species.json
plants_101.species_detail.json
```

### Species data

Contains basic plant identity:

```json
{
    "id": 3,
    "common_name": "White Fir",
    "scientific_name": [
        "Abies concolor"
    ]
}
```

### Species detail data

Contains richer plant information:

```json
{
    "id": 3,
    "family": "Pinaceae",
    "type": "tree",
    "watering": "average",
    "sunlight": [
        "full sun",
        "part shade"
    ],
    "drought_tolerant": true
}
```

---

## 3. Connecting the Datasets

The datasets describe the same plants.

We use the plant `id` to connect the information:

```text
Species data                 Detail data

ID: 3                        ID: 3
White Fir                    Pinaceae
                             tree
                             full sun
                             drought tolerant
```

This lets us bring the useful information together.

---

## 4. Cleaning the Data

The raw API response contained both useful plant information and technical information.

### Kept

```text
Plant names
Taxonomy
Care information
Sunlight
Watering
Soil
Plant descriptions
Plant traits
```

### Removed or sanitised

```text
Unnecessary API information
Subscription-only messages
API keys
Unnecessary URL parameters
HTML / iframe content
```

We also:

```text
Trimmed unnecessary whitespace
Normalised categories
Removed duplicate list values
Converted suitable values to numbers
Structured watering information where possible
Preserved genuine null values
```

**Goal:** keep useful plant information while removing noise.

---

## 5. Creating the Semantic-Search Dataset

The cleaned data was kept separate from the original data.

```text
species.json
      +
species_detail.json
      ↓
    CLEAN
      ↓
species_clean.json
      +
species_detail_clean.json
      ↓
semantic_search.json
```

The new semantic-search dataset contains the information needed for the embedding stage.

---

## 6. Creating `semantic_text`

The most important field is:

```text
semantic_text
```

Useful plant information was combined into a readable description.

Example:

```text
Name: White Fir.
Scientific name: Abies concolor.
Family: Pinaceae.
Genus: Abies.
Plant type: tree.
Life cycle: perennial.
Origin: Western United States; Mexico.
Watering: average.
Sunlight: full sun; part shade.
Soil: acidic; rocky; gravelly; dry; well-drained.
Growth rate: low.
Care level: moderate.
Trait: Drought tolerant.
Trait: Produces flowers.
Trait: Produces cones.
Trait: Medicinal.
Description: White Fir is an amazing evergreen tree...
```

---

## 7. Why Use `semantic_text`?

Instead of sending the whole raw JSON record to the embedding model, we selected the information that describes the plant.

```text
Raw JSON
   ↓
Lots of information
   ↓
Select useful plant information
   ↓
semantic_text
```

This gives the embedding model a focused description of the plant.

---

## 8. Metadata

Some information was kept separately as structured metadata.

```json
"metadata": {
    "type": "tree",
    "watering": "average",
    "sunlight": [
        "full sun",
        "part shade"
    ],
    "drought_tolerant": true,
    "indoor": false,
    "medicinal": true
}
```

### Two useful roles

```text
semantic_text
     ↓
Meaning and similarity

metadata
     ↓
Specific facts and filtering
```

This allows semantic search and structured filtering to work together.

---

# Semantic Search Implementation

## 9. Load the Required Tools

```python
import json

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
```

The main tools are:

```text
Sentence Transformers
        ↓
Turns text into embeddings

FAISS
        ↓
Searches the embeddings

NumPy
        ↓
Handles the numerical vectors
```

---

## 10. Load the Embedding Model

```python
model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)
```

The model converts text into numerical vectors.

```text
Plant description
      ↓
Embedding model
      ↓
Vector of numbers
```

---

## 11. Load the Prepared Dataset

```python
with open(
    "plants_101.semantic_search.json",
    "r",
    encoding="utf-8"
) as file:
    plants = json.load(file)

print(len(plants))
```

This loads the prepared plant records.

Expected result:

```text
30
```

---

## 12. Get the Plant Text

```python
documents = [
    plant["semantic_text"]
    for plant in plants
]
```

This selects the text that we want to convert into embeddings.

```text
Plant 1 → semantic_text
Plant 2 → semantic_text
Plant 3 → semantic_text
...
Plant 30 → semantic_text
```

---

## 13. Create the Plant Embeddings

```python
embeddings = model.encode(documents)

print(embeddings.shape)
```

Each plant description is converted into a numerical vector.

```text
"White Fir is drought tolerant..."
              ↓
       Embedding model
              ↓
   [0.02, -0.18, 0.41, ...]
```

The computer can now compare these vectors.

---

## 14. Create the FAISS Index

```python
dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(
    dimension
)
```

FAISS gives us a place to search through the plant vectors.

```text
30 plant embeddings
        ↓
    FAISS index
```

---

## 15. Add the Plant Embeddings

```python
index.add(
    np.array(
        embeddings,
        dtype="float32"
    )
)

print(index.ntotal)
```

The plant vectors are added to FAISS.

Expected result:

```text
30
```

---

# How a Search Works

## 16. User Enters a Search

```python
query_text = input(
    "Enter your plant search: "
)
```

Example:

```text
I want a drought tolerant tree
```

---

## 17. Turn the Search Into a Vector

```python
query = model.encode(
    [query_text]
)

query = np.array(
    query,
    dtype="float32"
)
```

The user's search is converted into the same type of vector as the plants.

```text
User search
     ↓
Embedding model
     ↓
Query vector
```

---

## 18. Find the Closest Plants

```python
D, I = index.search(
    query,
    k=3
)
```

`k=3` means:

```text
Find the 3 closest plant matches
```

FAISS compares the query vector with the plant vectors.

```text
Query vector
     ↓
Compare with plant vectors
     ↓
Find closest matches
```

---

## 19. Display the Results

```python
for i in I[0]:
    print(
        plants[i]["common_name"]
    )
```

The vector positions are used to find the actual plant names.

```text
Most similar plants:

White Fir
...
...
```

---

## 20. Continuous Search

The program can also keep accepting searches:

```python
while True:

    user_query = input(
        "Enter another plant search: "
    ).strip()

    if user_query.lower() == "quit":
        break
```

This allows multiple searches without restarting the program.

Example:

```text
tree that grows in partial shade

low maintenance garden tree

tree suitable for a Christmas tree

tree for well drained soil

quit
```

---

## 21. Example Semantic Searches

```text
I want a drought tolerant tree
tree that grows in partial shade
tree that likes full sun
low maintenance garden tree
tree suitable for a Christmas tree
evergreen tree for privacy
tree that attracts birds
tree for well drained soil
tree that can handle dry soil
tree suitable for cold weather
fast growing tree
slow growing ornamental tree
tree resistant to pests and diseases
tree for landscaping
tree native to Japan
tree native to North America
tree native to Europe
maple with autumn colour
fir tree for a garden
ornamental maple for a small space
```

---

## 22. Why Is This Semantic Search?

Traditional keyword search focuses heavily on matching words.

Semantic search works with the meaning represented by the text.

```text
User:
"I want a tree that doesn't need much water"
                ↓
          Query embedding
                ↓
        Compare plant vectors
                ↓
      Find similar meanings
```

The system can search for related ideas, such as drought tolerance, rather than only looking for the exact words typed by the user.

---

## 23. Complete Pipeline

```text
RAW API DATA
      ↓
CLEANING
      ↓
CLEAN SPECIES + DETAIL DATA
      ↓
SEMANTIC-SEARCH DATASET
      ↓
semantic_text
      ↓
EMBEDDING MODEL
      ↓
PLANT VECTORS
      ↓
FAISS INDEX
      ↓
USER SEARCH
      ↓
QUERY EMBEDDING
      ↓
VECTOR COMPARISON
      ↓
TOP PLANT MATCHES
```

---

## 24. Key Takeaway

```text
Clean the data
       ↓
Keep the useful plant information
       ↓
Create semantic_text
       ↓
Turn text into vectors
       ↓
Store vectors in FAISS
       ↓
Compare user searches with plant vectors
       ↓
Return similar plants
```

> **We took messy plant data, cleaned and organised it, turned the useful information into vectors, and used those vectors to find plants with similar meanings.**
