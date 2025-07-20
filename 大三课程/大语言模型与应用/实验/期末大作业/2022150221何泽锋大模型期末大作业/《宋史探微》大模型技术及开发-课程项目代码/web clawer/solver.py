import os
import json
import time
import re
import logging
import heapq
from datetime import datetime
from typing import List, Dict, Any, Tuple
from urllib.parse import urlparse, urljoin, unquote

import requests
from bs4 import BeautifulSoup
import PyPDF2
import markdown

import config
from config import (
    SYSTEM_CONFIG, DATA_SOURCES, TEXT_PROCESSING,
    FILE_CONFIG, OUTPUT_FILES, LOGGING_CONFIG
)

# 设置日志
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG["level"]),
    format=LOGGING_CONFIG["format"],
    handlers=[
        logging.FileHandler(LOGGING_CONFIG["file"]),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WebScraper:
    """Web数据爬取类（强化主题过滤和爬取效率）"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(DATA_SOURCES["headers"])
        self.allowed_keywords = DATA_SOURCES["allowed_namespaces"]
        self.disallowed_domains = DATA_SOURCES["disallowed_domains"]
        self.crawled_urls = set()
        self.allowed_languages = set(DATA_SOURCES.get("allowed_languages", ["zh-cn"]))
        self.max_pages = DATA_SOURCES["max_pages"]
        self.pages_crawled = 0
        self.valid_pages_crawled = 0

    def is_valid_domain(self, url: str) -> bool:
        """检查域名是否允许"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        for disallowed in self.disallowed_domains:
            if disallowed in domain:
                return False
        return True

    def is_relevant_content(self, content: str) -> bool:
        """检查内容是否包含宋代相关关键词"""
        for keyword in self.allowed_keywords:
            if re.search(keyword, content, re.IGNORECASE):
                return True
        return False

    def is_relevant_url(self, url: str) -> bool:
        """检查URL路径是否包含关键词（提高内链相关性）"""
        try:
            # 解码URL中的特殊字符
            decoded_url = unquote(url)
            for keyword in self.allowed_keywords:
                if keyword in decoded_url:
                    return True
        except:
            pass
        return False

    def scrape_url(self, url: str) -> Dict[str, Any]:
        """爬取单个URL的内容（支持任意网站）"""
        if not self.is_valid_domain(url):
            logger.warning(f"跳过禁止域名的页面: {url}")
            return None

        try:
            # 检查页面限制
            if self.valid_pages_crawled >= self.max_pages:
                logger.warning(f"已达到最大爬取页面限制({self.max_pages})")
                return None

            self.pages_crawled += 1
            logger.info(f"开始爬取({self.pages_crawled}): {url}")

            response = self.session.get(url, timeout=DATA_SOURCES["timeout"])
            response.raise_for_status()
            response.encoding = response.apparent_encoding or SYSTEM_CONFIG["encoding"]

            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('title') or soup.find('h1')
            title_text = title.text.strip() if title else urlparse(url).path

            content = self._extract_content(soup)
            if not content or not self.is_relevant_content(content):
                logger.warning(f"内容无关或为空，跳过: {url}")
                return None

            self.valid_pages_crawled += 1
            logger.info(f"成功爬取({self.valid_pages_crawled}/{self.max_pages}): {url}")

            return {
                "url": url,
                "title": title_text,
                "content": content,
                "soup": soup,  # 保存soup对象用于内链提取
                "timestamp": datetime.now().isoformat(),
                "source_type": "web"
            }

        except Exception as e:
            logger.error(f"爬取失败 {url}: {str(e)}")
            return None

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """通用内容提取（适配多种网站结构）"""
        # 移除无用元素
        for selector in TEXT_PROCESSING["remove_elements"]:
            for elem in soup.select(selector):
                elem.decompose()

        # 优先提取主要内容区域
        main_areas = [
            soup.find('main'),
            soup.find('article'),
            soup.find('section', {'class': re.compile(r'content|article|main', re.IGNORECASE)}),
            soup.find('div', {'class': re.compile(r'content|article|main', re.IGNORECASE)})
        ]

        content = ""
        for area in main_areas:
            if area:
                paragraphs = []
                for elem in area.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
                    text = elem.get_text(strip=True)
                    if text and len(text) > 20:  # 提高内容质量门槛
                        if elem.name.startswith('h'):
                            paragraphs.append(f"\n\n## {text} ##\n")
                        elif elem.name == 'li':
                            paragraphs.append(f"• {text}")
                        else:
                            paragraphs.append(text)
                content = '\n'.join(paragraphs)
                if content:
                    break  # 找到主要内容后停止

        # 兜底处理：提取整个页面文本（去除脚本和样式）
        if not content:
            content = soup.get_text(separator='\n', strip=True)
            content = re.sub(r'\s{2,}', '\n', content)  # 压缩空白

        # 最终清洗
        content = self.clean_text(content)
        return content

    def clean_text(self, text: str) -> str:
        """通用文本清洗"""
        for pattern in TEXT_PROCESSING["remove_patterns"]:
            text = re.sub(pattern, '', text, flags=re.MULTILINE)
        text = re.sub(r'\[.*?\]', '', text)  # 移除方括号内容（如标注）
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def get_link_relevance_score(self, link: Any, base_url: str) -> int:
        """计算链接的相关性评分"""
        score = 0

        # 1. URL路径包含关键词
        new_url = urljoin(base_url, link['href'])
        if self.is_relevant_url(new_url):
            score += 3

        # 2. 链接文本包含关键词
        link_text = link.get_text(strip=True)
        for keyword in self.allowed_keywords:
            if keyword in link_text:
                score += 2

        # 3. 父元素文本包含关键词
        parent = link.parent
        if parent:
            parent_text = parent.get_text(strip=True)
            for keyword in self.allowed_keywords:
                if keyword in parent_text:
                    score += 1

        return score

    def collect_web_data_with_depth(self, start_urls: List[str], depth: int):
        """按深度爬取任意网站（智能过滤，优先级队列）"""
        # 使用优先级队列：(优先级, url, 深度)
        # 优先级 = 深度 * -1 (深度小的优先) + 相关性评分
        url_queue = []
        for url in start_urls:
            if self.is_valid_domain(url):
                # 初始URL优先级最高
                heapq.heappush(url_queue, (-10, url, 0))

        crawled_data = []

        while url_queue and self.valid_pages_crawled < self.max_pages:
            priority, url, current_depth = heapq.heappop(url_queue)
            if url in self.crawled_urls:
                continue

            result = self.scrape_url(url)
            if result:
                crawled_data.append(result)
                self.crawled_urls.add(url)

                if current_depth < depth:
                    soup = result.get('soup')
                    if soup:
                        try:
                            # 获取所有内链并按相关性排序
                            links = soup.find_all('a', href=True)
                            relevant_links = []

                            for link in links:
                                new_url = urljoin(url, link['href'])

                                # 过滤无效链接
                                if not new_url or new_url in self.crawled_urls:
                                    continue

                                # 过滤锚点链接
                                parsed_new = urlparse(new_url)
                                parsed_base = urlparse(url)
                                if parsed_new.path == parsed_base.path and parsed_new.fragment:
                                    continue

                                # 过滤外部链接
                                if self.is_external_link(new_url, url):
                                    continue

                                # 计算相关性评分
                                relevance = self.get_link_relevance_score(link, url)
                                if relevance > 0:  # 只保留相关链接
                                    # 优先级 = 深度(负值) + 相关性(负值，越大越优先)
                                    # 深度越小优先级越高，相关性越大优先级越高
                                    priority_score = -current_depth - 1 + (relevance * -0.1)
                                    heapq.heappush(url_queue, (priority_score, new_url, current_depth + 1))

                                    # 限制每个页面添加的内链数量
                                    if len(relevant_links) >= DATA_SOURCES["max_links_per_page"]:
                                        break

                        except Exception as e:
                            logger.error(f"提取内链失败 {url}: {str(e)}")

                # 控制爬取速度
                if DATA_SOURCES["delay_between_requests"] > 0:
                    time.sleep(DATA_SOURCES["delay_between_requests"])

        return crawled_data

    def is_external_link(self, new_url: str, base_url: str) -> bool:
        """判断是否为外部链接（跨域名）"""
        base_domain = urlparse(base_url).netloc.lower()
        new_domain = urlparse(new_url).netloc.lower()
        return base_domain != new_domain and new_domain != ''


class DocumentProcessor:
    """文档处理类（强化主题检测）"""

    def __init__(self):
        os.makedirs(FILE_CONFIG["upload_folder"], exist_ok=True)
        os.makedirs(FILE_CONFIG["output_folder"], exist_ok=True)

    def process_file(self, file_path: str) -> Dict[str, Any]:
        """处理上传的文件（支持任意格式，强化内容过滤）"""
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return None

        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in FILE_CONFIG["supported_formats"]:
            logger.error(f"不支持的文件格式: {file_ext}")
            return None

        if os.path.getsize(file_path) > FILE_CONFIG["max_file_size"]:
            logger.error(f"文件过大: {file_path}")
            return None

        content = self._extract_file_content(file_path, file_ext)
        if not content or not self.is_relevant_content(content):
            logger.warning(f"文档内容无关或为空，跳过: {file_path}")
            return None

        return {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "source_type": "document"
        }

    def _extract_file_content(self, file_path: str, file_ext: str) -> str:
        """统一文件内容提取"""
        if file_ext == '.txt':
            return self._process_txt(file_path)
        elif file_ext == '.md':
            return self._process_markdown(file_path)
        elif file_ext == '.pdf':
            return self._process_pdf(file_path)
        elif file_ext == '.html':
            return self._process_html(file_path)
        return ""

    def is_relevant_content(self, content: str) -> bool:
        """检查文档内容是否相关"""
        for keyword in config.DATA_SOURCES["allowed_namespaces"]:
            if re.search(keyword, content, re.IGNORECASE):
                return True
        return False

    def _process_txt(self, file_path: str) -> str:
        """处理TXT文件"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    def _process_markdown(self, file_path: str) -> str:
        """处理Markdown文件"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            md_content = f.read()
        html = markdown.markdown(md_content)
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text()

    def _process_pdf(self, file_path: str) -> str:
        """处理PDF文件"""
        text = ""
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text

    def _process_html(self, file_path: str) -> str:
        """处理HTML文件"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        scraper = WebScraper()
        return scraper.clean_text(soup.get_text())


class TextCleaner:
    """文本清洗类"""

    def clean_text(self, text: str) -> str:
        """温和的文本清洗，保留大部分内容"""
        for pattern in TEXT_PROCESSING["remove_patterns"]:
            text = re.sub(pattern, '', text, flags=re.MULTILINE)
        text = re.sub(r'\[\d+\]', '', text)  # 清理引用标记
        text = re.sub(r'[ \t]+', ' ', text)  # 合并空格和制表符
        text = re.sub(r'\n{3,}', '\n\n', text)  # 最多保留两个换行
        text = re.sub(r'「(.+?)」', r'"\1"', text)  # 中文引号转英文
        return text.strip()

    def chunk_text(self, text: str) -> List[str]:
        """智能文本分块，尽量保持段落完整性"""
        paragraphs = re.split(r'\n\n+', text)
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # 长段落分割为句子
            if len(para) > TEXT_PROCESSING["chunk_size"]:
                sentences = re.split(r'([。！？])', para)
                temp_chunk = current_chunk
                for i in range(0, len(sentences) - 1, 2):
                    sentence = sentences[i] + (sentences[i + 1] if i + 1 < len(sentences) else '')
                    if len(temp_chunk) + len(sentence) > TEXT_PROCESSING["chunk_size"]:
                        if temp_chunk and len(temp_chunk) >= TEXT_PROCESSING["min_chunk_size"]:
                            chunks.append(temp_chunk.strip())
                        temp_chunk = sentence
                    else:
                        temp_chunk += sentence
                current_chunk = temp_chunk
            else:
                if len(current_chunk) + len(para) + 2 <= TEXT_PROCESSING["chunk_size"]:
                    current_chunk = current_chunk + ("\n\n" + para) if current_chunk else para
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = para

        if current_chunk:
            chunks.append(current_chunk.strip())

        # 实现块重叠
        if TEXT_PROCESSING["chunk_overlap"] > 0:
            overlapped_chunks = []
            for i, chunk in enumerate(chunks):
                if i > 0:
                    prev_chunk = chunks[i - 1]
                    overlap = prev_chunk[-TEXT_PROCESSING["chunk_overlap"]:]
                    last_punct = max(overlap.rfind(p) for p in '。，；')
                    if last_punct > 0:
                        overlap = overlap[last_punct + 1:]
                    chunk = overlap + chunk
                overlapped_chunks.append(chunk)
            chunks = overlapped_chunks

        return chunks


class RAGDataCollector:
    """RAG数据收集主类"""

    def __init__(self):
        self.scraper = WebScraper()
        self.processor = DocumentProcessor()
        self.cleaner = TextCleaner()
        self.raw_data = []
        self.cleaned_data = []

    def collect_web_data(self, urls: List[str] = None):
        """收集网页数据"""
        if not urls:
            urls = DATA_SOURCES["default_urls"]
            logger.info("使用默认URL列表")

        logger.info(f"开始爬取 {len(urls)} 个网页")
        crawled_data = self.scraper.collect_web_data_with_depth(urls, DATA_SOURCES["crawl_depth"])
        self.raw_data.extend([d for d in crawled_data if d])
        logger.info(f"成功爬取 {len(self.raw_data)} 个相关网页")

    def collect_document_data(self, file_paths: List[str]):
        """收集文档数据"""
        logger.info(f"开始处理 {len(file_paths)} 个文档")
        valid_files = 0
        for file_path in file_paths:
            result = self.processor.process_file(file_path)
            if result:
                self.raw_data.append(result)
                valid_files += 1
        logger.info(f"成功处理 {valid_files} 个相关文档")

    def preprocess_data(self):
        """预处理所有数据"""
        logger.info("开始预处理数据")
        self.cleaned_data = []
        for item in self.raw_data:
            cleaned_content = self.cleaner.clean_text(item["content"])
            chunks = self.cleaner.chunk_text(cleaned_content)
            for i, chunk in enumerate(chunks):
                self.cleaned_data.append({
                    "id": f"{item.get('url', item.get('file_name', 'unknown'))}_{i}",
                    "source": item.get('url', item.get('file_path', 'unknown')),
                    "title": item.get('title', item.get('file_name', 'unknown')),
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "content": chunk,
                    "content_length": len(chunk),
                    "timestamp": item["timestamp"],
                    "source_type": item["source_type"]
                })
        logger.info(f"预处理完成，生成 {len(self.cleaned_data)} 个文本块")

    def save_data(self):
        """保存数据到JSON文件"""
        os.makedirs(FILE_CONFIG["output_folder"], exist_ok=True)

        # 生成时间戳后缀 (格式: 20250603_143022)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 移除raw_data中的soup对象（不可JSON序列化）
        cleaned_raw_data = []
        for item in self.raw_data:
            cleaned_item = item.copy()
            cleaned_item.pop('soup', None)  # 移除soup字段
            cleaned_raw_data.append(cleaned_item)

        # 保存原始数据（添加时间戳后缀）
        raw_filename, raw_ext = os.path.splitext(OUTPUT_FILES["raw_data"])
        raw_path = os.path.join(FILE_CONFIG["output_folder"], f"{raw_filename}_{timestamp}{raw_ext}")
        with open(raw_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned_raw_data, f, ensure_ascii=False, indent=2)
        logger.info(f"原始数据已保存到: {raw_path}")

        # 保存清洗后的数据（使用相同的时间戳后缀）
        cleaned_filename, cleaned_ext = os.path.splitext(OUTPUT_FILES["cleaned_data"])
        cleaned_path = os.path.join(FILE_CONFIG["output_folder"], f"{cleaned_filename}_{timestamp}{cleaned_ext}")
        with open(cleaned_path, 'w', encoding='utf-8') as f:
            json.dump(self.cleaned_data, f, ensure_ascii=False, indent=2)
        logger.info(f"清洗后的数据已保存到: {cleaned_path}")

        # 生成数据报告
        self._generate_report()

    def _generate_report(self):
        """生成数据处理报告"""
        report_path = os.path.join(FILE_CONFIG["output_folder"], "data_report.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"=== {SYSTEM_CONFIG['project_name']} 数据处理报告 ===\n")
            f.write(f"处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## 数据源统计\n")
            f.write(f"总数据源数量: {len(self.raw_data)}\n")
            web_sources = [d for d in self.raw_data if d['source_type'] == 'web']
            doc_sources = [d for d in self.raw_data if d['source_type'] == 'document']
            f.write(f"- 网页数据: {len(web_sources)} 个\n")
            f.write(f"- 文档数据: {len(doc_sources)} 个\n\n")

            f.write("## 文本块统计\n")
            f.write(f"总文本块数量: {len(self.cleaned_data)}\n")
            if self.cleaned_data:
                avg_length = sum(item['content_length'] for item in self.cleaned_data) / len(self.cleaned_data)
                f.write(f"平均文本块长度: {avg_length:.0f} 字符\n")
                min_length = min(item['content_length'] for item in self.cleaned_data)
                max_length = max(item['content_length'] for item in self.cleaned_data)
                f.write(f"最小文本块长度: {min_length} 字符\n")
                f.write(f"最大文本块长度: {max_length} 字符\n\n")

            f.write("## 数据源详情\n")
            for item in self.raw_data:
                source = item.get('url', item.get('file_name', 'unknown'))
                chunks_count = len([c for c in self.cleaned_data if c['source'] == source])
                f.write(f"- {source}: {chunks_count} 个文本块\n")

        logger.info(f"数据报告已生成: {report_path}")


def display_sample_data(cleaned_data: List[Dict[str, Any]], num_samples: int = 3) -> None:
    """显示样本数据"""
    print("\n=== 清洗后的数据样本 ===")
    for i, sample in enumerate(cleaned_data[:num_samples]):
        print(f"\n--- 样本 {i + 1} ---")
        print(f"ID: {sample['id']}")
        print(f"来源: {sample['source']}")
        print(f"标题: {sample['title']}")
        print(f"块索引: {sample['chunk_index'] + 1}/{sample['total_chunks']}")
        print(f"内容长度: {sample['content_length']} 字符")
        print(f"内容预览:")
        print("-" * 50)
        preview = sample['content'][:200] + "..." if len(sample['content']) > 200 else sample['content']
        print(preview)
        print("-" * 50)


def main():
    """主函数"""
    logger.info(f"启动{SYSTEM_CONFIG['project_name']} v{SYSTEM_CONFIG['version']}")
    collector = RAGDataCollector()

    # === 用户选择数据源类型 ===
    print("\n=== 数据源选择 ===")
    print("1. 网页搜索（含任意网站内链）")
    print("2. 本地文档导入")
    choice = input("请输入选项（1/2）: ").strip()

    if choice == "1":
        # 网页数据采集
        print("\n=== 网页数据采集 ===")
        user_urls = input("请输入要爬取的URL（多个用逗号分隔，回车使用默认URL）: ").strip()
        urls = [url.strip() for url in user_urls.split(',')] if user_urls else DATA_SOURCES["default_urls"]
        collector.collect_web_data(urls)

    elif choice == "2":
        # 文档数据导入
        print("\n=== 文档数据导入 ===")
        print(f"支持的文件格式: {', '.join(FILE_CONFIG['supported_formats'])}")
        file_paths = []
        while True:
            file_path = input("请输入文档路径（回车结束）: ").strip()
            if not file_path:
                break
            if os.path.exists(file_path):
                file_paths.append(file_path)
                print(f"已添加: {file_path}")
            else:
                print(f"文件不存在: {file_path}")
        if file_paths:
            collector.collect_document_data(file_paths)
        else:
            logger.error("未提供任何文档，程序退出")
            return
    else:
        logger.error("无效选项，程序退出")
        return

    # 预处理数据
    if not collector.raw_data:
        logger.error("未收集到任何数据，程序退出")
        return

    print("\n=== 数据预处理 ===")
    collector.preprocess_data()

    # 保存数据
    print("\n=== 保存数据 ===")
    collector.save_data()

    # 显示统计信息
    print("\n=== 数据统计 ===")
    print(f"原始数据条目: {len(collector.raw_data)}")
    print(f"清洗后文本块: {len(collector.cleaned_data)}")

    # 按来源类型统计
    web_count = len([d for d in collector.raw_data if d['source_type'] == 'web'])
    doc_count = len([d for d in collector.raw_data if d['source_type'] == 'document'])
    print(f"- 网页数据: {web_count} 条")
    print(f"- 文档数据: {doc_count} 条")

    # 显示样本数据
    if collector.cleaned_data:
        display_sample_data(collector.cleaned_data)

    print(f"\n查看详细报告: {os.path.join(FILE_CONFIG['output_folder'], 'data_report.txt')}")
    logger.info("数据采集和预处理完成！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("用户中断程序")
    except Exception as e:
        logger.error(f"程序异常: {str(e)}", exc_info=True)