import json

import faiss
import numpy as np
from google import genai
from sentence_transformers import SentenceTransformer

from env import (
    SBERT_MODEL,
    JSON_WITH_EMBEDDINGS,
    GEMINI_MODEL,
    GEMINI_API_KEY,
)


# Load plant data
with open(
    JSON_WITH_EMBEDDINGS,
    "r",
    encoding="utf-8"
) as file:
    species_details_with_embeddings = json.load(file)


# Load embedding model
model = SentenceTransformer(SBERT_MODEL)


# Create numpy array from stored embeddings
embeddings = np.array([
    species["embeddings"]
    for species in species_details_with_embeddings
])


# Create FAISS index
dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)
index.add(embeddings)


# Create Gemini client
client = genai.Client(
    api_key=GEMINI_API_KEY
)


def search_plants(prompt, k=5):
    """Find the most relevant plants using FAISS."""

    query_embedding = model.encode([prompt])

    distances, indices = index.search(
        query_embedding,
        k=k
    )

    plants = [
        species_details_with_embeddings[idx]
        for idx in indices[0]
    ]

    return plants


def generate_answer(prompt, plants):
    """Generate an answer using the retrieved plant information."""

    context = "\n\n".join(
        f"""
        Plant: {plant["common_name"]}
        Description: {plant["description"]}
        Semantic information: {plant["semantic_text"]}
        """
        for plant in plants
    )

    rag_prompt = f"""
    You are a helpful plant assistant.

    Answer the user's question using only the plant
    information provided below.

    If the information does not contain enough information
    to answer the question, say that you don't have enough
    information.

    Plant information:
    {context}

    User question:
    {prompt}
    """

    interaction = client.interactions.create(
        model=GEMINI_MODEL,
        input=rag_prompt
    )

    return interaction.output_text


if __name__ == "__main__":
    # Ask the user questions
    while True:

        prompt = input(
            "Enter search query (type 'quit' to stop): "
        )

        if prompt.strip().lower() == "quit":
            break

        # Retrieve relevant plants
        print("Retrieving relevant plants")
        plants = search_plants(prompt, k=10)

        # Generate RAG answer
        print(f"Checking with {GEMINI_MODEL}")
        answer = generate_answer(prompt, plants)

        print("\nAnswer:")
        print(answer)
