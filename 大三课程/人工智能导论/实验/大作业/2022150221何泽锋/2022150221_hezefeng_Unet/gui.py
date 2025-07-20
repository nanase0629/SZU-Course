import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import torch
import numpy as np
import cv2
from unet import Unet

# 初始化设备
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 加载模型
def load_model(ckpt_path):
    model = Unet(1, 1).to(device)
    model.load_state_dict(torch.load(ckpt_path, map_location=device))
    model.eval()
    return model

# 计算Dice系数
def compute_dice(pred, ground_truth):
    # 确保输入图像是单通道或者三通道，进行相应的处理
    if pred.ndim == 3 and pred.shape[2] == 3:  # 如果是三通道彩色图像
        pred = cv2.cvtColor(pred, cv2.COLOR_BGR2GRAY)
    elif pred.ndim == 3 and pred.shape[2] == 1:  # 如果是单通道图像，但以三通道形式表示
        pred = pred[:, :, 0]
    # 确保图像是单通道灰度图像
    pred = pred.astype(np.float32) / 255.0

    if ground_truth.ndim == 3 and ground_truth.shape[2] == 3:  # 如果是三通道彩色图像
        ground_truth = cv2.cvtColor(ground_truth, cv2.COLOR_BGR2GRAY)
    elif ground_truth.ndim == 3 and ground_truth.shape[2] == 1:  # 如果是单通道图像，但以三通道形式表示
        ground_truth = ground_truth[:, :, 0]
    # 确保图像是单通道灰度图像
    ground_truth = ground_truth.astype(np.float32) / 255.0

    intersection = np.sum(pred * ground_truth)
    dice = (2. * intersection) / (np.sum(pred) + np.sum(ground_truth))
    return dice

# 分割图像
def segment_image(model, image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    image = cv2.resize(image, (256, 256))
    image = image.astype(np.float32) / 255.0
    image = np.expand_dims(image, axis=0)
    image = np.expand_dims(image, axis=0)
    image = torch.from_numpy(image).to(device)
    with torch.no_grad():
        output = model(image)
        output = torch.sigmoid(output)
        output = output.squeeze(0).cpu().numpy()  # 确保输出是二维的
        output = (output > 0.5).astype(np.uint8) * 255
    return output

# 显示图像
def display_images(original, ground_truth, prediction, dice_score):
    root = tk.Toplevel()
    root.title("Results")

    # 创建一个框架用于包含图片标签和文本标签
    frame = tk.Frame(root)
    frame.pack()

    # 将原始图像转换为PIL图像并显示
    original = Image.fromarray(original)
    original_photo = ImageTk.PhotoImage(original)
    original_label = tk.Label(frame, image=original_photo)
    original_label.image = original_photo
    original_label.grid(row=0, column=0)
    tk.Label(frame, text="原始图像").grid(row=1, column=0)

    # 将Ground Truth图像转换为PIL图像并显示
    ground_truth = Image.fromarray(ground_truth, mode='L')
    ground_truth_photo = ImageTk.PhotoImage(ground_truth)
    ground_truth_label = tk.Label(frame, image=ground_truth_photo)
    ground_truth_label.image = ground_truth_photo
    ground_truth_label.grid(row=0, column=1)
    tk.Label(frame, text="标签").grid(row=1, column=1)

    # 确保prediction是二维的，然后转换为PIL图像并显示
    if prediction.ndim == 3:
        prediction = prediction.squeeze(0)  # 移除额外的维度
    prediction = Image.fromarray(prediction, mode='L')
    prediction_photo = ImageTk.PhotoImage(prediction)
    prediction_label = tk.Label(frame, image=prediction_photo)
    prediction_label.image = prediction_photo
    prediction_label.grid(row=0, column=2)
    tk.Label(frame, text="分割图像").grid(row=1, column=2)

    # 创建Dice Score标签并显示
    dice_label = tk.Label(frame, text=f"Dice Score: {dice_score:.4f}")
    dice_label.grid(row=2, column=0, columnspan=3)


# GUI主函数
def main_gui():
    root = tk.Tk()
    root.title("Liver Segmentation")
    root.geometry("300x100")
    model = load_model("./model/best_weights.pth")

    def select_and_segment():
        original_path = filedialog.askopenfilename(title="Select Original Image", parent=root)
        ground_truth_path = filedialog.askopenfilename(title="Select Ground Truth Image", parent=root)
        if original_path and ground_truth_path:
            original = cv2.imread(original_path, cv2.IMREAD_GRAYSCALE)
            ground_truth = cv2.imread(ground_truth_path, cv2.IMREAD_GRAYSCALE)
            prediction = segment_image(model, original_path)
            dice_score = compute_dice(prediction, ground_truth)
            display_images(original, ground_truth, prediction, dice_score)

    button = tk.Button(root, text="Select and Segment Images", command=select_and_segment)
    button.pack()

    root.mainloop()

if __name__ == "__main__":
    main_gui()
