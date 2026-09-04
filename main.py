import api_requests as api

from env import SPECIES_API

# Test api request
print(api.get(SPECIES_API))
