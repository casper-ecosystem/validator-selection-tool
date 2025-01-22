import os
import requests
import csv
import time

# Adjustable rate limit
RATE_LIMIT = 100  # Requests per minute
RATE_PERIOD = 60  # Seconds
REQUEST_INTERVAL = RATE_PERIOD / RATE_LIMIT  # Time delay between requests

def rate_limited_request(url, headers):
    """Wrapper function to enforce rate limiting on API requests."""
    time.sleep(REQUEST_INTERVAL)  # Enforce delay
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise error if request fails
    return response

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
        print("Fetching auction metrics...")
        # Make the GET request
        response = rate_limited_request(url, headers)

        # Parse the JSON response
        data = response.json().get("data", {})
        print("Auction metrics fetched successfully:")
        for key, value in data.items():
            print(f"  {key}: {value}")
        return data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching auction metrics: {e}")
        return None

def fetch_validator_performance(public_key, eras, auth_key):
    # API endpoint for validator performance
    base_url = f"https://api.cspr.cloud/validators/{public_key}/relative-performances"

    # Headers
    headers = {
        "accept": "application/json",
        "authorization": auth_key,
    }

    performances = {}
    try:
        # Construct the query for eras
        era_param = ",".join(map(str, eras))
        url = f"{base_url}?era_id={era_param}&page=1"

        # Make the GET request
        response = rate_limited_request(url, headers)

        # Parse the JSON response
        data = response.json().get("data", [])
        for entry in data:
            performances[entry["era_id"]] = entry["score"]

    except requests.exceptions.RequestException as e:
        print(f"Error fetching validator performance for {public_key}: {e}")

    return performances

def check_voting_participation(public_key, auth_key, contract_package_hash, start_block, end_block):
    # API endpoint for account fungible token actions
    base_url = f"https://api.cspr.cloud/accounts/{public_key}/ft-token-actions"

    # Headers
    headers = {
        "accept": "application/json",
        "authorization": auth_key,
    }

    try:
        # Add the contract_package_hash to the query
        url = (
            f"{base_url}?from_block_height={start_block}"
            f"&to_block_height={end_block}&contract_package_hash={contract_package_hash}"
        )

        # Make the GET request
        response = rate_limited_request(url, headers)

        # Parse the JSON response
        data = response.json().get("data", [])
        for action in data:
            if action.get("ft_action_type_id") == 2:
                return 1  # Participated

    except requests.exceptions.RequestException as e:
        print(f"Error checking voting participation for {public_key}: {e}")

    return 0  # Did not participate


def filter_out_validators(validators):
    print("Filtering out ineligible validators...")
    eligible_validators = [
        v for v in validators 
        if v.get("is_3_months_old", False) 
        and v.get("average_performance", 0) >= 98.0
        and v.get("account_info_active", False)
        and 1 <= v.get("fee", 0) <= 10
        and v.get("rank", float('inf')) > 10
        and v.get("delegators_number", float('-inf')) < 1200
        and v.get("onchain_voting_participation", 0) >= 0.5
    ]
    print(f"Filtered out {len(validators) - len(eligible_validators)} ineligible validators.")
    return eligible_validators

