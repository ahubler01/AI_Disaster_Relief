import requests
import json

# API configuration
API_KEY = "02202c7c96b9a91ae814ab6c81ca2acceedb7381"
BASE_URL = "https://tessadem.com/api/elevation"

# Joplin area coordinates (approximate bounding box)
# Southwest corner: 37.0, -94.7
# Northeast corner: 37.1, -94.6
locations = "37.001,-94.642|37.225,-94.339"

# Parameters for the API request
params = {
    "key": API_KEY,
    "mode": "area",
    "rows": 100,
    "columns": 100,
    "locations": locations,
    "format": "json"
}

def get_elevation_data():
    try:
        response = requests.get(BASE_URL, params=params)
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            print(f"Request Balance: {response.headers.get('Request-Balance')}")
            return data
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

if __name__ == "__main__":
    elevation_data = get_elevation_data()
    if elevation_data:
        # Save the data to a JSON file
        with open('joplin_elevation.json', 'w') as f:
            json.dump(elevation_data, f, indent=4)
        print("Elevation data saved to joplin_elevation.json") 