---
name: article-fetcher
description: "抓取微信公众号、小红书、豆瓣、知乎文章，自动上传 OSS 图片，LLM 智能提取关键词，一键存档到 Obsidian 本地知识库（可选 Notion）"
homepage: https://github.com/ajayhao/article-fetcher
metadata:
  { "openclaw": { "emoji": "📰", "version": "1.1.0", "requires": { "bins": ["python3"], "env": ["ALIYUN_OSS_AK", "ALIYUN_OSS_SK", "ALIYUN_OSS_BUCKET_ID", "ALIYUN_OSS_ENDPOINT"] }, "primaryEnv": "OBSIDIAN_VAULT_PATH", "install": [{ "id": "pip", "kind": "pip", "packages": "requests oss2 python-dotenv beautifulsoup4 lxml notion-client markdownify", "label": "Install Python dependencies" }] } }
---

# Article Fetcher v1.1.0

抓取微信公众号、小红书、豆瓣、知乎文章，自动上传 OSS 图床，LLM 智能关键词提取，默认存档到 Obsidian 本地知识库（可选 Notion 双写）。

## 存档模式

四种场景按需灵活切换，不存档时仅终端输出抓取结果：

| 场景 | Obsidian | Notion | 行为 |
|------|:---:|:---:|------|
| 🏠 **本地优先** | ✅ | ❌ | 存档到 Obsidian 本地知识库 |
| ☁️ **纯云端** | ❌ | ✅ | 存档到 Notion 数据库 |
| 🏠+☁️ **双写** | ✅ | ✅ | Obsidian + Notion 双存档 |
| 🔍 **预览** | ❌ | ❌ | 仅终端输出，不存档 |

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量（`~/.hermes/.env` 或系统环境变量）

```bash
# ========== 必需：OSS 图床 ==========
ALIYUN_OSS_AK=your_ak
ALIYUN_OSS_SK=your_sk
ALIYUN_OSS_BUCKET_ID=your_bucket
ALIYUN_OSS_ENDPOINT=oss-cn-shanghai.aliyuncs.com

# ========== 推荐：Obsidian 本地存档 ==========
# Windows 示例：
OBSIDIAN_VAULT_PATH=D:\GitRepo\AjayObsidianVault
# macOS 示例：
# OBSIDIAN_VAULT_PATH=/Users/yourname/ObsidianVault
# Linux / 云服务器示例：
# OBSIDIAN_VAULT_PATH=/home/yourname/ObsidianVault

# ========== 可选：Notion 云端存档 ==========
NOTION_API_KEY=secret_xxx
NOTION_ARTICLE_DATABASE_ID=database_id

# ========== 可选：LLM 关键词提取（OpenAI 兼容接口，与 video-summarizer 共用配置）==========
LLM_API_KEY=***
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-v4-pro

# ========== 可选：Cookies（反爬，Netscape 格式）==========
WECHAT_COOKIES_FILE=~/.cookies/wechat_cookies.txt
ZHIHU_COOKIES_FILE=~/.cookies/zhihu_cookies.txt
```

### 3. 使用

```bash
cd <skill-dir>
python3 main.py "文章 URL" [标签1] [标签2]
```

**支持平台**：微信公众号 (`mp.weixin.qq.com`)、小红书 (`xiaohongshu.com` / `xhslink.com`)、豆瓣 (`douban.com`)、知乎 (`zhihu.com`)

## 处理流程

```
URL → 平台识别 → 内容抓取 → 图片上传 OSS → 关键词提取 (LLM → 词频降级)
                                              │
                         ┌────────────────────┴────────────────────┐
                         ▼                                         ▼
                  OBSIDIAN_VAULT_PATH?                     NOTION_API_KEY?
                    ✅ → Obsidian .md                       ✅ → Notion 页面
                    都不配 → 终端输出
```

## Obsidian 存档格式

文章存入 `{OBSIDIAN_VAULT_PATH}/1-输入-收件箱/文章收藏/`，命名规则 `{YYYY-MM-DD}_{platform}_{title}.md`。

### 文件示例

```markdown
---
title: "AI Agent 技术全景解析"
source: wechat
author: "张三"
link: "https://mp.weixin.qq.com/s/xxx"
tags:
  - AI Agent
  - LLM
  - 技术架构
pub_date: "2026-05-10 14:30:00"
words: 3500
fetched: "2026-06-22 20:15:00"
article_id: "uuid"
---

# AI Agent 技术全景解析

正文内容（HTML → Markdown 转换，OSS 图片已内嵌）...
```

### 设计要点

- **Frontmatter**：YAML 格式，Obsidian 原生兼容，tag 列表可直接被 Dataview 查询
- **文件命名**：日期前缀确保按时间线排序
- **HTML→Markdown**：通过 `markdownify` 转换，保留链接、图片、粗斜体等格式
- **非阻塞**：Obsidian 写入失败不影响 Notion 存档（如果配置了双写）

## Notion 数据库字段（可选）

配置 `NOTION_API_KEY` + `NOTION_ARTICLE_DATABASE_ID` 后启用双写。

| 字段 | 类型 | 说明 |
|------|------|------|
| Title | title | 文章标题（≤200 字符） |
| Source | rich_text | 来源平台 |
| Author | rich_text | 作者 |
| Link | url | 原文链接 |
| Tags | multi_select | 自动提取关键词 + 手动标签 |
| PubDate | date | 发布时间 |
| Words | number | 字数统计（剔除 HTML） |
| ts | date | 存档时间（东八区） |

## 关键说明

- **Cookies**：知乎/微信反爬需配置（Netscape 格式），小红书/豆瓣无需登录
- **关键词**：LLM 优先（OpenAI 兼容接口），未配置或失败自动降级本地词频
- **图片**：上传失败不阻断，成功多少记录多少
- **时间**：统一 `YYYY-MM-DD HH:MM:SS`，缺失时留空（不伪造）
- **模块**：`main.py` 可作 Python 模块调用：`from main import fetch_and_archive_article`
- **Obsidian 优先**：本地知识库零外部依赖，符合"数据私有化"理念

## 安全与隐私

- **URL 校验**：严格白名单匹配 hostname，拒绝路径拼接攻击
- **Cookie 隔离**：Netscape Cookies 按域名过滤，仅附加到匹配的请求
- **LLM 数据外发**：配置 `LLM_API_KEY` 时，文章内容会发送至对应 API（仅用于关键词提取）
- **敏感信息**：AK/SK/Key 等仅存储于本地，skill 不会外泄
- **Obsidian 数据完全本地**：`.md` 文件写入本地磁盘，零网络外发
- **权限最小化**：OSS Bucket 建议仅授予 PutObject/GetObject；Notion Integration 仅授予目标数据库读写权限
- **依赖锁定**：requirements.txt 使用精确版本号，避免供应链风险

## 扩展平台

1. `fetchers/` 下创建 `xxx_fetcher.py`，继承 `BaseFetcher` 实现 `fetch_article()`
2. `detector/platform_detector.py` 的 `ALLOWED_HOSTS` 添加平台域名
3. `main.py` 的 `FETCHER_REGISTRY` 注册
