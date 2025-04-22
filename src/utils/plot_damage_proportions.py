import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import os 

def get_damage_counts(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    damage_counts = defaultdict(int)
    for feature in data['features']['lng_lat']:
        damage_level = feature['properties']['subtype']
        damage_counts[damage_level] += 1
    
    return damage_counts

def main():
    # Directory containing the JSON files
    labels_dir = os.path.join(os.getcwd(), 'data', 'raw', 'tier3', 'labels')
    
    # Get all post-disaster JSON files
    post_disaster_files = [f for f in os.listdir(labels_dir) 
                          if f.endswith('_post_disaster.json')]
    
    # Initialize data structure to store damage counts per disaster
    disaster_damage_counts = defaultdict(lambda: defaultdict(int))
    
    # Process each file
    for file_name in post_disaster_files:
        # Extract disaster name from filename
        disaster_name = file_name.split('_')[0]
        
        # Get damage counts for this file
        file_path = os.path.join(labels_dir, file_name)
        damage_counts = get_damage_counts(file_path)
        
        # Add to disaster totals
        for damage_level, count in damage_counts.items():
            disaster_damage_counts[disaster_name][damage_level] += count
    
    # Convert to DataFrame
    damage_data = []
    for disaster, counts in disaster_damage_counts.items():
        total = sum(counts.values())
        for damage_level, count in counts.items():
            damage_data.append({
                'Disaster': disaster,
                'Damage Level': damage_level,
                'Count': count,
                'Proportion': count / total
            })
    
    df = pd.DataFrame(damage_data)
    
    # Create stacked bar plot
    plt.figure(figsize=(12, 8))
    sns.set_style("whitegrid")
    
    # Pivot the data for stacked bar plot
    pivot_df = df.pivot(index='Disaster', columns='Damage Level', values='Proportion')
    
    # Define damage level order and colors
    damage_order = ['no-damage', 'minor-damage', 'major-damage', 'destroyed']
    colors = ['#2ecc71', '#f1c40f', '#e67e22', '#e74c3c']
    
    # Plot stacked bars
    pivot_df[damage_order].plot(kind='bar', stacked=True, color=colors, width=0.8)
    
    # Customize plot
    plt.title('Proportion of Building Damage Levels by Disaster', fontsize=14, pad=20)
    plt.xlabel('Disaster', fontsize=12)
    plt.ylabel('Proportion of Buildings', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Damage Level', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Add percentage labels
    for i, disaster in enumerate(pivot_df.index):
        bottom = 0
        for damage_level in damage_order:
            if damage_level in pivot_df.columns:
                value = pivot_df.loc[disaster, damage_level]
                if value > 0.05:  # Only show labels for significant proportions
                    plt.text(i, bottom + value/2, f'{value:.1%}', 
                            ha='center', va='center', color='black', fontweight='bold')
                bottom += value
    
    plt.tight_layout()
    plt.savefig('damage_proportions.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    main() 