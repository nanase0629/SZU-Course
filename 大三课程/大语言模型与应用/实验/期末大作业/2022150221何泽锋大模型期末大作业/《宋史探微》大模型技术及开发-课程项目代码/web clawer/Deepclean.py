import json
import os
import re
from typing import List, Dict, Any


def clean_content(content: str) -> str:
    """深度清洗文本内容，专门针对宋代史文本"""
    if not content:
        return ""

    # 初始处理：统一换行符和处理转义字符
    content = content.replace('\u00A0', ' ').replace('\t', ' ')  # 处理特殊空格和制表符
    content = content.replace('\r', '\n').replace('\\n', '\n')
    content = content.replace('##', '')
    content = content.replace("\n", '')
    # 1. 优先去除明显的无用内容块
    patterns_to_remove = [
        r'【阅读全文】', r'日期：\d{4}-\d{2}-\d{2}', r'\[\s*\d+\s*\]',  # 引用标记
        r'创建同名条目\n条目\n历史版本\n\d+', r'\n*历史版本\n\d+',  # 历史版本信息
        r'^[^\n]+-快懂百科\n',  # 标题行
        r'^[\u4e00-\u9fa5]+[之一二三四五六七八九十]+$',  # 分类描述行
        r'•\s*閩東語\s*/\s*Mìng-dĕ̤ng-ngṳ̄\s*\n?',  # 多语言标识
        r'•\s*Srpskohrvatski\s*/\s*српскохрватски\s*\n?',  # 多语言标识
        r'(doi|DOI|issn|ISSN|isbn|ISBN)[:：]\s*[^\s\n]+',  # 学术引用
        r'JSTOR\s+\d+', r'\(PDF\)', r'第\d+[頁页]\.?', r'\d+頁',  # 格式标记
        r'文物出版社\d+年出版', r'词条标签：.*', r'免责声明.*',  # 出版和声明
        r'网页[、\s]*微信[、\s]*知乎.*帮助[、\s]*首页',  # 导航元素
        r'任务[、\s]*任务中心.*个人中心',  # 任务中心
        r'词条[、\s]*添加义项.*分享到[、\s]*QQ空间[、\s]*新浪微博',  # 分享工具
        r'当前先前\d{2}:\d{2}\d{4}年\d{1,2}月\d{1,2}日.*?\d{2}:\d{2}[^\n]*',  # 编辑历史
        r'^(中文名|外文名|简称|首都|主要城市|时间)[\s:：].*?$',  # 标题属性
        r'报料邮箱:[^\n@]*@[^\n]*',  # 匹配报料邮箱（如 news@thepaper.cn）
        r'互联网新闻信息服务许可证[:：]\s*\d+',  # 许可证编号
        r'增值电信业务经营许可证[:：]\s*[A-Za-z0-9\-]+',  # 增值电信业务许可证
        r'©\s*\d{4}-\d{4}\s*[^\n]*',  # 版权声明（如 © 2014-2025）
        r'[^\n]{10,50}有限公司'  # 公司名称（匹配包含"有限公司"的长字符串）
    ]

    for pattern in patterns_to_remove:
        content = re.sub(pattern, '', content, flags=re.MULTILINE)

    # 2. 处理参考文献 (更精确的匹配)
    content = re.sub(r'［[^］]{1,30］\s*[^，]{10,50}，\s*[^，]{10,50}，\s*\d{4}年\s*[^。]{0,50}[。\n]?', '', content)
    content = re.sub(r'［[^］]{1,30］\s*[^，]{10,50}，\s*[^，]{10,50}出版社[^。]{0,50}[。\n]?', '', content)
    content = re.sub(r'[A-Z][a-z]+,?\s+[A-Z][a-zA-Z\s\.\,\&]+\s+\"?[^\"]+\"?,\s+[^,]+,\s+\d{4}[^\n]*', '', content)

    # 3. 处理换行符和空白
    # 先压缩连续换行符，再处理特殊换行情况
    content = re.sub(r'\n{3,}', '\n\n', content)  # 多个换行保留最多2个
    content = re.sub(r'\n\s+\n', '\n\n', content)  # 换行间的空白
    content = re.sub(r'^\s+', '', content, flags=re.MULTILINE)  # 行首空白
    content = re.sub(r'\s+$', '', content, flags=re.MULTILINE)  # 行尾空白

    # 特殊换行情况：数字行、项目符号行
    content = re.sub(r'^\d+\s*$', '', content, flags=re.MULTILINE)  # 单独数字行
    content = re.sub(r'^[•·]\s*', '', content, flags=re.MULTILINE)  # 项目符号行

    # 4. 清理内容结构
    # 书籍卷册信息保留内容
    content = re.sub(r'《([^》]*)》卷(\d+)〈([^〉]*)〉', r'《\1》第\2卷记载：', content)

    # 城市列表处理
    content = re.sub(r'主要城市\s*[:：]?\s*', '主要城市：', content)
    content = re.sub(r'([\u4e00-\u9fa5]+)\s+([\u4e00-\u9fa5]+)', r'\1、\2', content)  # 仅限中文间空格替换

    # 5. 统一标点和格式
    content = re.sub(r'[ \t]{2,}', ' ', content)  # 多个空格变一个
    content = re.sub(r'["""]{2,}', '"', content)  # 多个引号变一个
    content = re.sub(r"['']\s*", "'", content)  # 多个单引号变一个
    content = content.replace('，', '，').replace('。', '。')  # 确保中文标点
    content = re.sub(r'公元(\d+)年', r'\1年', content)  # 简化年份

    # 6. 最终整理
    content = re.sub(r'\n{2,}', '\n\n', content)  # 确保段落间最多一个空行
    content = content.strip()

    # 安全清洗
    content = clean_attack_content(content)

    return content


