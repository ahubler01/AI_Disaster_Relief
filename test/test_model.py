import os
import json
import cv2
import numpy as np
import matplotlib.pyplot as plt
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet50
import torch.nn as nn
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns

# Define damage classes and colors
damage_classes = {
    "no-damage": 0,
    "minor-damage": 1,
    "major-damage": 2,
    "destroyed": 3
}

damage_colors = {
    "no-damage": (0, 255, 0),      # Green
    "minor-damage": (255, 255, 0), # Yellow
    "major-damage": (255, 165, 0), # Orange
    "destroyed": (255, 0, 0)       # Red
}

class ImprovedDamageClassifier(nn.Module):
    def __init__(self, num_classes=4, dropout_prob=0.5):
        super(ImprovedDamageClassifier, self).__init__()
        self.resnet = resnet50(pretrained=True)
        self.resnet = nn.Sequential(*list(self.resnet.children())[:-1])
        
        self.fc1 = nn.Linear(2048, 1024)
        self.bn1 = nn.BatchNorm1d(1024)
        self.fc2 = nn.Linear(1024, 512)
        self.bn2 = nn.BatchNorm1d(512)
        self.fc3 = nn.Linear(512, num_classes)
        self.dropout = nn.Dropout(dropout_prob)

    def forward(self, x):
        x = self.resnet(x)
        x = x.view(x.size(0), -1)
        
        x = self.fc1(x)
        x = self.bn1(x)
        x = nn.ReLU()(x)
        x = self.dropout(x)
        
        x = self.fc2(x)
        x = self.bn2(x)
        x = nn.ReLU()(x)
        x = self.dropout(x)
        
        x = self.fc3(x)
        return x

def load_model(checkpoint_path):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ImprovedDamageClassifier(num_classes=4).to(device)
    model.load_state_dict(torch.load(checkpoint_path, map_location=device))
    model.eval()
    return model, device

def preprocess_image(image):
    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    return transform(image)

def predict_damage(model, device, image):
    with torch.no_grad():
        image = preprocess_image(image).unsqueeze(0).to(device)
        outputs = model(image)
        _, predicted = torch.max(outputs, 1)
        return predicted.item()

def visualize_predictions(model, device, json_dir, image_dir, output_dir, num_images=10):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Initialize lists for performance metrics
    all_true_labels = []
    all_predicted_labels = []
    building_info = []

    processed_count = 0
    for json_file in os.listdir(json_dir):
        if processed_count >= num_images:
            break
            
        if not json_file.endswith(".json") or 'post' not in json_file:
            continue

        json_path = os.path.join(json_dir, json_file)
        with open(json_path, "r") as f:
            data = json.load(f)

        image_name = data.get("metadata", {}).get("img_name")
        if not image_name:
            continue

        image_path = os.path.join(image_dir, image_name)
        image = cv2.imread(image_path)
        if image is None:
            continue

        # Create a copy for visualization
        vis_image = image.copy()

        for building in data.get("features", {}).get("xy", []):
            wkt_string = building.get("wkt", "")
            if not wkt_string.startswith("POLYGON (("):
                continue

            coords = wkt_string[10:-2].split(", ")
            polygon = np.array([list(map(float, coord.split())) for coord in coords])

            # Crop the building
            x_min, y_min = polygon.min(axis=0).astype(int)
            x_max, y_max = polygon.max(axis=0).astype(int)
            building_crop = image[y_min:y_max, x_min:x_max]

            if building_crop.shape[0] == 0 or building_crop.shape[1] == 0:
                continue

            # Get true label
            true_label = building.get("properties", {}).get("subtype", "unknown")
            if true_label not in damage_classes:
                continue
            true_class = damage_classes[true_label]

            # Make prediction
            predicted_class = predict_damage(model, device, building_crop)
            predicted_label = list(damage_classes.keys())[predicted_class]

            # Store metrics
            all_true_labels.append(true_class)
            all_predicted_labels.append(predicted_class)
            building_info.append({
                'image_name': image_name,
                'building_id': building.get("properties", {}).get("uid", "unknown"),
                'true_label': true_label,
                'predicted_label': predicted_label
            })

            # Get color for predicted label
            pred_color = damage_colors[predicted_label]

            # Draw polygon with predicted label color
            pts = polygon.reshape((-1, 1, 2)).astype(np.int32)
            cv2.polylines(vis_image, [pts], isClosed=True, color=pred_color, thickness=2)
            
            # Add predicted label
            centroid = np.mean(polygon, axis=0).astype(int)
            cv2.putText(vis_image, predicted_label, tuple(centroid), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, pred_color, 1, cv2.LINE_AA)

        # Save the visualization
        output_path = os.path.join(output_dir, f"prediction_{image_name}")
        cv2.imwrite(output_path, vis_image)
        print(f"Saved prediction visualization: {output_path}")
        
        processed_count += 1

    # Create performance metrics
    class_report = classification_report(all_true_labels, all_predicted_labels, 
                                      target_names=list(damage_classes.keys()),
                                      output_dict=True)
    
    # Convert to DataFrame and save
    metrics_df = pd.DataFrame(class_report).transpose()
    metrics_df.to_csv(os.path.join(output_dir, 'performance_metrics.csv'))
    
    # Create confusion matrix
    cm = confusion_matrix(all_true_labels, all_predicted_labels)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=damage_classes.keys(),
                yticklabels=damage_classes.keys())
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.savefig(os.path.join(output_dir, 'confusion_matrix.png'))
    plt.close()

    # Save building-level predictions
    predictions_df = pd.DataFrame(building_info)
    predictions_df.to_csv(os.path.join(output_dir, 'building_predictions.csv'), index=False)

    return metrics_df

def main():
    # Set paths
    checkpoint_path = "checkpoints/improved_model.pth"
    json_dir = os.path.join(os.getcwd(), "data/raw/sample/labels")
    image_dir = os.path.join(os.getcwd(), "data/raw/sample/images")
    output_dir = "output/predictions_visualization"

    # Load model
    print("Loading model...")
    model, device = load_model(checkpoint_path)
    print("Model loaded successfully!")

    # Generate visualizations and get metrics
    print("Generating visualizations and computing metrics...")
    metrics_df = visualize_predictions(model, device, json_dir, image_dir, output_dir, num_images=20)
    
    # Print performance metrics
    print("\nPerformance Metrics:")
    print(metrics_df)
    print("\nVisualization complete! Check the output directory for results.")

if __name__ == "__main__":
    main() 