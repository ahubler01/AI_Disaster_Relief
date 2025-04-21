import os
import json
import folium
from folium import Circle
from pathlib import Path
import pandas as pd
from shapely import wkt
from shapely.geometry.multipolygon import MultiPolygon
from collections import Counter

def read_label(label_path):
    """Read JSON label file"""
    with open(label_path) as json_file:
        return json.load(json_file)

def get_damage_type(properties):
    """Get damage type from properties"""
    if 'subtype' in properties:
        return properties['subtype']
    return 'no-damage'

def get_damage_dict(coords):
    """Count damage types in coordinates"""
    damage_list = [get_damage_type(coord['properties']) for coord in coords]
    return Counter(damage_list)

def get_centroid(coords):
    """Calculate centroid of polygons"""
    if not coords:
        return {'centroid_x': None, 'centroid_y': None, 'latlong': None}
    
    try:
        polygons = []
        for polygon in coords:
            try:
                poly = wkt.loads(polygon['wkt'])
                if not poly.is_empty:
                    polygons.append(poly)
            except (ValueError, KeyError):
                continue
        
        if not polygons:
            return {'centroid_x': None, 'centroid_y': None, 'latlong': None}
            
        multi_polygon = MultiPolygon(polygons)
        if multi_polygon.is_empty:
            return {'centroid_x': None, 'centroid_y': None, 'latlong': None}
            
        centroid = multi_polygon.centroid
        if centroid.is_empty:
            return {'centroid_x': None, 'centroid_y': None, 'latlong': None}
            
        return {'centroid_x': centroid.x, 'centroid_y': centroid.y, 'latlong': centroid}
    except Exception as e:
        print(f"Error calculating centroid: {str(e)}")
        return {'centroid_x': None, 'centroid_y': None, 'latlong': None}

def metadata_with_damage(label_path):
    """Extract metadata and damage information"""
    data = read_label(label_path)
    coords = data['features']['lng_lat']
    
    damage_dict = get_damage_dict(coords)
    centroid = get_centroid(coords)
    
    data['metadata'].update(centroid)
    data['metadata']['path'] = label_path
    data['metadata'].update(damage_dict)
    return data['metadata']

def generate_metadata_df(disaster_labels):
    """Create dataframe with metadata from disaster labels"""
    metadata_list = [metadata_with_damage(label_path) for label_path in disaster_labels]
    df = pd.DataFrame(metadata_list)
    
    # Separate numeric columns and Point objects
    numeric_cols = ['centroid_x', 'centroid_y', 'no-damage', 'minor-damage', 'major-damage', 'destroyed', 'un-classified']
    
    # Fill NaN values for numeric columns only
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].fillna(df[col].mean())
    
    # Drop the latlong column as we don't need it for the map
    if 'latlong' in df.columns:
        df = df.drop('latlong', axis=1)
    
    return df

