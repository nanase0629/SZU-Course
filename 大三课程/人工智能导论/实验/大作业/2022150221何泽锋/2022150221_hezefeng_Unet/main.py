import torch
import argparse
import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
from torch.utils.data import DataLoader
from torch import nn, optim
from torchvision.transforms import transforms
from unet import Unet
from dataset import LiverDataset
from common_tools import transform_invert


def makedir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)


val_interval = 1
# 是否使用cuda
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 均为灰度图像，只需要转换为tensor
x_transforms = transforms.ToTensor()
y_transforms = transforms.ToTensor()

# 训练和验证损失曲线
train_curve = list()
valid_curve = list()


# 训练模型
def train_model(model, criterion, optimizer, dataload, args):
    makedir('./model')
    model_path = args.ckpt
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path, map_location=device))
        start_epoch = 0
        print('加载成功！')
    else:
        start_epoch = 0
        print('无保存模型，将从头开始训练！')

    # 初始化最小损失为一个很大的数
    best_val_loss = float('inf')
    best_weights = None
    num_epochs = args.epoch

    for epoch in range(start_epoch + 1, num_epochs):
        print(f'Epoch {epoch}/{num_epochs}')
        print('-' * 10)
        dt_size = len(dataload.dataset)
        epoch_loss = 0
        step = 0
        for x, y in dataload:
            step += 1
            inputs = x.to(device)
            labels = y.to(device)
            optimizer.zero_grad()  # 清空梯度
            outputs = model(inputs)  # 前向传播

            loss = criterion(outputs, labels)  # 计算损失
            loss.backward()  # 反向传播

            optimizer.step()  # 更新权重
            epoch_loss += loss.item()  # 累计损失

        epoch_loss /= step
        print(f"Epoch {epoch} Loss: {epoch_loss:.3f}")

        # 定期保存模型
        if (epoch + 1) % 50 == 0:
            torch.save(model.state_dict(), f'./model/weights_{epoch + 1}.pth')

        # 验证模型
        valid_dataset = LiverDataset("data/val", transform=x_transforms, target_transform=y_transforms)
        valid_loader = DataLoader(valid_dataset, batch_size=4, shuffle=True)
        if (epoch + 2) % val_interval == 0:
            loss_val = 0.
            model.eval()
            with torch.no_grad():
                step_val = 0
                for x, y in valid_loader:
                    step_val += 1
                    x = x.type(torch.FloatTensor)
                    inputs = x.to(device)
                    labels = y.to(device)
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)
                    loss_val += loss.item()

                loss_val /= step_val
                print(f"Epoch {epoch} Validation Loss: {loss_val:.3f}")

                # 如果当前验证损失小于最佳损失，则保存模型
                if loss_val < best_val_loss:
                    best_val_loss = loss_val
                    best_weights = model.state_dict().copy()
                    print(f"保存最优模型")
                    print()
                    torch.save(best_weights, './model/best_weights.pth')

    print(f"训练完成，最优模型权重保存在 './model/best_weights.pth'")

    train_x = range(len(train_curve))
    train_y = train_curve

    train_iters = len(dataload)
    valid_x = np.arange(1, len(valid_curve) + 1) * train_iters * val_interval
    valid_y = valid_curve

    plt.plot(train_x, train_y, label='Train')
    plt.plot(valid_x, valid_y, label='Valid')

    plt.legend(loc='upper right')
    plt.ylabel('loss value')
    plt.xlabel('Iteration')
    plt.show()
    return model


# 训练过程
def train(args):
    model = Unet(1, 1).to(device)
    batch_size = args.batch_size
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters())
    liver_dataset = LiverDataset("./data/train", transform=x_transforms, target_transform=y_transforms)
    dataloaders = DataLoader(liver_dataset, batch_size=batch_size, shuffle=True, num_workers=4)

    train_model(model, criterion, optimizer, dataloaders, args)


# 显示模型的输出结果
def test(args):
    model = Unet(1, 1)
    model.load_state_dict(torch.load(args.ckpt, map_location='cuda'))
    liver_dataset = LiverDataset("data/val", transform=x_transforms, target_transform=y_transforms)
    dataloaders = DataLoader(liver_dataset, batch_size=1)

    save_root = './data/predict'

    model.eval()
    plt.ion()
    index = 0
    with torch.no_grad():
        for x, ground in dataloaders:
            x = x.type(torch.FloatTensor)
            y = model(x)
            x = torch.squeeze(x)
            x = x.unsqueeze(0)
            ground = torch.squeeze(ground)
            ground = ground.unsqueeze(0)
            img_ground = transform_invert(ground, y_transforms)
            img_x = transform_invert(x, x_transforms)
            img_y = torch.squeeze(y).numpy()

            pred_dir = os.path.join(save_root, f"predict_{index}")
            os.makedirs(pred_dir, exist_ok=True)

            src_path = os.path.join(pred_dir, "source_image_%d.png" % index)
            save_path = os.path.join(pred_dir, "output_image_%d.png" % index)
            ground_path = os.path.join(pred_dir, "ground_truth_%d.png" % index)
            img_ground.save(ground_path)
            img_x.save(src_path)
            cv2.imwrite(save_path, img_y * 255)
            index = index + 1

    print("分割完成")


# 计算Dice系数
def dice_calc(args):
    root = './data/predict'
    nums = len(os.listdir(root))
    dice = list()
    dice_mean = 0
    for i in range(nums):
        predict_folder = os.path.join(root, f"predict_{i}")
        ground_path = os.path.join(predict_folder, "ground_truth_%d.png" % i)
        predict_path = os.path.join(predict_folder, "output_image_%d.png" % i)
        img_ground = cv2.imread(ground_path)
        img_predict = cv2.imread(predict_path)
        intersec = 0
        x = 0
        y = 0
        for w in range(256):
            for h in range(256):
                intersec += img_ground.item(w, h, 1) * img_predict.item(w, h, 1) / (255 * 255)
                x += img_ground.item(w, h, 1) / 255
                y += img_predict.item(w, h, 1) / 255
        if x + y == 0:
            current_dice = 1
        else:
            current_dice = round(2 * intersec / (x + y), 3)
        dice_mean += current_dice
        dice.append(current_dice)
    dice_mean /= len(dice)
    print("dice:\n", dice)
    print("dice_mean:", dice_mean)


if __name__ == '__main__':
    print(f"当前使用的设备是: {device}")
    # 参数解析
    parse = argparse.ArgumentParser()
    parse.add_argument("--action", type=str, help="train, test or dice", default="train")
    parse.add_argument("--batch_size", type=int, default=4)
    parse.add_argument("--ckpt", type=str, help="the path of model weight file", default="./model/best_weights.pth")
    parse.add_argument('--epoch', type=int, default=10)
    args = parse.parse_args()

    if args.action == "train":
        train(args)
    elif args.action == "test":
        test(args)
    elif args.action == "dice":
        dice_calc(args)
