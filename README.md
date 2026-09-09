# Plants 101

## Introduction
### Concepts
### Goals
### Dataset

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