def generate_circle(row):
    """Generate circles for different damage types with proper sizing"""
    COLOR_MAP = {
        "no-damage": 'green',
        "minor-damage": 'blue',
        "major-damage": 'orange',
        "destroyed": 'red',
        "un-classified": 'gray'
    }
    
    # Calculate total buildings
    total_buildings = row.get('no-damage', 0) + row.get('minor-damage', 0) + row.get('major-damage', 0) + row.get('destroyed', 0)
    
    # Create popup content with damage counts and percentages
    popup_content = f"""
    <div style='width: 300px'>
        <h4 style='text-align: center; margin-bottom: 10px;'>Damage Assessment</h4>
        <table style='width: 100%; border-collapse: collapse;'>
            <tr style='background-color: #f2f2f2;'>
                <th style='padding: 8px; text-align: left; border: 1px solid #ddd;'>Damage Level</th>
                <th style='padding: 8px; text-align: center; border: 1px solid #ddd;'>Count</th>
                <th style='padding: 8px; text-align: center; border: 1px solid #ddd;'>%</th>
            </tr>
            <tr>
                <td style='padding: 8px; border: 1px solid #ddd;'><span style='color: green;'>⬤</span> No Damage</td>
                <td style='padding: 8px; text-align: center; border: 1px solid #ddd;'>{int(row.get('no-damage', 0))}</td>
                <td style='padding: 8px; text-align: center; border: 1px solid #ddd;'>{int(row.get('no-damage', 0)/total_buildings*100) if total_buildings > 0 else 0}%</td>
            </tr>
            <tr>
                <td style='padding: 8px; border: 1px solid #ddd;'><span style='color: blue;'>⬤</span> Minor Damage</td>
                <td style='padding: 8px; text-align: center; border: 1px solid #ddd;'>{int(row.get('minor-damage', 0))}</td>
                <td style='padding: 8px; text-align: center; border: 1px solid #ddd;'>{int(row.get('minor-damage', 0)/total_buildings*100) if total_buildings > 0 else 0}%</td>
            </tr>
            <tr>
                <td style='padding: 8px; border: 1px solid #ddd;'><span style='color: orange;'>⬤</span> Major Damage</td>
                <td style='padding: 8px; text-align: center; border: 1px solid #ddd;'>{int(row.get('major-damage', 0))}</td>
                <td style='padding: 8px; text-align: center; border: 1px solid #ddd;'>{int(row.get('major-damage', 0)/total_buildings*100) if total_buildings > 0 else 0}%</td>
            </tr>
            <tr>
                <td style='padding: 8px; border: 1px solid #ddd;'><span style='color: red;'>⬤</span> Destroyed</td>
                <td style='padding: 8px; text-align: center; border: 1px solid #ddd;'>{int(row.get('destroyed', 0))}</td>
                <td style='padding: 8px; text-align: center; border: 1px solid #ddd;'>{int(row.get('destroyed', 0)/total_buildings*100) if total_buildings > 0 else 0}%</td>
            </tr>
            <tr style='background-color: #f2f2f2;'>
                <td style='padding: 8px; border: 1px solid #ddd;'><strong>Total Buildings</strong></td>
                <td style='padding: 8px; text-align: center; border: 1px solid #ddd;'><strong>{int(total_buildings)}</strong></td>
                <td style='padding: 8px; text-align: center; border: 1px solid #ddd;'><strong>100%</strong></td>
            </tr>
        </table>
    </div>
    """
    
    for damage_type, color in COLOR_MAP.items():
        count = row.get(damage_type, 0)
        if count > 0:
            circle = Circle(
                location=[row['centroid_y'], row['centroid_x']],
                radius=count,  # Direct count as radius for better scaling
                color=color,
                fill=False,
                weight=4,  # Increased outline thickness
                opacity=0.8
            )
            # Add popup to the circle
            popup = folium.Popup(popup_content, max_width=300)
            circle.add_child(popup)
            yield circle

def create_sunda_map():
    """Create an interactive map of Sunda tsunami damage"""
    # Path to Sunda data
    base_path = r'C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\tier3\labels'
    labels_generator = Path(base_path).rglob(pattern='sunda-tsunami_*post_*.json')
    
    # Get all Sunda labels
    sunda_labels = [str(label) for label in labels_generator]
    
    if not sunda_labels:
        print("No Sunda data found. Please check the data path.")
        return None
    
    # Generate metadata dataframe
    df = generate_metadata_df(sunda_labels)
    
    # Calculate map center
    center_lat = df['centroid_y'].mean()
    center_lng = df['centroid_x'].mean()
    
    # Create map centered on Sunda
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=13,
        tiles='OpenStreetMap'
    )
    
    # Add circles for each location
    for idx, row in df.iterrows():
        if pd.isna(row['centroid_y']) or pd.isna(row['centroid_x']):
            continue
            
        # Create popup content
        popup_content = f"""
        <div style='width: 200px'>
            <h4>{row.get('img_name', 'Location')}</h4>
            <p><b>Total buildings:</b> {row.get('no-damage', 0) + row.get('minor-damage', 0) + row.get('major-damage', 0) + row.get('destroyed', 0)}</p>
            <p><span style='color:green'><b>No damage:</b> {row.get('no-damage', 0)}</span></p>
            <p><span style='color:blue'><b>Minor damage:</b> {row.get('minor-damage', 0)}</span></p>
            <p><span style='color:orange'><b>Major damage:</b> {row.get('major-damage', 0)}</span></p>
            <p><span style='color:red'><b>Destroyed:</b> {row.get('destroyed', 0)}</span></p>
        </div>
        """
        
        # Generate and add circles for each damage type
        for circle in generate_circle(row):
            circle.add_to(m)
    
    # Add zoom control
    m.add_child(folium.LatLngPopup())
    
    return m

if __name__ == "__main__":
    # Create the map
    sunda_map = create_sunda_map()
    
    if sunda_map:
        # Save the map to an HTML file
        sunda_map.save('sunda_tsunami_map.html')
        print("Map saved as 'sunda_tsunami_map.html'")
    else:
        print("Failed to create map. Please check your data path and structure.")
