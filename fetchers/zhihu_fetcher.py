"""
知乎文章抓取器
"""
from bs4 import BeautifulSoup
from fetchers.base_fetcher import BaseFetcher
import re
from datetime import datetime


class ZhihuFetcher(BaseFetcher):
    """知乎文章抓取器"""

    def fetch_article(self, url: str) -> dict:
        self.headers['Referer'] = 'https://www.zhihu.com/'
        self._apply_cookies()

        try:
            html = self._fetch_html(url, headers=self.headers, timeout=30)
            soup = BeautifulSoup(html, 'html.parser')

            if 'answer' in url:
                return self._extract_answer(soup, url, html)
            return self._extract_article(soup, url, html)
        except Exception as e:
            print(f"抓取知乎内容失败: {e}")
            return {'title': '', 'author': '', 'pub_date': '', 'content': '', 'images': [], 'original_url': url}

    def _extract_article(self, soup, url, html):
        """专栏文章"""
        title_tag = soup.find('h1', class_='Post-Title') or soup.find('h1')
        title = title_tag.get_text().strip() if title_tag else '未知标题'

        author_tag = soup.find('meta', itemprop='author')
        author = author_tag['content'] if author_tag and author_tag.get('content') else '未知作者'

        pub_date = self._extract_date(html)
        content_div = soup.find('div', class_='RichText') or soup.find('div', itemprop='articleBody')
        content = str(content_div) if content_div else ''

        images = self._extract_images(content_div)
        return {'title': title, 'author': author, 'pub_date': pub_date, 'content': content, 'images': images, 'original_url': url}

    def _extract_answer(self, soup, url, html):
        """回答"""
        title_tag = soup.find('h1', class_='QuestionHeader-title') or soup.find('h1')
        title = title_tag.get_text().strip() if title_tag else '未知标题'

        author_tag = soup.find('span', class_='AuthorInfo-name') or soup.find('a', class_='UserLink-link')
        author = author_tag.get_text().strip() if author_tag else '未知作者'

        pub_date = self._extract_date(html)
        content_div = soup.find('div', class_='RichContent-inner') or soup.find('div', class_='Answer-richContent')
        content = str(content_div) if content_div else ''

        images = self._extract_images(content_div)
        return {'title': title, 'author': author, 'pub_date': pub_date, 'content': content, 'images': images, 'original_url': url}

    def _extract_date(self, html):
        """从 script 标签提取时间"""
        match = re.search(r'"created":\s*(\d+)', html) or re.search(r'"updatedTime":\s*(\d+)', html)
        if match:
            return datetime.fromtimestamp(int(match.group(1))).strftime('%Y-%m-%d %H:%M:%S')
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def _extract_images(self, content_div) -> list:
        if not content_div:
            return []
        images = []
        for fig in content_div.find_all('figure', class_='img'):
            img = fig.find('img')
            if img:
                src = img.get('data-actualsrc') or img.get('data-original') or img.get('src')
                if src:
                    images.append(src)
        return images
