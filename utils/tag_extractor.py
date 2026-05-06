"""
关键词提取模块
优先使用 LLM 理解文章核心内容并提取关键词
LLM 不可用或未配置时，降级为本地词频分析
"""
import re
import json
import requests
from utils.logger import logger
from config import config


# ============ LLM 关键词提取 ============

# 从 config 读取（若配置不存在则使用默认值）
DASHSCOPE_API_KEY = getattr(config, 'dashscope_api_key', None)
DASHSCOPE_BASE_URL = getattr(config, 'dashscope_base_url', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
DASHSCOPE_MODEL = getattr(config, 'dashscope_model', 'qwen3.5-plus')

# 关键词提取专用 prompt
TAG_EXTRACT_SYSTEM = (
    '你是一个专业的内容分析专家，擅长从文章中提取核心关键词。'
    '请分析文章内容，提取 5-8 个最能代表文章核心主题的关键词。'
)

TAG_EXTRACT_PROMPT = (
    '请分析以下文章的内容，提取 5-8 个核心关键词。\n\n'
    '## 要求\n'
    '1. 关键词应为文章的核心概念、技术术语、主题词或关键实体\n'
    '2. 避免通用词汇（如"方法""技巧""总结"）\n'
    '3. 中文关键词 2-8 字，英文关键词 2-15 字符\n'
    '4. 按重要性降序排列（最重要的在前）\n\n'
    '## 输出格式\n'
    '请严格按以下 JSON 格式输出：\n\n'
    '```json\n'
    '{{\n'
    '  "tags": ["关键词1", "关键词2", "关键词3", "关键词4", "关键词5"]\n'
    '}}\n'
    '```\n\n'
    '## 文章内容\n\n'
    '{content}\n\n'
    '请开始分析：'
)


def extract_tags_llm(text: str, max_tags: int = 5, title: str = '') -> list:
    """
    使用 LLM 分析文章内容并提取关键词

    Args:
        text (str): 文章纯文本内容
        max_tags (int): 最多提取的关键词数量
        title (str): 文章标题（可选，帮助 LLM 更好理解主题）

    Returns:
        list: 关键词列表，失败时返回空列表
    """
    if not DASHSCOPE_API_KEY:
        return []

    try:
        import requests

        # 限制输入长度（LLM context 限制）
        MAX_CHARS = 12000
        content = text[:MAX_CHARS]
        if len(text) > MAX_CHARS:
            content = text[:MAX_CHARS // 2] + '\n...[内容过长，已截断]...\n' + text[-MAX_CHARS // 2:]

        # 构建带标题的 prompt
        user_prompt = TAG_EXTRACT_PROMPT.format(content=content)
        if title:
            user_prompt = f'## 文章标题\n\n{title}\n\n' + user_prompt

        headers = {
            'Authorization': f'Bearer {DASHSCOPE_API_KEY}',
            'Content-Type': 'application/json'
        }

        data = {
            'model': DASHSCOPE_MODEL,
            'messages': [
                {'role': 'system', 'content': TAG_EXTRACT_SYSTEM},
                {'role': 'user', 'content': user_prompt}
            ],
            'stream': False
        }

        # 重试机制：超时 + 可重试 HTTP 错误（超时 60s → 90s → 120s）
        RETRYABLE_STATUS = {429, 500, 502, 503, 504}
        response = None
        for attempt in range(3):
            try:
                timeout = [60, 90, 120][attempt]
                response = requests.post(
                    f'{DASHSCOPE_BASE_URL}/chat/completions',
                    headers=headers,
                    json=data,
                    timeout=timeout
                )
                if response.status_code == 200:
                    break
                if response.status_code in RETRYABLE_STATUS:
                    if attempt < 2:
                        continue
                else:
                    return []
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                if attempt >= 2:
                    return []
                continue

        if response is None or response.status_code != 200:
            return []

        ai_response = response.json()['choices'][0]['message']['content']

        # 提取 JSON
        json_match = re.search(r'```json\s*(.*?)\s*```', ai_response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = ai_response

        result = json.loads(json_str)
        tags = result.get('tags', [])

        # 过滤：长度校验 + 去重
        filtered = []
        seen = set()
        for tag in tags:
            tag = tag.strip()
            if not tag or len(tag) < 2 or len(tag) > 15:
                continue
            if tag.lower() in seen:
                continue
            seen.add(tag.lower())
            filtered.append(tag)
            if len(filtered) >= max_tags:
                break

        return filtered

    except Exception as e:
        logger.warning(f"LLM 关键词提取失败，降级为本地词频分析: {e}")
        return []


# ============ 本地词频分析（降级方案） ============

# 中文常见停用词 + 通用技术词（避免提取到无意义词）
_STOPWORDS = {
    # 中文通用停用词
    '这个', '那个', '什么', '怎么', '为什么', '不是', '就是',
    '一个', '一些', '我们', '你们', '他们', '自己',
    '可以', '应该', '可能', '需要', '这里', '这样', '那么',
    '如果', '因为', '所以', '但是', '而且', '已经', '非常',
    '真正', '好的', '没有', '还有', '通过', '进行', '使用',
    '利用', '实现', '提供', '支持', '包括', '能够',
    '错误', '正确', '重要', '主要', '不同', '其他', '另外',
    # 中文通用名词（太宽泛）
    '文件', '内容', '信息', '数据', '代码', '功能', '方法',
    '问题', '结果', '方式', '过程', '步骤', '情况', '原因',
    '系统', '用户', '时间', '空间', '页面', '服务', '项目',
    '部分', '方式', '类型', '格式', '模式', '机制', '规则',
    '个文件', '个方法', '个函数', '个类', '个参数',
    # 英文通用技术词（太宽泛）
    'src', 'api', 'ts', 'js', 'ai', 'code', 'app', 'git',
    'get', 'set', 'log', 'file', 'type', 'data', 'info',
    'http', 'url', 'id', 'db', 'os', 'io', 'ui', 'ux',
    'new', 'run', 'cmd', 'fn', 'arg', 'val', 'str', 'obj',
    'func', 'mod', 'req', 'res', 'err', 'ctx', 'cfg',
}


def extract_tags_local(text: str, max_tags: int = 5) -> list:
    """
    基于词频统计提取关键词（本地降级方案）

    Args:
        text (str): 文章纯文本内容
        max_tags (int): 最多提取的关键词数量

    Returns:
        list: 关键词列表
    """
    # 提取中文词汇（2-8 字）
    chinese_words = re.findall(r'[\u4e00-\u9fa5]{2,8}', text)
    # 英文技术术语：PascalCase（如 'AutoCompact'）或全大写（如 'MCP'）
    english_words = re.findall(r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)*|[A-Z]{2,10})\b', text)

    all_words = chinese_words + [w.lower() for w in english_words]

    # 统计词频
    freq = {}
    for word in all_words:
        w = word.lower()
        if w not in _STOPWORDS and len(w) >= 2:
            freq[w] = freq.get(w, 0) + 1

    # 按频率排序，取前 max_tags
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w for w, _ in sorted_words[:max_tags]]


# ============ 主入口 ============

def extract_tags(html_content: str, max_tags: int = 5, title: str = '') -> list:
    """
    提取文章关键词（LLM 优先，本地词频降级）

    策略：
    1. 尝试 LLM 分析（需配置 DASHSCOPE_API_KEY）
    2. LLM 失败或未配置 → 降级为本地词频分析

    Args:
        html_content (str): 文章 HTML 内容
        max_tags (int): 最多提取的关键词数量
        title (str): 文章标题（可选，帮助 LLM 更好理解主题）

    Returns:
        list: 关键词列表
    """
    # 清理 HTML 标签，提取纯文本（取前 8000 字符）
    text = re.sub(r'<[^>]+>', ' ', html_content)
    text = re.sub(r'\s+', ' ', text).strip()[:8000]

    if not text:
        return []

    # 优先尝试 LLM 提取
    if DASHSCOPE_API_KEY:
        llm_tags = extract_tags_llm(text, max_tags, title)
        if llm_tags:
            return llm_tags

    # 降级为本地词频分析
    return extract_tags_local(text, max_tags)
