import requests

from env import PERENUAL_API_KEY


def get(url, params=None):
    """Send an authenticated GET request and return the JSON response."""
    request_params = dict(params or {})
    request_params["key"] = PERENUAL_API_KEY

    try:
        response = requests.get(url, params=request_params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as error:
        return {"error": str(error)}
    except ValueError as error:
        return {"error": f"Invalid JSON response: {error}"}
