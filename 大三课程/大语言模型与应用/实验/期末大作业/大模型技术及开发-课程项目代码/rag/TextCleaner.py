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
from config_web import (
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

    def __init__(self, max_pages=None, crawl_depth=None):
        self.session = requests.Session()
        self.session.headers.update(DATA_SOURCES["headers"])
        self.allowed_keywords = DATA_SOURCES["allowed_namespaces"]
        self.disallowed_domains = DATA_SOURCES["disallowed_domains"]
        self.crawled_urls = set()
        self.allowed_languages = set(DATA_SOURCES.get("allowed_languages", ["zh-cn"]))
        # 使用传入的参数或配置文件中的默认值
        self.max_pages = max_pages if max_pages is not None else DATA_SOURCES["max_pages"]
        self.crawl_depth = crawl_depth if crawl_depth is not None else DATA_SOURCES["crawl_depth"]
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

    def collect_web_data_with_depth(self, start_urls: List[str]):
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

                if current_depth < self.crawl_depth:
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
        for keyword in DATA_SOURCES["allowed_namespaces"]:
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
        text = re.sub(r'\n{3,}', '\n\n', text)
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

    def clean_content(self, content: str) -> str:
        """深度清洗文本内容，专门针对宋代史文本"""
        if not content:
            return ""

        # 去除开头连续的栏目/导航/广告块（如首页、讲述历史上那些有趣的事、人物等）
        content = re.sub(
            r'^(首页|讲述历史上那些有趣的事[、,，人物]*|专题|影视|解梦|百家姓|成语|明星|历史|教育|三国|新闻|手机版|百科|再现历史|生活|说剧|英文版|历史话题|MILITARY TOPIC|探寻历史风云旧事)[\\s\\-\\|、,，]*\n+', 
            '', 
            content, 
            flags=re.MULTILINE
        )
        # 可多次去除，直到开头不再有这些栏目
        while True:
            new_content = re.sub(
                r'^(首页|讲述历史上那些有趣的事[、,，人物]*|专题|影视|解梦|百家姓|成语|明星|历史|教育|三国|新闻|手机版|百科|再现历史|生活|说剧|英文版|历史话题|MILITARY TOPIC|探寻历史风云旧事)[\\s\\-\\|、,，]*\n+', 
                '', 
                content, 
                flags=re.MULTILINE
            )
            if new_content == content:
                break
            content = new_content

        # 初始处理：统一换行符和处理转义字符
        content = content.replace('\u00A0', '').replace('\t', '')  # 处理特殊空格和制表符
        content = content.replace('\r', '\n').replace('\\n', '\n')
        content = content.replace('##', '')

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
        content = re.sub(r'\u3010[^\u3011]{1,30}\u3011\s*[^，]{10,50}，\s*[^，]{10,50}，\s*\d{4}年\s*[^。]{0,50}[。\n]?', '', content)
        content = re.sub(r'\u3010[^\u3011]{1,30}\u3011\s*[^，]{10,50}，\s*[^，]{10,50}出版社[^。]{0,50}[。\n]?', '', content)
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
        content = re.sub(r"''+", "'", content)   # 多个单引号变一个
        content = content.replace('，', '，').replace('。', '。')  # 确保中文标点
        content = re.sub(r'公元(\d+)年', r'\1年', content)  # 简化年份

        # 6. 最终整理
        # 先统一所有空白字符为普通换行
        content = re.sub(r'[ \u3000\t\r\f\v]+', '', content)  # 移除所有空格、全角空格、制表符等
        # 再压缩多余空行
        content = re.sub(r'\n{3,}', '\n\n', content)  # 多于2个换行压缩为2个
        content = re.sub(r'(\n\s*){3,}', '\n\n', content)  # 多于2个"空白+换行"压缩为2个
        content = content.strip()

        # 移除常见栏目/导航/广告等短行
        patterns_to_remove_extra = [
            r'^[\\s\\|\\-\\·\\•\\u4e00-\\u9fa5]{2,40}$',  # 只含栏目词、符号、短行
            r'^(首页|专题|百科|再现历史|生活|说剧|英文版|历史话题|MILITARY TOPIC|探寻历史风云旧事|人物|影视|解梦|百家姓|成语|明星|历史|教育|三国|新闻|手机版)\\s*$',
            r'^[\\|\\-\\·\\•\\s]+$',  # 只含分隔符的行
            r'^[\\s\\|\\-\\·\\•]+$',  # 只含空白和符号
            r'^[\\u4e00-\\u9fa5]{1,8}$',  # 单独一行的短栏目词
        ]
        for pattern in patterns_to_remove_extra:
            content = re.sub(pattern, '', content, flags=re.MULTILINE)

        # 移除多余的"|"和"-"分隔符
        content = re.sub(r'\\|', '', content)
        content = re.sub(r'-{2,}', '', content)

        # 再次压缩多余空行
        content = re.sub(r'\n{2,}', '\n', content)
        
        # 清洗攻击性内容
        content = self.clean_attack_content(content)

        return content

    def clean_attack_content(self, content: str) -> str:
        """检测并清洗攻击性内容，提升知识库安全性"""
        if not content:
            return ""

        # 常见prompt injection、代码注入、敏感词等
        attack_patterns = [
            r'(忽略(之前|以上)?所有指令)',
            r'(你现在是.*?助手)',
            r'(请以.*?身份回答)',
            r'(你被劫持|你被控制|你被黑客攻击)',
            r'(os\.system|subprocess|eval|exec|import os|import sys)',
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

class RAGDataCollector:
    """RAG数据收集主类"""

    def __init__(self, max_pages=None, crawl_depth=None):
        self.scraper = WebScraper(max_pages, crawl_depth)
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
        crawled_data = self.scraper.collect_web_data_with_depth(urls)
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

        # 返回生成的文件名供后续处理使用
        return cleaned_path

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


def get_json_files(directory):
    """获取目录下所有JSON文件"""
    if not os.path.exists(directory):
        print(f"错误：目录 '{directory}' 不存在")
        return []
    return [f for f in os.listdir(directory)
            if f.lower().endswith('.json') and os.path.isfile(os.path.join(directory, f))]


def select_json_file(input_dir):
    """让用户选择JSON文件或输入路径"""
    json_files = get_json_files(input_dir)

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
                    return os.path.join(input_dir, json_files[choice_idx])
                print("错误：无效的选择")
            except ValueError:
                print("错误：请输入数字")

    return input("\n请输入JSON文件路径: ").strip()


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
                cleaned_content = TextCleaner.clean_content(original_content)

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

    return output_file  # 返回处理后的文件路径


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

        return output_path  # 返回生成的txt文件路径
    except Exception as e:
        print(f"处理失败: {e}")
        return None


def main():
    """主函数"""
    logger.info(f"启动{SYSTEM_CONFIG['project_name']} v{SYSTEM_CONFIG['version']}")

    # 获取用户输入的爬取深度和数量
    try:
        depth = int(input("\n请输入爬取深度 (建议1-3，0表示只爬取起始URL): ").strip())
        if depth < 0:
            print("深度不能为负数，使用默认值1")
            depth = 1

        max_pages = int(input("请输入最大爬取页面数量 (建议50-500): ").strip())
        if max_pages <= 0:
            print("数量必须大于0，使用默认值100")
            max_pages = 100

        # 如果深度为0，只爬取1个页面
        if depth == 0:
            max_pages = 1
            print("深度为0，将只爬取1个页面")

    except ValueError:
        print("输入无效，使用默认配置")
        depth = DATA_SOURCES["crawl_depth"]
        max_pages = DATA_SOURCES["max_pages"]

    collector = RAGDataCollector(max_pages, depth)


    # 网页数据采集
    print("\n=== 网页数据采集 ===")
    user_urls = input("请输入要爬取的URL（多个用逗号分隔，回车使用默认URL）: ").strip()
    urls = [url.strip() for url in user_urls.split(',')] if user_urls else DATA_SOURCES["default_urls"]
    collector.collect_web_data(urls)


    # 预处理数据
    if not collector.raw_data:
        logger.error("未收集到任何数据，程序退出")
        return

    print("\n=== 数据预处理 ===")
    collector.preprocess_data()

    # 保存数据
    print("\n=== 保存数据 ===")
    cleaned_json_path = collector.save_data()

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

    # Deepclean步骤 (自动处理)
    print("\n=== Deepclean步骤 ===")
    input_file = cleaned_json_path
    output_dir = "output/reclean"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, generate_output_filename(input_file))

    print(f"\n输入文件: {input_file}")
    print(f"输出文件: {output_file}")

    preview_file(input_file)
    processed_file = process_json_array(input_file, output_file)

    # JsontoTXT步骤 (自动处理)
    if processed_file:
        input_path = processed_file
        output_txt_dir = "output/txt"
        txt_file = process_json_to_txt(input_path, output_txt_dir)
        if txt_file:
            print(f"转换为TXT文件保存到: {txt_file}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("用户中断程序")
    except Exception as e:
        logger.error(f"程序异常: {str(e)}", exc_info=True)