def is_valid_content(content: str) -> bool:
    """判断内容是否有效（包含有用的历史信息）"""
    if len(content) < 50:  # 提高最小长度要求
        return False

    # 检查是否包含无用的残留信息
    useless_patterns = [
        r'^[\s•·\-=\n]*$',  # 空白内容
        r'^[\d\s•·\-=]+$',  # 纯数字和符号
        r'^(展开|更多|词条|免责声明|参考文献|导航|帮助)$',
        r'^[A-Z][a-z]+,?\s+[A-Z][a-z]+$',  # 参考文献作者行
    ]

    for pattern in useless_patterns:
        if re.search(pattern, content, re.MULTILINE):
            return False

    # 检查是否包含宋代相关的关键词
    song_keywords = [
        '宋', '宋朝', '北宋', '南宋', '赵匡胤', '岳飞', '开封', '临安',
        '辽国', '金国', '元朝', '蒙古', '科举', '王安石', '变法',
        '靖康', '苏轼', '李清照', '辛弃疾', '朱熹', '理学'
    ]

    if any(keyword in content for keyword in song_keywords):
        return True

    # 检查历史相关术语
    history_terms = ['世纪', '王朝', '皇帝', '年号', '战争', '条约', '政权', '文化', '经济']
    if any(term in content for term in history_terms):
        return True

    # 检查历史时间模式
    if re.search(r'\b\d{3,4}年\b', content) or re.search(r'\b[唐宋元明]\b', content):
        return True

    return False

