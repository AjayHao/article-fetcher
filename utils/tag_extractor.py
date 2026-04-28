"""
关键词提取模块
使用 LLM 分析文章内容并提炼关键词，失败时降级到基于词频的方案
"""
import json
import re
import requests
import os


def extract_tags(html_content: str, max_tags: int = 5) -> list:
    """
    使用 LLM 提取文章关键词

    Args:
        html_content (str): 文章 HTML 内容
        max_tags (int): 最多提取的关键词数量

    Returns:
        list: 关键词列表
    """
    # 清理 HTML 标签，提取纯文本（取前 8000 字符作为上下文）
    text = re.sub(r'<[^>]+>', ' ', html_content)
    text = re.sub(r'\s+', ' ', text).strip()[:8000]

    if not text:
        return []

    # 获取 API 配置（尝试多个可能的 API endpoint）
    api_key = os.getenv('DASHSCOPE_API_KEY')
    model = os.getenv('DASHSCOPE_MODEL', 'qwen-turbo')
    base_url = os.getenv('DASHSCOPE_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
    # coding.dashscope 是编程专用 API，不支持对话模型，改用标准 API
    if 'coding.dashscope' in base_url:
        base_url = 'https://dashscope.aliyuncs.com/compatible-mode/v1'

    if api_key:
        try:
            resp = requests.post(
                f'{base_url}/chat/completions',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': model,
                    'messages': [
                        {
                            'role': 'system',
                            'content': '你是一个专业的内容分析助手。请阅读用户提供的文章内容，提炼出最核心的关键词。'
                        },
                        {
                            'role': 'user',
                            'content': f'请阅读以下文章内容，提炼出 {max_tags} 个最能概括文章核心主题的关键词（中文为主，技术术语可用英文）。\n\n'
                                       f'要求：\n'
                                       f'1. 每个关键词 2-6 个字符\n'
                                       f'2. 覆盖文章的核心技术点、主题领域\n'
                                       f'3. 不要使用过于宽泛的词（如"技术"、"文章"、"api"、"src"、"ts"、"ai"、"code"）\n'
                                       f'4. 优先选择文章中反复出现的专有名词、技术概念\n'
                                       f'5. 直接返回 JSON 数组格式，如 ["关键词1", "关键词2"]，不要其他文字\n\n'
                                       f'文章内容：\n{text}'
                        }
                    ],
                    'temperature': 0.3,
                    'max_tokens': 200
                },
                timeout=30
            )
            resp.raise_for_status()
            data = resp.json()
            content = data['choices'][0]['message']['content'].strip()

            # 尝试解析 JSON
            # 移除可能的 markdown 代码块标记
            content = re.sub(r'^```(?:json)?\s*', '', content)
            content = re.sub(r'\s*```$', '', content)

            tags = json.loads(content)
            if isinstance(tags, list):
                tags = [str(t).strip() for t in tags if str(t).strip() and len(str(t).strip()) >= 2]
                if tags:
                    return tags[:max_tags]

        except Exception as e:
            print(f"LLM 提取关键词失败: {e}")

    # 降级方案：基于文本频率提取
    return _fallback_extract(text, max_tags)


def _fallback_extract(text: str, max_tags: int) -> list:
    """
    基于文本频率的降级关键词提取方案
    """
    # 中文常见停用词 + 通用技术词（避免提取到无意义词）
    stopwords = {
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

    # 提取中文词汇（2-6 字）
    chinese_words = re.findall(r'[\u4e00-\u9fa5]{2,8}', text)
    # 英文技术术语：PascalCase（如 'AutoCompact'）或全大写（如 'MCP'）
    english_words = re.findall(r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)*|[A-Z]{2,10})\b', text)

    all_words = chinese_words + [w.lower() for w in english_words]

    # 统计词频
    freq = {}
    for word in all_words:
        w = word.lower()
        if w not in stopwords and len(w) >= 2:
            freq[w] = freq.get(w, 0) + 1

    # 按频率排序，取前 max_tags
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w for w, _ in sorted_words[:max_tags]]
