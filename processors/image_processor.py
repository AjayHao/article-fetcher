import oss2
import os
import uuid
from urllib.parse import urlparse
from config import config

class ImageProcessor:
    """
    图片处理器，负责将图片上传到阿里云OSS
    """

    def __init__(self):
        # 初始化OSS客户端
        auth = oss2.Auth(config.aliyun_oss_ak, config.aliyun_oss_sk)
        self.bucket = oss2.Bucket(auth, f'https://{config.aliyun_oss_endpoint}', config.aliyun_oss_bucket_id)

    def upload_images(self, image_urls: list, platform: str, article_id: str) -> dict:
        """
        批量上传图片到OSS

        Args:
            image_urls (list): 图片URL列表
            platform (str): 平台标识符 (wechat, xhs, douban, zhihu)
            article_id (str): 文章唯一标识

        Returns:
            dict: 原始URL到OSS URL的映射字典
        """
        url_mapping = {}

        for idx, img_url in enumerate(image_urls):
            try:
                # 解析原始图片URL，获取文件扩展名
                parsed_url = urlparse(img_url)
                ext = os.path.splitext(parsed_url.path)[1]

                # 生成OSS存储路径
                oss_path = f"articles/{platform}/{article_id}/{uuid.uuid4()}{ext}"

                # 下载图片内容
                import requests
                response = requests.get(img_url)
                response.raise_for_status()

                # 上传到OSS
                result = self.bucket.put_object(oss_path, response.content)

                if result.status == 200:
                    # 生成OSS访问URL
                    oss_url = f"https://{config.aliyun_oss_bucket_id}.{config.aliyun_oss_endpoint}/{oss_path}"
                    url_mapping[img_url] = oss_url
                else:
                    print(f"上传图片失败: {img_url}")

            except Exception as e:
                print(f"处理图片时发生错误: {img_url}, 错误: {str(e)}")
                continue

        return url_mapping