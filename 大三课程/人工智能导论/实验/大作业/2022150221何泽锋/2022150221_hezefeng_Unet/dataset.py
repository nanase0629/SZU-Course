from torch.utils.data import Dataset
import PIL.Image as Image
import os


def make_dataset(root):
    # root = "./data/train"
    imgs = []
    ori_path = os.path.join(root, "Data")
    ground_path = os.path.join(root, "Ground")
    names = os.listdir(ori_path)
    n = len(names)
    for i in range(n):
        img = os.path.join(ori_path, names[i])
        mask = os.path.join(ground_path, names[i])
        imgs.append((img, mask))
    return imgs


class LiverDataset(Dataset):
    def __init__(self, root, transform=None, target_transform=None):
        imgs = make_dataset(root)
        self.imgs = imgs
        self.transform = transform  # 图像变换函数
        self.target_transform = target_transform  # 标签图像变换函数

    def __getitem__(self, index):
        x_path, y_path = self.imgs[index]
        img_x = Image.open(x_path).convert('L')  # 加载并转换为灰度图
        img_y = Image.open(y_path).convert('L')
        if self.transform is not None:
            img_x = self.transform(img_x)
        if self.target_transform is not None:
            img_y = self.target_transform(img_y)
        return img_x, img_y

    def __len__(self):
        return len(self.imgs)   # 返回数据集中的样本数量
