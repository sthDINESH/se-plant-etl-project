# Import libraries required for semantic search and vector similarity

import json

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load prepared semantic search data
with open(
    "plants_101.semantic_search.json",
    "r",
    encoding="utf-8"
) as file:
    plants = json.load(file)

print(len(plants))

# Get semantic text from each plant
documents = [
    plant["semantic_text"]
    for plant in plants
]


# Create embeddings
embeddings = model.encode(documents)


print(embeddings.shape)

# Get the number of dimensions in each embedding
dimension = embeddings.shape[1]

# Create the FAISS index
index = faiss.IndexFlatL2(dimension)

# Add embeddings to the index
index.add(
    np.array(embeddings, dtype="float32")
)

# Check how many vectors are stored
print(index.ntotal)


# Test search query
####query_text = "I want a drought tolerant tree"
query_text = input("Enter your plant search: ")
# Convert query into an embedding
query = model.encode([query_text])

# Convert query to float32 for FAISS
query = np.array(
    query,
    dtype="float32"
)

# Search for the top 3 most similar plants
D, I = index.search(
    query,
    k=3
)

# Print results
print("\nMost similar plants:")

for i in I[0]:
    print(plants[i]["common_name"])

# Additional feature: continuous searching

print("\nContinuous semantic search")
print("Type 'quit' to exit.")

while True:


    user_query = input(
        "\nEnter another plant search: "
    ).strip()


    if user_query.lower() == "quit":
        print("Goodbye!")
        break


    if not user_query:
        print("Please enter a search.")
        continue


    query_embedding = model.encode(
        [user_query]
    )


    query_embedding = np.array(
        query_embedding,
        dtype="float32"
    )


    D, I = index.search(
        query_embedding,
        k=5
    )


    print("\nMost similar plants:")


    for position, plant_index in enumerate(
        I[0],
        start=1
    ):


        plant = plants[plant_index]


        print(
            f"{position}. "
            f"{plant['common_name']}"
        )

# Semantic search queries 

#I want a drought tolerant tree
#tree that grows in partial shade
#tree that likes full sun
#low maintenance garden tree
#easy to care for ornamental tree
#medicinal tree
#tree suitable for a Christmas tree
#evergreen tree for privacy
#tree suitable for a windbreak
#tree with colourful autumn leaves
#tree with red autumn foliage
#tree with yellow autumn leaves
#Japanese ornamental tree
#small decorative tree for a garden
#tree suitable for a small yard
#tree with attractive bark
#tree with unusual foliage
#tree with beautiful spring flowers
#tree that produces fruit
#tree that produces cones
#tree that attracts birds
#tree that attracts wildlife
#tree for well drained soil
#tree for rocky soil
#tree for acidic soil
#tree that can handle dry soil
#tree suitable for cold weather
#hardy tree for difficult conditions
#fast growing tree
#slow growing ornamental tree
#tree that needs frequent watering
#tree that needs average watering
#tree that can grow in sun or shade
#tree resistant to pests and diseases
#tree with low pruning requirements
#tree for landscaping
#tree for a patio or courtyard
#tree for a privacy screen
#tree with blue green foliage
#tree with golden foliage
#tree with pink or red foliage
#tree with strong branches
#tree that provides shade
#tree suitable for wildlife shelter
#tree native to Japan
#tree native to North America
#tree native to Europe
#maple with autumn colour
#fir tree for a garden
#ornamental maple for a small space






















