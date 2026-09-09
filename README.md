# Plants 101

## Introduction
### Concept
The concept of this project was to build a data pipeline that retrieves data from an API, transforms it, and loads it for use in a search and recommendation system enhanced with semantic search and RAG.

<br>

<img src="presentation/concept-image.png" alt="Plant Data Pipeline Banner" width="1350" height="120">

<br>

### Goals
🌱 Build a successful ETL pipeline using plant data from an external API <br>
🌱 Make plant information easier for users to discover <br>
🌱 Allow users to search using natural language rather than exact plant names <br>
🌱 Recommend plants based on what the user is looking for <br>
🌱 Provide useful, data-driven answers through RAG <br>

<br>

### Why this dataset?

|  **Interest** |  **Data Structure** |  **Potential** |
|---|---|---|
| Our group has a shared interest in houseplants. | The API provides a wide range of plant and care information in a semi-structured format. | This gave us the opportunity to clean and transform real-world data, while also supporting semantic search, recommendations and RAG. |

<br>

### Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root and add your Perenual API key:

```env
PERENUAL_API_KEY=your_real_perenual_api_key
GEMINI_API_KEY=your_real_gemini_api_key
AWS_PROFILE=your_aws_profile(if not default)
```

Run the application:

```bash
python main.py
```

The `.env` file contains a secret and should not be committed to Git.

## Processes
### ETL
### Semantic Search
### RAG

## Lessons learnt
## Future enhancements
## Strong for employers

## Conclusion
