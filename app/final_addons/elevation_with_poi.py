import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import geopandas as gpd
import pandas as pd

def create_elevation_poi_map():
    # Read the elevation data
    with open(r'C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\elevation\joplin_elevation.json', 'r') as f:
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
    roads_gdf = gpd.read_file(r'C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\responsetime\roads_joplin.geojson')

    # Read the POI CSV file
    poi_df = pd.read_csv(r'C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\poi_csv.csv')

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
    ax.set_xlim(-94.60, -94.42)
    ax.set_ylim(37.00, 37.175)

    # Add title and labels
    plt.title('Joplin Area Elevation Map with Roads and POI Centroids')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')

    # Add legend
    plt.legend()

    # Set the aspect ratio to equal to maintain proper geographic proportions
    ax.set_aspect('equal')

    return fig

if __name__ == "__main__":
    fig = create_elevation_poi_map()
    plt.show() 