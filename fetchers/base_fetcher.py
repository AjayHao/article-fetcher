"""
基础抓取器：定义统一接口 + 共享 HTTP 请求逻辑
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from utils.http_client import get_with_retry, DEFAULT_USER_AGENT
from utils.logger import logger


class BaseFetcher(ABC):
    """基础抓取器抽象类"""

    # 所有子类共享的默认请求头
    DEFAULT_HEADERS = {
        'User-Agent': DEFAULT_USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }

    def __init__(self, cookies_file: str = None):
        self.cookies_file = cookies_file
        self.cookies = self._load_cookies() if cookies_file else {}
        self.headers = dict(self.DEFAULT_HEADERS)

    def _load_cookies(self) -> dict:
        """加载 Netscape 格式 Cookies 文件"""
        try:
            cookies = {}
            with open(self.cookies_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 跳过纯注释行（# 后面跟空格或 tab）
                    if not line or line.startswith('# ') or line.startswith('#\t'):
                        continue
                    # #HttpOnly 开头的行：移除 #HttpOnly 前缀，域名列前移
                    if line.startswith('#HttpOnly'):
                        line = line[len('#HttpOnly'):].strip()
                    if '\t' not in line:
                        continue
                    parts = line.split('\t')
                    # Netscape 格式: domain\tflag\tpath\tsecure\texpiration\tname\tvalue
                    # #HttpOnly 行去掉前缀后也是 7 字段格式
                    if len(parts) >= 7 and '=' not in parts[0]:
                        cookies[parts[5]] = parts[6]
            logger.debug(f"加载 Cookies: {len(cookies)} 个 ({self.cookies_file})")
            return cookies
        except Exception as e:
            logger.warning(f"加载 Cookies 失败：{e}")
            return {}

    def _apply_cookies(self):
        """将 Cookies 添加到请求头"""
        if self.cookies:
            self.headers['Cookie'] = '; '.join(f"{k}={v}" for k, v in self.cookies.items())

    def _fetch_html(self, url: str, headers: dict = None, timeout: int = 30) -> str:
        """发送 GET 请求并返回 HTML 文本"""
        resp = get_with_retry(url, headers=headers or self.headers, timeout=timeout)
        resp.encoding = 'utf-8'
        return resp.text

    @abstractmethod
    def fetch_article(self, url: str) -> Dict:
        """
        抓取文章内容

        Returns:
            dict: title, author, pub_date, content (HTML), images, original_url
        """
        pass
