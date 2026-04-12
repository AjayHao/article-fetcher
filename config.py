import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class ConfigManager:
    """配置管理器，集中管理所有环境变量配置"""

    def __init__(self):
        # 调试模式
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'

        # 阿里云 OSS 配置
        self.aliyun_oss_ak = os.getenv('ALIYUN_OSS_AK')
        self.aliyun_oss_sk = os.getenv('ALIYUN_OSS_SK')
        self.aliyun_oss_bucket_id = os.getenv('ALIYUN_OSS_BUCKET_ID')
        self.aliyun_oss_endpoint = os.getenv('ALIYUN_OSS_ENDPOINT')

        # Notion 配置
        self.notion_api_key = os.getenv('NOTION_API_KEY')
        self.notion_article_database_id = os.getenv('NOTION_ARTICLE_DATABASE_ID')

        # 可选配置：Cookies（用于反爬）
        self.wechat_cookies = os.getenv('WECHAT_COOKIES_FILE')
        self.xhs_cookies = os.getenv('XHS_COOKIES_FILE')
        self.zhihu_cookies = os.getenv('ZHIHU_COOKIES_FILE')

        # 验证必需的配置是否存在
        self._validate_config()

    def _validate_config(self):
        """验证配置是否完整"""
        missing_configs = []

        if not self.aliyun_oss_ak:
            missing_configs.append('ALIYUN_OSS_AK')
        if not self.aliyun_oss_sk:
            missing_configs.append('ALIYUN_OSS_SK')
        if not self.aliyun_oss_bucket_id:
            missing_configs.append('ALIYUN_OSS_BUCKET_ID')
        if not self.aliyun_oss_endpoint:
            missing_configs.append('ALIYUN_OSS_ENDPOINT')
        if not self.notion_api_key:
            missing_configs.append('NOTION_API_KEY')
        if not self.notion_article_database_id:
            missing_configs.append('NOTION_ARTICLE_DATABASE_ID')

        if missing_configs:
            raise ValueError(f"缺少必要的环境变量配置：{', '.join(missing_configs)}")

# 创建全局配置实例
config = ConfigManager()
