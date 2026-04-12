# Article Fetcher

Article Fetcher 是一个强大的技能工具，可以抓取微信公众号、小红书、豆瓣、知乎等平台的文章，并将文章内容存档到Notion数据库。它还具有自动处理图片上传至阿里云OSS的功能，确保文章中的图片能够长期稳定访问。

## 功能特性

- ✅ **多平台支持**: 支持微信公众号、小红书、豆瓣、知乎四个平台的文章抓取
- ✅ **智能识别**: 自动识别文章来源平台
- ✅ **内容提取**: 自动提取文章标题、作者、发布时间、正文内容
- ✅ **图片处理**: 自动将文章中的图片上传到阿里云OSS并替换链接
- ✅ **格式转换**: 将HTML内容转换为Markdown格式
- ✅ **字数统计**: 统计正文内容字数（不包含图片链接）
- ✅ **Notion存档**: 将处理后的文章存档到指定的Notion数据库
- ✅ **标签支持**: 支持为文章添加标签

## 安装要求

- Python 3.7+
- pip包管理器

## 安装步骤

1. 克隆项目：
   ```bash
   git clone <repository-url>
   cd article-fetcher
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 配置环境变量：
   ```bash
   cp .env.example .env
   ```
   
   编辑 `.env` 文件并填入相应配置：
   ```
   ALIYUN_OSS_AK=your_oss_access_key
   ALIYUN_OSS_SK=your_oss_secret_key
   ALIYUN_OSS_BUCKET_ID=your_bucket_id
   ALIYUN_OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
   NOTION_API_KEY=your_notion_integration_token
   NOTION_ARTICLE_DATABASE_ID=your_notion_database_id
   ```

## Notion数据库设置

在您的Notion工作区中创建一个新的数据库，并确保包含以下字段：

- **Title** (Title类型) - 文章标题
- **Source** (Text类型) - 来源平台
- **Author** (Text类型) - 作者
- **Link** (URL类型) - 原文链接
- **Tags** (Multi-select类型) - 标签
- **PubDate** (Date类型) - 发布日期
- **Words** (Number类型) - 字数统计
- **ts** (Date类型) - 存档时间

## 使用方法

### 1. 命令行使用

```bash
python main.py <文章链接> [标签1] [标签2] ...
```

例如：
```bash
python main.py https://mp.weixin.qq.com/example wechat technology
python main.py https://www.zhihu.com/question/123456789 answer ai
```

### 2. 作为模块导入

```python
from main import fetch_and_archive_article

result = fetch_and_archive_article(
    url="https://example.com/article",
    tags=["tag1", "tag2"]
)

if result['success']:
    print(f"文章已成功存档: {result['title']}")
else:
    print(f"操作失败: {result['message']}")
```

## 支持的平台

| 平台 | 识别关键词 | 代码标识 |
|------|------------|----------|
| 微信公众号 | weixin.qq.com, mp.weixin.qq.com | wechat |
| 小红书 | xiaohongshu.com, xhslink.com | xhs |
| 豆瓣 | douban.com | douban |
| 知乎 | zhihu.com | zhihu |

## 安全说明

- 所有敏感配置信息通过环境变量管理，不在代码中硬编码
- 使用HTTPS协议进行所有外部请求
- 遵循最小权限原则，只访问必要的资源

## 注意事项

1. **反爬虫措施**: 部分网站可能有反爬虫机制，请适量请求，避免被封IP
2. **内容版权**: 请确保您有权抓取和存档这些内容
3. **Rate Limiting**: 请遵循各平台的使用条款和API限制
4. **稳定性**: 由于网页结构可能发生变化，若遇到抓取失败请及时更新解析规则

## 故障排除

如果遇到问题，请检查：
1. 环境变量是否配置正确
2. Notion集成是否已授权访问数据库
3. 网络连接是否正常
4. 防火墙或代理设置是否影响访问

## 扩展开发

要添加对新平台的支持，您需要：
1. 在 `detector/platform_detector.py` 中添加平台识别逻辑
2. 创建一个新的抓取器类继承自 `BaseFetcher`
3. 在 `main.py` 中注册新的抓取器

## 许可证

MIT License