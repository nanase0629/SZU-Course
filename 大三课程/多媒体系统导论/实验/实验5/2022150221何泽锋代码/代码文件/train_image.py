import os
import json
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.models as models
import torchvision.transforms as transforms
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import matplotlib.pyplot as plt
from tqdm import tqdm
import glob
import random
from sklearn.model_selection import train_test_split
import pickle

import config


# 三元组数据集类
class TripletDataset(Dataset):
    def __init__(self, image_dir, groundtruth, query_regions=None, transform=None):
        self.image_dir = image_dir
        self.groundtruth = groundtruth
        self.query_regions = query_regions or {}
        self.transform = transform

        # 构建三元组
        self.triplets = self._generate_triplets()

    def _generate_triplets(self):
        triplets = []
        all_images = set()

        # 收集所有图像
        for query, similar_list in self.groundtruth.items():
            all_images.add(query)
            for similar in similar_list:
                all_images.add(similar)

        all_images = list(all_images)

        # 为每个查询图像生成三元组
        for query, similar_list in self.groundtruth.items():
            for similar in similar_list:
                # 随机选择一个不相似的图像
                while True:
                    negative = random.choice(all_images)
                    if negative not in similar_list and negative != query:
                        break

                triplets.append((query, similar, negative))

        return triplets

    def __len__(self):
        return len(self.triplets)

    def __getitem__(self, idx):
        anchor_img, positive_img, negative_img = self.triplets[idx]

        # 加载图像，对于anchor（查询图像）使用查询区域
        if anchor_img in self.query_regions:
            anchor_path = os.path.join(self.image_dir, anchor_img)
            anchor = crop_query_region(anchor_path, self.query_regions[anchor_img])
        else:
            anchor = Image.open(os.path.join(self.image_dir, anchor_img)).convert('RGB')

        positive = Image.open(os.path.join(self.image_dir, positive_img)).convert('RGB')
        negative = Image.open(os.path.join(self.image_dir, negative_img)).convert('RGB')

        # 应用变换
        if self.transform:
            anchor = self.transform(anchor)
            positive = self.transform(positive)
            negative = self.transform(negative)

        return anchor, positive, negative, anchor_img, positive_img, negative_img


