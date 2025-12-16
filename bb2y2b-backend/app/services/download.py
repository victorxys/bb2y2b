"""
视频下载服务 - 基于 batch_download.py 的核心逻辑
"""
import os
import re
import json
import time
import random
import logging
import urllib.parse
import requests
from functools import reduce
from hashlib import md5
from typing import Optional, Dict, List, Tuple
from pathlib import Path
from moviepy.editor import AudioFileClip, concatenate_audioclips, ImageClip, ColorClip, concatenate_videoclips, CompositeVideoClip
from tqdm import tqdm

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 项目根目录 (bb2y2b-backend 的父目录)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# 动态确定正确的路径
import os
_cwd = Path(os.getcwd())
if (_cwd.parent / 'cookie.json').exists():
    PROJECT_ROOT = _cwd.parent
elif (_cwd / 'cookie.json').exists():
    PROJECT_ROOT = _cwd
elif (Path(__file__).parent.parent.parent.parent / 'cookie.json').exists():
    PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

COOKIE_FILE_PATH = PROJECT_ROOT / 'cookie.json'
VIDEO_OUTPUT_PATH = PROJECT_ROOT / 'video'
COVER_OUTPUT_PATH = PROJECT_ROOT / 'cover'
MERGED_VIDEO_PATH = PROJECT_ROOT / 'merged_video'
SUBTITLE_OUTPUT_PATH = PROJECT_ROOT / 'srt'


