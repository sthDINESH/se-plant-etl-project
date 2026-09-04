# se-plant-etl-project

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project dependencies:

```bash
python -m pip install -r requirements.txt
```

Create a `.env` file in the project root and add your Perenual API key:

```env
PERENUAL_API_KEY=your_real_api_key
```

Run the application:

```bash
python main.py
```

The `.env` file contains a secret and should not be committed to Git.