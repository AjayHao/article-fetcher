---
name: article-fetcher
description: "抓取微信公众号/小红书/豆瓣/知乎文章，自动上传 OSS 图片，提取关键词，一键存档到 Notion"
metadata:
  {
    "openclaw":
      {
        "emoji": "📰",
        "requires": { "bins": [], "env": ["ALIYUN_OSS_AK", "ALIYUN_OSS_SK", "ALIYUN_OSS_BUCKET_ID", "ALIYUN_OSS_ENDPOINT", "NOTION_API_KEY", "NOTION_ARTICLE_DATABASE_ID"] },
        "install":
          [
            {
              "id": "pip",
              "kind": "pip",
              "packages": "requests oss2 python-dotenv beautifulsoup4 lxml",
              "label": "Install Python dependencies",
            },
          ],
      },
  }
---

# Article Fetcher — OpenClaw Skill

抓取微信公众号、小红书、豆瓣、知乎等平台文章，自动处理图片上传至阿里云 OSS，
LLM 智能提取关键词，一键存档到 Notion 数据库。

**版本**: 0.1.0  
**发布**: 2026-04-29  
**许可**: MIT  
**作者**: Ajay Hao

---

> ⚠️ **安全提示**
> - 确保您有权抓取并存档目标内容
> - 遵循各平台 robots.txt 和使用条款
> - 控制抓取频率，避免被封 IP
> - OSS Bucket 配置最小权限（仅 PutObject/GetObject）

---

## 🎯 核心能力

- **多平台支持**: 微信公众号、小红书、豆瓣、知乎
- **智能识别**: 自动识别文章来源平台
- **内容提取**: 标题、作者、发布时间、正文（HTML）、图片
- **图床集成**: 阿里云 OSS 自动上传，按 `article-001.jpg` 格式命名
- **关键词提取**: LLM 智能分析文章内容，提炼 5 个核心关键词
- **一键存档**: HTML 内容解析为 Notion 结构化块，保留原始排版
- **字数统计**: 剔除 HTML 标签后自动统计

## 🏗️ 处理流程

```
用户输入 (文章 URL)
  ↓
Step 1: 平台识别（detector/）
  ↓
Step 2: 内容抓取（fetchers/，注册表模式，易扩展）
  ↓
Step 3: 图片上传 OSS + 替换 HTML 中的原始链接
  ↓
Step 4: LLM 提取关键词 → 合并命令行标签
  ↓
Step 5: 字数统计（剔除 HTML 标签）
  ↓
Step 6: HTML 解析为 Notion 块 → 写入 Notion 页面
```

## 📂 模块结构

```
article-fetcher/
├── main.py                      # 主程序入口 + 抓取器注册表
├── config.py                    # 配置管理（环境变量）
├── detector/
│   └── platform_detector.py     # URL → 平台识别
├── fetchers/
│   ├── base_fetcher.py          # 基础抓取器（共享 HTTP + Cookies）
│   ├── wechat_fetcher.py        # 微信公众号
│   ├── xhs_fetcher.py           # 小红书
│   ├── douban_fetcher.py        # 豆瓣
│   └── zhihu_fetcher.py         # 知乎
├── processors/
│   └── image_processor.py       # 图片上传 OSS
├── archiver/
│   └── notion_archiver.py       # HTML → Notion 结构化块
└── utils/
    ├── http_client.py           # HTTP 客户端（带重试）
    ├── logger.py                # 日志配置
    ├── word_counter.py          # 字数统计
    └── tag_extractor.py         # LLM 关键词提取
```

## ⚙️ 配置

### 环境变量（`~/.openclaw/.env`）

```bash
# ========== 必需 ==========
ALIYUN_OSS_AK=your_access_key_id
ALIYUN_OSS_SK=your_access_key_secret
ALIYUN_OSS_BUCKET_ID=your_bucket_name
ALIYUN_OSS_ENDPOINT=oss-cn-shanghai.aliyuncs.com
NOTION_API_KEY=nop_xx…xxxx
NOTION_ARTICLE_DATABASE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# ========== 可选 ==========
DEBUG=false
# Cookies 文件路径（反爬）
# WECHAT_COOKIES_FILE=/path/to/wechat_cookies.txt
# ZHIHU_COOKIES_FILE=/path/to/zhihu_cookies.txt
```

### Notion 数据库字段

| 字段 | 类型 | 说明 |
|------|------|------|
| **Title** | title | 文章标题（≤200 字符） |
| **Source** | rich_text | 来源平台 |
| **Author** | rich_text | 作者 |
| **Link** | url | 原文链接 |
| **Tags** | multi_select | 关键词（自动提取 + 手动传入） |
| **PubDate** | date | 发布日期 |
| **Words** | number | 字数统计 |
| **ts** | date | 存档时间（东八区） |

### OSS 路径规范

- **图片**: `articles/<平台码>/<article_id>/article-001.jpg`
- **HTML 预览**: `articles/html/<标题>_<uuid>.html`

## 📋 使用方法

### 命令行

```bash
cd ~/.openclaw/workspace-engineer/skills/article-fetcher

# 基础用法
python main.py "文章 URL"

# 带标签
python main.py "文章 URL" 标签1 标签2

# 示例
python main.py "https://mp.weixin.qq.com/s/xxx" 技术 AI
python main.py "https://www.xiaohongshu.com/explore/xxx" 教程 笔记
```

### Python 模块

```python
from main import fetch_and_archive_article

result = fetch_and_archive_article(
    url="https://example.com/article",
    tags=["tag1", "tag2"]
)

if result['success']:
    print(f"✅ {result['message']}")
    print(f"📰 标题：{result['title']}")
    print(f"🏷️ 关键词：{', '.join(result['tags'])}")
    print(f"🔢 字数：{result['word_count']}")
else:
    print(f"❌ {result['message']} ({result['error_code']})")
```

## 🔌 扩展新平台

1. 在 `fetchers/` 下创建 `xxx_fetcher.py`，继承 `BaseFetcher` 并实现 `fetch_article()` 方法
2. 在 `detector/platform_detector.py` 中添加 URL 识别规则
3. 在 `main.py` 的 `FETCHER_REGISTRY` 中注册

```python
# main.py
FETCHER_REGISTRY = {
    'wechat': WechatFetcher,
    'xhs':    XHSFetcher,
    'douban': DoubanFetcher,
    'zhihu':  ZhihuFetcher,
    # 新增:
    # 'juejin': JuejinFetcher,
}
```

## 🔧 故障排查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 抓取失败 | 反爬机制 | 配置 Cookies 或使用代理 |
| 图片上传失败 | OSS 配置错误 | 检查 AK/SK/Bucket 配置 |
| Notion 推送失败 | API Key 过期 | 更新 `NOTION_API_KEY` |
| 平台识别失败 | URL 格式异常 | 检查 URL 完整性 |
| 文章无内容 | 页面结构变化 | 更新对应 Fetcher 的选择器 |

查看详细日志：
```bash
DEBUG=true python main.py "URL" 2>&1 | tee fetch.log
cat logs/article-fetcher.log
```

## 📝 输出格式（Notion 页面）

页面内容包含：
- 📄 提示文字 + HTML 预览书签（保留原始排版）
- 🔗 原文链接

数据库记录 8 个字段 + 页面正文结构化块（标题、段落、图片、列表、代码块等）。

---

**维护人**: Ajay Hao  
**OpenClaw Skill**: 开发中
