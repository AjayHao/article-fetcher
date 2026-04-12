import requests
from bs4 import BeautifulSoup
from fetchers.base_fetcher import BaseFetcher
import re
from datetime import datetime
import json


class ZhihuFetcher(BaseFetcher):
    """
    知乎文章抓取器
    """

    def __init__(self):
        super().__init__()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'https://www.zhihu.com/',
        }

    def fetch_article(self, url: str) -> dict:
        """
        抓取知乎文章内容

        Args:
            url (str): 知乎文章链接

        Returns:
            dict: 包含文章信息的字典
        """
        try:
            response = requests.get(url, headers=self.headers)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 知乎专栏文章和回答的处理略有不同
            if '/zhuanlan.' in url or '/p/' in url:
                # 知乎专栏文章
                return self._extract_zhuanlan_article(soup, url)
            elif '/answer/' in url:
                # 知乎回答
                return self._extract_answer(soup, url)
            else:
                # 默认按专栏文章处理
                return self._extract_zhuanlan_article(soup, url)

        except Exception as e:
            print(f"抓取知乎文章时发生错误: {str(e)}")
            return {
                'title': '',
                'author': '',
                'pub_date': '',
                'content': '',
                'images': [],
                'original_url': url
            }

    def _extract_zhuanlan_article(self, soup, url):
        """
        提取知乎专栏文章信息
        """
        # 提取标题
        title_tag = soup.find('h1', attrs={'class': re.compile(r'.*Title.*')}) or soup.find('h1')
        title = title_tag.get_text().strip() if title_tag else '未知标题'

        # 提取作者
        author_tag = soup.find('meta', attrs={'itemprop': 'author'})
        if author_tag:
            author = author_tag.get('content', '未知作者')
        else:
            # 尝试从其他可能的位置获取作者
            author_tag = soup.find('a', attrs={'class': re.compile(r'.*AuthorInfo-name.*')})
            if author_tag:
                author = author_tag.get_text().strip()
            else:
                author = '未知作者'

        # 从页面的script标签中寻找发布时间
        pub_date = ''
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'createdAt' in script.string:
                # 查找createdAt时间戳
                match = re.search(r'"createdAt":\s*(\d+)', script.string)
                if match:
                    timestamp = int(match.group(1))
                    pub_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    break
        if not pub_date:
            # 尝试查找其他可能的时间标记
            pub_date_meta = soup.find('meta', attrs={'name': 'pubDate'})
            if pub_date_meta:
                pub_date = pub_date_meta.get('content', '')
            else:
                pub_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 提取正文内容
        content_div = soup.find('div', attrs={'class': re.compile(r'.*RichContent.*')})
        if not content_div:
            content_div = soup.find('div', attrs={'class': 'Post-RichTextContainer'})
        if not content_div:
            content_div = soup.find('div', attrs={'class': re.compile(r'.*AnswerItem.*')})
        content = str(content_div) if content_div else ''

        # 提取图片链接
        images = []
        if content_div:
            img_tags = content_div.find_all('img')
            for img in img_tags:
                src = img.get('data-original') or img.get('src') or img.get('data-default-watered-src')
                if src:
                    # 处理知乎图片的特殊格式
                    if src.startswith('//'):
                        src = 'https:' + src
                    if 'zhimg.com' in src:
                        images.append(src)

        return {
            'title': title,
            'author': author,
            'pub_date': pub_date,
            'content': content,
            'images': images,
            'original_url': url
        }

    def _extract_answer(self, soup, url):
        """
        提取知乎回答信息
        """
        # 提取问题标题作为文章标题
        title_tag = soup.find('h1', attrs={'class': re.compile(r'.*QuestionHeader-title.*')})
        if not title_tag:
            title_tag = soup.find('a', attrs={'class': re.compile(r'.*question_link.*')})
        title = title_tag.get_text().strip() if title_tag else '知乎回答'

        # 提取回答者
        author_tag = soup.find('meta', attrs={'itemprop': 'name'})
        if author_tag:
            author = author_tag.get('content', '匿名用户')
        else:
            author_tag = soup.find('a', attrs={'class': re.compile(r'.*AuthorInfo-name.*')})
            if author_tag:
                author = author_tag.get_text().strip()
            else:
                author = '匿名用户'

        # 尝试提取发布时间
        pub_date = ''
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and ('created' in script.string or 'updated' in script.string):
                # 查找时间戳
                match_created = re.search(r'"createdTime":\s*"([^"]+)"', script.string)
                match_updated = re.search(r'"updatedTime":\s*"([^"]+)"', script.string)

                if match_created:
                    # 处理ISO时间格式
                    time_str = match_created.group(1)
                    try:
                        # 尝试解析ISO格式时间
                        dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                        pub_date = dt.strftime('%Y-%m-%d %H:%M:%S')
                        break
                    except ValueError:
                        pass
                elif match_updated:
                    time_str = match_updated.group(1)
                    try:
                        dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                        pub_date = dt.strftime('%Y-%m-%d %H:%M:%S')
                        break
                    except ValueError:
                        pass
        if not pub_date:
            pub_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 提取回答内容
        content_div = soup.find('div', attrs={'class': re.compile(r'.*RichContent.*')})
        if not content_div:
            content_div = soup.find('span', attrs={'class': re.compile(r'.*RichText.*')})
        content = str(content_div) if content_div else ''

        # 提取图片链接
        images = []
        if content_div:
            img_tags = content_div.find_all('img')
            for img in img_tags:
                src = img.get('data-original') or img.get('src') or img.get('data-default-watered-src')
                if src:
                    if src.startswith('//'):
                        src = 'https:' + src
                    if 'zhimg.com' in src:
                        images.append(src)

        return {
            'title': title,
            'author': author,
            'pub_date': pub_date,
            'content': content,
            'images': images,
            'original_url': url
        }