# 特征提取网络
class FeatureExtractorNet(nn.Module):
    def __init__(self, embedding_dim=512, pretrained=True):
        super(FeatureExtractorNet, self).__init__()
        # 使用预训练的ResNet50作为基础网络
        base_model = models.resnet50(pretrained=pretrained)
        # 移除最后的全连接层
        self.base_model = nn.Sequential(*list(base_model.children())[:-1])
        # 添加新的全连接层，将特征维度降到embedding_dim
        self.fc = nn.Linear(2048, embedding_dim)
        self.embedding_dim = embedding_dim

    def forward(self, x):
        x = self.base_model(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        # L2归一化
        x = nn.functional.normalize(x, p=2, dim=1)
        return x


# 三元组损失函数
class TripletLoss(nn.Module):
    def __init__(self, margin=0.3):
        super(TripletLoss, self).__init__()
        self.margin = margin

    def forward(self, anchor, positive, negative):
        # 计算正样本对之间的距离
        pos_dist = torch.sum((anchor - positive) ** 2, dim=1)
        # 计算负样本对之间的距离
        neg_dist = torch.sum((anchor - negative) ** 2, dim=1)
        # 计算三元组损失
        loss = torch.clamp(pos_dist - neg_dist + self.margin, min=0.0)
        # 返回平均损失
        return torch.mean(loss)


# 加载Holidays数据集的groundtruth
def load_holidays_groundtruth(gt_path):
    with open(gt_path, 'r') as f:
        gt_data = json.load(f)

    queries = {}
    for item in gt_data.values():
        query_img = item['query']
        similar_imgs = item['similar']
        queries[query_img] = similar_imgs

    return queries


# 加载Oxford5k数据集的groundtruth
def load_oxford_groundtruth(gt_dir):
    queries = {}
    query_regions = {}  # 存储查询区域信息

    # 获取所有查询文件
    query_files = glob.glob(os.path.join(gt_dir, '*_query.txt'))

    for query_file in query_files:
        # 从查询文件名中提取查询ID
        query_id = os.path.basename(query_file).split('_query.txt')[0]

        # 读取查询图像信息
        with open(query_file, 'r') as f:
            line = f.readline().strip().split(' ')

            # 处理图像名称，移除前缀（如oxc1_）
            raw_img_name = line[0]
            if '_' in raw_img_name:
                # 移除前缀，保留主要部分
                img_name_parts = raw_img_name.split('_')
                if len(img_name_parts) >= 2:
                    # 通常格式是 oxc1_oxford_003410，我们要保留oxford_003410
                    img_name = '_'.join(img_name_parts[1:])
                else:
                    img_name = raw_img_name
            else:
                img_name = raw_img_name

            # 添加.jpg扩展名
            if not img_name.endswith('.jpg'):
                img_name += '.jpg'

            # 解析查询区域坐标
            if len(line) >= 5:
                x1, y1, x2, y2 = map(float, line[1:5])
                query_regions[img_name] = (x1, y1, x2, y2)
            else:
                query_regions[img_name] = None

        # 读取good和ok的相关图像
        good_imgs = []
        good_file = os.path.join(gt_dir, f"{query_id}_good.txt")
        if os.path.exists(good_file):
            with open(good_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        # 同样处理相关图像的名称
                        if not line.endswith('.jpg'):
                            line += '.jpg'
                        good_imgs.append(line)

        ok_file = os.path.join(gt_dir, f"{query_id}_ok.txt")
        if os.path.exists(ok_file):
            with open(ok_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        if not line.endswith('.jpg'):
                            line += '.jpg'
                        good_imgs.append(line)

        queries[img_name] = good_imgs

    return queries, query_regions


def crop_query_region(image_path, region_coords):
    """
    根据查询区域坐标裁剪图像

    Args:
        image_path: 图像路径
        region_coords: 区域坐标 (x1, y1, x2, y2)

    Returns:
        裁剪后的PIL图像
    """
    if region_coords is None:
        # 如果没有区域信息，返回整个图像
        return Image.open(image_path).convert('RGB')

    x1, y1, x2, y2 = region_coords
    image = Image.open(image_path).convert('RGB')

    # 裁剪查询区域
    cropped_image = image.crop((x1, y1, x2, y2))
    return cropped_image


# 划分数据集为训练集和验证集
def split_dataset(groundtruth, test_size=0.2, random_state=42):
    queries = list(groundtruth.keys())
    train_queries, val_queries = train_test_split(queries, test_size=test_size, random_state=random_state)

    train_gt = {q: groundtruth[q] for q in train_queries}
    val_gt = {q: groundtruth[q] for q in val_queries}

    return train_gt, val_gt


# 计算mAP
def calculate_map(model, dataloader, groundtruth, device):
    model.eval()
    features = {}
    filenames = []

    # 提取所有图像特征
    with torch.no_grad():
        for images, names in dataloader:
            images = images.to(device)
            batch_features = model(images)

            for i, name in enumerate(names):
                features[name] = batch_features[i].cpu().numpy()
                filenames.append(name)

    # 计算AP和mAP
    ap_scores = []

    for query, relevant_imgs in groundtruth.items():
        if query not in features:
            continue

        query_feature = features[query]

        # 计算所有图像与查询图像的相似度
        similarities = {}
        for img in filenames:
            if img == query:  # 跳过查询图像本身
                continue

            img_feature = features[img]
            # 计算余弦相似度
            similarity = np.dot(query_feature, img_feature) / (
                    np.linalg.norm(query_feature) * np.linalg.norm(img_feature))
            similarities[img] = similarity

        # 按相似度排序
        sorted_results = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
        retrieved_imgs = [img for img, _ in sorted_results[:5]]  # 取前5个结果

        # 计算AP
        ap = calculate_ap(retrieved_imgs, relevant_imgs)
        ap_scores.append(ap)

    # 计算mAP
    map_score = np.mean(ap_scores) if ap_scores else 0
    return map_score


def calculate_ap(retrieved, relevant):
    """计算平均精度(AP)"""
    relevant_set = set(relevant)
    precision_sum = 0
    num_relevant_retrieved = 0

    for i, item in enumerate(retrieved):
        if item in relevant_set:
            num_relevant_retrieved += 1
            precision = num_relevant_retrieved / (i + 1)
            precision_sum += precision

    if len(relevant_set) == 0:
        return 0

    return precision_sum / len(relevant_set)


# 训练函数
def train(model, train_loader, val_loader, val_eval_loader, val_gt, criterion, optimizer, scheduler, device,
          num_epochs=50):
    best_map = 0.0
    train_losses = []
    val_maps = []

    for epoch in range(num_epochs):
        # 训练阶段
        model.train()
        running_loss = 0.0

        for anchor, positive, negative, _, _, _ in tqdm(train_loader, desc=f"Epoch {epoch + 1}/{num_epochs}"):
            anchor, positive, negative = anchor.to(device), positive.to(device), negative.to(device)

            # 前向传播
            anchor_feat = model(anchor)
            positive_feat = model(positive)
            negative_feat = model(negative)

            # 计算损失
            loss = criterion(anchor_feat, positive_feat, negative_feat)

            # 反向传播和优化
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        epoch_loss = running_loss / len(train_loader)
        train_losses.append(epoch_loss)

        # 验证阶段
        model.eval()
        val_map = calculate_map(model, val_eval_loader, val_gt, device)
        val_maps.append(val_map)

        print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {epoch_loss:.4f}, Val mAP: {val_map:.4f}")

        # 保存最佳模型
        if val_map > best_map:
            best_map = val_map
            torch.save(model.state_dict(), 'best_model.pth')
            print(f"Model saved with mAP: {best_map:.4f}")

        # 学习率调整
        scheduler.step(val_map)

    # 绘制训练曲线
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(train_losses)
    plt.title('Training Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')

    plt.subplot(1, 2, 2)
    plt.plot(val_maps)
    plt.title('Validation mAP')
    plt.xlabel('Epoch')
    plt.ylabel('mAP')

    plt.tight_layout()
    plt.savefig('training_curves.png')
    plt.show()

    return train_losses, val_maps


# 评估函数
def evaluate(model, test_loader, test_gt, device):
    map_score = calculate_map(model, test_loader, test_gt, device)
    print(f"Test mAP: {map_score:.4f}")
    return map_score


# 图像数据集类（用于评估）
class ImageDataset(Dataset):
    def __init__(self, image_dir, transform=None, file_list=None, query_regions=None):
        self.image_dir = image_dir
        self.transform = transform
        self.query_regions = query_regions or {}

        if file_list:
            self.image_files = file_list
        else:
            self.image_files = [f for f in os.listdir(image_dir)
                                if f.endswith(('.jpg', '.jpeg', '.png'))]

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        img_name = self.image_files[idx]
        img_path = os.path.join(self.image_dir, img_name)

        # 如果是查询图像且有区域信息，则裁剪查询区域
        if img_name in self.query_regions:
            image = crop_query_region(img_path, self.query_regions[img_name])
        else:
            image = Image.open(img_path).convert('RGB')

        if self.transform:
            image = self.transform(image)

        return image, img_name


def save_features(model, dataloader, image_dir, save_path, device):
    """优化特征文件格式，仅保存文件名而非完整路径"""
    model.eval()
    features = {}
    with torch.no_grad():
        for images, names in tqdm(dataloader, desc="提取特征"):
            images = images.to(device)
            batch_features = model(images)

            for i, name in enumerate(names):
                features[name] = batch_features[i].cpu().numpy()

    # 只保存文件名和特征，不保存dataset_path
    data = {
        'features': features
    }
    with open(save_path, 'wb') as f:
        pickle.dump(data, f)


def main():
    # 固定随机种子
    torch.manual_seed(42)
    np.random.seed(42)
    random.seed(42)

    # 设置设备
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # 设置数据集路径
    dataset_name = config.DATASET_CONFIG['chose']  # 或 "Holidays"

    if dataset_name == "Holidays":
        image_dir = config.DATASET_CONFIG['Holidays']['image_dir']
        gt_path = config.DATASET_CONFIG['Holidays']['gr_path']
        groundtruth = load_holidays_groundtruth(gt_path)
        query_regions = {}
    else:  # Oxford5k
        image_dir = config.DATASET_CONFIG['Oxford5k']['image_dir']
        gt_dir = config.DATASET_CONFIG['Oxford5k']['gt_dir']
        groundtruth, query_regions = load_oxford_groundtruth(gt_dir)

    # 划分数据集
    train_gt, val_gt = split_dataset(groundtruth)

    # 定义数据变换
    train_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.RandomCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    val_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # 创建数据集和数据加载器
    train_dataset = TripletDataset(image_dir, train_gt, query_regions, transform=train_transform)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=4)

    # 创建用于验证的数据加载器
    all_images = set()
    for query, similar_list in groundtruth.items():
        all_images.add(query)
        for similar in similar_list:
            all_images.add(similar)

    val_eval_dataset = ImageDataset(image_dir, transform=val_transform,
                                    file_list=list(all_images), query_regions=query_regions)
    val_eval_loader = DataLoader(val_eval_dataset, batch_size=32, shuffle=False, num_workers=4)

    # 创建模型
    model = FeatureExtractorNet(embedding_dim=512, pretrained=True)
    model = model.to(device)

    # 定义损失函数和优化器
    criterion = TripletLoss(margin=0.3)
    optimizer = optim.Adam(model.parameters(), lr=0.0001)

    # 学习率调度器
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.1, patience=5, verbose=True)

    # 训练模型
    train_losses, val_maps = train(model, train_loader, None, val_eval_loader, val_gt,
                                   criterion, optimizer, scheduler, device, num_epochs=config.TRAIN_CONFIG['epoch'])

    # 加载最佳模型
    model.load_state_dict(torch.load('best_model.pth'))

    # 在整个数据集上评估
    test_dataset = ImageDataset(image_dir, transform=val_transform,
                                file_list=list(all_images), query_regions=query_regions)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False, num_workers=4)

    final_map = evaluate(model, test_loader, groundtruth, device)
    print(f"Final mAP on full dataset: {final_map:.4f}")

    # 保存最终模型
    torch.save({
        'model_state_dict': model.state_dict(),
        'embedding_dim': model.embedding_dim,
        'mAP': final_map,
        'query_regions': query_regions
    }, f'{dataset_name}_model.pth')

    # 保存特征文件
    save_features(model, test_loader, image_dir, config.TRAIN_CONFIG['save_path']['single'].format(dataset_type=dataset_name.lower()), device)


