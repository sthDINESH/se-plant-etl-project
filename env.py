import os

from dotenv import load_dotenv


load_dotenv()
PERENUAL_API_KEY = os.getenv("PERENUAL_API_KEY")

PERENUAL_ENDPOINT = 'https://perenual.com/api/v2/'
SPECIES_API = PERENUAL_ENDPOINT + 'species-list'
