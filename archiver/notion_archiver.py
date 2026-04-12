from notion_client import Client
from datetime import datetime
from config import config

class NotionArchiver:
    """
    Notion存档器，负责将文章数据存档到Notion数据库
    """

    def __init__(self):
        # 初始化Notion客户端
        self.notion = Client(auth=config.notion_api_key)

    def archive_article(self, article_data: dict) -> bool:
        """
        存档文章到Notion数据库

        Args:
            article_data (dict): 文章数据，包含:
                - title: 文章标题
                - source: 来源平台
                - author: 作者
                - link: 原文链接
                - tags: 标签列表
                - pub_date: 发布时间
                - content: 文章内容
                - words: 字数统计

        Returns:
            bool: 存档是否成功
        """
        try:
            # 准备数据库属性
            properties = {
                "Title": {
                    "title": [
                        {
                            "text": {
                                "content": article_data.get("title", "")
                            }
                        }
                    ]
                },
                "Source": {
                    "rich_text": [
                        {
                            "text": {
                                "content": article_data.get("source", "")
                            }
                        }
                    ]
                },
                "Author": {
                    "rich_text": [
                        {
                            "text": {
                                "content": article_data.get("author", "")
                            }
                        }
                    ]
                },
                "Link": {
                    "url": article_data.get("link")
                },
                "PubDate": {
                    "date": {
                        "start": article_data.get("pub_date", datetime.now().isoformat())
                    }
                },
                "Words": {
                    "number": article_data.get("words", 0)
                },
                "ts": {
                    "date": {
                        "start": datetime.now().isoformat()
                    }
                }
            }

            # 如果有标签，添加到属性中
            if article_data.get("tags"):
                properties["Tags"] = {
                    "multi_select": [{"name": tag} for tag in article_data["tags"]]
                }

            # 创建页面
            response = self.notion.pages.create(
                parent={"database_id": config.notion_article_database_id},
                properties=properties
            )

            # 如果有正文内容，作为块添加到页面
            content = article_data.get("content")
            if content:
                # 分割内容为多个块以避免超过限制
                content_blocks = self._create_content_blocks(content)
                if content_blocks:
                    self.notion.blocks.children.append(
                        block_id=response['id'],
                        children=content_blocks
                    )

            return True

        except Exception as e:
            print(f"存档到Notion时发生错误: {str(e)}")
            return False

    def _create_content_blocks(self, content: str):
        """
        将内容拆分为多个Notion块
        """
        if not content:
            return []

        # 简单地将长内容分割为段落块
        paragraphs = content.split('\n\n')
        blocks = []

        for paragraph in paragraphs:
            if paragraph.strip():
                # 限制每个块的长度
                if len(paragraph) > 2000:
                    # 如果段落太长，则进一步分割
                    chunks = [paragraph[i:i+2000] for i in range(0, len(paragraph), 2000)]
                    for chunk in chunks:
                        blocks.append({
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": chunk
                                        }
                                    }
                                ]
                            }
                        })
                else:
                    blocks.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": paragraph
                                    }
                                }
                            ]
                        }
                    })

        return blocks[:100]  # 限制块数量以避免超出API限制