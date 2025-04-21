import rioxarray
import geopandas as gpd

# Load the data
population_data = rioxarray.open_rasterio(
    r"C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\GHS_POP_E2030_GLOBE_R2023A_54009_100_V1_0_R5_C10.tif",
    masked=True
)
joplin_boundary = gpd.read_file("joplin.geojson")

# Print CRS information
print("Population data CRS:")
print(population_data.rio.crs)
print("\nJoplin boundary CRS:")
print(joplin_boundary.crs)

# Print bounds
print("\nPopulation data bounds:")
print(f"X range: {population_data.x.min().item()} to {population_data.x.max().item()}")
print(f"Y range: {population_data.y.min().item()} to {population_data.y.max().item()}")

print("\nJoplin boundary bounds (in its current CRS):")
print(joplin_boundary.total_bounds) 