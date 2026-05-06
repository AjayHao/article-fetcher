---
name: article-fetcher
description: "抓取微信公众号、小红书、豆瓣、知乎文章，自动上传 OSS 图片，LLM 智能提取关键词，一键存档到 Notion"
homepage: https://github.com/openclaw/openclaw
metadata:
  {
    "openclaw":
      {
        "emoji": "📰",
        "requires": { "bins": ["python3"], "env": ["ALIYUN_OSS_AK", "ALIYUN_OSS_SK", "ALIYUN_OSS_BUCKET_ID", "ALIYUN_OSS_ENDPOINT", "NOTION_API_KEY", "NOTION_ARTICLE_DATABASE_ID"] },
        "primaryEnv": "NOTION_API_KEY",
        "install":
          [
            {
              "id": "pip",
              "kind": "pip",
              "packages": "requests oss2 python-dotenv beautifulsoup4 lxml notion-client",
              "label": "Install Python dependencies",
            },
          ],
      },
  }
---

# Article Fetcher

抓取微信公众号、小红书、豆瓣、知乎文章，自动上传 OSS 图床，LLM 智能关键词提取，一键存档到 Notion。

## Setup

```bash
pip install requests oss2 python-dotenv beautifulsoup4 lxml notion-client
```

配置环境变量（`~/.openclaw/.env`）：

```bash
# 必需
ALIYUN_OSS_AK=your_ak
ALIYUN_OSS_SK=your_sk
ALIYUN_OSS_BUCKET_ID=your_bucket
ALIYUN_OSS_ENDPOINT=oss-cn-shanghai.aliyuncs.com
NOTION_API_KEY=secret_xxx
NOTION_ARTICLE_DATABASE_ID=database_id

# 可选：LLM 关键词提取（DashScope）
DASHSCOPE_API_KEY=sk-xxx
DASHSCOPE_MODEL=qwen3.5-plus

# 可选：Cookies（反爬）
ZHIHU_COOKIES_FILE=~/.cookies/zhihu_cookies.txt
WECHAT_COOKIES_FILE=~/.cookies/wechat_cookies.txt
```

## Usage

```bash
cd ~/.openclaw/workspace-engineer/skills/article-fetcher

# 基础用法
python3 main.py "文章 URL"

# 附加手动标签
python3 main.py "文章 URL" 标签1 标签2
```

支持平台：微信公众号 (`mp.weixin.qq.com`)、小红书 (`xiaohongshu.com` / `xhslink.com`)、豆瓣 (`douban.com`)、知乎 (`zhihu.com`)。

## Architecture

```
URL → 平台识别 → 内容抓取 (fetcher) → 图片上传 OSS → 关键词提取 (LLM/降级词频) → Notion 存档
```

新增平台：
1. `fetchers/` 下创建 `xxx_fetcher.py`，继承 `BaseFetcher` 实现 `fetch_article()`
2. `detector/platform_detector.py` 添加 URL 正则
3. `main.py` 的 `FETCHER_REGISTRY` 注册

## Key Notes

- 知乎/微信反爬需要配置 Cookies（Netscape 格式），其他平台无需登录
- 关键词提取采用 LLM 优先策略，未配置或失败时自动降级为本地词频分析
- 图片上传失败不阻断流程，成功多少记录多少
- 所有时间格式统一 `YYYY-MM-DD HH:MM:SS`，缺失时留空（不伪造当前时间）
