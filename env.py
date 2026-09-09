import os

from dotenv import load_dotenv

load_dotenv()
PERENUAL_API_KEY = os.getenv("PERENUAL_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FLASK_DEBUG_MODE = os.getenv("FLASK_DEBUG_ON", False)

# URI for mongoDB database
MONGODB_URI = 'mongodb://localhost:27017/'

# Perenual endpoints
PERENUAL_ENDPOINT = 'https://perenual.com/api/v2/'
SPECIES_API = PERENUAL_ENDPOINT + 'species-list'
SPECIES_DETAIL_API = PERENUAL_ENDPOINT + 'species/details/'

# AWS profile
AWS_PROFILE = os.getenv("AWS_PROFILE", 'default')

# S3 bucket
S3_BUCKET = 'se-data-with-ai-etl-project'
S3_ETL_JSON_KEY = 'plants_101/species_search.json'
S3_ETL_JSON_WITH_EMBEDDINGS_KEY = 'plants_101/species_search_with_embeddings.json'

# Sentence transformer model
SBERT_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'

# Configuration to selectively enable different ETL stages
CONFIG = {
    'EXTRACT': True,
    'TRANSFORM': True,
    'LOAD': True,
}

# Paths to output directories and files
OUTPUT_DIR = "outputs"
JSON_WITH_EMBEDDINGS = f"{OUTPUT_DIR}/species_search_with_embeddings.json"

# Gemini model to use
GEMINI_MODEL = 'gemini-3.5-flash'