def visualize_retrieval_with_region(model, query_img, image_dir, test_loader, query_regions, top_k=5):
    # 提取所有图像特征
    model.eval()
    features = {}
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    with torch.no_grad():
        for images, names in test_loader:
            images = images.to(device)
            batch_features = model(images)

            for i, name in enumerate(names):
                features[name] = batch_features[i].cpu().numpy()

    # 加载查询图像（包含区域裁剪）
    query_path = os.path.join(image_dir, query_img)
    if query_img in query_regions:
        query_image = crop_query_region(query_path, query_regions[query_img])
        original_image = Image.open(query_path).convert('RGB')
    else:
        query_image = Image.open(query_path).convert('RGB')
        original_image = query_image

    # 计算相似度并获取结果
    query_feature = features[query_img]
    similarities = {}
    for img, feature in features.items():
        if img != query_img:
            similarity = np.dot(query_feature, feature) / (np.linalg.norm(query_feature) * np.linalg.norm(feature))
            similarities[img] = similarity

    sorted_results = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
    top_results = sorted_results[:top_k]

    # 可视化
    plt.figure(figsize=(20, 8))

    # 显示原始查询图像
    plt.subplot(2, top_k + 1, 1)
    plt.imshow(original_image)
    plt.title("Original Query")
    plt.axis('off')

    # 显示查询区域
    plt.subplot(2, top_k + 1, top_k + 2)
    plt.imshow(query_image)
    plt.title("Query Region")
    plt.axis('off')

    # 显示检索结果
    for i, (img, sim) in enumerate(top_results):
        img_path = os.path.join(image_dir, img)
        plt.subplot(2, top_k + 1, i + 2)
        plt.imshow(Image.open(img_path))
        plt.title(f"Rank {i + 1}: {sim:.3f}")
        plt.axis('off')

    plt.tight_layout()
    plt.savefig(f'retrieval_with_region_{query_img}.png', dpi=150, bbox_inches='tight')
    plt.show()


