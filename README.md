# Article Fetcher 📰

抓取微信公众号、小红书、豆瓣、知乎等平台文章，自动上传图片至阿里云 OSS，
LLM 智能提取关键词，一键存档到 Notion。

## Quick Start

```bash
cd ~/.openclaw/workspace-engineer/skills/article-fetcher

# 安装依赖
pip install requests oss2 python-dotenv beautifulsoup4 lxml

# 运行
python main.py "https://mp.weixin.qq.com/s/xxx" 标签1 标签2
```

## 配置

在 `~/.openclaw/.env` 中添加：

```bash
# 阿里云 OSS
ALIYUN_OSS_AK=...
ALIYUN_OSS_SK=...
ALIYUN_OSS_BUCKET_ID=...
ALIYUN_OSS_ENDPOINT=oss-cn-shanghai.aliyuncs.com

# Notion
NOTION_API_KEY=...
NOTION_ARTICLE_DATABASE_ID=...
```

## 输出

Notion 数据库记录包含：标题、来源平台、作者、原文链接、关键词（multi_select）、
发布日期、字数、存档时间。页面正文为结构化 HTML 块，保留原始排版。

## 扩展示例

新增平台只需 3 步：
1. `fetchers/` 下创建 Fetcher 类（继承 `BaseFetcher`）
2. `detector/platform_detector.py` 添加 URL 识别
3. `main.py` 的 `FETCHER_REGISTRY` 注册

详见 [SKILL.md](SKILL.md)。
