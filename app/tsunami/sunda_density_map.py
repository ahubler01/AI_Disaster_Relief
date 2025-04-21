import rioxarray
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

def create_sunda_population_density_map():
    # Load the data
    population_data = rioxarray.open_rasterio(
        r"C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\tsunami\GHS_POP_E2030_GLOBE_R2023A_54009_100_V1_0_R10_C29.tif",
        masked=False
    )

    # Load Sunda boundary
    sunda_boundary = gpd.read_file(r"C:\Users\yanit\OneDrive\Bureau\Data Insights And Visualization\tsunami\sunda.geojson")

    # First clip in original projection
    sunda_boundary_moll = sunda_boundary.to_crs('ESRI:54009')
    clipped_pop_moll = population_data.rio.clip(sunda_boundary_moll.geometry)

    # Then reproject to UTM
    clipped_pop_utm = clipped_pop_moll.rio.reproject('EPSG:32748')  # UTM zone 48S for Sunda
    sunda_boundary_utm = sunda_boundary.to_crs('EPSG:32748')

    # Create visualization with a white background
    fig, ax = plt.subplots(figsize=(15, 15), facecolor='white')
    ax.set_facecolor('white')

    # Create custom colormap from white to dark red
    colors = ['#ffffff', '#fff7ec', '#fee8c8', '#fdd49e', '#fdbb84', '#fc8d59', '#ef6548', '#d7301f', '#990000']
    n_bins = 256  # Number of color gradients
    custom_cmap = LinearSegmentedColormap.from_list("custom", colors, N=n_bins)

    # Plot population density
    population = clipped_pop_utm[0].values * 10  # Multiply by 10 to scale up the values
    valid_pop = population[~np.isnan(population)]
    valid_pop = valid_pop[valid_pop >= 0]

    im = ax.imshow(population,
                  extent=[clipped_pop_utm.x.min(), clipped_pop_utm.x.max(),
                         clipped_pop_utm.y.min(), clipped_pop_utm.y.max()],
                  cmap=custom_cmap,
                  norm=plt.Normalize(vmin=0, vmax=np.percentile(valid_pop, 98))
    )

    # Add even smaller colorbar with formatted labels
    cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.04)  # Reduced fraction for smaller colorbar
    cbar.set_label('Population Density (people/cell)', fontsize=12, labelpad=15)
    # Format colorbar labels to include comma separators
    cbar.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))

    # Plot Sunda boundary with a more aesthetic style
    sunda_boundary_utm.boundary.plot(
        ax=ax,
        color='#2F4F4F',  # Dark slate gray
        linewidth=2.5,
        linestyle='-',
        label='Sunda Tsunami Area',
        alpha=0.8
    )

    # Add title and legend with improved styling
    plt.title('Population Density in Sunda Tsunami Area', 
              fontsize=16, 
              pad=20, 
              fontweight='bold', 
              fontfamily='sans-serif')

    # Improve legend appearance
    leg = plt.legend(fontsize=12, 
                    loc='upper right',
                    frameon=True,
                    facecolor='white',
                    edgecolor='#2F4F4F',
                    framealpha=0.9)

    # Remove axes coordinates
    ax.set_xticks([])
    ax.set_yticks([])

    # Add a subtle border around the plot
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color('#2F4F4F')
        spine.set_linewidth(2)

    plt.tight_layout()
    return fig

if __name__ == "__main__":
    fig = create_sunda_population_density_map()
    plt.savefig('sunda_population_density.png', dpi=300, bbox_inches='tight')
    plt.show() 