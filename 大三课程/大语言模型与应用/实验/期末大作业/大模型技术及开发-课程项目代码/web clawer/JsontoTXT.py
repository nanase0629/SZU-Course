import os
import json


def get_json_files(directory):
    """获取目录下所有JSON文件"""
    if not os.path.exists(directory):
        print(f"错误：目录 '{directory}' 不存在")
        return []
    return [f for f in os.listdir(directory)
            if f.lower().endswith('.json') and os.path.isfile(os.path.join(directory, f))]


def select_json_file():
    """让用户选择JSON文件或输入路径"""
    default_dir = "output/reclean"
    json_files = get_json_files(default_dir)

    if json_files:
        print("\n找到以下JSON文件:")
        for i, filename in enumerate(json_files, 1):
            print(f"[{i}] {filename}")
        print("\n[0] 手动输入文件路径")

        while True:
            choice = input("\n请选择文件 (输入编号): ").strip()
            if choice == '0':
                break
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(json_files):
                    return os.path.join(default_dir, json_files[choice_idx])
                print("错误：无效的选择")
            except ValueError:
                print("错误：请输入数字")

    return input("\n请输入JSON文件路径: ").strip()


def process_json_to_txt(input_path, output_dir):
    """处理JSON文件并保存为TXT"""
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 生成输出文件名（替换扩展名）
    base_name = os.path.basename(input_path)
    txt_name = os.path.splitext(base_name)[0] + ".txt"
    output_path = os.path.join(output_dir, txt_name)

    try:
        # 读取JSON数据
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 处理content字段（去除换行符）
        contents = []
        for item in data:
            content = item.get('content', '')  # 使用get()避免KeyError
            content = content.replace('\n', '')  # 去除换行符
            contents.append(content)

        # 保存为TXT文件（用##分隔）
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n##\n'.join(contents))

        print(f"\n处理完成！文件已保存到: {output_path}")
    except Exception as e:
        print(f"处理失败: {e}")


def main():
    print("开始处理JSON文件...")
    print("=" * 50)

    # 获取输入文件
    input_file = select_json_file()
    if not input_file or not os.path.isfile(input_file):
        print("错误：无效的文件路径，程序退出")
        return

    # 设置输出目录
    output_dir = "output/txt"

    # 处理文件
    process_json_to_txt(input_file, output_dir)


if __name__ == "__main__":
    main()