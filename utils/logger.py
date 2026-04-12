"""
日志工具模块
提供统一的日志记录功能
"""
import logging
import sys
from pathlib import Path

# 创建日志目录
log_dir = Path.home() / '.openclaw' / 'workspace-engineer' / 'skills' / 'article-fetcher' / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)

# 配置日志格式
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 创建控制台处理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# 创建文件处理器（调试模式启用）
file_handler = logging.FileHandler(log_dir / 'article-fetcher.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# 创建 logger
logger = logging.getLogger('article-fetcher')
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# 导出 logger 实例
__all__ = ['logger']
