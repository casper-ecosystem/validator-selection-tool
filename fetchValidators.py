import os
import requests

def fetch_auction_metrics():
    # Get the authorization key from the environment variable
    auth_key = os.getenv("CSPR_CLOUD_KEY")
    if not auth_key:
        print("Error: CSPR_CLOUD_KEY environment variable is not set.")
        return

    # API endpoint
    url = "https://api.cspr.cloud/auction-metrics"

    # Headers
    headers = {
        "accept": "application/json",
        "authorization": auth_key,
    }

    try:
        # Make the GET request
        response = requests.get(url, headers=headers)

        # Raise an HTTPError if the response was unsuccessful
        response.raise_for_status()

        # Parse the JSON response
        data = response.json().get("data", {})

        # Output the results with one value per line
        for key, value in data.items():
            print(f"{key}: {value}")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_auction_metrics()

