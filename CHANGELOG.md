# Changelog

## v1.2.0 (2026-07-05)

### 🆕 知乎 403 二级回退

- **Playwright 浏览器回退**：`zhihu_fetcher.py` 新增 `_fetch_with_playwright()`，HTTP 403 时自动启动 headless Chromium 抓取
- **Cookies 注入**：Netscape Cookies 自动注入到 Playwright 浏览器上下文
- **二级策略**：HTTP (Cookies) → Playwright → 失败放弃（不生成垃圾文件）
- **`_parse()` 提取**：HTTP 和 Playwright 两条路径复用同一解析逻辑
- **Playwright 渲染等待**：`page.goto()` 后新增 `wait_for_timeout(3000)`，解决页面未渲染完就取内容报错
- **Pin 类型支持**：新增 `_extract_pin()` 方法，支持知乎想法（`/pin/`）解析，含图片懒加载修复

### 🐛 修复

- **ObsidianArchiver 无参构造**：`__init__` 改为可选 `vault_path` 参数，兼容各种调用场景
- **图片懒加载**：_extract_pin 中将 `data-original`/`data-actualsrc` 回填到 `src`，避免 OSS 替换时失配

### 📝 文档

- SKILL.md / README.md 新增知乎 403 回退策略说明
- metadata 新增 `playwright install chromium` 安装步骤

---

## v1.1.0 (2026-06-22)

### 🆕 Obsidian 本地存档

- **新增 `obsidian_archiver.py`**：HTML → Markdown 转换（`markdownify`），YAML Frontmatter，存入 `1-输入-收件箱/文章收藏/`
- **4 场景存档调度**：Obsidian 优先 / Notion 可选 / 双写 / 仅预览
- **`config.py` 重构**：Notion 移出必需校验，新增 `obsidian_available` / `notion_available` / `archive_available` 属性
- **文件名简化**：仅保留标题，去除日期前缀

### 🐛 修复

- **OSS URL 双协议头防御**：`image_processor.py` endpoint 前置 `lstrip` 处理
- **小红书 JSON 提取**：`xhs_fetcher.py` 改用 `html.unescape()` + `get_text()` 防 BS4 转义破坏 JSON
- **HTTP Session 复用**：`http_client.py` 改为模块级单例 + 连接池
- **微信图片空白**：`main.py` 新增 `data-src` → `src` 修复，解决懒加载图片在 Markdown 中丢失
- **`__init__.py` 恢复**：5 个子包补回 `__init__.py`，解决包导入失败

### 🔧 优化

- **`.env` 加载策略**：`$AGENT_HOME` > `$HERMES_HOME` > 当前目录，agent 无关通用方案
- **标签 Obsidian 兼容**：`tag_extractor.py` LLM prompt 约束 + 统一清洗空格→`-`
- **跨平台路径示例**：文档中 `OBSIDIAN_VAULT_PATH` 展示 Windows/macOS/Linux 三平台

### 📝 文档

- **SKILL.md / README.md 全面重写**：4 场景存档表、Obsidian Frontmatter 规范、Notion 降级为可选
- `openclaw` metadata → `hermes`，路径 `~/.hermes` → `$AGENT_HOME`

---

## v1.0.2 (2026-05-10)

### 🏗️ LLM 多平台抽象

- **统一 LLM 配置**：`config.py` 移除 DashScope 专属字段（`dashscope_api_key`/`dashscope_base_url`/`dashscope_model`），改为 `LLM_API_KEY` + `LLM_BASE_URL` + `LLM_MODEL` 通用配置
- **复用 video-summarizer 配置**：LLM 三个环境变量与 video-summarizer 共享 `.env`，无需重复设置
- **重构 `tag_extractor.py`**：`extract_tags_llm()` 改为 OpenAI 兼容接口，支持 DeepSeek / DashScope / OpenAI / Groq 等任意平台
- **LLM 可用性标记**：config 新增 `llm_available` 属性，一次判断即可决定是否启用 LLM
- **升级日志**：LLM 调用增加模型名称打印（如 `deepseek-v4-pro`），便于排错

---

## v1.0.1 (2026-05-07)

### 🔒 安全修复（ClawScan 扫描）

- **Cookie 域隔离**: `base_fetcher.py` 重构 `_load_cookies()` 保留 domain 字段，新增 `_apply_cookies_for_url(url)` 按目标域名过滤，防止登录态泄露到非目标站点
- **URL 严格校验**: `platform_detector.py` 改用 `urllib.parse.urlparse` + 白名单匹配 hostname，拒绝路径拼接攻击（如 `https://evil.com/mp.weixin.qq.com/...`）
- **依赖版本锁定**: `requirements.txt` `>=` → `==` 精确版本，降低供应链风险

### 📝 文档

- **安全说明**: SKILL.md 新增「安全与隐私」章节，披露 LLM 数据外发、Cookie 隔离、权限最小化等安全边界
- **扩展指南**: 更新平台扩展步骤（`ALLOWED_HOSTS` 替换旧正则描述）

---

## v1.0.0 (2026-05-07)

### 🎯 正式发布

- **文档精简**: SKILL.md 重写为精简扼要格式，层次清晰，面向用户与 Agent
- **版本标注**: 统一版本号为 v1.0.0（SKILL.md metadata、README、CHANGELOG）
- **清理冗余**: 移除 `tests/` 目录、`__init__.py`、`__pycache__/` 缓存文件
- **安全加固**: 消除 `config.py` 中 `DEBUG` 变量暴露到全局模块命名空间
- **SKILL.md**: 新增 Notion 数据库字段说明、扩展平台指南、模块调用示例

---

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
