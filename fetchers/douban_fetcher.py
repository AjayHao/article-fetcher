"""
豆瓣文章抓取器
"""
from bs4 import BeautifulSoup
from fetchers.base_fetcher import BaseFetcher
import re
from datetime import datetime


class DoubanFetcher(BaseFetcher):
    """豆瓣文章抓取器"""

    PAGE_TYPES = {
        'note': {'content': ['#link-report', '.note'], 'title': ['span[property="v:summary"]', 'h1']},
        'review': {'content': ['#link-report'], 'title': ['span[property="v:summary"]', 'h1']},
        'status': {'content': ['.status-content'], 'title': None},
    }

    def fetch_article(self, url: str) -> dict:
        self.headers['Referer'] = 'https://www.douban.com/'
        try:
            html = self._fetch_html(url, headers=self.headers, timeout=30)
            soup = BeautifulSoup(html, 'html.parser')

            page_type = self._detect_page_type(url)
            return self._extract(soup, url, page_type)
        except Exception as e:
            print(f"抓取豆瓣文章失败: {e}")
            return {'title': '', 'author': '', 'pub_date': '', 'content': '', 'images': [], 'original_url': url}

    def _detect_page_type(self, url: str) -> str:
        if 'note' in url:
            return 'note'
        elif 'review' in url:
            return 'review'
        elif 'status' in url:
            return 'status'
        return 'note'

    def _extract(self, soup, url, page_type):
        cfg = self.PAGE_TYPES.get(page_type, self.PAGE_TYPES['note'])

        # 标题
        title = '未知标题'
        if cfg['title']:
            for sel in cfg['title']:
                tag = soup.select_one(sel) if not sel.startswith('#') else soup.find(id=sel[1:])
                if not tag:
                    tag = soup.find(class_=sel[1:] if sel.startswith('.') else None, id=sel[1:] if sel.startswith('#') else None)
                if tag:
                    title = tag.get_text().strip()
                    break

        # 作者
        author_tag = (soup.find('a', class_='note-author') or
                      soup.find('a', property='v:reviewer') or
                      soup.find('a', class_='statustitle') or
                      soup.find('a', href=re.compile(r'/people/')))
        author = author_tag.get_text().strip() if author_tag else '未知作者'

        # 发布时间
        pub_date_tag = (soup.find('span', property='v:dtreviewed') or
                        soup.find('span', class_='note-time') or
                        soup.find('span', class_='pubdate'))
        pub_date = ''
        if pub_date_tag:
            pub_date = self._parse_date(pub_date_tag.get_text().strip())
        if not pub_date:
            pub_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 正文
        content = ''
        for sel in cfg['content']:
            tag = soup.find(id=sel[1:]) if sel.startswith('#') else soup.find(class_=sel[1:])
            if tag:
                # 移除版权信息等无关元素
                for unwanted in tag.find_all(class_=re.compile(r'copyright|actions|share')):
                    unwanted.decompose()
                content = str(tag)
                break

        # 广播特殊处理
        if page_type == 'status' and not content:
            content = (soup.find(class_='status-content') or soup.find(class_='status-content')).get_text().strip() if soup.find(class_='status-content') else ''
            title = content[:50] + '...' if len(content) > 50 else content or '豆瓣广播'

        # 图片
        images = []
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-original')
            if src and 'doubanio.com' in src:
                images.append(src)

        return {
            'title': title, 'author': author, 'pub_date': pub_date,
            'content': content, 'images': images, 'original_url': url
        }

    def _parse_date(self, date_text):
        if not date_text:
            return ''
        match = re.search(r'(\d{4}[-/]\d{2}[-/]\d{2})', date_text)
        if match:
            return match.group(1).replace('/', '-') + ' 00:00:00'
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
