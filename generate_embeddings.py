import json
import boto3

from sentence_transformers import SentenceTransformer
from clean_data import build_semantic_text

from env import (
    S3_ETL_JSON_KEY,
    S3_BUCKET,
    AWS_PROFILE,
    OUTPUT_DIR,
    JSON_WITH_EMBEDDINGS,
)

# 1. Fetch search json file from S3
print(f"Fetching {S3_ETL_JSON_KEY} from {S3_BUCKET}")

session = boto3.Session(profile_name=AWS_PROFILE)
s3_client = session.client("s3")

species_details = json.loads(s3_client.get_object(
    Bucket=S3_BUCKET,
    Key=S3_ETL_JSON_KEY,
)['Body'].read())


# 2. Load a pretrained Sentence Transformer model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# 3. Add semantic text and encodings to facilitate semantic search
species_details_with_embeddings = []
for detail in species_details:
    semantic_text = build_semantic_text(detail)
    detail['semantic_text'] = semantic_text
    detail['embeddings'] = model.encode([semantic_text]).squeeze().tolist()
    species_details_with_embeddings.append(detail)

# 4. Dump the json with embeddings into output directory
SEARCH_OUTPUT_JSON = f'{OUTPUT_DIR}/species_search_with_embeddings.json'

with open(JSON_WITH_EMBEDDINGS, "w", encoding="utf-8") as file:
    json.dump(
        species_details_with_embeddings,
        file,
        indent=4,
        ensure_ascii=False
        )
    print(f"✓ Saved {JSON_WITH_EMBEDDINGS}")

# # 5. Save to S3
#     print("Saving json with embeddings to S3")

#     s3_client.upload_file(
#         Filename=SEARCH_OUTPUT_JSON,
#         Bucket=S3_BUCKET,
#         Key=S3_ETL_JSON_WITH_EMBEDDINGS_KEY,
#     )
#     print(f"✓ {S3_ETL_JSON_WITH_EMBEDDINGS_KEY} saved to {S3_BUCKET}")