# 实现在线检索系统
def build_retrieval_system(model_path, image_dir, dataset_type="oxford", transform=None):
    """
    Args:
        model_path: 模型路径
        image_dir: 图像目录
        dataset_type: 数据集类型 ("oxford" 或 "holidays")
        transform: 图像变换
    """
    # 加载模型
    checkpoint = torch.load(model_path)
    model = FeatureExtractorNet(embedding_dim=checkpoint['embedding_dim'])
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()

    if torch.cuda.is_available():
        model = model.cuda()

    # 获取查询区域信息
    if dataset_type == "oxford" and 'oxford_query_regions' in checkpoint:
        query_regions = checkpoint['oxford_query_regions']
    elif dataset_type == "holidays" and 'holidays_query_regions' in checkpoint:
        query_regions = checkpoint['holidays_query_regions']
    else:
        query_regions = {}

    # 如果没有提供transform，使用默认的
    if transform is None:
        transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    # 创建数据集和数据加载器
    dataset = ImageDataset(image_dir, transform=transform, query_regions=query_regions)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=False, num_workers=4)

    # 提取所有图像特征
    features = {}
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    with torch.no_grad():
        for images, names in tqdm(dataloader, desc="提取特征"):
            images = images.to(device)
            batch_features = model(images)

            for i, name in enumerate(names):
                features[name] = batch_features[i].cpu().numpy()

    # 创建检索函数
    def retrieve(query_path, top_k=5):
        # 获取查询图像名称
        query_name = os.path.basename(query_path)

        # 加载并预处理查询图像
        if query_name in query_regions:
            query_image = crop_query_region(query_path, query_regions[query_name])
        else:
            query_image = Image.open(query_path).convert('RGB')

        query_tensor = transform(query_image).unsqueeze(0).to(device)

        # 提取查询图像特征
        with torch.no_grad():
            query_feature = model(query_tensor).cpu().numpy().squeeze()

        # 计算相似度
        similarities = {}
        for img, feature in features.items():
            if img != query_name:  # 跳过查询图像本身
                similarity = np.dot(query_feature, feature) / (np.linalg.norm(query_feature) * np.linalg.norm(feature))
                similarities[img] = similarity

        # 按相似度排序
        sorted_results = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
        return sorted_results[:top_k]

    return retrieve, query_regions


