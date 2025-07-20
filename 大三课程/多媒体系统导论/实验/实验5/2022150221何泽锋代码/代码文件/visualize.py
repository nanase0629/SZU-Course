import sys
import os
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QScrollArea, QComboBox, QGridLayout,
    QProgressBar, QMessageBox, QDialog, QLineEdit, QFormLayout
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import torch
from torchvision import transforms
from PIL import Image as PILImage
import pickle
import torch.nn as nn
import torchvision.models as models
import numpy.core._dtype_ctypes

# 路径处理工具函数
def resource_path(relative_path):
    """获取资源的绝对路径，支持开发环境和PyInstaller打包环境"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller打包后的临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    # 开发环境
    return os.path.join(os.path.abspath("."), relative_path)


# 配置路径（使用resource_path处理）
MODEL_PATH = resource_path("best_multi_dataset_model.pth")
OXFORD_FEATURES_PATH = resource_path("oxford_features.pkl")
HOLIDAYS_FEATURES_PATH = resource_path("holidays_features.pkl")


# 直接在可视化代码中定义FeatureExtractorNet类
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


class DatasetSelectionDialog(QDialog):
    """数据集选择对话框，优化路径验证和用户交互"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择数据集路径")
        self.resize(600, 200)

        layout = QVBoxLayout(self)

        # 创建表单布局
        form_layout = QFormLayout()

        # Oxford数据集路径选择
        self.oxford_path = QLineEdit()
        oxford_browse_btn = QPushButton("浏览...")
        oxford_browse_btn.clicked.connect(lambda: self.browse_directory(self.oxford_path, "选择Oxford数据集"))

        oxford_layout = QHBoxLayout()
        oxford_layout.addWidget(self.oxford_path)
        oxford_layout.addWidget(oxford_browse_btn)

        # Holidays数据集路径选择
        self.holidays_path = QLineEdit()
        holidays_browse_btn = QPushButton("浏览...")
        holidays_browse_btn.clicked.connect(lambda: self.browse_directory(self.holidays_path, "选择Holidays数据集"))

        holidays_layout = QHBoxLayout()
        holidays_layout.addWidget(self.holidays_path)
        holidays_layout.addWidget(holidays_browse_btn)

        # 添加到表单布局
        form_layout.addRow("Oxford数据集路径:", oxford_layout)
        form_layout.addRow("Holidays数据集路径:", holidays_layout)

        # 按钮布局
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.validate_paths)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)

        # 添加所有布局到主布局
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)

    def browse_directory(self, line_edit, dialog_title):
        """打开目录选择对话框并更新对应的行编辑控件"""
        directory = QFileDialog.getExistingDirectory(self, dialog_title)
        if directory:
            line_edit.setText(directory)

    def validate_paths(self):
        """验证用户选择的路径有效性"""
        oxford_dir = self.oxford_path.text()
        holidays_dir = self.holidays_path.text()

        if not oxford_dir or not holidays_dir:
            QMessageBox.critical(self, "错误", "请选择两个数据集的路径!")
            return

        if not os.path.isdir(oxford_dir) or not os.path.isdir(holidays_dir):
            QMessageBox.critical(self, "错误", "所选路径不是有效的目录!")
            return

        self.accept()

    def get_selected_paths(self):
        """获取用户选择的有效路径"""
        return self.oxford_path.text(), self.holidays_path.text()


