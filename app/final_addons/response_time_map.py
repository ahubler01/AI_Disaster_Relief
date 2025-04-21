import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import geopandas as gpd
from scipy.spatial import cKDTree
import networkx as nx
from shapely.geometry import Point, LineString, Polygon
import pandas as pd

def create_road_network(roads_gdf):
    G = nx.Graph()
    
    # Add nodes and edges from road segments
    for idx, row in roads_gdf.iterrows():
        # Handle different geometry types
        if isinstance(row.geometry, LineString):
            coords = list(row.geometry.coords)
        elif isinstance(row.geometry, Polygon):
            coords = list(row.geometry.exterior.coords)
        else:
            continue  # Skip if not LineString or Polygon
            
        for i in range(len(coords) - 1):
            # Add nodes with their coordinates
            G.add_node(coords[i], pos=coords[i])
            G.add_node(coords[i+1], pos=coords[i+1])
            
            # Get road type from various possible property names
            road_type = None
            for prop in ['highway', 'type', 'street', 'road']:
                if prop in row and row[prop]:
                    road_type = row[prop]
                    break
            
            # Add edge with weight based on road type
            weight = get_road_weight(road_type)
            G.add_edge(coords[i], coords[i+1], weight=weight)
    
    return G

def get_road_weight(road_type):
    if not road_type:
        return 5.0  # Default weight for unknown road types
    
    # Convert to lowercase for case-insensitive matching
    road_type = str(road_type).lower()
    
    # Assign weights based on road type (minutes per kilometer)
    # These are estimated average speeds converted to minutes per km
    weights = {
        'motorway': 0.5,    # ~120 km/h
        'trunk': 0.6,       # ~100 km/h
        'primary': 0.75,    # ~80 km/h
        'secondary': 1.0,   # ~60 km/h
        'tertiary': 1.25,   # ~48 km/h
        'residential': 1.5, # ~40 km/h
        'service': 2.0,     # ~30 km/h
        'pedestrian': 5.0,  # ~12 km/h
        'street': 1.5,      # ~40 km/h
        'road': 1.5,        # ~40 km/h
        'multipolygon': 5.0,
        'unknown': 5.0
    }
    
    # Try to match the road type with our weights
    for key in weights:
        if key in road_type:
            return weights[key]
    
    return 5.0  # Default weight if no match found

