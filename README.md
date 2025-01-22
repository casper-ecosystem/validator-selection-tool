# Casper Validator Selection Tool

This repository contains a Python script designed to assist in the transparent and fair selection of validators for the Casper Association's staking program. The script fetches and processes validator metrics from the CSPR.cloud API, applying specific criteria to filter eligible candidates. The results are outputted as CSV files for further review and use.

## Features

- Fetches auction metrics and validator data from the CSPR.cloud API.
- Computes voting participation for validators across multiple voting rounds.
- Handles validators with zero `network_share` appropriately, ensuring accurate voting calculations.
- Filters validators based on customizable eligibility criteria, including performance, activity, and voting participation.
- Outputs results as CSV files for detailed analysis.

## Requirements

- Python 3.7+
- `requests` library
- API Key for the CSPR.cloud API, stored in the `CSPR_CLOUD_KEY` environment variable (API keys can be generated for free on the [CSPR.build console](https://console.cspr.build/))

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/casper-ecosystem/validator-selection-tool.git
   cd validator-selection-tool
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the `CSPR_CLOUD_KEY` environment variable with your API key:
   ```bash
   export CSPR_CLOUD_KEY=your_api_key
   ```

## Usage

1. Run the script:
   ```bash
   python fetch_validators.py
   ```

2. The script will fetch data for the last auction era and process the validator list based on the defined criteria.

3. Two CSV files will be generated:
   - `era_<LAST_ERA_ID>_validators.csv`: Contains the complete list of validators with detailed metrics.
   - `era_<LAST_ERA_ID>_delegation_candidates.csv`: Contains the filtered list of eligible validators for delegation.

## Configuration

The script uses a set of predefined criteria to filter validators. These include:

- Performance thresholds (e.g., `average_performance` >= 98.0).
- Active status and account information.
- Participation in voting rounds (average participation >= 0.5).
- Fee range and other network metrics.

You can modify these criteria in the `filter_out_validators` function to suit your requirements.

### API Rate Limiting

The script enforces a rate limit on API requests to prevent exceeding the CSPR.cloud API restrictions.

By default, the script allows **100 requests per minute**, but this can be adjusted by setting the `API_RATE_LIMIT` environment variable.

To change the rate limit, use:

```bash
export API_RATE_LIMIT=200  # Adjusts the limit to 200 requests per minute
```

This ensures compliance with different API tiers (e.g., Free vs. Pro plan).

## Casper Association Delegation Policy

This tool aligns with the [Casper Association Delegation Policy](https://forum.casper.network/t/cvv002-casper-association-delegation-policy/1220), which was accepted by Mainnet validators through an on-chain governance vote. The policy ensures a systematic and transparent delegation process to enhance network decentralization and incentivize optimal validator performance.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! If you have ideas for improvements or new features, feel free to open an issue or submit a pull request.

## Disclaimer

This tool is provided as-is and is designed to assist with validator selection. Users are responsible for ensuring compliance with their specific requirements and regulations.

