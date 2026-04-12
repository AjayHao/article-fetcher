import html2text

class ContentConverter:
    """
    内容转换器，负责将HTML内容转换为Markdown格式
    """

    def __init__(self):
        # 配置html2text转换器
        self.h = html2text.HTML2Text()
        self.h.ignore_links = False  # 保留链接
        self.h.ignore_images = False  # 保留图片
        self.h.body_width = 0  # 不限制行宽
        self.h.single_line_break = True  # 使用单行换行

    def html_to_markdown(self, html_content: str) -> str:
        """
        将HTML内容转换为Markdown格式

        Args:
            html_content (str): HTML格式的内容

        Returns:
            str: Markdown格式的内容
        """
        if not html_content:
            return ""

        return self.h.handle(html_content)