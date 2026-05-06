# Changelog

## v0.2.0 (2026-05-06)

### ✨ 关键词提取优化

- **LLM 优先策略**: 关键词提取优先调用 DashScope LLM 理解文章核心内容
- **智能降级**: LLM 失败或未配置 `DASHSCOPE_API_KEY` 时自动降级为本地词频分析
- **标题上下文**: 传递文章标题给 LLM，提升关键词提取准确度
- **超时重试**: 3 次重试机制（60s → 90s → 120s），兼容 429/5xx 错误
- **新增配置**: `.env.example` 添加 `DASHSCOPE_API_KEY`/`DASHSCOPE_BASE_URL`/`DASHSCOPE_MODEL` 说明

### 📝 文档更新

- SKILL.md 更新关键词提取描述（纯本地 → LLM 优先 + 降级方案）

---

## v0.1.1 (2026-05-01)

### 🐛 Bug 修复

- **关键词提取**: 移除 LLM API 依赖，改为纯本地词频方案，解决 Coding Plan Key 不能用于后端脚本的合规问题
- **知乎抓取**: 修复 `#HttpOnly` 前缀导致 Cookies 解析失败（base_fetcher.py）
- **知乎清理**: 移除知乎 HTML 中 64K+ CSS 噪音（内嵌 `<style>` 标签、动态 class、JS 属性）
- **知乎图片提取**: 修复图片选择器不匹配问题，提取 `_r.jpg` + `_720w.jpg` 双变体 URL
- **Notion 存档**: 修复单段文本超过 2000 字符导致 400 错误，段落/引用/代码块自动拆分
- **Notion 图片**: 修复知乎图片 SVG 占位符未被跳过的问题，增加 `data-original` 优先级

### 🔧 优化

- **Cookies 路径**: 默认路径改为 `~/.cookies/<platform>_cookies.txt`，可通过环境变量覆盖
- **安全文档**: SKILL.md 新增完整的「安全与隐私说明」章节
- **SKILL.md**: 更新关键词提取描述（LLM → 纯本地词频）

---

## v0.1.0 (2026-04-29)

### ✨ 初始版本

- 多平台支持：微信公众号、小红书、豆瓣、知乎
- 图片上传阿里云 OSS
- 关键词提取（LLM + 词频降级方案）
- 一键存档到 Notion
