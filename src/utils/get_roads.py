import requests
import json
import geopandas as gpd
import os
import dotenv
# Get the current working directory
current_dir = os.getcwd()

dotenv.load_dotenv()

# Overpass API endpoint
overpass_url = os.getenv("OVERPASS_URL")

# Joplin area bounding box
bbox = "37.0,-94.7,37.1,-94.6"  # southwest lat, southwest lon, northeast lat, northeast lon

# Overpass QL query to get roads
overpass_query = f"""
[out:json][timeout:25];
(
  way["highway"]({bbox});
  relation["highway"]({bbox});
);
out body;
>;
out skel qt;
"""

def get_roads():
    try:
        response = requests.post(overpass_url, data=overpass_query)
        if response.status_code == 200:
            data = response.json()
            
            # Process the data into a GeoDataFrame
            features = []
            for element in data['elements']:
                if element['type'] == 'way':
                    # Get the coordinates for each node in the way
                    coords = []
                    for node_id in element['nodes']:
                        # Find the node in the elements
                        for node in data['elements']:
                            if node['type'] == 'node' and node['id'] == node_id:
                                coords.append([node['lon'], node['lat']])
                                break
                    
                    if coords:
                        features.append({
                            'type': 'Feature',
                            'geometry': {
                                'type': 'LineString',
                                'coordinates': coords
                            },
                            'properties': {
                                'id': element['id'],
                                'highway': element.get('tags', {}).get('highway', 'unknown'),
                                'name': element.get('tags', {}).get('name', 'Unknown'),
                                'lanes': element.get('tags', {}).get('lanes', 'unknown')
                            }
                        })
            
            # Create GeoDataFrame
            gdf = gpd.GeoDataFrame.from_features(features)
            
            # Save to GeoJSON
            gdf.to_file(os.path.join(current_dir, "data", "roads.geojson"), driver='GeoJSON')
            print(f"Found {len(gdf)} road segments and saved to roads.geojson")
            
            return gdf
            
        else:
            print(f"Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

if __name__ == "__main__":
    get_roads() 