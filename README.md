# AI_Disaster_Relief

## Overview

This project aims to classify building damage levels using deep learning techniques. We leverage ResNet-50 (a powerful Convolutional Neural Network architecture) for feature extraction and fine-tuning on a custom dataset of pre- and post-disaster building images. By identifying different levels of damage, the model assists in prioritizing disaster relief efforts.

## Directory Structure

```bash
.
├── data
│   ├── test
│   └── train
├── src
│   ├── 01_EDA.ipynb
│   └── 02_Train_RESNET_50.ipynb
├── .gitignore
└── README.md
```

## Model Architecture: ResNet-50

**ResNet-50** is a widely-used CNN architecture known for its effectiveness in image classification tasks. It introduces residual blocks that help avoid vanishing gradients and maintain performance even when the network is very deep.

1. Pretrained Weights

- We use ImageNet-pretrained weights, which allows faster convergence and often better accuracy with limited data.

2. Frozen Layers

- We typically freeze the initial layers to retain their learned representations of general image features (edges, textures, shapes).
- We fine-tune the later layers to capture disaster-specific features such as debris, collapse patterns, and roof damage.

3. Fully-Connected (FC) Layers

- After the ResNet-50 backbone, we add custom FC layers with dropout and batch normalization to classify damage levels (e.g., minor, moderate, severe, destroyed).

## Setup Instructions

1. **Conda Environment Setup**

- Create a new environment (replace env_name with your preferred name):

```bash
conda create -n env_name python=3.11.8
```

- Activate the environment:

```bash
conda activate env_name
```

- Install dependencies

```bash
pip install -r requirements.txt
```

## Contributors

- Yan Bernard xdYanou
- Armand hubler, the_ahub
- Zaid Alsaheb, haxybaxy
