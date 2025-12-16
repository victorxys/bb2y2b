"""
B站API服务 - 获取UP主空间视频列表
"""
import time
import random
import urllib.parse
import requests
import logging
import json
import os
from functools import reduce
from hashlib import md5
from typing import Tuple, List, Dict, Optional
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cookie文件路径（相对于项目根目录）
COOKIE_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'cookie.json')


class BilibiliService:
    """B站API服务类"""
    
    def __init__(self):
        self.img_key: Optional[str] = None
        self.sub_key: Optional[str] = None
        self.sessdata: Optional[str] = None
        self._load_cookie()
        self._init_wbi_keys()
    
    def _load_cookie(self) -> None:
        """从cookie.json加载Cookie"""
        try:
            if os.path.exists(COOKIE_FILE_PATH):
                with open(COOKIE_FILE_PATH, 'r') as f:
                    cookies = json.load(f)
                    self.sessdata = cookies.get('SESSDATA')
                    logger.info(f"Cookie加载成功: SESSDATA={self.sessdata[:10] if self.sessdata else 'None'}...")
            else:
                logger.warning(f"Cookie文件不存在: {COOKIE_FILE_PATH}")
        except Exception as e:
            logger.error(f"加载Cookie失败: {e}")
    
    def _get_random_user_agent(self) -> str:
        """获取随机User-Agent"""
        user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
        return random.choice(user_agents)
    
    def _get_mixin_key(self, orig: str) -> str:
        """对 imgKey 和 subKey 进行字符顺序打乱编码"""
        mixin_key_enc_tab = [
            46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
            33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40,
            61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11,
            36, 20, 34, 44, 52
        ]
        return reduce(lambda s, i: s + orig[i], mixin_key_enc_tab, '')[:32]
    
    def _enc_wbi(self, params: dict, img_key: str, sub_key: str) -> dict:
        """为请求参数进行 wbi 签名"""
        mixin_key = self._get_mixin_key(img_key + sub_key)
        curr_time = round(time.time())
        params['wts'] = curr_time
        params = dict(sorted(params.items()))
        # 过滤 value 中的 "!'()*" 字符
        params = {
            k: ''.join(filter(lambda chr: chr not in "!'()*", str(v)))
            for k, v in params.items()
        }
        query = urllib.parse.urlencode(params)
        wbi_sign = md5((query + mixin_key).encode()).hexdigest()
        params['w_rid'] = wbi_sign
        return params
    
    def _init_wbi_keys(self) -> None:
        """获取最新的 img_key 和 sub_key"""
        try:
            headers = {
                'User-Agent': self._get_random_user_agent()
            }
            logger.info("正在获取WBI Keys...")
            resp = requests.get('https://api.bilibili.com/x/web-interface/nav', headers=headers, timeout=10)
            resp.raise_for_status()
            json_content = resp.json()
            img_url: str = json_content['data']['wbi_img']['img_url']
            sub_url: str = json_content['data']['wbi_img']['sub_url']
            self.img_key = img_url.rsplit('/', 1)[1].split('.')[0]
            self.sub_key = sub_url.rsplit('/', 1)[1].split('.')[0]
            logger.info(f"WBI Keys获取成功: img_key={self.img_key[:8]}..., sub_key={self.sub_key[:8]}...")
        except Exception as e:
            logger.error(f"获取WBI Keys失败: {e}")
            self.img_key = None
            self.sub_key = None
    
    def get_space_videos(self, space_id: str, page: int = 1, page_size: int = 30) -> Dict:
        """
        获取UP主空间视频列表
        
        Args:
            space_id: UP主空间ID
            page: 页码
            page_size: 每页数量
            
        Returns:
            包含视频列表的字典
        """
        if not self.img_key or not self.sub_key:
            self._init_wbi_keys()
        
        if not self.img_key or not self.sub_key:
            return {"error": "无法获取WBI签名密钥", "videos": []}
        
        # 构建签名参数
        signed_params = self._enc_wbi(
            params={
                'mid': space_id,
                'pn': page,
                'ps': page_size
            },
            img_key=self.img_key,
            sub_key=self.sub_key
        )
        
        url = 'https://api.bilibili.com/x/space/wbi/arc/search'
        headers = {
            "User-Agent": self._get_random_user_agent(),
            'Referer': 'https://www.bilibili.com/',
        }
        
        # 添加Cookie
        cookies = {}
        if self.sessdata:
            cookies['SESSDATA'] = self.sessdata
        
        try:
            logger.info(f"请求B站API: space_id={space_id}, page={page}, has_cookie={bool(cookies)}")
            response = requests.get(url, headers=headers, params=signed_params, cookies=cookies, timeout=15)
            logger.info(f"B站API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"B站API响应code: {data.get('code')}, message: {data.get('message')}")
                if data.get('code') == 0:
                    videos = data.get('data', {}).get('list', {}).get('vlist', [])
                    logger.info(f"获取到 {len(videos)} 个视频")
                    return {
                        "success": True,
                        "data": data.get('data', {}),
                        "page": data.get('data', {}).get('page', {}),
                        "videos": videos
                    }
                else:
                    logger.error(f"B站API返回错误: {data.get('message')}")
                    return {"error": data.get('message', '未知错误'), "videos": []}
            else:
                logger.error(f"B站API请求失败: {response.status_code}")
                return {"error": f"请求失败: {response.status_code}", "videos": []}
        except Exception as e:
            logger.error(f"B站API请求异常: {e}")
            return {"error": str(e), "videos": []}
    
    def scan_all_videos(self, space_id: str, video_keyword: Optional[str] = None) -> List[Dict]:
        """
        扫描UP主所有视频
        
        Args:
            space_id: UP主空间ID
            video_keyword: 视频关键字过滤（逗号分隔）
            
        Returns:
            视频列表
        """
        logger.info(f"开始扫描空间: space_id={space_id}, keyword={video_keyword}")
        all_videos = []
        page = 1
        
        # 首先获取第一页，确定总数
        result = self.get_space_videos(space_id, page=1)
        
        if "error" in result and result.get("error"):
            logger.error(f"扫描失败: {result.get('error')}")
            return []
        
        page_info = result.get("page", {})
        total_count = page_info.get("count", 0)
        page_size = page_info.get("ps", 30)
        total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 1
        
        # 处理第一页视频
        videos = result.get("videos", [])
        filtered_videos = self._filter_videos(videos, video_keyword)
        all_videos.extend(filtered_videos)
        
        # 获取剩余页面（限制最多5页，避免请求过多）
        max_pages = min(total_pages, 5)
        for page in range(2, max_pages + 1):
            time.sleep(random.uniform(1, 2))  # 随机延迟
            result = self.get_space_videos(space_id, page=page)
            if "error" not in result or not result.get("error"):
                videos = result.get("videos", [])
                filtered_videos = self._filter_videos(videos, video_keyword)
                all_videos.extend(filtered_videos)
        
        return all_videos
    
    def _filter_videos(self, videos: List[Dict], video_keyword: Optional[str]) -> List[Dict]:
        """根据关键字过滤视频"""
        if not video_keyword:
            return videos
        
        keywords = [kw.strip() for kw in video_keyword.split(',') if kw.strip()]
        if not keywords:
            return videos
        
        filtered = []
        for video in videos:
            title = video.get('title', '')
            if any(kw in title for kw in keywords):
                filtered.append(video)
        
        return filtered


# 单例实例
bilibili_service = BilibiliService()