class DownloadService:
    """视频下载服务类"""
    
    def __init__(self):
        self.sessdata: Optional[str] = None
        self.img_key: Optional[str] = None
        self.sub_key: Optional[str] = None
        self._load_cookie()
        self._init_wbi_keys()
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保输出目录存在"""
        VIDEO_OUTPUT_PATH.mkdir(exist_ok=True)
        COVER_OUTPUT_PATH.mkdir(exist_ok=True)
        MERGED_VIDEO_PATH.mkdir(exist_ok=True)
        SUBTITLE_OUTPUT_PATH.mkdir(exist_ok=True)
    
    def _load_cookie(self) -> None:
        """从cookie.json加载Cookie"""
        try:
            if COOKIE_FILE_PATH.exists():
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
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        return random.choice(user_agents)
    
    def _get_headers(self, referer: str = 'https://www.bilibili.com/') -> Dict:
        """获取请求头"""
        return {
            'User-Agent': self._get_random_user_agent(),
            'Referer': referer,
        }
    
    def _get_cookies(self) -> Dict:
        """获取Cookie字典"""
        cookies = {}
        if self.sessdata:
            cookies['SESSDATA'] = self.sessdata
        return cookies
    
    def _get_mixin_key(self, orig: str) -> str:
        """对 imgKey 和 subKey 进行字符顺序打乱编码"""
        mixin_key_enc_tab = [
            46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
            33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40,
            61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11,
            36, 20, 34, 44, 52
        ]
        return reduce(lambda s, i: s + orig[i], mixin_key_enc_tab, '')[:32]
    
    def _enc_wbi(self, params: dict) -> dict:
        """为请求参数进行 wbi 签名"""
        if not self.img_key or not self.sub_key:
            self._init_wbi_keys()
        
        if not self.img_key or not self.sub_key:
            logger.error("无法获取WBI签名密钥")
            return params
        
        mixin_key = self._get_mixin_key(self.img_key + self.sub_key)
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
    
    def get_video_info(self, bvid: str) -> Optional[Dict]:
        """
        获取视频信息
        
        Args:
            bvid: B站视频BV号
            
        Returns:
            视频信息字典，包含 title, videos, cover, pages_and_cids 等
        """
        video_info_url = f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}'
        
        retries = 5
        while retries > 0:
            try:
                response = requests.get(
                    video_info_url, 
                    headers=self._get_headers(),
                    cookies=self._get_cookies(),
                    timeout=15
                )
                video_info = response.json()
                
                if video_info['code'] == 0:
                    data = video_info['data']
                    title = data['title']
                    pic = data['pic']
                    desc = data.get('desc', '')
                    videos = data['videos']
                    pages = data['pages']
                    cids = [page['cid'] for page in pages]
                    
                    # 构建 [page, cid] 格式的列表
                    pages_and_cids = [[page['page'], cid] for page, cid in zip(pages, cids)]
                    
                    return {
                        'title': title,
                        'cover': pic,
                        'description': desc,
                        'video_count': videos,
                        'pages_and_cids': pages_and_cids
                    }
                else:
                    retries -= 1
                    logger.warning(f"获取视频{bvid}信息失败, 剩余尝试次数{retries}/5")
                    time.sleep(5)
                    
            except requests.RequestException as e:
                retries -= 1
                logger.error(f"请求异常: {e}, 剩余尝试次数{retries}/5")
                time.sleep(5)
        
        return None
    
    def get_download_links(self, bvid: str, cid: int, download_type: str = 'dash') -> Optional[str]:
        """
        获取下载链接 (使用WBI签名)
        
        Args:
            bvid: B站视频BV号
            cid: 视频cid
            download_type: 下载类型 'dash' 或 'mp4'
            
        Returns:
            音频下载URL
        """
        download_url = 'https://api.bilibili.com/x/player/wbi/playurl'
        
        # fnval=16 表示DASH格式，会返回分离的音视频流
        # fnval=1 表示MP4格式
        fnval = 16 if download_type == 'dash' else 1
        
        # 构建参数并进行WBI签名
        params = {
            'bvid': bvid,
            'cid': cid,
            'qn': 80,  # 1080P
            'fnval': fnval,
            'fnver': 0,
            'fourk': 1,
        }
        
        # 使用WBI签名
        signed_params = self._enc_wbi(params)
        
        max_attempts = 5
        for attempt in range(1, max_attempts + 1):
            try:
                response = requests.get(
                    download_url, 
                    params=signed_params, 
                    headers=self._get_headers(f'https://www.bilibili.com/video/{bvid}'),
                    cookies=self._get_cookies(),
                    timeout=15
                )
                download_info = response.json()
                
                logger.info(f"获取下载链接响应: code={download_info.get('code')}, message={download_info.get('message')}")
                
                if download_info['code'] == 0:
                    if download_type == 'dash':
                        # DASH格式返回音频流
                        audio_list = download_info.get('data', {}).get('dash', {}).get('audio', [])
                        if audio_list:
                            # 选择最高质量的音频
                            audio_list.sort(key=lambda x: x.get('bandwidth', 0), reverse=True)
                            audio_url = audio_list[0].get('base_url') or audio_list[0].get('baseUrl')
                            logger.info(f"获取到音频链接: {audio_url[:50]}...")
                            return audio_url
                        else:
                            logger.error("DASH格式中没有找到音频流")
                            return None
                    else:
                        # MP4格式
                        durl = download_info.get('data', {}).get('durl', [])
                        if durl:
                            return durl[0].get('url')
                        return None
                else:
                    logger.warning(f"第{attempt}次获取链接失败: code={download_info.get('code')}, message={download_info.get('message')}")
                    # 如果是-403风控错误，重新获取WBI keys
                    if download_info.get('code') == -403:
                        self._init_wbi_keys()
                        signed_params = self._enc_wbi(params)
                    time.sleep(3)
                    
            except Exception as e:
                logger.error(f"获取下载链接异常: {e}")
                time.sleep(3)
        
        return None
    
    def download_audio(self, url: str, output_path: str, progress_callback=None) -> Tuple[bool, int]:
        """
        下载音频文件
        
        Args:
            url: 音频URL
            output_path: 输出文件路径
            progress_callback: 进度回调函数 (downloaded_bytes, total_bytes)
            
        Returns:
            (是否下载成功, 文件大小)
        """
        try:
            headers = self._get_headers()
            response = requests.get(url, headers=headers, stream=True, timeout=120)
            
            file_size = int(response.headers.get('Content-Length', 0))
            
            if file_size < 500 * 1024:  # 小于500KB跳过
                logger.warning(f"文件大小 {file_size/1024:.2f}KB 太小，跳过")
                return False, 0
            
            downloaded = 0
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=32768):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            progress_callback(downloaded, file_size)
            
            logger.info(f"下载完成: {output_path}, 大小: {file_size/1024/1024:.2f}MB")
            return True, file_size
            
        except Exception as e:
            logger.error(f"下载失败: {e}")
            return False, 0

    def get_ai_subtitle(self, bvid: str, cid: int) -> Optional[Dict]:
        """
        获取AI生成的字幕/总结内容
        
        根据 https://socialsisteryi.github.io/bilibili-API-collect/docs/video/summary.html
        
        Args:
            bvid: B站视频BV号
            cid: 视频cid
            
        Returns:
            AI字幕数据字典，包含 summary, outline 等
        """
        # AI总结接口
        summary_url = 'https://api.bilibili.com/x/web-interface/view/conclusion/get'
        
        params = {
            'bvid': bvid,
            'cid': cid,
            'up_mid': '',  # UP主mid，可选
        }
        
        # 使用WBI签名
        signed_params = self._enc_wbi(params)
        
        try:
            response = requests.get(
                summary_url,
                params=signed_params,
                headers=self._get_headers(f'https://www.bilibili.com/video/{bvid}'),
                cookies=self._get_cookies(),
                timeout=15
            )
            result = response.json()
            
            if result.get('code') == 0:
                data = result.get('data', {})
                model_result = data.get('model_result', {})
                
                if model_result:
                    logger.info(f"获取到AI字幕: bvid={bvid}, cid={cid}")
                    return {
                        'summary': model_result.get('summary', ''),
                        'outline': model_result.get('outline', []),
                        'result_type': model_result.get('result_type', 0),
                    }
                else:
                    logger.info(f"视频没有AI字幕: bvid={bvid}")
                    return None
            else:
                logger.warning(f"获取AI字幕失败: code={result.get('code')}, message={result.get('message')}")
                return None
                
        except Exception as e:
            logger.error(f"获取AI字幕异常: {e}")
            return None

    def download_subtitle(self, bvid: str, cid: int, output_path: str) -> Optional[str]:
        """
        下载AI字幕并保存为TXT格式
        
        Args:
            bvid: B站视频BV号
            cid: 视频cid
            output_path: 输出文件路径
            
        Returns:
            保存的文件路径，失败返回None
        """
        logger.info(f"开始获取AI字幕: bvid={bvid}, cid={cid}")
        subtitle_data = self.get_ai_subtitle(bvid, cid)
        
        if not subtitle_data:
            logger.warning(f"未获取到AI字幕数据: bvid={bvid}, cid={cid}")
            return None
        
        try:
            # 生成字幕内容
            content_lines = []
            
            # 添加总结
            summary = subtitle_data.get('summary', '')
            if summary:
                content_lines.append("【AI总结】")
                content_lines.append(summary)
                content_lines.append("")
                logger.info(f"添加AI总结，长度: {len(summary)} 字符")
            
            # 添加大纲（带时间戳）
            outline = subtitle_data.get('outline', [])
            if outline:
                content_lines.append("【视频大纲】")
                logger.info(f"添加视频大纲，共 {len(outline)} 个章节")
                for idx, item in enumerate(outline, 1):
                    title = item.get('title', '')
                    timestamp = item.get('timestamp', 0)
                    # 格式化时间戳
                    minutes = int(timestamp // 60)
                    seconds = int(timestamp % 60)
                    time_str = f"{minutes:02d}:{seconds:02d}"
                    content_lines.append(f"{idx}. [{time_str}] {title}")
                    
                    # 添加子内容
                    part_outline = item.get('part_outline', [])
                    for sub_item in part_outline:
                        sub_timestamp = sub_item.get('timestamp', 0)
                        sub_content = sub_item.get('content', '')
                        sub_minutes = int(sub_timestamp // 60)
                        sub_seconds = int(sub_timestamp % 60)
                        sub_time_str = f"{sub_minutes:02d}:{sub_seconds:02d}"
                        content_lines.append(f"   - [{sub_time_str}] {sub_content}")
                content_lines.append("")
            
            # 生成最终内容
            final_content = '\n'.join(content_lines)
            logger.info(f"生成字幕内容，总长度: {len(final_content)} 字符")
            
            # 确保输出目录存在
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            # 验证文件是否保存成功
            if Path(output_path).exists():
                file_size = Path(output_path).stat().st_size
                logger.info(f"AI字幕保存成功: {output_path}, 文件大小: {file_size} 字节")
                return output_path
            else:
                logger.error(f"字幕文件保存失败，文件不存在: {output_path}")
                return None
            
        except Exception as e:
            logger.error(f"保存AI字幕失败: {e}", exc_info=True)
            return None

    def download_video_with_progress(
        self, 
        task_id: str,
        bvid: str, 
        start_p: int = 1, 
        end_p: Optional[int] = None,
        video_type: str = 'sleep',
    ) -> Optional[Dict]:
        """
        下载视频（音频）并合并，带进度跟踪
        
        Args:
            task_id: 任务ID
            bvid: B站视频BV号
            start_p: 起始分P
            end_p: 结束分P
            video_type: 视频类型
            
        Returns:
            下载结果字典
        """
        from app.services.download_manager import download_manager, TaskStatus
        
        logger.info(f"开始下载视频: task_id={task_id}, bvid={bvid}, start_p={start_p}, end_p={end_p}")
        
        # 更新任务状态
        download_manager.update_task(
            task_id,
            status=TaskStatus.DOWNLOADING,
            stage="fetching_info",
            stage_message="正在获取视频信息..."
        )
        
        # 1. 获取视频信息
        video_info = self.get_video_info(bvid)
        if not video_info:
            logger.error(f"无法获取视频信息: {bvid}")
            download_manager.update_task(
                task_id,
                status=TaskStatus.ERROR,
                error_message="无法获取视频信息"
            )
            return None
        
        title = video_info['title']
        video_count = video_info['video_count']
        pages_and_cids = video_info['pages_and_cids']
        cover_url = video_info['cover']
        
        logger.info(f"视频标题: {title}, 总分P数: {video_count}")
        
        # 更新任务标题
        download_manager.update_task(task_id, title=title)
        
        # 设置结束分P
        if end_p is None:
            end_p = video_count
        
        # 文件名前缀
        file_prefix = f"{bvid}_{start_p}_{end_p}"
        
        # 2. 获取所有分P的下载链接
        download_manager.update_task(
            task_id,
            stage="fetching_links",
            stage_message="正在获取下载链接..."
        )
        
        page_download_links = []
        for page, cid in pages_and_cids:
            if page < start_p or page > end_p:
                continue
            
            download_link = self.get_download_links(bvid, cid, 'dash')
            if download_link:
                page_download_links.append({
                    'page': page,
                    'cid': cid,
                    'download_link': download_link
                })
            else:
                logger.error(f"无法获取第{page}P的下载链接")
                download_manager.update_task(
                    task_id,
                    status=TaskStatus.ERROR,
                    error_message=f"无法获取第{page}P的下载链接"
                )
                return None
            
            time.sleep(0.3)
        
        if not page_download_links:
            logger.error("没有可下载的分P")
            download_manager.update_task(
                task_id,
                status=TaskStatus.ERROR,
                error_message="没有可下载的分P"
            )
            return None
        
        total_pages = len(page_download_links)
        logger.info(f"获取到 {total_pages} 个分P的下载链接")
        
        download_manager.update_task(
            task_id,
            total_pages=total_pages,
            stage="downloading",
            stage_message=f"准备下载 {total_pages} 个分P"
        )
        
        # 3. 下载所有音频片段
        audio_files = []
        temp_dir = MERGED_VIDEO_PATH / 'temp'
        temp_dir.mkdir(exist_ok=True)
        
        total_downloaded_bytes = 0
        estimated_total_bytes = 0
        
        for idx, item in enumerate(page_download_links):
            page = item['page']
            download_link = item['download_link']
            
            audio_file = temp_dir / f"{file_prefix}_{page}.mp3"
            
            logger.info(f"下载第 {page}/{end_p} P ({idx+1}/{total_pages})")
            
            download_manager.update_task(
                task_id,
                current_page=idx + 1,
                stage="downloading",
                stage_message=f"下载第 {page} P ({idx+1}/{total_pages})"
            )
            
            # 创建进度回调
            def progress_cb(downloaded: int, total: int):
                nonlocal total_downloaded_bytes, estimated_total_bytes
                if estimated_total_bytes == 0 and total > 0:
                    # 估算总大小
                    estimated_total_bytes = total * total_pages
                    download_manager.update_task(task_id, total_bytes=estimated_total_bytes)
                
                current_total = total_downloaded_bytes + downloaded
                download_manager.update_task(task_id, current_bytes=current_total)
            
            success, file_size = self.download_audio(download_link, str(audio_file), progress_cb)
            if success:
                audio_files.append(str(audio_file))
                total_downloaded_bytes += file_size
            else:
                logger.warning(f"第{page}P下载失败，跳过")
            
            time.sleep(0.2)
        
        if not audio_files:
            logger.error("没有成功下载任何音频文件")
            download_manager.update_task(
                task_id,
                status=TaskStatus.ERROR,
                error_message="没有成功下载任何音频文件"
            )
            return None
        
        # 4. 合并音频
        logger.info(f"开始合并 {len(audio_files)} 个音频文件")
        
        download_manager.update_task(
            task_id,
            status=TaskStatus.MERGING,
            stage="merging",
            stage_message=f"正在加载 {len(audio_files)} 个音频文件...",
            merge_progress=0
        )
        
        merged_audio_path = temp_dir / f"{file_prefix}_merged.mp3"
        
        try:
            # 逐个加载音频文件并更新进度 (0-30%)
            audio_clips = []
            total_duration = 0
            total_files = len(audio_files)
            for idx, audio_file in enumerate(audio_files):
                load_progress = int(((idx + 1) / total_files) * 30)
                download_manager.update_task(
                    task_id,
                    stage="merging",
                    stage_message=f"加载音频 {idx+1}/{total_files}...",
                    merge_progress=load_progress
                )
                clip = AudioFileClip(audio_file)
                audio_clips.append(clip)
                total_duration += clip.duration
            
            # 加载完成，开始合并 (30-40%)
            download_manager.update_task(
                task_id,
                stage="merging",
                stage_message=f"合并音频片段... 总时长: {self._format_duration(total_duration)}",
                total_duration=total_duration,
                merge_progress=35
            )
            
            final_audio = concatenate_audioclips(audio_clips)
            
            # 合并完成，开始写入 (40%)
            download_manager.update_task(
                task_id,
                stage="merging",
                stage_message=f"写入音频文件... 总时长: {self._format_duration(total_duration)}",
                merge_progress=40
            )
            
            # 写入音频文件 (40-95%)
            final_audio.write_audiofile(
                str(merged_audio_path), 
                logger=None,
                verbose=False
            )
            
            # 写入完成 (100%)
            download_manager.update_task(
                task_id,
                stage="merging",
                stage_message="音频合并完成",
                merge_progress=100
            )
            
            # 关闭所有音频剪辑
            for clip in audio_clips:
                clip.close()
            final_audio.close()
            
            logger.info(f"音频合并完成: {merged_audio_path}")
            
        except Exception as e:
            logger.error(f"音频合并失败: {e}")
            download_manager.update_task(
                task_id,
                status=TaskStatus.ERROR,
                error_message=f"音频合并失败: {str(e)}"
            )
            return None
        
        # 5. 下载封面
        download_manager.update_task(
            task_id,
            stage="downloading_cover",
            stage_message="正在下载封面..."
        )
        
        cover_path = COVER_OUTPUT_PATH / f"{file_prefix}.jpg"
        try:
            response = requests.get(cover_url, headers=self._get_headers(), timeout=30)
            with open(cover_path, 'wb') as f:
                f.write(response.content)
            logger.info(f"封面下载完成: {cover_path}")
        except Exception as e:
            logger.warning(f"封面下载失败: {e}")
            cover_path = None
        
        # 5.5 下载AI字幕
        download_manager.update_task(
            task_id,
            stage="downloading_subtitle",
            stage_message="正在获取AI字幕..."
        )
        
        subtitle_path = SUBTITLE_OUTPUT_PATH / f"{file_prefix}.txt"
        logger.info(f"准备下载字幕: bvid={bvid}, 字幕路径={subtitle_path}")
        
        # 使用第一个分P的cid获取字幕
        first_cid = page_download_links[0]['cid'] if page_download_links else None
        if first_cid:
            logger.info(f"使用第一个分P获取字幕: cid={first_cid}")
            try:
                saved_subtitle = self.download_subtitle(bvid, first_cid, str(subtitle_path))
                if saved_subtitle:
                    logger.info(f"AI字幕下载完成: {subtitle_path}")
                    # 验证文件是否真的有内容
                    if subtitle_path.exists():
                        file_size = subtitle_path.stat().st_size
                        logger.info(f"字幕文件大小: {file_size} 字节")
                        if file_size == 0:
                            logger.warning(f"字幕文件为空，删除空文件: {subtitle_path}")
                            subtitle_path.unlink()  # 删除空文件
                            subtitle_path = None
                    else:
                        logger.error(f"字幕文件不存在: {subtitle_path}")
                        subtitle_path = None
                else:
                    logger.info(f"视频没有AI字幕或获取失败: {bvid}")
                    # 如果字幕获取失败但文件已创建，删除空文件
                    if subtitle_path.exists():
                        logger.info(f"删除空的字幕文件: {subtitle_path}")
                        subtitle_path.unlink()
                    subtitle_path = None
            except Exception as e:
                logger.error(f"下载字幕时发生异常: {e}")
                # 如果出现异常但文件已创建，删除空文件
                if subtitle_path.exists():
                    logger.info(f"异常后删除可能的空字幕文件: {subtitle_path}")
                    subtitle_path.unlink()
                subtitle_path = None
        else:
            logger.warning(f"没有找到分P信息，无法下载字幕: {bvid}")
            subtitle_path = None
        
        # 6. 移动合并后的音频到输出目录
        final_audio_path = VIDEO_OUTPUT_PATH / f"{file_prefix}.mp3"
        try:
            import shutil
            shutil.move(str(merged_audio_path), str(final_audio_path))
            logger.info(f"音频文件已保存: {final_audio_path}")
        except Exception as e:
            logger.error(f"移动音频文件失败: {e}")
            final_audio_path = merged_audio_path
        
        # 7. 清理临时文件
        for audio_file in audio_files:
            try:
                os.remove(audio_file)
            except:
                pass
        
        # 8. 更新任务完成状态
        download_manager.update_task(
            task_id,
            status=TaskStatus.COMPLETED,
            stage="completed",
            stage_message="下载完成",
            download_path=str(final_audio_path),
            cover_path=str(cover_path) if cover_path else None,
            subtitle_path=str(subtitle_path) if subtitle_path else None
        )
        
        # 返回结果
        return {
            'bvid': bvid,
            'title': title,
            'start_p': start_p,
            'end_p': end_p,
            'video_path': str(final_audio_path),
            'cover_path': str(cover_path) if cover_path else None,
            'subtitle_path': str(subtitle_path) if subtitle_path else None,
            'audio_path': str(final_audio_path),
            'video_count': len(audio_files)
        }
    
    def download_video(
        self, 
        bvid: str, 
        start_p: int = 1, 
        end_p: Optional[int] = None,
        video_type: str = 'sleep',
        progress_callback=None
    ) -> Optional[Dict]:
        """
        下载视频（音频）并合并 - 简化版本，不带进度管理
        """
        # 创建临时任务ID
        task_id = f"temp_{bvid}_{int(time.time())}"
        return self.download_video_with_progress(task_id, bvid, start_p, end_p, video_type)
    
    def _format_duration(self, seconds: float) -> str:
        """格式化时长"""
        seconds = int(seconds)
        if seconds < 60:
            return f"{seconds}秒"
        elif seconds < 3600:
            return f"{seconds // 60}分{seconds % 60}秒"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}小时{minutes}分"
    
    def _create_video_with_cover(
        self, 
        audio_path: str, 
        cover_path: Optional[str], 
        output_path: str,
        video_type: str = 'sleep'
    ):
        """
        创建带封面的视频（封面显示10秒后黑屏，音频继续播放）
        
        Args:
            audio_path: 音频文件路径
            cover_path: 封面图片路径
            output_path: 输出视频路径
            video_type: 视频类型
        """
        # 读取音频
        audio_clip = AudioFileClip(audio_path)
        audio_duration = audio_clip.duration
        
        if cover_path and os.path.exists(cover_path):
            # 封面显示10秒
            image_clip = ImageClip(cover_path).set_duration(10)
            
            # 黑屏持续剩余时间
            black_duration = audio_duration - 10
            if black_duration > 0:
                black_clip = ColorClip(
                    size=image_clip.size, 
                    color=(0, 0, 0)
                ).set_duration(black_duration)
                
                # 合并封面和黑屏
                video_clip = concatenate_videoclips([image_clip, black_clip])
            else:
                video_clip = image_clip.set_duration(audio_duration)
        else:
            # 没有封面，全程黑屏
            video_clip = ColorClip(
                size=(1280, 720), 
                color=(0, 0, 0)
            ).set_duration(audio_duration)
        
        # 添加音频
        final_clip = video_clip.set_audio(audio_clip)
        final_clip = final_clip.set_fps(24)
        
        # 导出视频
        final_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            logger=None
        )
        
        # 关闭剪辑
        audio_clip.close()
        video_clip.close()
        final_clip.close()


# 单例实例
download_service = DownloadService()
