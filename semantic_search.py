import json
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

from env import (
    SBERT_MODEL,
    JSON_WITH_EMBEDDINGS,
)


INPUT_JSON = 'outputs/species_search_with_embeddings.json'

with open(
    JSON_WITH_EMBEDDINGS,
    "r",
    encoding="utf-8"
) as file:
    species_details_with_embeddings = json.load(file)
    

# 1. Load a pretrained Sentence Transformer model
model = SentenceTransformer(SBERT_MODEL)

# Create a np array with embeddings from json
embeddings = np.array([
    species['embeddings']
    for species in species_details_with_embeddings
])

# Find the dimension of embeddings
dimension = embeddings.shape[1]

# Create an FAISS search index 
index = faiss.IndexFlatL2(dimension)

# Add embeddings into index to store them as vectors
index.add(embeddings)

# Prompt the user for query and display the results of vector search
quit = False

while not quit:
    # Prompt user for a query prompt
    prompt = input("Enter search query(type 'quit' to stop):")

    if prompt.lower() == 'quit':
        break

    # Create embeddings for query prompt
    query = model.encode([prompt])

    # Get distances and index based on vector search
    distances, indices = index.search(query, k=5)

    print("Distances", distances)
    print("indices", indices)

    # Print top 2 similar documents
    print('Most similar documents:')
    for idx in indices[0]:
        print(
            f"{species_details_with_embeddings[idx]['common_name']}:\n"
            f"{species_details_with_embeddings[idx]['description']}\n\n"
        )