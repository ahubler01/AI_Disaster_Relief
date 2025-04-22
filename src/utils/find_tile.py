import geopandas as gpd
from pyproj import Transformer
import numpy as np
import os

# Get the current working directory
current_dir = os.getcwd()

# Joplin's coordinates in WGS84
joplin_lon = -94.5133
joplin_lat = 37.0842

# Create transformer from WGS84 to Mollweide (EPSG:54009 is World Mollweide)
transformer = Transformer.from_crs("EPSG:4326", "+proj=moll +lon_0=0 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs")

# Transform coordinates
joplin_x, joplin_y = transformer.transform(joplin_lat, joplin_lon)

# Read tile schema
tiles = gpd.read_file(os.path.join(current_dir, "static", "shp", "GHSL2_0_MWD_L1_tile_schema_land.shp"))

# Find tile containing Joplin
for idx, row in tiles.iterrows():
    if (row['left'] <= joplin_x <= row['right'] and 
        row['bottom'] <= joplin_y <= row['top']):
        print(f"Joplin is in tile: {row['tile_id']}")
        print(f"Tile bounds: left={row['left']}, right={row['right']}, top={row['top']}, bottom={row['bottom']}")
        print(f"Joplin's Mollweide coordinates: x={joplin_x}, y={joplin_y}") 