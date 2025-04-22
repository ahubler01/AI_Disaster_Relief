import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import geopandas as gpd
import pandas as pd
import os

def create_elevation_poi_map(disaster="Joplin Tornado"):
    # Get the current working directory
    current_dir = os.getcwd()
    
    # Set parameters based on disaster type
    if disaster == "Joplin Tornado":
        elevation_file = "joplin_elevation.json"
        roads_file = "roads_joplin.geojson"
        poi_file = "poi_csv.csv"
        area_name = "Joplin Area"
        x_limits = (-94.60, -94.42)
        y_limits = (37.00, 37.175)
    else:  # Sunda Tsunami
        elevation_file = "sunda_elevation.json"
        roads_file = "sunda_roads.geojson"
        poi_file = "poi_sunda.csv"
        area_name = "Sunda Area"
        x_limits = (105.796, 105.880)
        y_limits = (-6.420, -6.218)
    
    # Read the elevation data
    with open(os.path.join(current_dir, "data", "raw", elevation_file), 'r') as f:
        data = json.load(f)

    # Extract elevation data and convert to 2D array
    elevation_data = data['results']
    rows = len(elevation_data)
    cols = len(elevation_data[0])
    elevation_array = np.zeros((rows, cols))

    # Get the bounds from the elevation data
    # The first and last points in the data contain the coordinates
    first_point = elevation_data[0][0]
    last_point = elevation_data[-1][-1]

    xmin = first_point['longitude']
    xmax = last_point['longitude']
    ymin = first_point['latitude']
    ymax = last_point['latitude']

    # Fill the elevation array
    for i in range(rows):
        for j in range(cols):
            elevation_array[i, j] = elevation_data[i][j]['elevation']

    # Read the GeoJSON files
    roads_gdf = gpd.read_file(os.path.join(current_dir, "data", "raw", roads_file))

    # Read the POI CSV file
    poi_df = pd.read_csv(os.path.join(current_dir, "data", "raw", poi_file))

    # Create a custom colormap for elevation
    colors = ['#0000ff', '#00ffff', '#00ff00', '#ffff00', '#ff0000']  # Blue to Red
    cmap = LinearSegmentedColormap.from_list('elevation', colors)

    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8))

    # Create meshgrid for the contour plot
    x = np.linspace(xmin, xmax, cols)
    y = np.linspace(ymin, ymax, rows)
    X, Y = np.meshgrid(x, y)

    # Plot the elevation data with increased opacity (from 0.3 to 0.5)
    contour = ax.contourf(X, Y, elevation_array, cmap=cmap, levels=20, alpha=0.5)
    plt.colorbar(contour, label='Elevation (meters)')

    # Plot roads with a semi-transparent gray color
    roads_gdf.plot(ax=ax, color='gray', linewidth=0.5, alpha=0.5, label='Roads')

    # Plot POI centroids
    ax.scatter(poi_df['centroid_x'], poi_df['centroid_y'], 
               c='red', s=50, alpha=0.7, label='POI Centroids')

    # Set axis limits
    ax.set_xlim(x_limits)
    ax.set_ylim(y_limits)

    # Add title and labels
    plt.title(f'{area_name} Elevation Map with Roads and POI Centroids')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')

    # Add legend
    plt.legend()

    # Set the aspect ratio to equal to maintain proper geographic proportions
    ax.set_aspect('equal')

    return fig

if __name__ == "__main__":
    # Test both versions
    fig_joplin = create_elevation_poi_map("Joplin Tornado")
    fig_sunda = create_elevation_poi_map("Sunda Tsunami")
    plt.show() 