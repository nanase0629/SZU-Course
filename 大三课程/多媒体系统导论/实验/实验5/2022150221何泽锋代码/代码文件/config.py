import os
import torch
import torchvision.transforms as transforms
from sklearn.model_selection import train_test_split

# 数据集配置
DATASET_CONFIG = {
    'chose': "Holidays",  # Oxford5k
    "Holidays": {
        "image_dir": "dataset/Holidays_images",
        "gt_path": "groundtruth.json",
        "regions": {},
        "dataset_type": "Holidays"
    },
    "Oxford5k": {
        "image_dir": "dataset/oxbuild_images",
        "gt_dir": "gt_files",
        "regions": None,
        "dataset_type": "Oxford5k"
    }
}

# 训练配置
TRAIN_CONFIG = {
    'epoch': 1,
    "seed": 42,
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "batch_size": 32,
    "num_workers": 4,
    "lr": 1e-4,
    "margin": 0.3,
    "save_path": {
        "single": "{dataset_type}_features.pkl",
        "multi": {
            "holidays": "holidays_features.pkl",
            "oxford": "oxford_features.pkl"
        }
    },
    "model_path": {
        "single": "best_{dataset_type}_model.pth",
        "multi": "best_multi_model.pth"
    }
}