class FeatureLoadingThread(QThread):
    """特征加载线程，动态拼接用户指定的数据集路径"""
    progress_updated = pyqtSignal(int, str)
    loading_complete = pyqtSignal(dict)

    def __init__(self, feature_files, oxford_dir, holidays_dir):
        super().__init__()
        self.feature_files = feature_files
        self.oxford_dir = oxford_dir
        self.holidays_dir = holidays_dir

    def run(self):
        all_features = {}
        total_files = len(self.feature_files)

        for i, (dataset_name, file_path) in enumerate(self.feature_files.items()):
            self.progress_updated.emit(int((i / total_files) * 100), f"加载 {dataset_name} 特征...")

            try:
                # 使用resource_path获取特征文件路径（固定在exe同目录）
                full_path = resource_path(file_path)
                self.progress_updated.emit(int((i / total_files) * 100), f"正在读取特征文件: {full_path}")

                with open(full_path, 'rb') as f:
                    data = pickle.load(f)
                    features = data['features']

                    # 根据数据集类型设置根路径（用户选择的路径）
                    if dataset_name == "oxford":
                        root_dir = self.oxford_dir
                    else:  # holidays
                        root_dir = self.holidays_dir

                    # 拼接用户指定的路径和文件名
                    valid_count = 0
                    invalid_count = 0

                    for img_name, feature in features.items():
                        key = f"{dataset_name}_{img_name}"
                        # 确保路径存在
                        img_path = os.path.join(root_dir, img_name)
                        if os.path.exists(img_path):
                            all_features[key] = {
                                'feature': feature,
                                'path': img_path,
                                'dataset': dataset_name
                            }
                            valid_count += 1
                        else:
                            invalid_count += 1
                            # 只在加载时记录一次错误，避免过多消息
                            if invalid_count <= 5:  # 限制错误消息数量
                                self.progress_updated.emit(100, f"警告: 图像 {img_name} 不存在于 {root_dir}")

                    self.progress_updated.emit(int((i / total_files) * 100),
                                               f"已加载 {valid_count} 个有效特征，{invalid_count} 个文件不存在")

            except Exception as e:
                self.progress_updated.emit(100, f"加载失败: {str(e)}")
                return

        self.progress_updated.emit(100, f"特征加载完成，共加载 {len(all_features)} 个有效特征")
        self.loading_complete.emit(all_features)


