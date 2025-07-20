from fpdf import FPDF
import os
from typing import Optional


class TxtToPdfConverter:
    def __init__(self, font_size=12, line_height=1.5, margin=15):
        """初始化TXT转PDF转换器"""
        self.font_size = font_size
        self.line_height = line_height
        self.margin = margin

    def convert(self, txt_file: str, pdf_file: Optional[str] = None, title: Optional[str] = None) -> str:
        """
        将TXT文件转换为PDF文件

        参数:
            txt_file (str): 输入的TXT文件路径
            pdf_file (str, optional): 输出的PDF文件路径。默认为None，将使用TXT文件名。
            title (str, optional): PDF文件的标题。默认为None，将使用TXT文件名。

        返回:
            str: 生成的PDF文件路径
        """
        # 检查输入文件是否存在
        if not os.path.exists(txt_file):
            raise FileNotFoundError(f"输入文件不存在: {txt_file}")

        # 如果没有指定输出文件名，使用输入文件名并替换扩展名
        if pdf_file is None:
            base_name = os.path.splitext(os.path.basename(txt_file))[0]
            output_dir = os.path.dirname(txt_file)
            pdf_file = os.path.join(output_dir, f"{base_name}.pdf")

        # 确保输出目录存在
        output_dir = os.path.dirname(pdf_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 如果没有指定标题，使用输入文件名
        if title is None:
            title = os.path.splitext(os.path.basename(txt_file))[0]

        # 创建PDF对象
        pdf = FPDF()
        pdf.add_page()

        # 添加支持中文的字体
        fonts_added = False
        for font_path in [
            "/System/Library/Fonts/PingFang.ttc",  # macOS
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # Linux
            "C:/Windows/Fonts/simhei.ttf"  # Windows
        ]:
            if os.path.exists(font_path):
                try:
                    pdf.add_font('chinese', '', font_path, uni=True)
                    fonts_added = True
                    break
                except:
                    continue

        # 如果没有找到系统中文字体，使用内置字体
        if not fonts_added:
            print("警告: 未找到中文字体，中文可能无法正确显示")
            pdf.set_font('Arial', size=self.font_size)
        else:
            pdf.set_font('chinese', size=self.font_size)

        # 设置标题
        pdf.cell(200, 10, txt=title, ln=True, align='C')
        pdf.ln(10)  # 空行

        # 读取TXT文件内容
        with open(txt_file, 'r', encoding='utf-8') as file:
            content = file.read()

        # 将内容分割成段落
        paragraphs = content.split('\n\n')

        # 添加每个段落
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            pdf.multi_cell(
                w=0,
                h=self.font_size * self.line_height,
                txt=paragraph,
                border=0,
                align='L',
                fill=False
            )
            pdf.ln(self.font_size * 0.5)

        # 保存PDF文件
        pdf.output(pdf_file)
        print(f"成功将 {txt_file} 转换为 {pdf_file}")
        return pdf_file


def batch_convert(input_path: str, output_dir: Optional[str] = None, **kwargs) -> list:
    """
    批量转换TXT文件为PDF文件

    参数:
        input_path (str): 输入路径，可以是文件或目录
        output_dir (str, optional): 输出目录。默认为None，将使用输入文件的目录。
        **kwargs: 传递给TxtToPdfConverter.convert的参数

    返回:
        list: 生成的PDF文件路径列表
    """
    converter = TxtToPdfConverter(**kwargs)
    pdf_files = []

    if os.path.isfile(input_path):
        # 处理单个文件
        if input_path.lower().endswith('.txt'):
            output_file = None
            if output_dir:
                base_name = os.path.splitext(os.path.basename(input_path))[0]
                output_file = os.path.join(output_dir, f"{base_name}.pdf")
            pdf_files.append(converter.convert(input_path, output_file))
        else:
            print(f"跳过非TXT文件: {input_path}")

    elif os.path.isdir(input_path):
        # 处理目录中的所有TXT文件
        for filename in os.listdir(input_path):
            if filename.lower().endswith('.txt'):
                txt_file = os.path.join(input_path, filename)
                output_file = None
                if output_dir:
                    base_name = os.path.splitext(filename)[0]
                    output_file = os.path.join(output_dir, f"{base_name}.pdf")
                pdf_files.append(converter.convert(txt_file, output_file))
    else:
        raise ValueError(f"输入路径不存在: {input_path}")

    return pdf_files


# 设置输入和输出路径
if __name__ == "__main__":
    # 示例1: 转换单个文件
    input_file = "output/txt/recleaned_data_20250606_160205.txt"  # 替换为实际的输入文件路径
    output_file = "output/pdf/result.pdf"  # 替换为实际的输出文件路径

    converter = TxtToPdfConverter(font_size=12, line_height=1.5, margin=15)
    converter.convert(input_file, output_file, title="")

    # 示例2: 批量转换目录中的所有TXT文件
    # input_directory = "output/txt/recleaned_data_20250606_160205.txt"  # 替换为实际的输入目录路径
    # output_directory = "output/pdf/"  # 替换为实际的输出目录路径
    #
    # batch_convert(
    #     input_path=input_directory,
    #     output_dir=output_directory,
    #     font_size=14,
    #     line_height=1.8,
    #     margin=10
    # )