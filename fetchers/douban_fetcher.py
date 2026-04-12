import requests
from bs4 import BeautifulSoup
from fetchers.base_fetcher import BaseFetcher
import re
from datetime import datetime


class DoubanFetcher(BaseFetcher):
    """
    豆瓣文章抓取器
    """

    def __init__(self):
        super().__init__()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'https://www.douban.com/',
        }

    def fetch_article(self, url: str) -> dict:
        """
        抓取豆瓣文章内容

        Args:
            url (str): 豆瓣文章链接

        Returns:
            dict: 包含文章信息的字典
        """
        try:
            response = requests.get(url, headers=self.headers)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 根据豆瓣的不同页面类型提取信息
            if 'note' in url:
                # 豆瓣笔记
                return self._extract_note_info(soup, url)
            elif 'review' in url:
                # 豆瓣评论
                return self._extract_review_info(soup, url)
            elif 'status' in url:
                # 豆瓣广播
                return self._extract_status_info(soup, url)
            else:
                # 默认按笔记处理
                return self._extract_note_info(soup, url)

        except Exception as e:
            print(f"抓取豆瓣文章时发生错误: {str(e)}")
            return {
                'title': '',
                'author': '',
                'pub_date': '',
                'content': '',
                'images': [],
                'original_url': url
            }

    def _extract_note_info(self, soup, url):
        """
        提取豆瓣笔记信息
        """
        # 提取标题
        title_tag = soup.find('span', {'property': 'v:summary'}) or soup.find('h1')
        title = title_tag.get_text().strip() if title_tag else '未知标题'

        # 提取作者
        author_tag = soup.find('a', {'class': 'note-author'}) or soup.find('a', {'property': 'v:reviewer'})
        if not author_tag:
            # 尝试其他可能的作者标签
            author_tag = soup.find('a', href=re.compile(r'/people/'))
        author = author_tag.get_text().strip() if author_tag else '未知作者'

        # 提取发布时间
        pub_date_tag = soup.find('span', {'property': 'v:dtreviewed'}) or soup.find('span', class_='note-time')
        pub_date = ''
        if pub_date_tag:
            date_text = pub_date_tag.get_text().strip()
            # 尝试解析日期格式
            pub_date = self._parse_douban_date(date_text)
        if not pub_date:
            pub_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 提取正文内容
        content_div = soup.find('div', {'id': 'link-report'}) or soup.find('div', {'class': 'note'})
        content = ''
        if content_div:
            # 移除一些不需要的元素
            for unwanted in content_div.find_all(['div', 'p'], class_=re.compile(r'(note-copyright|actions|share-component)')):
                unwanted.decompose()
            content = str(content_div)

        # 提取图片链接
        images = []
        img_tags = soup.find_all('img')
        for img in img_tags:
            src = img.get('src') or img.get('data-original')
            if src and ('img1.doubanio.com' in src or 'img2.doubanio.com' in src or 'img3.doubanio.com' in src):
                images.append(src)

        return {
            'title': title,
            'author': author,
            'pub_date': pub_date,
            'content': content,
            'images': images,
            'original_url': url
        }

    def _extract_review_info(self, soup, url):
        """
        提取豆瓣评论信息
        """
        # 提取标题
        title_tag = soup.find('span', {'property': 'v:summary'}) or soup.find('h1')
        title = title_tag.get_text().strip() if title_tag else '未知标题'

        # 提取作者
        author_tag = soup.find('a', {'property': 'v:reviewer'})
        if not author_tag:
            author_tag = soup.find('a', href=re.compile(r'/people/'))
        author = author_tag.get_text().strip() if author_tag else '未知作者'

        # 提取评分（如果有）
        rating_tag = soup.find('span', {'class': re.compile(r'.*allstar.*')})
        rating = rating_tag.get('class')[0] if rating_tag else ''

        # 提取发布时间
        pub_date_tag = soup.find('span', {'property': 'v:dtreviewed'})
        pub_date = ''
        if pub_date_tag:
            date_text = pub_date_tag.get_text().strip()
            pub_date = self._parse_douban_date(date_text)
        if not pub_date:
            pub_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 提取正文内容
        content_div = soup.find('div', {'id': 'link-report'})
        content = ''
        if content_div:
            content = str(content_div)

        # 提取图片链接
        images = []
        img_tags = soup.find_all('img')
        for img in img_tags:
            src = img.get('src') or img.get('data-original')
            if src and ('img1.doubanio.com' in src or 'img2.doubanio.com' in src or 'img3.doubanio.com' in src):
                images.append(src)

        return {
            'title': title,
            'author': author,
            'pub_date': pub_date,
            'content': content,
            'images': images,
            'original_url': url
        }

    def _extract_status_info(self, soup, url):
        """
        提取豆瓣广播信息
        """
        # 提取作者
        author_tag = soup.find('a', {'class': 'statustitle'})
        if not author_tag:
            author_tag = soup.find('a', href=re.compile(r'/people/'))
        author = author_tag.get_text().strip() if author_tag else '未知作者'

        # 提取内容
        content_div = soup.find('div', {'class': 'status-content'})
        content = ''
        if content_div:
            content = content_div.get_text().strip()

        # 提取发布时间
        pub_date_tag = soup.find('span', {'class': 'pubdate'})
        pub_date = ''
        if pub_date_tag:
            date_text = pub_date_tag.get_text().strip()
            pub_date = self._parse_douban_date(date_text)
        if not pub_date:
            pub_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 广播通常不会有单独的标题，使用内容的一部分作为标题
        title = content[:50] + '...' if len(content) > 50 else content
        if not title.strip():
            title = '豆瓣广播'

        # 提取图片链接
        images = []
        img_tags = soup.find_all('img')
        for img in img_tags:
            src = img.get('src') or img.get('data-original')
            if src and ('img1.doubanio.com' in src or 'img2.doubanio.com' in src or 'img3.doubanio.com' in src):
                images.append(src)

        return {
            'title': title,
            'author': author,
            'pub_date': pub_date,
            'content': content,
            'images': images,
            'original_url': url
        }

    def _parse_douban_date(self, date_text):
        """
        解析豆瓣日期格式
        """
        if not date_text:
            return ''

        # 尝试匹配不同的日期格式
        patterns = [
            r'(\d{4}-\d{2}-\d{2})',
            r'(\d{4}/\d{2}/\d{2})',
            r'(\d{2}-\d{2}-\d{4})',
            r'(\d{4}年\d{2}月\d{2}日)',
        ]

        for pattern in patterns:
            match = re.search(pattern, date_text)
            if match:
                date_str = match.group(1)
                # 尝试解析各种日期格式
                formats = ['%Y-%m-%d', '%Y/%m/%d', '%m-%d-%Y']
                for fmt in formats:
                    try:
                        parsed_date = datetime.strptime(date_str, fmt)
                        return parsed_date.strftime('%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        continue

        # 如果没找到匹配，返回当前时间
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')