class ImageRetrievalGUI(QMainWindow):
    def __init__(self, oxford_dir, holidays_dir):
        super().__init__()
        self.setWindowTitle("多数据集图像检索系统")
        self.setGeometry(100, 100, 1200, 800)

        # 用户选择的数据集路径
        self.oxford_dir = oxford_dir
        self.holidays_dir = holidays_dir

        # 数据集选择映射
        self.dataset_map = {
            "全部": [self.oxford_dir, self.holidays_dir],
            "Oxford5k": self.oxford_dir,
            "Holidays": self.holidays_dir
        }

        # 特征文件映射（仅文件名）
        self.feature_files = {
            "oxford": OXFORD_FEATURES_PATH,
            "holidays": HOLIDAYS_FEATURES_PATH
        }

        # 初始化组件
        self.init_widgets()
        self.load_model()
        self.load_features()  # 从文件加载特征

    def init_widgets(self):
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 顶部操作栏
        top_layout = QHBoxLayout()

        # 数据集选择下拉框
        self.dataset_combo = QComboBox()
        self.dataset_combo.addItems(["全部", "Oxford5k", "Holidays"])
        self.dataset_combo.currentTextChanged.connect(self.change_dataset)
        top_layout.addWidget(QLabel("检索数据集:"))
        top_layout.addWidget(self.dataset_combo)

        self.select_btn = QPushButton("选择查询图像")
        self.select_btn.clicked.connect(self.select_query_image)
        self.select_btn.setEnabled(False)  # 特征加载完成前禁用
        top_layout.addWidget(self.select_btn)

        main_layout.addLayout(top_layout)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.status_label = QLabel("准备加载特征...")
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(self.status_label)
        progress_layout.addWidget(self.progress_bar)
        main_layout.addLayout(progress_layout)

        # 图像显示区域
        display_layout = QHBoxLayout()

        # 查询图像区域
        query_group = QWidget()
        query_layout = QVBoxLayout(query_group)
        query_layout.addWidget(QLabel("查询图像"))

        self.query_label = QLabel()
        self.query_label.setFixedSize(256, 256)
        self.query_label.setStyleSheet("border: 1px solid #ddd;")
        query_layout.addWidget(self.query_label)

        display_layout.addWidget(query_group)

        # 结果区域
        results_group = QWidget()
        results_layout = QVBoxLayout(results_group)
        results_layout.addWidget(QLabel("检索结果"))

        self.results_scroll = QScrollArea()
        self.results_scroll.setWidgetResizable(True)
        self.results_widget = QWidget()
        self.results_grid = QGridLayout(self.results_widget)
        self.results_scroll.setWidget(self.results_widget)

        results_layout.addWidget(self.results_scroll)
        display_layout.addWidget(results_group)

        main_layout.addLayout(display_layout)

        # 当前使用的数据集
        self.current_datasets = [self.oxford_dir, self.holidays_dir]

    def load_model(self):
        """加载模型，使用resource_path处理路径"""
        try:
            # 加载检查点
            checkpoint_path = resource_path(MODEL_PATH)
            print(f"尝试加载模型的路径：{checkpoint_path}")
            checkpoint = torch.load(
                checkpoint_path,
                map_location=torch.device('cpu'),
                weights_only=False
            )

            # 使用本地定义的FeatureExtractorNet类
            self.model = FeatureExtractorNet(embedding_dim=checkpoint['embedding_dim'])
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.eval()

            # 加载查询区域
            self.oxford_regions = checkpoint.get('oxford_query_regions', {})
            self.holidays_regions = checkpoint.get('holidays_query_regions', {})

            print("模型加载成功")
        except Exception as e:
            QMessageBox.critical(self, "模型加载错误", f"无法加载模型: {str(e)}")
            sys.exit(1)

    def load_features(self):
        """从特征文件加载特征，使用用户指定的数据集路径"""
        # 检查特征文件是否存在
        missing_files = []
        for name, path in self.feature_files.items():
            full_path = resource_path(path)
            if not os.path.exists(full_path):
                missing_files.append(f"{name}: {full_path}")

        if missing_files:
            QMessageBox.critical(self, "错误",
                                 f"以下特征文件不存在:\n{', '.join(missing_files)}\n请确保特征文件在exe同目录。")
            sys.exit(1)

        # 创建并启动特征加载线程，传入用户路径
        self.feature_thread = FeatureLoadingThread(
            self.feature_files,
            self.oxford_dir,
            self.holidays_dir
        )
        self.feature_thread.progress_updated.connect(self.update_progress)
        self.feature_thread.loading_complete.connect(self.on_features_loaded)
        self.feature_thread.start()

    def update_progress(self, value, message):
        """更新进度条和状态标签"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)

    def on_features_loaded(self, features):
        """特征加载完成后的回调"""
        self.feature_dict = features
        self.select_btn.setEnabled(True)  # 启用查询按钮
        print(f"已成功加载 {len(self.feature_dict)} 张图像的特征")

    def preprocess_image(self, path, query_regions=None):
        """预处理图像（支持区域裁剪，使用用户路径）"""
        transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        img_name = os.path.basename(path)

        # 确定使用哪个数据集的查询区域
        if query_regions is None:
            if self.oxford_dir in path:
                query_regions = self.oxford_regions
            elif self.holidays_dir in path:
                query_regions = self.holidays_regions
            else:
                query_regions = {}

        # 应用查询区域裁剪
        if img_name in query_regions and query_regions[img_name]:
            x1, y1, x2, y2 = query_regions[img_name]
            img = PILImage.open(path).convert("RGB").crop((x1, y1, x2, y2))
        else:
            img = PILImage.open(path).convert("RGB")

        return transform(img).unsqueeze(0)

    def change_dataset(self, dataset_name):
        """切换检索的数据集"""
        self.current_datasets = self.dataset_map[dataset_name]
        print(f"已切换到数据集: {dataset_name}")

    def select_query_image(self):
        """打开文件选择对话框，使用resource_path处理路径"""
        path, _ = QFileDialog.getOpenFileName(self, "选择图像", "", "Images (*.jpg *.jpeg *.png)")
        if not path:
            return

        # 显示查询图像
        self.display_image(path, self.query_label)

        # 执行检索
        results = self.retrieve(path, top_k=5)  # 显示前5个结果
        self.display_results(results)

    def retrieve(self, query_path, top_k=10):
        """执行跨数据集检索，增强路径验证"""
        # 预处理查询图像
        query_tensor = self.preprocess_image(query_path)

        # 提取特征
        with torch.no_grad():
            query_feat = self.model(query_tensor).numpy().squeeze()

        # 计算相似度（根据选择的数据集过滤）
        similarities = []

        for key, item in self.feature_dict.items():
            # 如果选择了特定数据集，则过滤
            if isinstance(self.current_datasets, list):
                # "全部"数据集
                pass
            else:
                # 单个数据集
                dataset_prefix = 'oxford' if self.current_datasets == self.oxford_dir else 'holidays'
                if not key.startswith(dataset_prefix):
                    continue

            # 计算相似度
            sim = np.dot(query_feat, item['feature']) / (np.linalg.norm(query_feat) * np.linalg.norm(item['feature']))
            similarities.append((key, sim, item['path'], item['dataset']))

        # 按相似度排序
        similarities.sort(key=lambda x: x[1], reverse=True)

        # 调试：打印前3个结果的路径有效性
        for i, (key, sim, path, dataset) in enumerate(similarities[:3]):
            print(f"检索结果 {i + 1} - 路径: {path}, 存在: {os.path.exists(path)}")

        return similarities[:top_k]

    def display_image(self, path, label):
        """在QLabel中显示图像，增强路径处理和错误提示"""
        # 验证文件存在
        if not os.path.exists(path):
            label.setText(f"错误：文件不存在\n路径：{path}")
            return

        # 加载图像
        pixmap = QPixmap(path)
        if pixmap.isNull():
            label.setText(f"错误：无法加载图像\n路径：{path}\n可能格式不支持或文件损坏")
            return

        # 缩放并显示
        scaled_pixmap = pixmap.scaled(
            label.width(), label.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        label.setPixmap(scaled_pixmap)
        label.setAlignment(Qt.AlignCenter)

    def display_results(self, results):
        """显示检索结果（网格布局）"""
        # 清空现有结果
        while self.results_grid.count():
            child = self.results_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # 添加检索结果（每行显示3个）
        for i, (key, sim, path, dataset) in enumerate(results):
            row, col = divmod(i, 3)

            # 创建结果项
            result_item = QWidget()
            item_layout = QVBoxLayout(result_item)

            # 显示图像
            img_label = QLabel()
            img_label.setFixedSize(224, 224)
            img_label.setStyleSheet("border: 1px solid #ddd;")
            self.display_image(path, img_label)
            item_layout.addWidget(img_label)

            # 显示信息
            info_label = QLabel(f"相似度: {sim:.3f}\n数据集: {dataset.title()}")
            info_label.setAlignment(Qt.AlignCenter)
            item_layout.addWidget(info_label)

            # 添加到网格
            self.results_grid.addWidget(result_item, row, col)

        # 添加空白项以填充剩余空间
        for i in range(3 - len(results) % 3):
            if len(results) % 3 != 0:
                self.results_grid.addWidget(QLabel(""), row, col + i + 1)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # 设置高DPI支持
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    # 显示数据集选择对话框
    dialog = DatasetSelectionDialog()
    if dialog.exec_():
        oxford_dir, holidays_dir = dialog.get_selected_paths()

        # 验证用户输入
        if not oxford_dir or not holidays_dir:
            QMessageBox.critical(None, "错误", "请选择两个数据集的路径!")
            sys.exit(1)

        if not os.path.isdir(oxford_dir) or not os.path.isdir(holidays_dir):
            QMessageBox.critical(None, "错误", "所选路径不是有效的目录!")
            sys.exit(1)

        # 创建并显示主窗口
        window = ImageRetrievalGUI(oxford_dir, holidays_dir)
        window.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)