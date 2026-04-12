项目名称： Article Fetcher（文章收藏+Notion存档）
项目目标： 形成独立的技能(Skill)，并具备最终发布到Clawhub进行技能公开的标准，因此技能审查安全性、说明文档完整性需要格外关注
技能简介： 通过链接识别平台，抓取文章，将文章中的图片推送到阿里云OSS，并替换图片链接后，传送到Notion进行归档
支持平台： 微信公众号、小红书、豆瓣、知乎
运行平台： Linux Ubuntu 24.04
程序运行语言： Python为主
需求描述： 
1. 认真学习技能市场上wechat-article-parser(https://cn.clawhub-mirror.com/harven-droid/wechat-article-parser) 的实现原理, 自动提取文章标题、作者、发布时间、完整正文内容、图片链接提取。
2. 4个平台的字典名-字典码: 微信公众号-wechat, 小红书-xhs, 豆瓣-douban, 知乎-zhihu
3. 将图片上传至阿里云OSS，在bucket中的路径格式：`/articles/<平台字典码>/<文章Id>/`, 图床配置所谓openclaw的统一配置变量保存在.env中，具体如下：
ALIYUN_OSS_AK=oss_ak
ALIYUN_OSS_SK=oss_sk
ALIYUN_OSS_BUCKET_ID=buck_id
ALIYUN_OSS_ENDPOINT=oss-xxx.aliyuncs.com
4. 保持正文内容一字不变，进行html-to-markdown等成熟Python脚本库对正文进行markdown转换,将原图路径对应替换为上传至OSS后的路径。
5. 对正文内容进行字数统计（不包含图片链接）
6. 上传至Notion，Notion的API_KEY与数据库ID需要配置如下，同样保存在.env中
NOTION_API_KEY=xxx
NOTION_ARTICLE_DATABASE_ID=yyy
7. Notion数据库结构：
```
┌─────────┬──────────┬─────────┬──────┬──────┬─────────┬────────┬─────────────┐
│ Title   │ Source   │ Author  │ Link │ Tags │ PubDate │ Words  │ ts          │
│ title   │ text     │ text    │ url  │ multi│ date    │ number │ date        │
└─────────┴──────────┴─────────┴──────┴──────┴─────────┴────────┴─────────────┘
```