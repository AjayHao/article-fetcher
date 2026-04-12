---
name: article-fetcher
description: "抓取微信公众号/小红书/豆瓣/知乎文章，自动上传 OSS 图片，一键存档到 Notion"
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
              "packages": "requests oss2 python-dotenv html2text beautifulsoup4",
              "label": "Install Python dependencies",
            },
          ],
      },
  }
---

# Article Fetcher — OpenClaw Skill

抓取微信公众号、小红书、豆瓣、知乎文章，自动上传 OSS 图片，一键存档到 Notion。

**版本**: 1.0.0  
**发布**: 2026-04-12  
**许可**: MIT  
**作者**: Ajay Hao

---

> ⚠️ **安全提示**
> - 本技能会抓取第三方平台内容，请确保您有权存档
> - 遵循各平台 robots.txt 和使用条款
> - 建议控制抓取频率，避免被封 IP
> - OSS Bucket 请配置最小权限（仅写入/读取）

---

## 📖 技能描述

### 核心能力

- 📰 **多平台支持**: 微信公众号、小红书、豆瓣、知乎
- 🔍 **智能识别**: 自动识别文章来源平台
- 📝 **内容提取**: 标题、作者、发布时间、正文、图片
- ☁️ **图床集成**: 阿里云 OSS 自动上传，永久链接
- 🚀 **一键存档**: 自动推送 Notion 数据库
- 📊 **字数统计**: 自动统计正文字数

### 技术特性

- **模块化设计**: 平台识别器 + 多抓取器 + 处理器 + 存档器
- **图片处理**: 自动上传文章图片到 OSS 并替换链接
- **格式转换**: HTML → Markdown，保留内容结构
- **配置驱动**: 环境变量管理敏感信息

---

## 🔐 安全与隐私说明

### 敏感数据处理

| 文件/路径 | 用途 | 敏感性 | 用户控制 |
|-----------|------|--------|----------|
| `~/.openclaw/.env` | API Keys 存储 | 高 | 用户自行配置，skill 不修改 |
| `/tmp/article-fetcher-*/` | 临时缓存 | 低 | 处理完成后可手动清理 |

### 外部服务端点

| 服务 | 域名 | 用途 | 传输数据 |
|------|------|------|----------|
| 阿里云 OSS | `oss-cn-*.aliyuncs.com` | 图床上传 | 文章图片 |
| Notion API | `api.notion.com` | 文章存档 | 文章元数据、内容 |
| 微信公众号 | `mp.weixin.qq.com` | 内容抓取 | 无（仅读取） |
| 小红书 | `xiaohongshu.com` | 内容抓取 | 无（仅读取） |
| 豆瓣 | `douban.com` | 内容抓取 | 无（仅读取） |
| 知乎 | `zhihu.com` | 内容抓取 | 无（仅读取） |

### 最小权限建议

- **OSS Bucket**: 创建专用 Bucket，仅授予 PutObject/GetObject 权限
- **API Keys**: 使用子账号 Key，设置 IP 白名单
- **测试环境**: 首次使用建议在隔离环境测试

---

## 🎯 平台支持详情

### 微信公众号（完整支持）

**识别**: ✅ `mp.weixin.qq.com`, `weixin.qq.com`  
**内容**: ✅ 标题、作者、发布时间、正文、图片  
**反爬**: ⚠️ 可能需要 Cookies（可选）

#### 操作步骤

```bash
cd ~/.openclaw/workspace-engineer/skills/article-fetcher
python main.py "https://mp.weixin.qq.com/s/xxx"
```

---

### 小红书（基本支持）

**识别**: ✅ `xiaohongshu.com`, `xhslink.com`  
**内容**: ✅ 标题、作者、正文、图片  
**反爬**: ⚠️ 可能需要 Cookies（可选）

#### 操作步骤

```bash
python main.py "https://www.xiaohongshu.com/explore/xxx"
```

---

### 豆瓣（完整支持）

**识别**: ✅ `douban.com`  
**内容**: ✅ 标题、作者、发布时间、正文  
**反爬**: ✅ 低

#### 操作步骤

```bash
python main.py "https://www.douban.com/note/xxx"
```

---

### 知乎（基本支持）

**识别**: ✅ `zhihu.com`  
**内容**: ✅ 标题、作者、正文、图片  
**反爬**: ⚠️ 可能需要 Cookies（可选）

#### 操作步骤

```bash
python main.py "https://www.zhihu.com/question/xxx/answer/xxx"
```

---

## ⚙️ 配置详解

### 环境变量（~/.openclaw/.env）

