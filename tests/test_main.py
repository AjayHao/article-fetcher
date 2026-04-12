import unittest
from main import fetch_and_archive_article
from detector.platform_detector import detect_platform


class TestArticleFetcher(unittest.TestCase):
    """Article Fetcher 测试类"""

    def test_platform_detection(self):
        """测试平台检测功能"""
        # 微信公众号链接测试
        wechat_url = "https://mp.weixin.qq.com/s?__biz=example"
        self.assertEqual(detect_platform(wechat_url), 'wechat')

        # 小红书链接测试
        xhs_url = "https://www.xiaohongshu.com/explore/example"
        self.assertEqual(detect_platform(xhs_url), 'xhs')

        # 豆瓣链接测试
        douban_url = "https://www.douban.com/note/example"
        self.assertEqual(detect_platform(douban_url), 'douban')

        # 知乎链接测试
        zhihu_url = "https://zhuanlan.zhihu.com/p/123456789"
        self.assertEqual(detect_platform(zhihu_url), 'zhihu')

    def test_invalid_url(self):
        """测试无效URL检测"""
        invalid_url = "https://example.com/unknown-platform"
        self.assertIsNone(detect_platform(invalid_url))

    def test_empty_url(self):
        """测试空URL检测"""
        self.assertIsNone(detect_platform(""))


if __name__ == '__main__':
    # 仅运行基本测试，不实际抓取任何文章
    unittest.main()