import requests

# Define the API endpoint URL
api_url = "https://uselessfacts.jsph.pl/random.json?language=en"

# Make a GET request (for retrieving data)
response = requests.get(api_url)

# Make a POST request (for sending data)
# data_payload = {"key": "value"}
# response = requests.post(api_url, json=data_payload)
