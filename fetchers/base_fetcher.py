from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class BaseFetcher(ABC):
    """
    基础抓取器抽象类，定义统一的抓取接口
    """

    def __init__(self):
        pass

    @abstractmethod
    def fetch_article(self, url: str) -> Dict:
        """
        抓取文章内容

        Args:
            url (str): 文章链接

        Returns:
            Dict: 包含文章信息的字典，包括:
                  - title: 标题
                  - author: 作者
                  - pub_date: 发布时间
                  - content: 正文内容(HTML格式)
                  - images: 图片链接列表
        """
        pass