def process_json_array(input_file: str, output_file: str) -> None:
    """
    处理JSON数组文件
    """
    cleaned_data = []
    skipped_count = 0
    total_count = 0

    try:
        print("正在读取JSON文件...")
        with open(input_file, 'r', encoding='utf-8') as f:
            data_list = json.load(f)

        print(f"文件包含 {len(data_list)} 个条目")

        for i, data in enumerate(data_list):
            total_count += 1

            if i % 1000 == 0:
                print(f"处理进度: {i}/{len(data_list)}")

            if isinstance(data, dict) and 'content' in data and data['content']:
                original_content = data['content']
                cleaned_content = clean_content(original_content)

                if is_valid_content(cleaned_content):
                    cleaned_data.append({
                        'content': cleaned_content,
                        'source_id': data.get('id', f'unknown_{i}'),
                        'chunk_index': data.get('chunk_index', 0),
                        'title': data.get('title', ''),
                        'source': data.get('source', '')
                    })
                else:
                    skipped_count += 1
                    # 显示前几个被跳过的内容作为调试
                    if skipped_count <= 5:
                        print(f"跳过无效内容 (第{i}项): {cleaned_content[:100]}...")
            else:
                skipped_count += 1

    except FileNotFoundError:
        print(f"文件 {input_file} 不存在")
        return
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return
    except Exception as e:
        print(f"处理文件时出错: {e}")
        return

    # 保存清洗后的数据
    try:
        print("正在保存清洗后的数据...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)  # 使用标准JSON格式保存
    except Exception as e:
        print(f"保存文件时出错: {e}")
        return

    print(f"\n数据清洗完成！")
    print(f"原始条目数: {total_count}")
    print(f"有效条目数: {len(cleaned_data)}")
    print(f"跳过条目数: {skipped_count}")
    print(f"有效率: {len(cleaned_data) / total_count * 100:.2f}%")
    print(f"清洗后保存到: {output_file}")


def preview_file(input_file: str) -> None:
    """
    预览文件内容
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            # 读取前1000个字符来判断格式
            preview = f.read(1000)
            print("文件内容预览:")
            print("=" * 50)
            print(preview)
            print("=" * 50)

            # 尝试解析为JSON
            f.seek(0)
            try:
                data = json.load(f)
                if isinstance(data, list):
                    print(f"检测到JSON数组格式，包含 {len(data)} 个元素")
                    if len(data) > 0:
                        print("第一个元素的键:", list(data[0].keys()) if isinstance(data[0], dict) else "非字典类型")
                else:
                    print("检测到单个JSON对象")
            except:
                print("无法解析为标准JSON格式")

    except Exception as e:
        print(f"预览文件失败: {e}")


def get_json_files(directory):
    """获取目录下所有JSON文件"""
    if not os.path.exists(directory):
        print(f"错误：目录 '{directory}' 不存在")
        return []

    return [f for f in os.listdir(directory)
            if f.lower().endswith('.json') and os.path.isfile(os.path.join(directory, f))]


def select_json_file():
    """让用户选择JSON文件或输入路径"""
    input_dir = "output/clean"
    json_files = get_json_files(input_dir)

    if not json_files:
        print(f"在目录 '{input_dir}' 中未找到JSON文件")
        return None

    print("\n找到以下JSON文件:")
    for i, filename in enumerate(json_files, 1):
        print(f"[{i}] {filename}")

    print("\n[0] 手动输入文件路径")

    while True:
        choice = input("\n请选择文件 (输入编号): ").strip()

        if choice == '0':
            custom_path = input("请输入完整文件路径: ").strip()
            if os.path.isfile(custom_path) and custom_path.lower().endswith('.json'):
                return custom_path
            else:
                print("错误：无效的文件路径")
                continue

        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(json_files):
                return os.path.join(input_dir, json_files[choice_idx])
            else:
                print("错误：无效的选择")
        except ValueError:
            print("错误：请输入数字")


def generate_output_filename(input_filename):
    """生成输出文件名"""
    base_name = os.path.basename(input_filename)
    name_part, ext = os.path.splitext(base_name)

    # 处理格式如 "cleaned_data_时间戳.json"
    if name_part.startswith("cleaned_"):
        new_name = "recleaned" + name_part[7:]  # 替换前缀
    else:
        new_name = "recleaned_" + name_part

    return new_name + ext


def main():
    print("开始处理JSON文件...")
    print("=" * 50)

    # 选择输入文件
    input_file = select_json_file()
    if not input_file:
        print("未选择文件，程序退出")
        return

    # 生成输出文件路径
    output_dir = "output/reclean"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, generate_output_filename(input_file))

    print(f"\n输入文件: {input_file}")
    print(f"输出文件: {output_file}")

    # 预览文件
    preview_file(input_file)

    # 处理文件
    process_json_array(input_file, output_file)
    print(f"\n处理完成，文件已保存到: {output_file}")


def clean_attack_content(content: str) -> str:
    """检测并清洗攻击性内容，提升知识库安全性"""
    if not content:
        return ""

    # 常见prompt injection、代码注入、敏感词等
    attack_patterns = [
        r'(忽略(之前|以上)?所有指令)',
        r'(你现在是.*?助手)',
        r'(请以.*?身份回答)',
        r'(你被劫持|你被控制|你被黑客攻击)',        r'(os\.system|subprocess|eval|exec|import os|import sys)',
        r'(<script[\s\S]*?>[\s\S]*?</script>)',
        r'(黑客|炸弹|攻击|破解|木马|病毒|钓鱼|社工|爆破|入侵|后门|监听|扫描|绕过|劫持|植入|篡改|窃取|敏感信息)',
        r'(\bpassword\b|\bpasswd\b|\btoken\b|\bapi[_-]?key\b)',
        r'(base64\.b64decode|pickle\.loads|marshal\.loads)',
        r'(\bopenai\b.*?api)',
        r'(\bssh\b|\bftp\b|\btelnet\b|\brdp\b)',
        r'(\broot\b.*?密码)',
        r'(\bflag\b|\bctf\b)',
        r'(\badmin\b.*?密码)',
        r'(\b127\.0\.0\.1\b|localhost|内网穿透)',
        r'(\bcsrf\b|\bxss\b|\bsql注入\b|\b命令注入\b)',
        r'(\b爆破\b|\b撞库\b|\b社工库\b)',
        r'(\b刷单\b|\b薅羊毛\b|\b外挂\b)',
        r'(\b色情\b|\b赌博\b|\b毒品\b|\b枪支\b|\b走私\b)',
    ]
    for pattern in attack_patterns:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE)
    return content


if __name__ == "__main__":
    main()