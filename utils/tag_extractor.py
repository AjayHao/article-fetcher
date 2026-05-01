"""
关键词提取模块
基于词频统计提取关键词，不依赖外部 LLM API
"""
import re


def extract_tags(html_content: str, max_tags: int = 5) -> list:
    """
    基于词频提取文章关键词（纯本地方案，不调用外部 API）

    Args:
        html_content (str): 文章 HTML 内容
        max_tags (int): 最多提取的关键词数量

    Returns:
        list: 关键词列表
    """
    # 清理 HTML 标签，提取纯文本（取前 8000 字符）
    text = re.sub(r'<[^>]+>', ' ', html_content)
    text = re.sub(r'\s+', ' ', text).strip()[:8000]

    if not text:
        return []

    return _extract(text, max_tags)


def _extract(text: str, max_tags: int) -> list:
    """
    基于文本频率提取关键词
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