```bash
# ========== 必需配置 ==========

# 阿里云 OSS 图床
ALIYUN_OSS_AK=your_access_key_id
ALIYUN_OSS_SK=your_access_key_secret
ALIYUN_OSS_BUCKET_ID=your_bucket_name
ALIYUN_OSS_ENDPOINT=oss-cn-shanghai.aliyuncs.com

# Notion 存档
NOTION_API_KEY=nop_xxxxxxxxxxxxxxxx
NOTION_ARTICLE_DATABASE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### OSS Bucket 要求

- **访问权限**: 公开可读（直接 URL 访问）
- **CORS 配置**: 允许跨域访问（Notion 嵌入需要）
- **存储类型**: 标准存储（低频访问会影响加载速度）

### Notion 数据库配置

#### 数据库属性（Properties）

| 属性名 | 类型 | 说明 |
|--------|------|------|
| **Title** | `title` | 文章标题（≤200 字符） |
| **Source** | `rich_text` | 来源平台（wechat/xhs/douban/zhihu） |
| **Author** | `rich_text` | 作者名称 |
| **Link** | `url` | 原文链接 |
| **Tags** | `multi_select` | 标签（可选） |
| **PubDate** | `date` | 发布日期 |
| **Words** | `number` | 字数统计 |
| **ts** | `date` | 存档时间戳（ISO 8601，东八区 +08:00） |

#### 配置步骤

1. **创建数据库**（Table 视图）
2. **添加上述 8 个属性**（字段名必须完全匹配）
3. **获取 Database ID**：复制 URL 中 `?v=` 后的 ID
4. **配置环境变量**

---

## 🏗️ 系统架构

### 处理流程

```
用户输入 (文章 URL)
       ↓
Step 1: 平台识别
       ↓
Step 2: 内容抓取（根据平台选择抓取器）
       ↓
Step 3: 图片处理（上传 OSS + 替换链接）
       ↓
Step 4: 格式转换（HTML → Markdown）
       ↓
Step 5: 字数统计
       ↓
Step 6: Notion 存档
```

### 技术栈

| 层级 | 技术 |
|------|------|
| 核心层 | Python 3.7+ |
| 抓取层 | requests, BeautifulSoup4 |
| 转换层 | html2text |
| 存储层 | oss2, Notion API |

### 模块结构

```
article-fetcher/
├── main.py                 # 主程序入口
├── config.py              # 配置管理
├── detector/
│   └── platform_detector.py  # 平台识别器
├── fetchers/
│   ├── base_fetcher.py    # 基础抓取器
│   ├── wechat_fetcher.py  # 微信公众号
│   ├── xhs_fetcher.py     # 小红书
│   ├── douban_fetcher.py  # 豆瓣
│   └── zhihu_fetcher.py   # 知乎
├── processors/
│   ├── image_processor.py # 图片处理器
│   └── content_converter.py # 内容转换器
├── archiver/
│   └── notion_archiver.py # Notion 存档器
└── utils/
    └── word_counter.py    # 字数统计器
```

---

## 📋 使用方法

### 命令行

```bash
cd ~/.openclaw/workspace-engineer/skills/article-fetcher

# 基础用法
python main.py "文章 URL"

# 添加标签
python main.py "文章 URL" 标签 1 标签 2

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
    print(f"🏷️ 平台：{result['platform']}")
    print(f"🔢 字数：{result['word_count']}")
else:
    print(f"❌ {result['message']}")
```

---

## 📁 输出文件结构

### OSS 路径规范

**图片路径**: `/articles/<平台>/<文章 ID>/<图片文件>`

```
articles/wechat/abc123/image_001.jpg
articles/xhs/def456/image_002.jpg
articles/douban/ghi789/image_003.jpg
articles/zhihu/jkl012/image_004.jpg
```

---

## 🔧 故障排查

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 抓取失败 | 反爬机制 | 配置 Cookies 或使用代理 |
| 图片上传失败 | OSS 配置错误 | 检查 AK/SK/Bucket 配置 |
| Notion 推送失败 | API Key 过期 | 更新 NOTION_API_KEY |
| 平台识别失败 | URL 格式异常 | 检查 URL 完整性 |

### 查看详细日志

```bash
# 启用调试模式（修改 config.py）
DEBUG = True

# 查看错误输出
python main.py "URL" 2>&1 | tee fetch.log
```

---

## 📝 输出格式（Notion 页面）

1. **Title** — 文章标题
2. **Source** — 来源平台
3. **Author** — 作者
4. **Link** — 原文链接
5. **Tags** — 标签（可选）
6. **PubDate** — 发布日期
7. **Words** — 字数统计
8. **ts** — 存档时间
9. **Content** — 页面正文（Markdown 格式，图片已替换为 OSS 链接）

---

## 🔜 后续优化

### 计划中

- [ ] 添加更多平台支持（虎嗅、36 氪、Medium）
- [ ] 支持批量抓取（URL 列表文件）
- [ ] 添加 PDF 导出功能
- [ ] 支持定时抓取（RSS 订阅）
- [ ] 单元测试（核心函数覆盖率 80%+）

---

**维护人**: Ajay Hao  
**项目地址**: （待添加）  
**OpenClaw Skill**: 开发中
