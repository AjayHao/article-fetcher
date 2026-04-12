import requests
from bs4 import BeautifulSoup
from fetchers.base_fetcher import BaseFetcher
import re
from datetime import datetime
import json


class XHSFetcher(BaseFetcher):
    """
    小红书文章抓取器
    """

    def __init__(self):
        super().__init__()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'https://www.xiaohongshu.com/',
        }

    def fetch_article(self, url: str) -> dict:
        """
        抓取小红书文章内容

        Args:
            url (str): 小红书文章链接

        Returns:
            dict: 包含文章信息的字典
        """
        try:
            response = requests.get(url, headers=self.headers)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 从小红书页面的script标签中提取JSON数据
            script_tags = soup.find_all('script')

            note_data = None
            for script in script_tags:
                if script.string and 'window.__INITIAL_STATE__=' in script.string:
                    # 提取初始状态数据
                    json_str = script.string.replace('window.__INITIAL_STATE__=', '').strip()
                    # 修复JSON字符串中的可能问题
                    json_str = json_str.rstrip(';')

                    try:
                        initial_state = json.loads(json_str)

                        # 从小红书数据结构中提取笔记信息
                        note_data = self._extract_note_from_state(initial_state)
                        break
                    except json.JSONDecodeError:
                        continue

            if note_data:
                title = note_data.get('title', '未知标题')
                user_info = note_data.get('user', {})
                author = user_info.get('nickName', '未知作者')

                # 提取发布时间
                pub_date_timestamp = note_data.get('time')
                if pub_date_timestamp:
                    pub_date = datetime.fromtimestamp(pub_date_timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    pub_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # 提取内容
                content = note_data.get('desc', '')

                # 提取图片链接
                images = []
                if 'imageList' in note_data:
                    for img_item in note_data['imageList']:
                        if 'url' in img_item:
                            images.append(img_item['url'])
                elif 'video' in note_data and 'cover' in note_data['video']:
                    # 如果是视频，获取封面图
                    images.append(note_data['video']['cover'])
            else:
                # 如果无法解析JSON数据，尝试从HTML元素中提取
                title_elem = soup.find('h1') or soup.find(class_='title')
                title = title_elem.get_text().strip() if title_elem else '未知标题'

                author_elem = soup.find(class_='user-name') or soup.find(class_='author')
                author = author_elem.get_text().strip() if author_elem else '未知作者'

                pub_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                desc_elem = soup.find(class_='desc') or soup.find(class_='note-content')
                content = desc_elem.get_text().strip() if desc_elem else ''

                # 提取图片
                images = []
                img_elements = soup.find_all('img')
                for img in img_elements:
                    src = img.get('src') or img.get('data-src')
                    if src and ('img.xhscdn.com' in src or 'sns-img-qc.xhscdn.com' in src):
                        images.append(src)

            return {
                'title': title,
                'author': author,
                'pub_date': pub_date,
                'content': content,
                'images': images,
                'original_url': url
            }

        except Exception as e:
            print(f"抓取小红书文章时发生错误: {str(e)}")
            return {
                'title': '',
                'author': '',
                'pub_date': '',
                'content': '',
                'images': [],
                'original_url': url
            }

    def _extract_note_from_state(self, initial_state):
        """
        从小红书初始状态数据中提取笔记信息
        """
        try:
            # 根据小红书的数据结构，遍历查找笔记数据
            if 'note' in initial_state:
                if 'noteDetailByNoteId' in initial_state['note']:
                    for note_detail in initial_state['note']['noteDetailByNoteId'].values():
                        if 'note' in note_detail:
                            return note_detail['note']

            # 更深层级的遍历
            def traverse_dict(obj):
                if isinstance(obj, dict):
                    if 'note' in obj and isinstance(obj['note'], dict):
                        return obj['note']
                    for value in obj.values():
                        result = traverse_dict(value)
                        if result:
                            return result
                elif isinstance(obj, list):
                    for item in obj:
                        result = traverse_dict(item)
                        if result:
                            return result
                return None

            return traverse_dict(initial_state)
        except Exception:
            return None