def fetch_validators(last_era_id):
    # Get the authorization key from the environment variable
    auth_key = os.getenv("CSPR_CLOUD_KEY")
    if not auth_key:
        print("Error: CSPR_CLOUD_KEY environment variable is not set.")
        return

    # Define voting details as a list of dictionaries
    voting_details = [
        {
            "contract_package_hash": "f64d28df7fc354af183829bad6006525f88d37f0d982ba6125d58ddfa521e0fa",
            "start_block": 3798134,
            "end_block": 3808400,
            "column_name": "voting_participation_001"
        },
        {
            "contract_package_hash": "5743998e54844ae3587bf1c80c83695a767ab568f149be87db15216b57a20831",
            "start_block": 3991820,
            "end_block": 4012820,
            "column_name": "voting_participation_002"
        }
    ]

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
            includes_param = "account_info{url,is_active},average_performance,network_share"
            url = f"{base_url}?era_id={last_era_id}&page={page}&includes={includes_param}"

            # Make the GET request
            response = rate_limited_request(url, headers)

            # Parse the JSON response
            data = response.json()
            print(f"Processing page {page} of validators...")
            for idx, validator in enumerate(data.get("data", []), start=1):
                account_info = validator.get("account_info")
                validator["account_info_url"] = account_info.get("url", "") if account_info else ""
                validator["account_info_active"] = account_info.get("is_active", False) if account_info else False

                # Exception for specific public key due to inconsistency in the API response. Issue reported.
                # TODO: Remove the exception when the API is fixed.
                if validator.get("public_key") == "01faa681d910a8ac877b81537d75db42395b9da0da1a3457d223151305f803da0e":
                    validator["account_info_active"] = True

                average_performance = validator.get("average_performance")
                validator["average_performance"] = round(average_performance.get("score", 0.0), 1) if average_performance else 0

                # Check performances for specific eras
                eras_to_check = [last_era_id - 360, last_era_id - 720, last_era_id - 1080]
                performances = fetch_validator_performance(validator["public_key"], eras_to_check, auth_key)
                is_3_months_old = all(performances.get(era, 0) > 0 for era in eras_to_check)
                validator["is_3_months_old"] = is_3_months_old

                # Check voting participation for each vote
                total_participation = 0

                if float(validator.get("network_share", 1)) < 0.01:  # Treat near-zero values as zero
                    for vote in voting_details:
                        validator[vote["column_name"]] = 1  # Consider voted because they do not have voting tokens due to low weight
                        total_participation += 1
                    # Set onchain_voting_participation to 1
                    validator["onchain_voting_participation"] = 1.0
                else:
                    for vote in voting_details:
                        participation = check_voting_participation(
                            validator["public_key"], auth_key,
                            vote["contract_package_hash"],
                            vote["start_block"], vote["end_block"]
                        )
                        validator[vote["column_name"]] = participation
                        total_participation += participation

                    # Calculate onchain voting participation as average
                    validator["onchain_voting_participation"] = round(total_participation / len(voting_details), 2)

                validators.append(validator)
                if idx % 10 == 0:
                    print(f"Processed {idx} validators on page {page}...")

            # Check if there are more pages
            if page >= data.get("page_count", 0):
                break

            page += 1

        # Output the validators list as a single CSV file
        csv_file_name = f"era_{last_era_id}_validators.csv"
        print("Saving validators to CSV...")

        with open(csv_file_name, mode="w", newline="", encoding="utf-8") as csv_file:
            csv_writer = csv.writer(csv_file)

            # Write the header row
            if validators:
                csv_writer.writerow(validators[0].keys())

            # Write each validator as a row
            for validator in validators:
                csv_writer.writerow(validator.values())

        print(f"Validators data saved to {csv_file_name}")

        # Filter out ineligible validators and save to a new CSV file
        eligible_validators = filter_out_validators(validators)
        eligible_csv_file_name = f"era_{last_era_id}_delegation_candidates.csv"
        print("Saving eligible validators to CSV...")
        with open(eligible_csv_file_name, mode="w", newline="", encoding="utf-8") as csv_file:
            csv_writer = csv.writer(csv_file)

            # Write the header row
            if eligible_validators:
                csv_writer.writerow(eligible_validators[0].keys())

            # Write each eligible validator as a row
            for validator in eligible_validators:
                csv_writer.writerow(validator.values())

        print(f"Eligible validators data saved to {eligible_csv_file_name}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching validators: {e}")

if __name__ == "__main__":
    auction_metrics = fetch_auction_metrics()
    if auction_metrics:
        current_era_id = auction_metrics.get("current_era_id")
        if current_era_id is not None:
            last_era_id = current_era_id - 1
            fetch_validators(last_era_id)

