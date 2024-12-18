import os
import requests
import csv

def fetch_auction_metrics():
    # Get the authorization key from the environment variable
    auth_key = os.getenv("CSPR_CLOUD_KEY")
    if not auth_key:
        print("Error: CSPR_CLOUD_KEY environment variable is not set.")
        return None

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
        return data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching auction metrics: {e}")
        return None

def fetch_validators(last_era_id):
    # Get the authorization key from the environment variable
    auth_key = os.getenv("CSPR_CLOUD_KEY")
    if not auth_key:
        print("Error: CSPR_CLOUD_KEY environment variable is not set.")
        return

    # API endpoint for validators
    base_url = "https://api.cspr.cloud/validators"

    # Headers
    headers = {
        "accept": "application/json",
        "authorization": auth_key,
    }

    validators = []
    page = 1

    try:
        while True:
            # Add pagination to the request
            url = f"{base_url}?era_id={last_era_id}&page={page}"

            # Make the GET request
            response = requests.get(url, headers=headers)

            # Raise an HTTPError if the response was unsuccessful
            response.raise_for_status()

            # Parse the JSON response
            data = response.json()
            validators.extend(data.get("data", []))

            # Check if there are more pages
            if page >= data.get("page_count", 0):
                break

            page += 1

        # Output the validators list as a CSV file
        csv_file_name = f"era_{last_era_id}_validators.csv"
        with open(csv_file_name, mode="w", newline="", encoding="utf-8") as csv_file:
            csv_writer = csv.writer(csv_file)

            # Write the header row
            if validators:
                csv_writer.writerow(validators[0].keys())

            # Write each validator as a row
            for validator in validators:
                csv_writer.writerow(validator.values())

        print(f"Validators data saved to {csv_file_name}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching validators: {e}")

if __name__ == "__main__":
    auction_metrics = fetch_auction_metrics()
    if auction_metrics:
        current_era_id = auction_metrics.get("current_era_id")
        if current_era_id is not None:
            last_era_id = current_era_id - 1
            fetch_validators(last_era_id)

