import requests
from bs4 import BeautifulSoup
import logging
import re
from urllib.parse import urljoin, urlparse
import time

class WebScraper:
    def __init__(self, max_pages=2, crawl_depth=0):
        self.max_pages = max_pages
        self.crawl_depth = crawl_depth
        self.visited_urls = set()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape_url(self, url):
        """抓取单个URL的内容"""
        try:
            if url in self.visited_urls:
                return None
            self.visited_urls.add(url)

            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # 移除不需要的元素
            for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()

            # 提取标题
            title = soup.title.string if soup.title else ''
            title = title.strip() if title else ''

            # 提取正文内容
            content = ''
            for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                text = p.get_text().strip()
                if text:
                    content += text + '\n'

            return {
                'url': url,
                'title': title,
                'content': content.strip()
            }
        except Exception as e:
            logging.error(f"抓取URL失败 {url}: {str(e)}")
            return None

    def collect_web_data_with_depth(self, urls):
        """递归抓取网页内容"""
        results = []
        for url in urls:
            if len(results) >= self.max_pages:
                break

            result = self.scrape_url(url)
            if result:
                results.append(result)

            if self.crawl_depth > 0:
                try:
                    response = requests.get(url, headers=self.headers, timeout=10)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    links = soup.find_all('a', href=True)
                    
                    for link in links:
                        if len(results) >= self.max_pages:
                            break
                        
                        href = link['href']
                        absolute_url = urljoin(url, href)
                        parsed_url = urlparse(absolute_url)
                        
                        # 只处理同域名的链接
                        if parsed_url.netloc == urlparse(url).netloc:
                            result = self.scrape_url(absolute_url)
                            if result:
                                results.append(result)
                except Exception as e:
                    logging.error(f"处理链接失败 {url}: {str(e)}")

        return results 