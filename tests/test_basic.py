"""
Article Fetcher 基础测试
测试平台识别、日志、HTTP 客户端等基础功能
"""
import sys
import os

# 添加项目根路径到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from detector.platform_detector import detect_platform
from utils.logger import logger
from utils.http_client import get_with_retry


def test_platform_detector():
    """测试平台识别功能"""
    print("\n=== 测试平台识别 ===")

    test_cases = [
        ("https://mp.weixin.qq.com/s/abc123", "wechat"),
        ("https://weixin.qq.com/a/b", "wechat"),
        ("https://www.xiaohongshu.com/explore/xyz", "xhs"),
        ("https://xhslink.com/abc", "xhs"),
        ("https://www.douban.com/note/123", "douban"),
        ("https://www.zhihu.com/question/456/answer/789", "zhihu"),
        ("https://example.com/unknown", None),
    ]

    passed = 0
    failed = 0

    for url, expected in test_cases:
        result = detect_platform(url)
        if result == expected:
            print(f"✅ {url[:50]}... → {result}")
            passed += 1
        else:
            print(f"❌ {url[:50]}... → {result} (期望：{expected})")
            failed += 1

    print(f"\n结果：{passed} 通过，{failed} 失败")
    return failed == 0


def test_logger():
    """测试日志功能"""
    print("\n=== 测试日志功能 ===")

    logger.debug("这是一条调试消息")
    logger.info("这是一条信息消息")
    logger.warning("这是一条警告消息")
    logger.error("这是一条错误消息")

    print("✅ 日志功能正常")
    return True


def test_http_client():
    """测试 HTTP 客户端（带重试）"""
    print("\n=== 测试 HTTP 客户端 ===")

    try:
        # 测试一个稳定的 URL
        response = get_with_retry("https://httpbin.org/get", timeout=10, retries=2)
        if response.status_code == 200:
            print(f"✅ HTTP GET 测试成功 | 状态码：{response.status_code}")
            return True
        else:
            print(f"❌ HTTP GET 测试失败 | 状态码：{response.status_code}")
            return False
    except Exception as e:
        print(f"❌ HTTP GET 测试异常：{e}")
        return False


def main():
    """运行所有测试"""
    print("=" * 50)
    print("Article Fetcher 基础测试")
    print("=" * 50)

    results = {
        '平台识别': test_platform_detector(),
        '日志功能': test_logger(),
        'HTTP 客户端': test_http_client(),
    }

    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)

    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name}: {status}")

    all_passed = all(results.values())

    if all_passed:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n⚠️ 部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
