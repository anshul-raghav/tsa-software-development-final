"""Training script for the scan quality classifier.

Uses transfer learning with MobileNetV2 as the backbone.
Trains on augmented images of control panels with quality labels.

Usage:
    python -m app.ml.training.train_scan_quality --data_dir ./data/scan_quality --epochs 20
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms, models
import numpy as np
from PIL import Image

from app.core.logging import logger


CLASSES = ["good", "blurry", "glare", "partial", "tilted", "too_far", "too_close"]
NUM_CLASSES = len(CLASSES)


class ScanQualityDataset(Dataset):
    """Dataset of control panel images labeled by scan quality."""

    def __init__(self, data_dir: str, transform=None):
        self.samples: list[tuple[str, int]] = []
        self.transform = transform

        for class_idx, class_name in enumerate(CLASSES):
            class_dir = Path(data_dir) / class_name
            if not class_dir.exists():
                logger.warning(f"Missing class directory: {class_dir}")
                continue
            for img_path in class_dir.glob("*"):
                if img_path.suffix.lower() in (".jpg", ".jpeg", ".png", ".bmp"):
                    self.samples.append((str(img_path), class_idx))

        logger.info(f"Loaded {len(self.samples)} samples from {data_dir}")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        image = Image.open(path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, label


def build_model() -> nn.Module:
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)

    for param in model.features[:14].parameters():
        param.requires_grad = False

    model.classifier = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(model.last_channel, 128),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(128, NUM_CLASSES),
    )
    return model


def train(data_dir: str, output_path: str, epochs: int = 20, batch_size: int = 16, lr: float = 1e-3):
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.3, contrast=0.3),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    full_dataset = ScanQualityDataset(data_dir, transform=train_transform)
    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(full_dataset, [train_size, val_size])

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = build_model().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=lr)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)

    best_val_acc = 0.0

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        train_acc = correct / total if total > 0 else 0
        scheduler.step()

        model.eval()
        val_correct = 0
        val_total = 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, predicted = torch.max(outputs, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()

        val_acc = val_correct / val_total if val_total > 0 else 0

        logger.info(
            f"Epoch {epoch+1}/{epochs} - "
            f"Loss: {running_loss/len(train_loader):.4f} - "
            f"Train Acc: {train_acc:.4f} - "
            f"Val Acc: {val_acc:.4f}"
        )

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            torch.save(model, output_path)
            logger.info(f"Saved best model (val_acc={val_acc:.4f}) to {output_path}")

    logger.info(f"Training complete. Best validation accuracy: {best_val_acc:.4f}")
    return best_val_acc


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train scan quality classifier")
    parser.add_argument("--data_dir", required=True, help="Path to training data directory")
    parser.add_argument("--output", default="./app/ml/models/scan_quality_model.pth")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=1e-3)
    args = parser.parse_args()

    train(args.data_dir, args.output, args.epochs, args.batch_size, args.lr)