def calculate_response_times(hospitals_gdf, roads_gdf, grid_size=100):
    # Create road network
    G = create_road_network(roads_gdf)
    
    # Get the bounds of the area
    bounds = roads_gdf.total_bounds
    xmin, ymin, xmax, ymax = bounds
    
    # Create a grid of points
    x = np.linspace(xmin, xmax, grid_size)
    y = np.linspace(ymin, ymax, grid_size)
    X, Y = np.meshgrid(x, y)
    
    # Create response time grid
    response_times = np.full((grid_size, grid_size), np.inf)
    
    # Get all road nodes
    road_nodes = list(G.nodes())
    if not road_nodes:
        return X, Y, response_times
        
    tree = cKDTree([node for node in road_nodes])
    
    # Convert edge weights from minutes/km to actual minutes based on distance
    for u, v, data in G.edges(data=True):
        # Calculate actual distance in km
        lat = (u[1] + v[1]) / 2  # Use midpoint latitude
        km_per_degree_lon = 111.32 * np.cos(np.radians(lat))
        km_per_degree_lat = 111.32
        
        dx = (u[0] - v[0]) * km_per_degree_lon
        dy = (u[1] - v[1]) * km_per_degree_lat
        distance_km = np.sqrt(dx**2 + dy**2)
        
        # Convert to actual minutes (assuming 60 km/h = 1 km/min average speed)
        G[u][v]['weight'] = distance_km
    
    # For each hospital, calculate response times
    for _, hospital in hospitals_gdf.iterrows():
        # Get hospital centroid
        if isinstance(hospital.geometry, Polygon):
            hospital_centroid = hospital.geometry.centroid
        else:
            hospital_centroid = hospital.geometry
            
        # Find nearest road node to hospital
        _, nearest_idx = tree.query([hospital_centroid.x, hospital_centroid.y])
        start_node = road_nodes[nearest_idx]
        
        # Calculate shortest paths from hospital to all other nodes
        lengths = nx.single_source_dijkstra_path_length(G, start_node)
        
        # Update response times grid
        for i in range(grid_size):
            for j in range(grid_size):
                point = Point(X[i, j], Y[i, j])
                
                # Find nearest road node
                _, nearest_idx = tree.query([point.x, point.y])
                nearest_node = road_nodes[nearest_idx]
                
                if nearest_node in lengths:
                    # Calculate straight-line distance to nearest road (in km)
                    lat = point.y
                    km_per_degree_lon = 111.32 * np.cos(np.radians(lat))
                    km_per_degree_lat = 111.32
                    
                    # Calculate access distance (distance to nearest road)
                    dx = (point.x - nearest_node[0]) * km_per_degree_lon
                    dy = (point.y - nearest_node[1]) * km_per_degree_lat
                    access_distance = np.sqrt(dx**2 + dy**2)
                    
                    # Calculate road network distance (in km)
                    road_distance = lengths[nearest_node]  # Already in km
                    
                    # Calculate response time:
                    # 1. Initial dispatch time: 1 minute
                    # 2. Road travel time: 60 km/h = 1 km/min
                    # 3. Access time: 30 km/h = 0.5 km/min for off-road
                    response_time = (
                        1 +  # Dispatch time
                        road_distance +  # Road travel time (1 min/km)
                        (access_distance * 2)  # Access time (2 min/km for off-road)
                    )
                    
                    response_times[i, j] = min(response_times[i, j], response_time)
    
    # Print some statistics for debugging
    print(f"Min response time: {np.min(response_times):.2f} minutes")
    print(f"Max response time: {np.max(response_times):.2f} minutes")
    print(f"Mean response time: {np.mean(response_times):.2f} minutes")
    
    return X, Y, response_times

def create_response_time_map():
    # Load data
    hospitals_gdf = gpd.read_file(r'C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\responsetime\hospitals_joplin.geojson')
    roads_gdf = gpd.read_file(r'C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\responsetime\roads_joplin.geojson')
    
    # Calculate response times
    X, Y, response_times = calculate_response_times(hospitals_gdf, roads_gdf)
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create custom colormap for response times
    colors = ['#00ff00', '#90EE90', '#FFFF00', '#FFA500', '#FF0000']  # Green to Red gradient
    cmap = LinearSegmentedColormap.from_list('response_time', colors)
    
    # Set maximum response time for visualization (20 minutes)
    max_time = 20
    response_times = np.minimum(response_times, max_time)
    
    # Plot response times with more levels for better granularity
    contour = ax.contourf(X, Y, response_times, 
                         levels=np.linspace(0, max_time, 40),  # 40 levels
                         cmap=cmap,
                         extend='max')
    
    # Add colorbar with better labeling
    cbar = plt.colorbar(contour, label='Estimated Response Time (minutes)')
    cbar.set_ticks(np.linspace(0, max_time, 11))  # 11 ticks from 0 to max_time
    
    # Plot roads
    roads_gdf.plot(ax=ax, color='gray', linewidth=0.5, alpha=0.5)
    
    # Plot hospitals with larger markers
    hospitals_gdf.plot(ax=ax, color='blue', markersize=100, marker='*', label='Hospitals')
    
    # Read and plot POI centroids
    poi_df = pd.read_csv(r'C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\poi_csv.csv')
    ax.scatter(poi_df['centroid_x'], poi_df['centroid_y'], 
               c='red', s=50, alpha=0.7, label='POI Centroids')
    
    # Add title and labels
    plt.title('Emergency Response Time Map - Joplin Area')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    
    # Add legend
    plt.legend()
    
    # Set aspect ratio
    ax.set_aspect('equal')
    
    return fig

if __name__ == "__main__":
    fig = create_response_time_map()
    plt.show() 