# 多数据集训练
def train_multi_dataset():
    # 设置随机种子
    torch.manual_seed(42)
    np.random.seed(42)
    random.seed(42)

    # 设置设备
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # 加载Holidays数据集
    holidays_image_dir = config.DATASET_CONFIG['Holidays']['image_dir']
    holidays_gt_path = config.DATASET_CONFIG['Holidays']['gt_path']
    holidays_groundtruth = load_holidays_groundtruth(holidays_gt_path)
    holidays_query_regions = {}  # Holidays数据集没有查询区域信息

    # 加载Oxford5k数据集
    oxford_image_dir = config.DATASET_CONFIG['Oxford5k']['image_dir']
    oxford_gt_dir = config.DATASET_CONFIG['Oxford5k']['gt_dir']
    oxford_groundtruth, oxford_query_regions = load_oxford_groundtruth(oxford_gt_dir)

    # 划分数据集
    holidays_train_gt, holidays_val_gt = split_dataset(holidays_groundtruth)
    oxford_train_gt, oxford_val_gt = split_dataset(oxford_groundtruth)

    # 定义数据变换
    train_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.RandomCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    val_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # 创建数据集和数据加载器
    holidays_train_dataset = TripletDataset(holidays_image_dir, holidays_train_gt,
                                            holidays_query_regions, transform=train_transform)
    oxford_train_dataset = TripletDataset(oxford_image_dir, oxford_train_gt,
                                          oxford_query_regions, transform=train_transform)

    # 合并数据集
    combined_train_dataset = torch.utils.data.ConcatDataset([holidays_train_dataset, oxford_train_dataset])
    combined_train_loader = DataLoader(combined_train_dataset, batch_size=32, shuffle=True, num_workers=4)

    # 创建用于验证的数据集
    holidays_all_images = set()
    for query, similar_list in holidays_groundtruth.items():
        holidays_all_images.add(query)
        for similar in similar_list:
            holidays_all_images.add(similar)

    oxford_all_images = set()
    for query, similar_list in oxford_groundtruth.items():
        oxford_all_images.add(query)
        for similar in similar_list:
            oxford_all_images.add(similar)

    holidays_val_dataset = ImageDataset(holidays_image_dir, transform=val_transform,
                                        file_list=list(holidays_all_images),
                                        query_regions=holidays_query_regions)
    holidays_val_loader = DataLoader(holidays_val_dataset, batch_size=32, shuffle=False, num_workers=4)

    oxford_val_dataset = ImageDataset(oxford_image_dir, transform=val_transform,
                                      file_list=list(oxford_all_images),
                                      query_regions=oxford_query_regions)
    oxford_val_loader = DataLoader(oxford_val_dataset, batch_size=32, shuffle=False, num_workers=4)

    # 创建模型
    model = FeatureExtractorNet(embedding_dim=512, pretrained=True)
    model = model.to(device)

    # 定义损失函数和优化器
    criterion = TripletLoss(margin=0.3)
    optimizer = optim.Adam(model.parameters(), lr=0.0001)

    # 学习率调度器
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.1, patience=5, verbose=True)

    # 训练模型
    num_epochs = config.TRAIN_CONFIG['epoch']
    best_map = 0.0
    train_losses = []
    holidays_maps = []
    oxford_maps = []

    for epoch in range(num_epochs):
        # 训练阶段
        model.train()
        running_loss = 0.0

        for batch in tqdm(combined_train_loader, desc=f"Epoch {epoch + 1}/{num_epochs}"):
            anchor, positive, negative = batch[:3]
            anchor, positive, negative = anchor.to(device), positive.to(device), negative.to(device)

            # 前向传播
            anchor_feat = model(anchor)
            positive_feat = model(positive)
            negative_feat = model(negative)

            # 计算损失
            loss = criterion(anchor_feat, positive_feat, negative_feat)

            # 反向传播和优化
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        epoch_loss = running_loss / len(combined_train_loader)
        train_losses.append(epoch_loss)

        # 验证阶段
        model.eval()
        holidays_map = calculate_map(model, holidays_val_loader, holidays_val_gt, device)
        oxford_map = calculate_map(model, oxford_val_loader, oxford_val_gt, device)
        avg_map = (holidays_map + oxford_map) / 2

        holidays_maps.append(holidays_map)
        oxford_maps.append(oxford_map)

        print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {epoch_loss:.4f}")
        print(f"Holidays mAP: {holidays_map:.4f}, Oxford mAP: {oxford_map:.4f}, Avg mAP: {avg_map:.4f}")

        # 保存最佳模型
        if avg_map > best_map:
            best_map = avg_map
            torch.save({
                'model_state_dict': model.state_dict(),
                'embedding_dim': model.embedding_dim,
                'holidays_mAP': holidays_map,
                'oxford_mAP': oxford_map,
                'avg_mAP': avg_map,
                'holidays_query_regions': holidays_query_regions,
                'oxford_query_regions': oxford_query_regions
            }, 'best_multi_dataset_model.pth')
            print(f"当前最佳模型为 Epoch {epoch+1}，平均 mAP: {best_map:.4f}")

        # 学习率调整
        scheduler.step(avg_map)

    # 绘制训练曲线
    plt.figure(figsize=(15, 5))

    plt.subplot(1, 3, 1)
    plt.plot(train_losses)
    plt.title('Training Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')

    plt.subplot(1, 3, 2)
    plt.plot(holidays_maps, label='Holidays')
    plt.plot(oxford_maps, label='Oxford')
    plt.plot([(h + o) / 2 for h, o in zip(holidays_maps, oxford_maps)], label='Average')
    plt.title('Validation mAP')
    plt.xlabel('Epoch')
    plt.ylabel('mAP')
    plt.legend()

    plt.subplot(1, 3, 3)
    plt.plot(holidays_maps, 'o-', label='Holidays')
    plt.plot(oxford_maps, 's-', label='Oxford')
    plt.title('Dataset Comparison')
    plt.xlabel('Epoch')
    plt.ylabel('mAP')
    plt.legend()

    plt.tight_layout()
    plt.savefig('multi_dataset_training_curves.png')
    plt.show()

    # 加载最佳模型并进行最终评估
    checkpoint = torch.load('best_multi_dataset_model.pth', weights_only=False)
    model.load_state_dict(checkpoint['model_state_dict'])

    # 在完整数据集上评估
    holidays_test_dataset = ImageDataset(holidays_image_dir, transform=val_transform,
                                         file_list=list(holidays_all_images),
                                         query_regions=holidays_query_regions)
    holidays_test_loader = DataLoader(holidays_test_dataset, batch_size=32, shuffle=False, num_workers=4)

    oxford_test_dataset = ImageDataset(oxford_image_dir, transform=val_transform,
                                       file_list=list(oxford_all_images),
                                       query_regions=oxford_query_regions)
    oxford_test_loader = DataLoader(oxford_test_dataset, batch_size=32, shuffle=False, num_workers=4)

    holidays_final_map = evaluate(model, holidays_test_loader, holidays_groundtruth, device)
    oxford_final_map = evaluate(model, oxford_test_loader, oxford_groundtruth, device)

    print(f"Final Holidays mAP: {holidays_final_map:.4f}")
    print(f"Final Oxford mAP: {oxford_final_map:.4f}")
    print(f"Final Average mAP: {(holidays_final_map + oxford_final_map) / 2:.4f}")

    # 保存特征文件
    save_features(model, holidays_test_loader, holidays_image_dir, config.TRAIN_CONFIG['save_path']['multi']['holidays'], device)
    save_features(model, oxford_test_loader, oxford_image_dir, config.TRAIN_CONFIG['save_path']['multi']['oxford'], device)


if __name__ == "__main__":
    # main()
    # 如果要训练多数据集模型，取消下面的注释
    train_multi_dataset()