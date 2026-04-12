import re

def count_words(text: str) -> int:
    """
    统计文本字数，排除图片链接

    Args:
        text (str): 要统计的文本内容

    Returns:
        int: 文本字数（不包含图片链接）
    """
    if not text:
        return 0

    # 移除Markdown格式的图片链接 ![alt text](url)
    text_without_images = re.sub(r'!\[.*?\]\(.*?\)', '', text)

    # 移除HTML格式的图片 <img ... >
    text_without_images = re.sub(r'<img[^>]*>', '', text_without_images)

    # 移除空格和换行符，只计算实际字符
    clean_text = re.sub(r'\s+', '', text_without_images)

    return len(clean_text)