import requests
import json
import dotenv
import os

# Get the current working directory
current_dir = os.getcwd()

dotenv.load_dotenv()

def get_elevation_data(disaster="Joplin Tornado"):
    """
    Fetch elevation data for either Joplin or Sunda area using the TESSADEM API.
    
    Args:
        disaster (str): Either "Joplin Tornado" or "Sunda Tsunami"
    
    Returns:
        dict: Elevation data in JSON format
    """
    # Set parameters based on disaster type
    if disaster == "Joplin Tornado":
        # Joplin area coordinates (approximate bounding box)
        locations = "37.001,-94.642|37.225,-94.339"
        output_file = os.path.join(current_dir, "data", "joplin_elevation.json")
    else:  # Sunda Tsunami
        # Sunda area coordinates (approximate bounding box from sunda.geojson)
        locations = "-6.4306412229426115,105.79357115956361|-6.211238407940371,105.88173137250544"
        output_file = os.path.join(current_dir, "data", "sunda_elevation.json")
    
    # Parameters for the API request
    params = {
        "key": os.getenv("TESSADEM_API_KEY"),
        "mode": "area",
        "rows": 100,
        "columns": 100,
        "locations": locations,
        "format": "json"
    }
    
    try:
        response = requests.get(os.getenv("TESSADEM_BASE_URL"), params=params)
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            print(f"Request Balance: {response.headers.get('Request-Balance')}")
            
            # Save the data to a JSON file
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Elevation data saved to {output_file}")
            
            return data
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

if __name__ == "__main__":
    # Test both versions
    joplin_data = get_elevation_data("Joplin Tornado")
    sunda_data = get_elevation_data("Sunda Tsunami") 