import requests
import json
import geopandas as gpd

# Overpass API endpoint
overpass_url = "http://overpass-api.de/api/interpreter"

# Joplin area bounding box (from your elevation data)
# You might want to adjust these coordinates to match your exact area
bbox = "37.0,-94.7,37.1,-94.6"  # southwest lat, southwest lon, northeast lat, northeast lon

# Overpass QL query to get hospitals
overpass_query = f"""
[out:json][timeout:25];
(
  node["amenity"="hospital"]({bbox});
  way["amenity"="hospital"]({bbox});
  relation["amenity"="hospital"]({bbox});
);
out body;
>;
out skel qt;
"""

def get_hospitals():
    try:
        response = requests.post(overpass_url, data=overpass_query)
        if response.status_code == 200:
            data = response.json()
            
            # Process the data into a GeoDataFrame
            features = []
            for element in data['elements']:
                if element['type'] == 'node':
                    features.append({
                        'type': 'Feature',
                        'geometry': {
                            'type': 'Point',
                            'coordinates': [element['lon'], element['lat']]
                        },
                        'properties': {
                            'id': element['id'],
                            'name': element.get('tags', {}).get('name', 'Unknown'),
                            'emergency': element.get('tags', {}).get('emergency', 'no')
                        }
                    })
            
            # Create GeoDataFrame
            gdf = gpd.GeoDataFrame.from_features(features)
            
            # Save to GeoJSON
            gdf.to_file('hospitals.geojson', driver='GeoJSON')
            print(f"Found {len(gdf)} hospitals and saved to hospitals.geojson")
            
            return gdf
            
        else:
            print(f"Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

if __name__ == "__main__":
    get_hospitals() 