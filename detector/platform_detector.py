import re
from typing import Optional

def detect_platform(url: str) -> Optional[str]:
    """
    根据URL识别文章所属平台

    Args:
        url (str): 文章链接

    Returns:
        Optional[str]: 平台标识符 (wechat, xhs, douban, zhihu) 或 None
    """
    if not url:
        return None

    # 清理URL，移除可能的参数
    clean_url = url.split('?')[0].lower()

    # 微信公众号检测
    if re.search(r'weixin\.qq\.com|mp\.weixin\.qq\.com|upload\.weibo\.com', clean_url):
        return 'wechat'

    # 小红书检测
    if re.search(r'xiaohongshu\.com|xhslink\.com', clean_url):
        return 'xhs'

    # 豆瓣检测
    if re.search(r'douban\.com', clean_url):
        return 'douban'

    # 知乎检测
    if re.search(r'zhihu\.com', clean_url):
        return 'zhihu'

    return None