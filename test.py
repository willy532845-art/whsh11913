import requests

# Define the API endpoint URL
api_url = "https://uselessfacts.jsph.pl/random.json?language=en"

# Make a GET request (for retrieving data)
response = requests.get(api_url)

# Make a POST request (for sending data)
# data_payload = {"key": "value"}
# response = requests.post(api_url, json=data_payload)
if response.status_code == 200:
    # Request was successful, process the data
    data = response.json()  # Assuming the API returns JSON
    print(data['text'])
else:
    # Request failed, handle errors
    print(f"Error: {response.status_code} - {response.text}")
