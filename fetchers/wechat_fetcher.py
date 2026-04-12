"""
微信公众号文章抓取器
"""
import requests
from bs4 import BeautifulSoup
from fetchers.base_fetcher import BaseFetcher
import re
from datetime import datetime
from utils.logger import logger
from utils.http_client import get_with_retry, DEFAULT_USER_AGENT


class WechatFetcher(BaseFetcher):
    """微信公众号文章抓取器"""

    def __init__(self, cookies_file: str = None):
        super().__init__()
        self.cookies_file = cookies_file
        self.cookies = self._load_cookies() if cookies_file else {}

    def _load_cookies(self) -> dict:
        """加载 Cookies 文件（如果存在）"""
        try:
            cookies = {}
            with open(self.cookies_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        parts = line.strip().split('\t')
                        if len(parts) >= 6:
                            cookies[parts[5]] = parts[6]
            logger.debug(f"加载微信 Cookies: {len(cookies)} 个")
            return cookies
        except Exception as e:
            logger.warning(f"加载 Cookies 失败：{e}")
            return {}

    def fetch_article(self, url: str) -> dict:
        """
        抓取微信公众号文章内容

        Args:
            url (str): 微信公众号文章链接

        Returns:
            dict: 包含文章信息的字典
        """
        logger.info(f"开始抓取微信公众号文章：{url}")

        try:
            # 构建请求头
            headers = {
                'User-Agent': DEFAULT_USER_AGENT,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            }

            # 如果有 Cookies，添加到请求
            if self.cookies:
                headers['Cookie'] = '; '.join([f"{k}={v}" for k, v in self.cookies.items()])

            # 发送请求
            response = get_with_retry(url, headers=headers, timeout=30, retries=3)
            response.encoding = 'utf-8'

            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取标题
            title = self._extract_title(soup)

            # 提取作者
            author = self._extract_author(soup)

            # 提取发布时间
            pub_date = self._extract_pub_date(soup, response.text)

            # 提取正文内容
            content = self._extract_content(soup)

            # 提取图片链接
            images = self._extract_images(soup)

            logger.info(f"抓取成功 | 标题：{title} | 作者：{author} | 图片：{len(images)} 张")

            return {
                'title': title,
                'author': author,
                'pub_date': pub_date,
                'content': content,
                'images': images,
                'original_url': url
            }

        except Exception as e:
            logger.error(f"抓取微信公众号文章失败：{str(e)}")
            return {
                'title': '',
                'author': '',
                'pub_date': '',
                'content': '',
                'images': [],
                'original_url': url
            }

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取文章标题"""
        # 方案 1: id=activity-name
        title_tag = soup.find('h1', {'id': 'activity-name'})
        if title_tag:
            return title_tag.get_text().strip()

        # 方案 2: 第一个 h1 标签
        title_tag = soup.find('h1')
        if title_tag:
            return title_tag.get_text().strip()

        # 方案 3: meta 标签
        meta_title = soup.find('meta', {'property': 'og:title'})
        if meta_title and meta_title.get('content'):
            return meta_title['content']

        logger.warning("未找到文章标题")
        return '未知标题'

    def _extract_author(self, soup: BeautifulSoup) -> str:
        """提取作者"""
        # 方案 1: id=js_author_name
        author_tag = soup.find('a', {'id': 'js_author_name'})
        if author_tag:
            return author_tag.get_text().strip()

        # 方案 2: class=profile_nickname
        author_tag = soup.find('span', {'class': 'profile_nickname'})
        if author_tag:
            return author_tag.get_text().strip()

        # 方案 3: meta 标签
        meta_author = soup.find('meta', {'property': 'og:author'})
        if meta_author and meta_author.get('content'):
            return meta_author['content']

        logger.warning("未找到作者信息")
        return '未知作者'

    def _extract_pub_date(self, soup: BeautifulSoup, html_content: str) -> str:
        """提取发布时间"""
        # 方案 1: 从 script 标签中查找
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'publish_time' in script.string:
                match = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})', script.string)
                if match:
                    return match.group(1)

        # 方案 2: 查找时间戳
        timestamp_match = re.search(r'"ct":\s*(\d+)', html_content)
        if timestamp_match:
            timestamp = int(timestamp_match.group(1))
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

        # 方案 3: 返回当前时间
        logger.warning("未找到发布时间，使用当前时间")
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """提取正文内容"""
        # 方案 1: id=js_content
        content_div = soup.find('div', {'id': 'js_content'})
        if content_div:
            return str(content_div)

        # 方案 2: class=rich_media_content
        content_div = soup.find('div', {'class': 'rich_media_content'})
        if content_div:
            return str(content_div)

        logger.warning("未找到正文内容")
        return ''

    def _extract_images(self, soup: BeautifulSoup) -> list:
        """提取图片链接"""
        images = []

        # 查找正文区域
        content_div = soup.find('div', {'id': 'js_content'})
        if not content_div:
            content_div = soup.find('div', {'class': 'rich_media_content'})

        if content_div:
            img_tags = content_div.find_all('img')
            for img in img_tags:
                src = img.get('data-src') or img.get('src')
                if src:
                    # 处理微信图片的特殊参数
                    if 'wx_fmt=' in src:
                        src = src.split('?')[0]
                    images.append(src)

        logger.debug(f"提取到 {len(images)} 张图片")
        return images
