"""
Article Fetcher - 主程序入口
抓取文章并存档到 Notion
"""
from detector.platform_detector import detect_platform
from fetchers.wechat_fetcher import WechatFetcher
from fetchers.xhs_fetcher import XHSFetcher
from fetchers.douban_fetcher import DoubanFetcher
from fetchers.zhihu_fetcher import ZhihuFetcher
from processors.image_processor import ImageProcessor
from processors.content_converter import ContentConverter
from archiver.notion_archiver import NotionArchiver
from utils.word_counter import count_words
from utils.logger import logger
from config import config
import uuid
import sys


def fetch_and_archive_article(url: str, tags: list = None) -> dict:
    """
    抓取文章并存档到 Notion

    Args:
        url (str): 文章链接
        tags (list, optional): 标签列表

    Returns:
        dict: 操作结果
    """
    logger.info(f"开始处理文章：{url}")

    try:
        # 1. 检测平台
        platform = detect_platform(url)
        if not platform:
            logger.warning(f"不支持的平台：{url}")
            return {
                'success': False,
                'message': '不支持的平台或无法识别平台',
                'error_code': 'UNSUPPORTED_PLATFORM'
            }

        logger.info(f"识别平台：{platform}")

        # 2. 根据平台选择相应的抓取器
        fetcher_map = {
            'wechat': WechatFetcher(cookies_file=config.wechat_cookies),
            'xhs': XHSFetcher(cookies_file=config.xhs_cookies),
            'douban': DoubanFetcher(),
            'zhihu': ZhihuFetcher(cookies_file=config.zhihu_cookies),
        }

        fetcher = fetcher_map.get(platform)
        if not fetcher:
            logger.error(f"未找到平台 {platform} 的抓取器")
            return {
                'success': False,
                'message': f'未找到平台 {platform} 的抓取器',
                'error_code': 'FETCHER_NOT_FOUND'
            }

        # 3. 抓取文章内容
        logger.info(f"正在抓取 {platform} 平台的文章...")
        article_data = fetcher.fetch_article(url)

        if not article_data or not article_data.get('title'):
            logger.error("未能成功抓取文章内容")
            return {
                'success': False,
                'message': '未能成功抓取文章内容',
                'error_code': 'FETCH_FAILED'
            }

        # 生成文章 ID
        article_id = str(uuid.uuid4())
        logger.debug(f"生成文章 ID: {article_id}")

        # 4. 处理图片上传到 OSS
        logger.info("正在处理图片上传...")
        image_processor = ImageProcessor()
        image_urls = article_data.get('images', [])

        if image_urls:
            logger.info(f"发现 {len(image_urls)} 张图片，开始上传...")
            # 上传图片到 OSS 并获取 URL 映射
            url_mapping = image_processor.upload_images(image_urls, platform, article_id)
            logger.info(f"图片上传完成：{len(url_mapping)}/{len(image_urls)} 张成功")

            # 替换内容中的图片链接
            content = article_data.get('content', '')
            for original_url, oss_url in url_mapping.items():
                # 替换 HTML 格式的图片链接
                content = content.replace(original_url, oss_url)
                # 替换 Markdown 格式的图片链接
                content = content.replace(f']({original_url})', f']({oss_url})')

            article_data['content'] = content
        else:
            logger.debug("文章不含图片")

        # 5. 转换 HTML 内容为 Markdown
        logger.info("正在转换内容格式...")
        converter = ContentConverter()
        markdown_content = converter.html_to_markdown(article_data.get('content', ''))
        article_data['content'] = markdown_content

        # 6. 统计字数
        word_count = count_words(markdown_content)
        logger.info(f"字数统计：{word_count} 字")
        article_data['words'] = word_count

        # 7. 准备存档数据
        archive_data = {
            'title': article_data.get('title', ''),
            'source': platform,
            'author': article_data.get('author', ''),
            'link': url,
            'tags': tags or [],
            'pub_date': article_data.get('pub_date', ''),
            'content': article_data.get('content', ''),
            'words': word_count
        }

        # 8. 存档到 Notion
        logger.info("正在存档到 Notion...")
        archiver = NotionArchiver()
        success = archiver.archive_article(archive_data)

        if success:
            logger.info("文章存档成功")
            return {
                'success': True,
                'message': '文章已成功抓取并存档到 Notion',
                'article_id': article_id,
                'platform': platform,
                'title': article_data.get('title', ''),
                'word_count': word_count
            }
        else:
            logger.error("文章存档到 Notion 失败")
            return {
                'success': False,
                'message': '文章抓取成功但存档到 Notion 失败',
                'error_code': 'ARCHIVE_FAILED',
                'article_data': article_data
            }

    except Exception as e:
        logger.exception(f"处理过程中发生异常：{str(e)}")
        return {
            'success': False,
            'message': f'处理过程中发生错误：{str(e)}',
            'error_code': 'PROCESS_ERROR'
        }


def main():
    """主函数，用于命令行调用"""
    if len(sys.argv) < 2:
        print("用法：python main.py <文章链接> [标签 1] [标签 2] ...")
        print("")
        print("示例:")
        print("  python main.py https://mp.weixin.qq.com/s/xxx 技术 AI")
        print("  python main.py https://www.xiaohongshu.com/explore/xxx 教程 笔记")
        return

    url = sys.argv[1]
    tags = sys.argv[2:] if len(sys.argv) > 2 else []

    logger.info(f"命令行启动 | URL: {url} | 标签：{tags}")

    result = fetch_and_archive_article(url, tags)

    if result['success']:
        print(f"\n✅ {result['message']}")
        print(f"📰 标题：{result['title']}")
        print(f"🏷️ 平台：{result['platform']}")
        print(f"🔢 字数：{result['word_count']}")
        logger.info("任务完成")
    else:
        print(f"\n❌ {result['message']}")
        print(f"🔧 错误代码：{result.get('error_code', 'UNKNOWN')}")
        logger.error(f"任务失败：{result.get('error_code', 'UNKNOWN')}")


if __name__ == "__main__":
    main()
