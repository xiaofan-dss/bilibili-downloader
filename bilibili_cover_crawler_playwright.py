# -*- coding: utf-8 -*-
"""
哔哩哔哩用户视频封面爬虫 - Playwright版本
功能：使用Playwright模拟浏览器获取指定用户的所有视频封面
优势：更真实的浏览器环境，大大降低被反爬虫系统检测的风险
"""

import os
import re
import time
import json
import random
import asyncio
import logging
import aiohttp
import aiofiles
import subprocess
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
from pathlib import Path
from tqdm import tqdm
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
import config

# 初始化日志配置
logging.basicConfig(
    level=config.LOG_LEVEL,
    format=config.LOG_FORMAT,
    datefmt=config.LOG_DATE_FORMAT
)
logger = logging.getLogger(__name__)


class BilibiliVideoDownloader:
    """哔哩哔哩视频下载器"""
    
    def __init__(self):
        self.session = None
        self.temp_dir = Path(config.VIDEO_DOWNLOAD_CONFIG['temp_dir'])
        self.output_dir = Path(config.VIDEO_DOWNLOAD_CONFIG['output_dir'])
        self.temp_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
    async def init_session(self):
        """初始化HTTP会话"""
        if not self.session:
            import random
            
            # 随机选择User-Agent和请求头模板
            user_agent = random.choice(config.VIDEO_DOWNLOAD_CONFIG['user_agents'])
            headers_template = random.choice(config.VIDEO_DOWNLOAD_CONFIG['headers_templates'])
            
            # 构建请求头
            headers = headers_template.copy()
            headers['User-Agent'] = user_agent
            headers['Referer'] = random.choice(config.VIDEO_DOWNLOAD_CONFIG['referers'])
            
            timeout = aiohttp.ClientTimeout(total=config.VIDEO_DOWNLOAD_CONFIG['segment_timeout'])
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers=headers
            )
    
    async def close_session(self):
        """关闭HTTP会话"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def get_video_info(self, bvid):
        """获取视频信息"""
        try:
            await self.init_session()
            
            # 添加反爬延迟
            import random
            import asyncio
            delay = random.uniform(
                config.VIDEO_DOWNLOAD_CONFIG['anti_crawl']['request_delay_min'],
                config.VIDEO_DOWNLOAD_CONFIG['anti_crawl']['request_delay_max']
            )
            await asyncio.sleep(delay)
            
            url = config.VIDEO_API_CONFIG['video_info_api']
            params = {'bvid': bvid}
            
            # 添加API请求的请求头
            headers = {
                'Referer': random.choice(config.VIDEO_DOWNLOAD_CONFIG['referers']),
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Origin': 'https://www.bilibili.com'
            }
            
            logger.debug(f"请求视频信息: {bvid}, URL: {url}")
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('code') == 0:
                        logger.debug(f"成功获取视频信息: {bvid}")
                        return data.get('data')
                    else:
                        error_msg = data.get('message', '未知错误')
                        logger.error(f"获取视频信息失败: {bvid} - {error_msg}")
                        return None
                else:
                    logger.error(f"HTTP请求失败: {bvid} - 状态码: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"获取视频信息异常: {bvid} - {e}")
            return None
    
    async def get_play_url(self, bvid, cid):
        """获取视频播放URL"""
        try:
            await self.init_session()
            
            # 添加反爬延迟
            import random
            import asyncio
            delay = random.uniform(
                config.VIDEO_DOWNLOAD_CONFIG['anti_crawl']['request_delay_min'],
                config.VIDEO_DOWNLOAD_CONFIG['anti_crawl']['request_delay_max']
            )
            await asyncio.sleep(delay)
            
            url = config.VIDEO_API_CONFIG['play_url_api']
            params = {
                'bvid': bvid,
                'cid': cid,
                **config.VIDEO_API_CONFIG['required_params']
            }
            
            # 添加Referer头
            headers = {
                'Referer': random.choice(config.VIDEO_DOWNLOAD_CONFIG['referers']),
                'Accept': 'application/json, text/plain, */*',
                'Origin': 'https://www.bilibili.com'
            }
            
            logger.debug(f"请求播放URL: {bvid}, CID: {cid}")
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('code') == 0:
                        logger.debug(f"成功获取播放URL: {bvid}")
                        return data.get('data')
                    else:
                        error_msg = data.get('message', '未知错误')
                        logger.error(f"获取播放URL失败: {bvid} - {error_msg}")
                        return None
                else:
                    logger.error(f"HTTP请求失败: {bvid} - 状态码: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"获取播放URL异常: {bvid} - {e}")
            return None
    
    async def download_segment(self, url, output_path, progress_callback=None):
        """下载视频分段"""
        try:
            await self.init_session()
            
            # 添加下载延迟
            import random
            import asyncio
            delay = random.uniform(1, 3)  # 下载间隔较短
            await asyncio.sleep(delay)
            
            headers = {
                'Referer': random.choice(config.VIDEO_DOWNLOAD_CONFIG['referers']),
                'User-Agent': random.choice(config.VIDEO_DOWNLOAD_CONFIG['user_agents']),
                'Accept': '*/*',
                'Accept-Encoding': 'identity;q=1, *;q=0'
            }
            
            logger.debug(f"开始下载分段: {output_path.name}")
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    
                    async with aiofiles.open(output_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
                            downloaded += len(chunk)
                            if progress_callback:
                                progress_callback(downloaded, total_size)
                    
                    logger.debug(f"分段下载完成: {output_path.name}")
                    return True
                else:
                    logger.error(f"下载失败: {output_path.name} - 状态码: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"下载分段异常: {output_path.name} - {e}")
            return False
    
    def find_ffmpeg_path(self):
        """查找FFmpeg路径 - 跨平台支持"""
        import platform
        import shutil
        import os
        
        # 1. 优先使用配置文件中的自定义路径
        if config.FFMPEG_CONFIG.get('custom_path'):
            custom_path = config.FFMPEG_CONFIG['custom_path']
            if Path(custom_path).exists():
                logger.info(f"使用自定义FFmpeg路径: {custom_path}")
                return custom_path
            else:
                logger.warning(f"自定义FFmpeg路径不存在: {custom_path}")
        
        # 2. 检查PATH环境变量
        system_ffmpeg = shutil.which('ffmpeg')
        if system_ffmpeg:
            logger.info(f"在PATH中找到FFmpeg: {system_ffmpeg}")
            return system_ffmpeg
        
        # 3. 根据平台检查常见路径
        system = platform.system().lower()
        if system == 'windows':
            search_paths = config.FFMPEG_CONFIG['search_paths']['windows']
        elif system == 'linux':
            search_paths = config.FFMPEG_CONFIG['search_paths']['linux']
        elif system == 'darwin':  # macOS
            search_paths = config.FFMPEG_CONFIG['search_paths']['darwin']
        else:
            logger.warning(f"未知系统类型: {system}，使用通用检测")
            search_paths = ['ffmpeg', './ffmpeg', './bin/ffmpeg']
        
        # 4. 遍历搜索路径
        for path in search_paths:
            try:
                # 转换为绝对路径进行检查
                if os.path.isabs(path):
                    check_path = Path(path)
                else:
                    # 相对路径相对于当前工作目录
                    check_path = Path(os.getcwd()) / path
                
                logger.debug(f"检查路径: {check_path}")
                
                if check_path.exists() and check_path.is_file():
                    absolute_path = str(check_path.resolve())
                    logger.info(f"在搜索路径中找到FFmpeg: {absolute_path}")
                    return absolute_path
                    
            except Exception as e:
                logger.debug(f"检查路径 {path} 时出错: {e}")
                continue
        
        # 5. 所有路径都未找到
        logger.warning("未找到FFmpeg，已检查的路径:")
        for path in search_paths:
            try:
                if os.path.isabs(path):
                    check_path = Path(path)
                else:
                    check_path = Path(os.getcwd()) / path
                logger.warning(f"  - {check_path} (存在: {check_path.exists()})")
            except:
                logger.warning(f"  - {path} (检查失败)")
        
        return None
        
    def show_ffmpeg_install_guide(self):
        """显示FFmpeg安装指南 - 跨平台支持"""
        import platform
        
        system = platform.system().lower()
        
        print("❌ FFmpeg未找到，无法合并视频")
        print("📝 FFmpeg 安装指南:")
        print()
        
        if system == 'windows':
            print("👾 Windows 安装方法:")
            print("  方法1: 包管理器安装 (推荐)")
            print("    choco install ffmpeg          # Chocolatey")
            print("    scoop install ffmpeg          # Scoop")
            print("    winget install ffmpeg         # Windows Package Manager")
            print()
            print("  方法2: 手动安装")
            print("    1. 访问 https://ffmpeg.org/download.html")
            print("    2. 下载 Windows 版本")
            print("    3. 解压到 C:\\ffmpeg")
            print("    4. 将 C:\\ffmpeg\\bin 添加到系统 PATH")
            print("    5. 重启命令行")
            print()
            print("  方法3: 手动配置路径")
            print("    在 config.py 中设置: FFMPEG_CONFIG['custom_path'] = 'C:\\\\ffmpeg\\\\bin\\\\ffmpeg.exe'")
            
        elif system == 'linux':
            print("🐧 Linux 安装方法:")
            print("    sudo apt install ffmpeg       # Ubuntu/Debian")
            print("    sudo yum install ffmpeg       # CentOS/RHEL")
            print("    sudo pacman -S ffmpeg         # Arch Linux")
            print("    sudo dnf install ffmpeg       # Fedora")
            print()
            print("  或手动配置: FFMPEG_CONFIG['custom_path'] = '/usr/local/bin/ffmpeg'")
            
        elif system == 'darwin':
            print("🍎 macOS 安装方法:")
            print("    brew install ffmpeg           # Homebrew (推荐)")
            print("    sudo port install ffmpeg      # MacPorts")
            print()
            print("  或手动配置: FFMPEG_CONFIG['custom_path'] = '/usr/local/bin/ffmpeg'")
        
        print()
        print("📝 配置文件设置 (config.py):")
        print("  # 自定义FFmpeg路径")
        print("  FFMPEG_CONFIG = {")
        print("      'custom_path': '/path/to/your/ffmpeg',  # 替换为实际路径")
        print("      'enabled': True")
        print("  }")
        print()
        print("ℹ️  安装后请重新运行程序或运行: python check_ffmpeg.py 验证安装")
    
    async def merge_video_audio(self, video_path, audio_path, output_path):
        """合并视频和音频 - 使用配置中的FFmpeg路径"""
        try:
            # 检查FFmpeg是否启用
            if not config.FFMPEG_CONFIG.get('enabled', True):
                logger.error("FFmpeg功能已禁用")
                print("❌ FFmpeg功能已在配置中禁用")
                return False
            
            # 查找FFmpeg路径
            ffmpeg_path = self.find_ffmpeg_path()
            if not ffmpeg_path:
                self.show_ffmpeg_install_guide()
                return False
            
            # 构建FFmpeg命令
            cmd = [
                ffmpeg_path, '-y',
                '-i', str(video_path),
                '-i', str(audio_path),
                '-c:v', config.FFMPEG_CONFIG.get('video_codec', 'copy'),
                '-c:a', config.FFMPEG_CONFIG.get('audio_codec', 'aac'),
                '-preset', config.FFMPEG_CONFIG.get('quality_preset', 'fast')
            ]
            
            # 添加额外参数
            extra_args = config.FFMPEG_CONFIG.get('extra_args', [])
            if extra_args:
                cmd.extend(extra_args)
            
            cmd.append(str(output_path))
            
            logger.debug(f"FFmpeg命令: {' '.join(cmd)}")
            
            # 执行FFmpeg - 修复字符编码问题
            timeout = config.FFMPEG_CONFIG.get('timeout', 300)
            # 在Windows上明确指定编码为utf-8，避免GBK编码错误
            result = subprocess.run(cmd, 
                                   capture_output=True, 
                                   text=True, 
                                   timeout=timeout,
                                   encoding='utf-8',
                                   errors='ignore')  # 忽略无法解码的字符
            
            if result.returncode == 0:
                logger.info(f"合并成功: {output_path}")
                return True
            else:
                logger.error(f"FFmpeg合并失败 (返回码: {result.returncode}): {result.stderr}")
                print(f"❌ FFmpeg错误: {result.stderr[:200]}...")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg合并超时")
            print("❌ FFmpeg合并超时，可能文件过大")
            return False
        except Exception as e:
            logger.error(f"合并视频异常: {e}")
            print(f"❌ 合并异常: {e}")
            return False
    
    def sanitize_filename(self, filename):
        """清理文件名"""
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
        if len(filename) > 100:
            filename = filename[:100]
        return filename.strip()
    
    async def download_video(self, bvid, title=None):
        """下载单个视频"""
        try:
            print(f"\n📺 开始下载视频: {bvid}")
            
            # 首先检查FFmpeg是否可用
            ffmpeg_path = self.find_ffmpeg_path()
            if not ffmpeg_path:
                self.show_ffmpeg_install_guide()
                return False
            
            # 获取视频信息
            video_info = await self.get_video_info(bvid)
            if not video_info:
                print(f"⚠️ 无法获取视频信息: {bvid}")
                return False
            
            video_title = title or video_info.get('title', bvid)
            cid = video_info['pages'][0]['cid']  # 取第一个P
            
            print(f"🎥 视频标题: {video_title}")
            print(f"🆔 CID: {cid}")
            
            # 获取播放URL
            play_data = await self.get_play_url(bvid, cid)
            if not play_data:
                print(f"⚠️ 无法获取播放URL: {bvid}")
                return False
            
            # 选择最高质量的视频和音频
            dash = play_data.get('dash')
            if not dash:
                print(f"⚠️ 不支持DASH格式: {bvid}")
                return False
            
            video_streams = dash.get('video', [])
            audio_streams = dash.get('audio', [])
            
            if not video_streams or not audio_streams:
                print(f"⚠️ 缺少视频或音频流: {bvid}")
                return False
            
            # 选择最高质量
            video_stream = max(video_streams, key=lambda x: x.get('height', 0))
            audio_stream = max(audio_streams, key=lambda x: x.get('bandwidth', 0))
            
            video_url = video_stream['baseUrl']
            audio_url = audio_stream['baseUrl']
            
            print(f"🎥 视频质量: {video_stream.get('height', 'Unknown')}p")
            print(f"🎵 音频码率: {audio_stream.get('bandwidth', 'Unknown')}")
            
            # 准备文件名
            safe_title = self.sanitize_filename(video_title)
            video_temp = self.temp_dir / f"{bvid}_video.m4s"
            audio_temp = self.temp_dir / f"{bvid}_audio.m4s"
            output_file = self.output_dir / f"{bvid}_{safe_title}.mp4"
            
            if output_file.exists():
                print(f"✅ 文件已存在，跳过: {output_file.name}")
                return True
            
            # 下载视频和音频
            print(f"📥 下载视频流...")
            video_success = await self.download_segment(video_url, video_temp)
            
            if video_success:
                print(f"📥 下载音频流...")
                audio_success = await self.download_segment(audio_url, audio_temp)
                
                if audio_success:
                    print(f"🔧 合并视频和音频...")
                    merge_success = await self.merge_video_audio(video_temp, audio_temp, output_file)
                    
                    # 清理临时文件
                    try:
                        if video_temp.exists():
                            video_temp.unlink()
                        if audio_temp.exists():
                            audio_temp.unlink()
                    except:
                        pass
                    
                    if merge_success:
                        print(f"✅ 下载完成: {output_file.name}")
                        return True
                    else:
                        print(f"❌ 合并失败: {bvid}")
                        return False
                else:
                    print(f"❌ 音频下载失败: {bvid}")
                    return False
            else:
                print(f"❌ 视频下载失败: {bvid}")
                return False
                
        except Exception as e:
            logger.error(f"下载视频异常: {e}")
            print(f"❌ 下载异常: {bvid} - {e}")
            return False


class PlaywrightBilibiliCrawler:
    """基于Playwright的哔哩哔哩封面爬虫类"""
    
    def __init__(self):
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        self.request_count = 0
        self.last_request_time = 0
        self.failure_count = 0
        self.last_error_time = 0
        self.is_first_request = True
        self.video_downloader = None  # 视频下载器
        
    async def init_video_downloader(self):
        """初始化视频下载器"""
        if not self.video_downloader:
            self.video_downloader = BilibiliVideoDownloader()
            
    async def close_video_downloader(self):
        """关闭视频下载器"""
        if self.video_downloader:
            await self.video_downloader.close_session()
        
    async def initialize_browser(self):
        """初始化Playwright浏览器"""
        logger.info("开始初始化Playwright浏览器...")
        print(f"\n🚀 初始化Playwright浏览器...")
        
        self.playwright = await async_playwright().start()
        
        # 启动浏览器 - 使用更真实的设置
        self.browser = await self.playwright.chromium.launch(
            headless=config.PLAYWRIGHT_CONFIG['headless'],
            slow_mo=config.PLAYWRIGHT_CONFIG['slow_mo'],
            args=config.BROWSER_ARGS
        )
        
        # 创建浏览器上下文 - 更真实的设置
        user_agent = random.choice(config.USER_AGENTS)
        logger.debug(f"使用User-Agent: {user_agent}")
        
        self.context = await self.browser.new_context(
            viewport=config.PLAYWRIGHT_CONFIG['viewport'],
            user_agent=user_agent,
            java_script_enabled=config.PLAYWRIGHT_CONFIG['java_script_enabled'],
            ignore_https_errors=config.PLAYWRIGHT_CONFIG['ignore_https_errors'],
            # 添加更真实的浏览器特征
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
            geolocation={'latitude': 39.9042, 'longitude': 116.4074},  # 北京
            permissions=['geolocation']
        )
        
        # 设置更真实的请求头
        await self.context.set_extra_http_headers({
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'sec-ch-ua': '"Chromium";v="120", "Not_A Brand";v="8", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # 创建页面
        self.page = await self.context.new_page()
        
        # 设置超时
        self.page.set_default_timeout(config.PLAYWRIGHT_CONFIG['timeout'])
        
        # 添加反检测脚本
        await self.add_stealth_scripts()
        
        print("✅ 浏览器初始化完成")
        
        # 预热延迟
        print(f"🌡️ 预热等待 {config.INITIAL_WARMUP_DELAY} 秒...")
        with tqdm(total=config.INITIAL_WARMUP_DELAY, desc="预热中", unit="s") as pbar:
            for i in range(config.INITIAL_WARMUP_DELAY):
                await asyncio.sleep(1)
                pbar.update(1)
    
    async def add_stealth_scripts(self):
        """添加反检测脚本"""
        logger.debug("添加反检测脚本...")
        
        # 隐藏webdriver属性
        await self.page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        """)
        
        # 模拟真实用户的chrome属性
        await self.page.add_init_script("""
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {}
        };
        """)
        
        # 模拟真实的插件信息
        await self.page.add_init_script("""
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        """)
        
        # 模拟真实的语言设置
        await self.page.add_init_script("""
        Object.defineProperty(navigator, 'languages', {
            get: () => ['zh-CN', 'zh', 'en'],
        });
        """)
    
    async def wait_for_page_fully_loaded(self, url_description="页面"):
        """等待页面完全加载，包括JavaScript渲染"""
        logger.debug(f"等待{url_description}完全加载...")
        
        for attempt in range(config.MAX_WAIT_ATTEMPTS):
            try:
                # 等待多个加载状态
                for state in config.WAIT_FOR_LOAD_STATES:
                    logger.debug(f"等待加载状态: {state}")
                    await self.page.wait_for_load_state(state, timeout=30000)
                
                # 额外等待JavaScript完全执行
                logger.debug(f"额外等待 {config.ADDITIONAL_WAIT_TIME} 秒确保JS完全执行...")
                await asyncio.sleep(config.ADDITIONAL_WAIT_TIME)
                
                # 验证页面内容是否正常加载
                content_valid = await self.verify_page_content()
                if content_valid:
                    logger.debug(f"{url_description}加载完成并验证成功")
                    return True
                else:
                    logger.warning(f"{url_description}内容验证失败，第 {attempt + 1} 次尝试")
                    
                    # 如果不是最后一次尝试，且配置允许重试
                    if attempt < config.MAX_WAIT_ATTEMPTS - 1 and config.CONTENT_VERIFICATION.get('retry_on_empty', False):
                        logger.info("等待3秒后重新加载页面...")
                        await asyncio.sleep(3)
                        await self.page.reload(wait_until="networkidle")
                        continue
                    else:
                        # 如果配置不允许重试，或是最后一次尝试，则接受当前结果
                        if not config.CONTENT_VERIFICATION.get('retry_on_empty', False):
                            logger.info(f"{url_description}验证失败，但配置不允许重试，接受当前结果")
                            return True  # 返回Ture表示接受当前结果
                        break
                
            except Exception as e:
                logger.warning(f"{url_description}加载异常: {e}, 第 {attempt + 1} 次尝试")
                if attempt < config.MAX_WAIT_ATTEMPTS - 1:
                    await asyncio.sleep(5)  # 等待5秒后重试
                    continue
        
        # 如果到达这里，说明所有尝试都失败了
        if config.CONTENT_VERIFICATION.get('retry_on_empty', False):
            logger.error(f"{url_description}加载失败，已达到最大重试次数")
            return False
        else:
            logger.warning(f"{url_description}验证未通过，但继续执行")
            return True
    
    async def verify_page_content(self):
        """验证页面内容是否正常加载"""
        try:
            page_content = await self.page.content()
            page_title = await self.page.title()
            page_url = self.page.url
            
            logger.debug(f"验证页面: {page_url}")
            logger.debug(f"页面标题: {page_title}")
            
            # 检查是否是真正的错误页面（更精确的判断）
            # 只有当这些错误指示符出现在标题或特定位置时才认为是错误
            title_error_indicators = [
                '网络错误', '页面不存在', '访问被拒绝', '服务器错误',
                'Access Denied', 'Forbidden', 'Server Error', 'Page Not Found'
            ]
            
            # 检查标题中的错误指示符
            for indicator in title_error_indicators:
                if indicator in page_title:
                    logger.warning(f"标题中检测到错误指示符: {indicator}")
                    return False
            
            # 检查是否是哔哩哔哩的正常页面
            # 通过检查关键标识来确认页面正常
            bilibili_indicators = [
                'bilibili', 'bili', '哔哩哔哩', 'space.bilibili.com',
                'bili-header', 'bili-footer', 'bili-wrapper'
            ]
            
            has_bilibili_content = any(indicator in page_content.lower() for indicator in bilibili_indicators)
            if not has_bilibili_content:
                logger.warning("页面中未检测到哔哩哔哩相关内容")
                return False
            
            # 检查页面内容是否足够丰富
            if len(page_content) < 5000:  # 增加最小长度要求
                logger.warning(f"页面内容过少: {len(page_content)} 字符，可能未完全加载")
                return False
            
            # 检查是否有必要的HTML结构
            essential_tags = ['<html', '<body', '<head']
            for tag in essential_tags:
                if tag not in page_content:
                    logger.warning(f"缺少必要HTML标签: {tag}")
                    return False
            
            # 特定页面类型的验证
            if '/video' in page_url:
                # 视频页面应该有视频相关内容
                video_indicators = ['.video', '.small-item', '.bili-cover', 'video-list']
                has_video_content = any(indicator in page_content for indicator in video_indicators)
                if has_video_content:
                    logger.debug("检测到视频页面相关内容")
                else:
                    logger.info("视频页面中未检测到视频内容，可能是空页面或加载中")
                    # 不直接返回false，因为可能是用户没有公开视频
            
            logger.debug(f"页面内容验证通过 - 长度: {len(page_content)}, 标题: {page_title}")
            return True
            
        except Exception as e:
            logger.error(f"页面内容验证异常: {e}")
            return False
    
    async def close_browser(self):
        """关闭浏览器"""
        await self.close_video_downloader()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    def sanitize_filename(self, filename):
        """清理文件名，移除不允许的字符"""
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
        if len(filename) > config.MAX_FILENAME_LENGTH:
            filename = filename[:config.MAX_FILENAME_LENGTH]
        return filename.strip()
    
    async def smart_delay(self, is_api_request=False):
        """智能延迟机制"""
        # 首次请求的额外延迟
        if self.is_first_request:
            print(f"\n🔥 首次请求，额外等待 {config.FIRST_REQUEST_DELAY} 秒...")
            await asyncio.sleep(config.FIRST_REQUEST_DELAY)
            self.is_first_request = False
        
        # 检查是否需要长时间休息
        if self.request_count > 0 and self.request_count % config.MAX_CONSECUTIVE_REQUESTS == 0:
            print(f"\n💤 已连续请求 {config.MAX_CONSECUTIVE_REQUESTS} 次，休息 {config.LONG_BREAK_DURATION} 秒...")
            with tqdm(total=config.LONG_BREAK_DURATION, desc="休息中", unit="s") as pbar:
                for i in range(config.LONG_BREAK_DURATION):
                    await asyncio.sleep(1)
                    pbar.update(1)
            
            # 更新浏览器上下文
            await self.update_browser_context()
            self.failure_count = 0
        
        # 如果最近有错误，增加额外延迟
        if self.last_error_time > 0:
            time_since_error = time.time() - self.last_error_time
            if time_since_error < config.REQUEST_FAILURE_PENALTY:
                remaining_penalty = config.REQUEST_FAILURE_PENALTY - time_since_error
                if remaining_penalty > 0:
                    print(f"⚠️ 距离上次错误太近，额外等待 {remaining_penalty:.1f} 秒...")
                    await asyncio.sleep(remaining_penalty)
        
        # 计算基础延迟时间
        if is_api_request:
            base_delay = random.uniform(config.REQUEST_DELAY_MIN, config.REQUEST_DELAY_MAX)
        else:
            base_delay = random.uniform(config.DOWNLOAD_DELAY_MIN, config.DOWNLOAD_DELAY_MAX)
        
        # 根据失败次数增加延迟
        if self.failure_count > 0:
            penalty_multiplier = 1 + (self.failure_count * 0.5)
            base_delay *= penalty_multiplier
            print(f"😰 由于失败次数 ({self.failure_count})，延迟增加到 {base_delay:.1f} 秒")
        
        # 确保与上次请求的间隔
        elapsed = time.time() - self.last_request_time
        if elapsed < base_delay:
            actual_wait = base_delay - elapsed
            print(f"⏳ 等待 {actual_wait:.1f} 秒...")
            await asyncio.sleep(actual_wait)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    async def update_browser_context(self):
        """更新浏览器上下文（相当于更换身份）"""
        print("🔄 更新浏览器上下文...")
        
        # 关闭当前页面
        if self.page:
            await self.page.close()
        
        # 关闭当前上下文
        if self.context:
            await self.context.close()
        
        # 创建新的上下文
        self.context = await self.browser.new_context(
            viewport=config.PLAYWRIGHT_CONFIG['viewport'],
            user_agent=random.choice(config.USER_AGENTS),
            java_script_enabled=config.PLAYWRIGHT_CONFIG['java_script_enabled'],
            ignore_https_errors=config.PLAYWRIGHT_CONFIG['ignore_https_errors']
        )
        
        # 设置随机的额外请求头
        extra_headers = {
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br'
        }
        
        if random.random() < 0.5:
            extra_headers['Cache-Control'] = random.choice(['no-cache', 'max-age=0'])
        if random.random() < 0.3:
            extra_headers['Pragma'] = 'no-cache'
        if random.random() < 0.4:
            extra_headers['DNT'] = '1'
        
        await self.context.set_extra_http_headers(extra_headers)
        
        # 创建新页面
        self.page = await self.context.new_page()
        self.page.set_default_timeout(config.PLAYWRIGHT_CONFIG['timeout'])
    
    async def handle_request_error(self, error, attempt):
        """处理请求错误"""
        error_str = str(error)
        self.failure_count += 1
        self.last_error_time = time.time()
        
        # 检测各种反爬错误
        anti_crawl_keywords = [
            "请求过于频繁", "429", "Too Many Requests", 
            "rate limit", "Rate Limited", "访问频繁",
            "Too fast", "slow down", "限制", "blocked"
        ]
        
        is_anti_crawl = any(keyword in error_str for keyword in anti_crawl_keywords)
        
        if is_anti_crawl:
            # 逐渐增加冷却时间
            cooldown = config.ERROR_COOLDOWN * (attempt + 1) * (1 + self.failure_count * 0.3)
            print(f"\n⚠️ 检测到反爬措施: {error_str}")
            print(f"🧊 冷却 {cooldown:.0f} 秒 (第{attempt+1}次重试，连续失败{self.failure_count}次)...")
            
            # 进度条显示冷却进度
            with tqdm(total=int(cooldown), desc="冷却中", unit="s") as pbar:
                for i in range(int(cooldown)):
                    await asyncio.sleep(1)
                    pbar.update(1)
            
            # 更新浏览器上下文
            await self.update_browser_context()
            
            return True
        
        return False
    
    async def get_user_info(self, uid):
        """从用户空间页面获取用户信息"""
        for attempt in range(config.MAX_RETRIES):
            try:
                await self.smart_delay(is_api_request=True)
                
                # 构建用户空间页面URL
                space_url = config.USER_SPACE_BASE.format(uid=uid)
                print(f"🌐 访问用户空间页面: {space_url}")
                
                # 访问用户空间页面
                response = await self.page.goto(space_url, wait_until="networkidle")
                
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}")
                
                # 使用新的页面等待机制
                if not await self.wait_for_page_fully_loaded("用户空间页面"):
                    raise Exception("页面加载失败或内容异常")
                
                # 获取页面内容用于调试
                page_content = await self.page.content()
                
                # Debug日志：显示HTML信息
                if config.ENABLE_HTML_DEBUG and logger.isEnabledFor(logging.DEBUG):
                    html_preview = page_content[:config.HTML_DEBUG_MAX_LENGTH]
                    logger.debug(f"用户空间页面HTML内容预览 (前{config.HTML_DEBUG_MAX_LENGTH}字符):\n{html_preview}")
                    logger.debug(f"页面标题: {await self.page.title()}")
                    logger.debug(f"页面URL: {self.page.url}")
                
                # 检查是否是私人或不存在的用户
                if "用户不存在" in page_content or "该用户隐私设置" in page_content or "账号封禁" in page_content:
                    logger.warning(f"用户 {uid} 不存在、设置为私人或已被封禁")
                    print(f"⚠️ 用户 {uid} 不存在、设置为私人或已被封禁")
                    return None
                
                # 尝试获取用户名
                user_name = None
                
                # 使用配置文件中的用户名选择器（优先使用 .nickname）
                for selector in config.USER_NAME_SELECTORS:
                    try:
                        name_element = await self.page.wait_for_selector(selector, timeout=5000)
                        if name_element:
                            user_name = await name_element.text_content()
                            if user_name and user_name.strip():
                                user_name = user_name.strip()
                                logger.debug(f"通过选择器 '{selector}' 获取到用户名: {user_name}")
                                print(f"✅ 通过选择器 '{selector}' 获取到用户名: {user_name}")
                                if selector == '.nickname':
                                    logger.info(f"使用 nickname 选择器成功获取用户名: {user_name}")
                                break
                    except Exception as e:
                        logger.debug(f"选择器 '{selector}' 获取用户名失败: {e}")
                        continue
                
                # 如果没有获取到用户名，使用默认名称
                if not user_name:
                    user_name = f'用户_{uid}'
                    print(f"⚠️ 未获取到用户名，使用默认名称: {user_name}")
                
                self.failure_count = 0  # 成功后重置失败计数
                print(f"✅ 成功获取用户信息: {user_name}")
                
                return {
                    'name': user_name,
                    'uid': uid
                }
                    
            except Exception as e:
                if await self.handle_request_error(e, attempt):
                    continue
                if attempt < config.MAX_RETRIES - 1:
                    delay = config.RETRY_DELAY * (config.RETRY_BACKOFF ** attempt)
                    print(f"获取用户信息失败，{delay}秒后重试: {e}")
                    await asyncio.sleep(delay)
                else:
                    print(f"获取用户信息时发生错误: {e}")
                    return None
    
    async def scroll_and_collect_videos(self):
        """滚动页面并收集所有视频信息，支持分页点击"""
        videos = []
        collected_bvids = set()  # 用于去重
        current_page = 1
        
        print(f"🔄 开始收集视频信息，支持分页和滚动加载...")
        
        # 等待初始视频加载
        await asyncio.sleep(3)
        
        while True:
            print(f"📄 处理第 {current_page} 页...")
            
            # 在当前页面滚动收集视频
            page_videos = await self.collect_videos_from_current_page()
            
            # 添加新视频到总列表
            new_videos_count = 0
            for video in page_videos:
                if video['bvid'] not in collected_bvids:
                    videos.append(video)
                    collected_bvids.add(video['bvid'])
                    new_videos_count += 1
            
            print(f"📺 第 {current_page} 页获取到 {new_videos_count} 个新视频，总计 {len(videos)} 个")
            
            # 检查是否已经收集到了期望的视频数量（智能停止）
            if config.PAGINATION_CONFIG.get('smart_stop', True):
                expected_count = await self.get_expected_video_count()
                if expected_count and len(videos) >= expected_count:
                    print(f"✅ 已收集到期望数量（{len(videos)}/{expected_count}），无需继续查找下一页")
                    logger.info(f"智能停止：已收集到期望数量 {len(videos)}/{expected_count}")
                    break
            
            # 检查是否有下一页
            has_next_page = await self.check_and_click_next_page()
            if not has_next_page:
                print(f"🏁 已到达最后一页，停止收集")
                break
            
            current_page += 1
            
            # 页面切换后等待加载
            print(f"⏳ 等待第 {current_page} 页加载...")
            await asyncio.sleep(5)
        
        print(f"🎉 收集完成，共 {current_page} 页，收集到 {len(videos)} 个视频")
        
        # 验证视频数量是否正确
        if config.CONTENT_VERIFICATION.get('verify_video_count', False):
            expected_count = await self.get_expected_video_count()
            if expected_count:
                if len(videos) >= expected_count:
                    print(f"✅ 数量验证通过！收集到 {len(videos)} 个，期望 {expected_count} 个")
                else:
                    print(f"⚠️ 数量不足：收集到 {len(videos)} 个，期望 {expected_count} 个")
            await self.verify_video_count(len(videos))
        
        return videos
    
    async def collect_videos_from_current_page(self):
        """从当前页面滚动收集视频"""
        page_videos = []
        collected_bvids = set()
        scroll_count = 0
        no_new_videos_count = 0
        
        print(f"🔄 开始滚动收集当前页视频...")
        
        while scroll_count < config.MAX_SCROLL_ATTEMPTS:
            try:
                # 获取当前页面的视频封面元素（使用配置中的选择器）
                video_elements = []
                for selector in config.VIDEO_SELECTORS:
                    elements = await self.page.query_selector_all(selector)
                    if elements:
                        video_elements = elements
                        logger.debug(f"使用选择器 '{selector}' 找到 {len(elements)} 个元素")
                        break
                    else:
                        logger.debug(f"选择器 '{selector}' 未找到元素")
                
                if not video_elements:
                    print(f"⚠️ 未找到视频元素，尝试继续滚动...")
                    await self.page.evaluate(f"window.scrollBy(0, {config.SCROLL_STEP})")
                    await asyncio.sleep(2)
                    scroll_count += 1
                    continue
                
                # 记录当前视频数量
                current_videos_count = len(page_videos)
                
                # 提取视频信息
                for element in video_elements:
                    try:
                        video_info = await self.extract_video_info(element)
                        if video_info and video_info['bvid'] not in collected_bvids:
                            page_videos.append(video_info)
                            collected_bvids.add(video_info['bvid'])
                    except Exception as e:
                        # 忽略单个视频的解析错误
                        continue
                
                new_videos_count = len(page_videos) - current_videos_count
                
                # 检查是否有新视频
                if new_videos_count == 0:
                    no_new_videos_count += 1
                    if no_new_videos_count >= 5:  # 连续5次没有新视频，停止滚动
                        print(f"😪 连续 {no_new_videos_count} 次没有新视频，当前页滚动完成")
                        break
                    # print(f"⚠️ 本次滚动没有新视频，继续尝试... ({no_new_videos_count}/5)")
                else:
                    no_new_videos_count = 0
                    if new_videos_count > 0:
                        print(f"📺 本次滚动获取到 {new_videos_count} 个新视频，当前页总计 {len(page_videos)} 个")
                
                # 检查是否已到达页面底部
                is_at_bottom = await self.page.evaluate("""
                    () => {
                        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                        const windowHeight = window.innerHeight;
                        const documentHeight = document.documentElement.scrollHeight;
                        return scrollTop + windowHeight >= documentHeight - 1000;
                    }
                """)
                
                if is_at_bottom:
                    print(f"🏁 当前页已到达底部，停止滚动")
                    break
                
                # 模拟真实用户滚动行为
                scroll_distance = random.randint(600, 1200)  # 随机滚动距离
                await self.page.evaluate(f"window.scrollBy(0, {scroll_distance})")
                scroll_count += 1
                
                # 随机等待时间，模拟真实用户
                wait_time = random.uniform(1.0, 2.5)
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                print(f"⚠️ 滚动过程中发生错误: {e}")
                break
        
        print(f"✅ 当前页滚动完成，收集到 {len(page_videos)} 个视频")
        return page_videos
    
    async def get_expected_video_count(self):
        """获取页面显示的期望视频总数"""
        try:
            pagination_info = await self.get_pagination_info()
            if pagination_info and 'total_count' in pagination_info:
                expected_count = pagination_info['total_count']
                logger.debug(f"从分页信息获取到期望视频数: {expected_count}")
                return expected_count
            return None
        except Exception as e:
            logger.debug(f"获取期望视频数失败: {e}")
            return None
    
    async def check_and_click_next_page(self):
        """检查并点击下一页按钮"""
        try:
            print(f"🔍 检查是否有下一页...")
            
            # 多种下一页按钮选择器
            next_page_selectors = [
                '.vui_pagenation--btn-side:has-text("下一页")',  # "下一页"按钮
                '.vui_button:has-text("下一页")',
                'button:has-text("下一页")',
                '.pagination-next',
                '.next-page',
                '.page-next',
                'a:has-text("下一页")',
                '[aria-label="下一页"]',
                '.vui_pagenation--btn-side'  # 通用的分页侧边按钮
            ]
            
            next_button = None
            for selector in next_page_selectors:
                try:
                    # 等待元素出现
                    next_button = await self.page.wait_for_selector(selector, timeout=5000)
                    if next_button:
                        # 检查按钮是否可点击（不是禁用状态）
                        is_disabled = await next_button.is_disabled()
                        if not is_disabled:
                            # 进一步检查按钮文本确认是"下一页"
                            button_text = await next_button.text_content()
                            if button_text and ('下一页' in button_text or 'next' in button_text.lower()):
                                logger.debug(f"找到下一页按钮，选择器: {selector}, 文本: {button_text}")
                                break
                        next_button = None
                except Exception as e:
                    logger.debug(f"选择器 {selector} 查找下一页按钮失败: {e}")
                    continue
            
            if next_button:
                # 滚动到按钮位置
                await next_button.scroll_into_view_if_needed()
                await asyncio.sleep(1)
                
                # 点击下一页按钮
                print(f"👆 点击下一页按钮...")
                await next_button.click()
                
                # 等待页面跳转
                await asyncio.sleep(3)
                
                # 等待新页面加载完成
                await self.wait_for_page_fully_loaded("下一页")
                
                print(f"✅ 成功跳转到下一页")
                return True
            else:
                print(f"ℹ️ 未找到可点击的下一页按钮，可能已到达最后一页")
                
                # 进一步确认：检查分页信息
                pagination_info = await self.get_pagination_info()
                if pagination_info:
                    current_page = pagination_info.get('current_page', 1)
                    total_pages = pagination_info.get('total_pages', 1)
                    print(f"📊 分页信息: 当前第 {current_page} 页，共 {total_pages} 页")
                    if current_page >= total_pages:
                        print(f"🏁 已到达最后一页 ({current_page}/{total_pages})")
                
                return False
                
        except Exception as e:
            logger.error(f"检查下一页时发生错误: {e}")
            print(f"⚠️ 检查下一页时出错: {e}")
            return False
    
    async def get_pagination_info(self):
        """获取分页信息"""
        try:
            # 查找分页信息
            pagination_selectors = [
                '.vui_pagenation-go__count',
                '.pagination-info',
                '.page-info'
            ]
            
            for selector in pagination_selectors:
                try:
                    pagination_element = await self.page.query_selector(selector)
                    if pagination_element:
                        pagination_text = await pagination_element.text_content()
                        if pagination_text:
                            # 解析分页信息 "共 X 页 / Y 个"
                            import re
                            match = re.search(r'共\s*(\d+)\s*页\s*/\s*(\d+)\s*个', pagination_text)
                            if match:
                                total_pages = int(match.group(1))
                                total_count = int(match.group(2))
                                
                                # 尝试获取当前页码
                                current_page = 1
                                
                                # 查找当前激活的页码按钮
                                active_page_selectors = [
                                    '.vui_pagenation--btn-num.vui_pagenation--btn-active',
                                    '.vui_pagenation--btn-num[class*="active"]',
                                    '.current-page',
                                    '.page-active',
                                    '.active'
                                ]
                                
                                for page_selector in active_page_selectors:
                                    try:
                                        active_element = await self.page.query_selector(page_selector)
                                        if active_element:
                                            page_text = await active_element.text_content()
                                            if page_text and page_text.isdigit():
                                                current_page = int(page_text)
                                                break
                                    except:
                                        continue
                                
                                return {
                                    'current_page': current_page,
                                    'total_pages': total_pages,
                                    'total_count': total_count,
                                    'pagination_text': pagination_text
                                }
                except Exception as e:
                    continue
            
            return None
            
        except Exception as e:
            logger.debug(f"获取分页信息失败: {e}")
            return None
    
    async def verify_video_count(self, collected_count):
        """验证收集到的视频数量是否与页面显示一致"""
        try:
            if not config.VIDEO_COUNT_VERIFICATION.get('check_pagination', False):
                logger.debug("视频数量校验已禁用")
                return True
            
            logger.debug("开始验证视频数量...")
            print(f"🔍 正在验证视频数量...")
            
            # 查找分页信息元素
            pagination_text = None
            expected_count = None
            
            for selector in config.VIDEO_COUNT_VERIFICATION['pagination_selectors']:
                try:
                    pagination_element = await self.page.query_selector(selector)
                    if pagination_element:
                        pagination_text = await pagination_element.text_content()
                        if pagination_text and pagination_text.strip():
                            logger.debug(f"通过选择器 '{selector}' 获取到分页信息: {pagination_text}")
                            print(f"📊 找到分页信息: {pagination_text.strip()}")
                            break
                except Exception as e:
                    logger.debug(f"选择器 '{selector}' 获取分页信息失败: {e}")
                    continue
            
            if not pagination_text:
                print(f"⚠️ 未找到分页信息，无法验证视频数量")
                logger.warning("未找到分页信息")
                return True  # 不强制验证
            
            # 使用正则提取总数
            import re
            pattern = config.VIDEO_COUNT_VERIFICATION['count_pattern']
            match = re.search(pattern, pagination_text)
            
            if match:
                page_count = int(match.group(1))  # 页数
                expected_count = int(match.group(2))  # 总视频数
                logger.debug(f"提取到分页信息: {page_count} 页, {expected_count} 个视频")
                print(f"📈 页面显示: 共 {page_count} 页 / {expected_count} 个视频")
            else:
                print(f"⚠️ 无法从分页信息中提取数量: {pagination_text}")
                logger.warning(f"正则匹配失败: {pagination_text}")
                return True  # 不强制验证
            
            if expected_count is None:
                return True
            
            # 计算误差比例
            if expected_count > 0:
                difference = abs(collected_count - expected_count)
                error_ratio = difference / expected_count
                tolerance = config.VIDEO_COUNT_VERIFICATION['tolerance_ratio']
                
                print(f"📊 数量对比:")
                print(f"  页面显示: {expected_count} 个视频")
                print(f"  实际收集: {collected_count} 个视频")
                print(f"  差异数量: {difference} 个")
                print(f"  误差比例: {error_ratio:.2%} (允许误差: {tolerance:.2%})")
                
                if error_ratio <= tolerance:
                    print(f"✅ 视频数量验证通过！")
                    logger.info(f"视频数量验证通过: 期望{expected_count}, 实际{collected_count}, 误差{error_ratio:.2%}")
                    return True
                else:
                    print(f"⚠️ 视频数量不匹配！")
                    print(f"💡 可能的原因:")
                    print(f"  1. 页面未完全加载，尝试增加滚动次数")
                    print(f"  2. 部分视频被设为私人或已删除")
                    print(f"  3. 网络问题导致部分内容加载失败")
                    print(f"  4. 页面结构变化，需要更新选择器")
                    
                    logger.warning(f"视频数量不匹配: 期望{expected_count}, 实际{collected_count}, 误差{error_ratio:.2%}")
                    
                    # 返回True表示继续执行，但给出警告
                    return True
            else:
                print(f"⚠️ 页面显示视频数为0，无法验证")
                return True
                
        except Exception as e:
            logger.error(f"视频数量验证过程中发生错误: {e}")
            print(f"⚠️ 视频数量验证出错: {e}")
            return True  # 出错时不影响主流程
    
    async def extract_video_info(self, element):
        """从视频封面元素中提取信息"""
        try:
            logger.debug("开始从视频元素提取信息...")
            
            # 检查元素类型
            element_class = await element.get_attribute('class') or ''
            
            # 优先处理 bili-video-card 元素
            if 'bili-video-card' in element_class:
                logger.debug("检测到 bili-video-card 元素")
                return await self.extract_from_bili_video_card(element)
            
            # 处理 bili-cover-card__thumbnail 元素
            if 'bili-cover-card__thumbnail' in element_class:
                logger.debug("检测到 bili-cover-card__thumbnail 元素")
                return await self.extract_from_bili_cover_card(element)
            
            # 在子元素中查找 bili-video-card
            video_card_element = await element.query_selector('.bili-video-card')
            if video_card_element:
                logger.debug("在子元素中找到 bili-video-card")
                return await self.extract_from_bili_video_card(video_card_element)
            
            # 在子元素中查找 bili-cover-card__thumbnail
            thumbnail_element = await element.query_selector('.bili-cover-card__thumbnail')
            if thumbnail_element:
                logger.debug("在子元素中找到 bili-cover-card__thumbnail")
                return await self.extract_from_bili_cover_card(thumbnail_element)
            
            # 使用通用方法
            logger.debug("未找到特定元素，使用通用提取方法")
            return await self.extract_generic_video_info(element)
            
        except Exception as e:
            logger.debug(f"提取视频信息时发生错误: {e}")
            return None
    
    async def extract_from_bili_video_card(self, element):
        """从 bili-video-card 元素提取视频信息"""
        try:
            logger.debug("从 bili-video-card 元素提取信息...")
            
            # 获取视频链接和BV号
            link_element = await element.query_selector('a[href*="/video/"]')
            if not link_element:
                logger.debug("在 bili-video-card 中未找到视频链接")
                return None
            
            href = await link_element.get_attribute('href')
            if not href:
                logger.debug("链接元素没有 href 属性")
                return None
            
            # 提取BV号
            import re
            bv_match = re.search(r'/video/(BV[A-Za-z0-9]+)', href)
            if not bv_match:
                bv_match = re.search(r'(BV[A-Za-z0-9]+)', href)
                if not bv_match:
                    logger.debug(f"无法从链接中提取BV号: {href}")
                    return None
            
            bvid = bv_match.group(1)
            logger.debug(f"从 bili-video-card 提取到BV号: {bvid}")
            
            # 获取标题 - 优先使用 bili-video-card__title
            title = ''
            title_element = await element.query_selector('.bili-video-card__title')
            if title_element:
                # 尝试从标题元素获取文本
                title = await title_element.text_content() or ''
                if not title:
                    # 如果标题元素中有链接，从链接获取
                    title_link = await title_element.query_selector('a')
                    if title_link:
                        title = await title_link.text_content() or ''
                        if not title:
                            title = await title_link.get_attribute('title') or ''
                
                if title:
                    logger.debug(f"从 bili-video-card__title 获取标题: {title}")
            
            # 如果没有标题，从链接的title属性获取
            if not title:
                title = await link_element.get_attribute('title') or ''
                if title:
                    logger.debug(f"从链接title属性获取标题: {title}")
            
            # 如果还是没有标题，使用默认值
            if not title:
                title = f'BV{bvid}的视频'
            
            # 获取封面图片 - 从 img 元素获取
            pic = ''
            img_element = await element.query_selector('img')
            if img_element:
                pic = (await img_element.get_attribute('src') or 
                      await img_element.get_attribute('data-src') or 
                      await img_element.get_attribute('data-original') or
                      await img_element.get_attribute('lazy-src') or
                      await img_element.get_attribute('data-lazy-src') or '')
                
                if pic:
                    logger.debug(f"从 bili-video-card img 获取封面: {pic}")
            
            # 处理封面URL
            pic = self.process_image_url(pic)
            
            video_info = {
                'bvid': bvid,
                'title': title.strip(),
                'pic': pic,
                'created': int(time.time())
            }
            logger.debug(f"成功从 bili-video-card 提取信息: {video_info}")
            return video_info
            
        except Exception as e:
            logger.debug(f"从 bili-video-card 提取信息时发生错误: {e}")
            return None
    
    async def extract_from_bili_cover_card(self, element):
        """从 bili-cover-card__thumbnail 元素提取视频信息"""
        try:
            logger.debug("从 bili-cover-card__thumbnail 元素提取信息...")
            
            # 直接从 img 元素获取封面地址
            pic = ''
            img_element = await element.query_selector('img')
            if img_element:
                # 优先获取 src 属性，这就是封面地址
                pic = (await img_element.get_attribute('src') or 
                      await img_element.get_attribute('data-src') or 
                      await img_element.get_attribute('data-original') or
                      await img_element.get_attribute('lazy-src') or
                      await img_element.get_attribute('data-lazy-src') or '')
                
                if pic:
                    logger.debug(f"从 img 元素 src 获取封面地址: {pic}")
                else:
                    # 如果没有常规属性，尝试从 style 获取背景图片
                    style = await img_element.get_attribute('style') or ''
                    if 'background-image' in style:
                        import re
                        bg_match = re.search(r'background-image:\s*url\(["\']?([^"\')]+)', style)
                        if bg_match:
                            pic = bg_match.group(1)
                            logger.debug(f"从 img style 获取封面地址: {pic}")
            
            # 如果没有找到 img，尝试 picture 标签
            if not pic:
                picture_element = await element.query_selector('picture img, picture source')
                if picture_element:
                    pic = (await picture_element.get_attribute('src') or 
                          await picture_element.get_attribute('srcset') or
                          await picture_element.get_attribute('data-src') or '')
                    
                    if 'srcset' in str(pic) and pic:
                        pic = pic.split(',')[0].split(' ')[0]
                    
                    if pic:
                        logger.debug(f"从 picture 元素获取封面地址: {pic}")
            
            # 如果还是没有，尝试父元素中的 img
            if not pic:
                parent_element = await element.query_selector('xpath=..')
                if parent_element:
                    parent_img = await parent_element.query_selector('img')
                    if parent_img:
                        pic = (await parent_img.get_attribute('src') or 
                              await parent_img.get_attribute('data-src') or '')
                        if pic:
                            logger.debug(f"从父元素 img 获取封面地址: {pic}")
            
            # 如果没有获取到封面地址，返回null
            if not pic:
                logger.debug("未从 bili-cover-card__thumbnail 获取到封面地址")
                return None
            
            # 现在尝试获取BV号和标题（从链接和相关元素中）
            link_element = None
            href = None
            
            # 查找视频链接（从父元素或相邻元素）
            parent_element = await element.query_selector('xpath=..')
            if parent_element:
                # 在父元素中查找链接
                parent_link = await parent_element.query_selector('a[href*="/video/"]')
                if parent_link:
                    link_element = parent_link
                    href = await parent_link.get_attribute('href')
                    logger.debug(f"在父元素中找到视频链接: {href}")
                
                # 如果没有，在兄弟元素中查找
                if not href:
                    sibling_links = await element.query_selector_all('xpath=../a[contains(@href, "/video/")]')
                    if sibling_links:
                        link_element = sibling_links[0]
                        href = await link_element.get_attribute('href')
                        logger.debug(f"在兄弟元素中找到视频链接: {href}")
            
            # 如果还是没有链接，尝试从当前元素向上查找
            if not href:
                current = element
                for _ in range(3):  # 最多向上查找3层
                    try:
                        parent = await current.query_selector('xpath=..')
                        if parent:
                            link = await parent.query_selector('a[href*="/video/"]')
                            if link:
                                href = await link.get_attribute('href')
                                link_element = link
                                logger.debug(f"向上查找找到视频链接: {href}")
                                break
                            current = parent
                        else:
                            break
                    except:
                        break
            
            if not href:
                logger.debug("未找到视频链接，但已获取到封面地址")
                # 即使没有链接，也返回封面信息
                pic = self.process_image_url(pic)
                return {
                    'bvid': 'UNKNOWN',  # 暂时无法获取BV号
                    'title': '未知标题',
                    'pic': pic,
                    'created': int(time.time())
                }
            
            # 提取BV号
            import re
            bv_match = re.search(r'/video/(BV[A-Za-z0-9]+)', href)
            if not bv_match:
                bv_match = re.search(r'(BV[A-Za-z0-9]+)', href)
                if not bv_match:
                    logger.debug(f"无法从链接中提取BV号: {href}")
                    # 即使没有BV号，也返回封面
                    pic = self.process_image_url(pic)
                    return {
                        'bvid': 'UNKNOWN',
                        'title': '未知标题',
                        'pic': pic,
                        'created': int(time.time())
                    }
            
            bvid = bv_match.group(1)
            logger.debug(f"提取到BV号: {bvid}")
            
            # 获取标题
            title = ''
            
            # 从 bili-cover-card__title 获取
            parent_element = await element.query_selector('xpath=..')
            if parent_element:
                title_element = await parent_element.query_selector('.bili-cover-card__title')
                if title_element:
                    title = await title_element.text_content() or ''
                    logger.debug(f"从 bili-cover-card__title 获取标题: {title}")
            
            # 如果没有标题，从链接获取
            if not title and link_element:
                title = await link_element.get_attribute('title') or ''
                logger.debug(f"从链接title属性获取标题: {title}")
            
            # 如果还是没有标题，使用默认值
            if not title:
                title = f'BV{bvid}的视频'
            
            # 处理封面URL
            pic = self.process_image_url(pic)
            logger.debug(f"最终封面URL: {pic}")
            
            video_info = {
                'bvid': bvid,
                'title': title.strip(),
                'pic': pic,
                'created': int(time.time())
            }
            logger.debug(f"成功从 bili-cover-card__thumbnail 提取信息: {video_info}")
            return video_info
            
        except Exception as e:
            logger.debug(f"从 bili-cover-card__thumbnail 提取信息时发生错误: {e}")
            return None
    
    def process_image_url(self, pic_url):
        """处理图片URL，确保获取最佳质量的封面"""
        if not pic_url:
            return ''
        
        logger.debug(f"处理图片URL: {pic_url}")
        
        # 处理相对路径
        if pic_url.startswith('//'):
            pic_url = 'https:' + pic_url
        elif pic_url.startswith('/'):
            pic_url = 'https://i0.hdslb.com' + pic_url
        
        # 移除URL参数，保留原图获取最高质量
        if '@' in pic_url:
            base_url = pic_url.split('@')[0]
            logger.debug(f"移除URL参数，从 {pic_url} 变为 {base_url}")
            pic_url = base_url
        
        # 处理缩略图参数，尝试获取高清版本
        if '_' in pic_url and any(size in pic_url for size in ['_160x120', '_320x200', '_480x300']):
            # 移除小尺寸后缀，获取原图
            import re
            pic_url = re.sub(r'_\d+x\d+\.(jpg|jpeg|png|webp)', r'.\1', pic_url)
            logger.debug(f"移除尺寸后缀，获取高清版本: {pic_url}")
        
        # 确保是有效的图片URL
        if not any(pic_url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']):
            # 如果没有扩展名，添加默认扩展名
            if '?' not in pic_url and '#' not in pic_url:
                pic_url += '.jpg'
                logger.debug(f"添加默认扩展名: {pic_url}")
        
        logger.debug(f"最终处理后的图片URL: {pic_url}")
        return pic_url
    
    async def extract_generic_video_info(self, element):
        """通用视频信息提取方法（兼容旧版本）"""
        try:
            logger.debug("使用通用方法提取视频信息...")
            
            # 多种方式获取视频链接
            link_selectors = [
                'a[href*="/video/"]',
                'a[href*="BV"]',
                '.title a',
                '.video-title a',
                'a'
            ]
            
            link_element = None
            href = None
            
            for selector in link_selectors:
                link_element = await element.query_selector(selector)
                if link_element:
                    href = await link_element.get_attribute('href')
                    if href and '/video/' in href:
                        break
            
            if not href:
                logger.debug("通用方法未获取到视频链接")
                return None
            
            logger.debug(f"通用方法获取到视频链接: {href}")
            
            # 提取BV号
            import re
            bv_match = re.search(r'/video/(BV[A-Za-z0-9]+)', href)
            if not bv_match:
                bv_match = re.search(r'(BV[A-Za-z0-9]+)', href)
                if not bv_match:
                    logger.debug(f"通用方法无法从链接中提取BV号: {href}")
                    return None
            
            bvid = bv_match.group(1)
            logger.debug(f"通用方法提取到BV号: {bvid}")
            
            # 多种方式获取标题
            title_selectors = [
                '.title',
                '.video-title', 
                'a[title]',
                '.name',
                '.video-name',
                'h3',
                '.title-text'
            ]
            
            title = ''
            for selector in title_selectors:
                title_element = await element.query_selector(selector)
                if title_element:
                    title = await title_element.get_attribute('title')
                    if not title:
                        title = await title_element.text_content()
                    if title and title.strip():
                        title = title.strip()
                        break
            
            # 如果还是没有标题，使用链接的title属性
            if not title and link_element:
                title = await link_element.get_attribute('title') or ''
            
            logger.debug(f"通用方法提取到标题: {title}")
            
            # 多种方式获取封面图片 - 优先从 img src 获取
            img_selectors = [
                '.bili-cover-card__thumbnail img',  # 优先查找新版封面卡片
                'img',                              # 通用 img 元素
                '.cover img',                       # 封面区域的 img
                '.pic img',                         # 图片区域的 img
                '.video-cover img',                 # 视频封面 img
                'picture img'                       # picture 标签内的 img
            ]
            
            pic = ''
            for selector in img_selectors:
                img_element = await element.query_selector(selector)
                if img_element:
                    # 优先尝试 src 属性，然后尝试其他懒加载属性
                    pic = (await img_element.get_attribute('src') or 
                          await img_element.get_attribute('data-src') or 
                          await img_element.get_attribute('data-original') or
                          await img_element.get_attribute('lazy-src') or
                          await img_element.get_attribute('data-lazy-src') or
                          await img_element.get_attribute('srcset') or '')
                    
                    if pic:
                        # 如果是 srcset，取第一个 URL
                        if 'srcset' in str(pic):
                            pic = pic.split(',')[0].split(' ')[0]
                        
                        logger.debug(f"通用方法从 '{selector}' 获取封面: {pic}")
                        break
                    else:
                        # 如果没有常规属性，尝试从 style 获取背景图片
                        style = await img_element.get_attribute('style') or ''
                        if 'background-image' in style:
                            import re
                            bg_match = re.search(r'background-image:\s*url\(["\']?([^"\')]+)', style)
                            if bg_match:
                                pic = bg_match.group(1)
                                logger.debug(f"通用方法从 '{selector}' style 获取封面: {pic}")
                                break
            
            # 使用统一的图片URL处理方法
            pic = self.process_image_url(pic)
            logger.debug(f"通用方法处理后的封面URL: {pic}")
            
            # 验证必要信息
            if bvid and title:
                video_info = {
                    'bvid': bvid,
                    'title': title.strip(),
                    'pic': pic,
                    'created': int(time.time())
                }
                logger.debug(f"通用方法成功提取视频信息: {video_info}")
                return video_info
            else:
                logger.debug(f"通用方法缺少必要信息 - BV号: {bvid}, 标题: {title}")
                return None
                
        except Exception as e:
            logger.debug(f"通用方法提取视频信息时发生错误: {e}")
            return None
    
    async def get_user_videos(self, uid):
        """从用户视频页面获取所有视频信息"""
        videos = []
        
        print(f"📺 开始从用户空间页面获取视频列表...")
        
        for attempt in range(config.MAX_RETRIES):
            try:
                await self.smart_delay(is_api_request=True)
                
                # 构建用户视频页面URL
                video_url = config.USER_SPACE_URL.format(uid=uid)
                print(f"🌐 访问用户视频页面: {video_url}")
                
                # 访问用户视频页面
                response = await self.page.goto(video_url, wait_until="networkidle")
                
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}")
                
                # 使用新的页面等待机制
                if not await self.wait_for_page_fully_loaded("用户视频页面"):
                    raise Exception("视频页面加载失败或内容异常")
                
                # Debug日志：显示视频页面HTML信息
                if config.ENABLE_HTML_DEBUG and logger.isEnabledFor(logging.DEBUG):
                    page_content = await self.page.content()
                    html_preview = page_content[:config.HTML_DEBUG_MAX_LENGTH]
                    logger.debug(f"用户视频页面HTML内容预览 (前{config.HTML_DEBUG_MAX_LENGTH}字符):\n{html_preview}")
                    logger.debug(f"视频页面标题: {await self.page.title()}")
                    logger.debug(f"视频页面URL: {self.page.url}")
                else:
                    page_content = await self.page.content()
                
                # 检查页面内容
                if "用户不存在" in page_content or "该用户隐私设置" in page_content:
                    print(f"⚠️ 用户 {uid} 不存在或设置为私人")
                    return []
                
                if "暂无视频" in page_content or "没有找到相关视频" in page_content:
                    print(f"😕 用户 {uid} 没有公开视频")
                    return []
                
                # 开始滚动加载更多视频
                videos = await self.scroll_and_collect_videos()
                
                if videos:
                    self.failure_count = 0  # 成功后重置失败计数
                    print(f"✅ 成功获取到 {len(videos)} 个视频")
                    return videos
                else:
                    print(f"⚠️ 未获取到任何视频")
                    return []
                    
            except Exception as e:
                if await self.handle_request_error(e, attempt):
                    continue
                if attempt < config.MAX_RETRIES - 1:
                    delay = config.RETRY_DELAY * (config.RETRY_BACKOFF ** attempt)
                    print(f"获取视频列表失败，{delay}秒后重试: {e}")
                    await asyncio.sleep(delay)
                else:
                    print(f"获取视频列表时发生错误: {e}")
                    return []
    
    async def download_user_videos(self, uid, download_covers=True):
        """下载用户所有视频"""
        try:
            # 初始化浏览器
            await self.initialize_browser()
            
            # 初始化视频下载器
            await self.init_video_downloader()
            
            # 获取用户信息
            user_info = await self.get_user_info(uid)
            if not user_info:
                print(f"无法获取用户 {uid} 的信息")
                return False
            
            user_name = user_info['name']
            print(f"👤 用户: {user_name} (UID: {uid})")
            
            # 获取用户所有视频
            videos = await self.get_user_videos(uid)
            if not videos:
                print("没有找到任何视频")
                return False
            
            print(f"📺 找到 {len(videos)} 个视频")
            
            # 创建保存目录
            safe_user_name = self.sanitize_filename(user_name)
            user_dir = Path(config.VIDEO_DOWNLOAD_CONFIG['output_dir']) / f"{uid}_{safe_user_name}"
            user_dir.mkdir(parents=True, exist_ok=True)
            
            # 更新下载器输出目录
            self.video_downloader.output_dir = user_dir
            
            print(f"💾 视频将保存到: {user_dir}")
            
            # 下载封面（如果启用）
            if download_covers:
                cover_dir = user_dir / "covers"
                cover_dir.mkdir(exist_ok=True)
                print(f"\n🖼️ 开始下载封面...")
                await self.download_covers_for_videos(videos, cover_dir)
            
            # 下载视频
            print(f"\n📺 开始下载视频...")
            success_count = 0
            failed_videos = []
            
            with tqdm(total=len(videos), desc="下载视频") as pbar:
                for video in videos:
                    bvid = video['bvid']
                    title = video['title']
                    
                    success = await self.video_downloader.download_video(bvid, title)
                    if success:
                        success_count += 1
                    else:
                        failed_videos.append(video)
                    
                    pbar.update(1)
                    pbar.set_postfix({"成功": success_count, "失败": len(failed_videos)})
                    
                    # 防止请求过于频繁
                    await asyncio.sleep(random.uniform(2, 5))
            
            # 输出结果统计
            print(f"\n🎉 下载完成!")
            print(f"📊 总视频数: {len(videos)}")
            print(f"✅ 成功下载: {success_count}")
            print(f"❌ 失败数量: {len(failed_videos)}")
            
            if failed_videos:
                print("\n失败的视频:")
                for video in failed_videos[:10]:  # 只显示前10个失败的
                    print(f"  - {video['bvid']}: {video['title']}")
                if len(failed_videos) > 10:
                    print(f"  ... 还有 {len(failed_videos) - 10} 个")
                
                # 保存失败记录
                failed_log = user_dir / "failed_videos.json"
                with open(failed_log, 'w', encoding='utf-8') as f:
                    json.dump(failed_videos, f, ensure_ascii=False, indent=2)
                print(f"失败记录已保存到: {failed_log}")
            
            return True
            
        finally:
            await self.close_browser()
    
    async def download_single_video(self, bvid):
        """下载单个BV号视频"""
        try:
            # 初始化视频下载器
            await self.init_video_downloader()
            
            print(f"📺 下载单个视频: {bvid}")
            
            success = await self.video_downloader.download_video(bvid)
            
            if success:
                print(f"✅ 下载成功: {bvid}")
            else:
                print(f"❌ 下载失败: {bvid}")
            
            return success
            
        finally:
            await self.close_video_downloader()
    
    async def download_covers_for_videos(self, videos, cover_dir):
        """为视频列表下载封面"""
        success_count = 0
        
        with tqdm(total=len(videos), desc="下载封面") as pbar:
            for video in videos:
                bvid = video['bvid']
                title = video['title']
                pic_url = video['pic']
                
                if not pic_url:
                    pbar.update(1)
                    continue
                
                # 生成文件名
                safe_title = self.sanitize_filename(title)
                ext = self.get_image_extension(pic_url)
                filename = f"{bvid}_{safe_title}{ext}"
                save_path = cover_dir / filename
                
                # 检查文件是否已存在
                if save_path.exists():
                    success_count += 1
                    pbar.update(1)
                    continue
                
                # 下载封面
                if await self.download_cover(pic_url, save_path):
                    success_count += 1
                
                pbar.update(1)
                pbar.set_postfix({"成功": success_count})
        
        print(f"✅ 封面下载完成: {success_count}/{len(videos)}")
    
    async def download_cover(self, pic_url, save_path):
        """下载单个封面图片"""
        for attempt in range(config.MAX_RETRIES):
            try:
                await self.smart_delay(is_api_request=False)
                
                # 确保URL是完整的
                if pic_url.startswith('//'):
                    pic_url = 'https:' + pic_url
                elif pic_url.startswith('/'):
                    pic_url = 'https://i0.hdslb.com' + pic_url
                
                # 使用页面发起请求下载图片
                response = await self.page.goto(pic_url)
                
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}")
                
                # 获取图片数据
                image_data = await response.body()
                
                # 创建目录
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                
                # 保存文件
                with open(save_path, 'wb') as f:
                    f.write(image_data)
                
                # 成功下载后减少失败计数
                if self.failure_count > 0:
                    self.failure_count = max(0, self.failure_count - 1)
                
                return True
                
            except Exception as e:
                if await self.handle_request_error(e, attempt):
                    continue
                if attempt < config.MAX_RETRIES - 1:
                    delay = config.RETRY_DELAY * (config.RETRY_BACKOFF ** attempt)
                    print(f"下载失败，{delay}秒后第 {attempt + 2} 次重试: {e}")
                    await asyncio.sleep(delay)
                else:
                    print(f"下载失败，已重试 {config.MAX_RETRIES} 次: {e}")
                    return False
        
        return False
    
    def get_image_extension(self, pic_url):
        """从URL获取图片扩展名"""
        try:
            parsed = urlparse(pic_url)
            path = parsed.path
            _, ext = os.path.splitext(path)
            if ext.lower() in config.ALLOWED_IMAGE_FORMATS:
                return ext
            else:
                return '.jpg'  # 默认扩展名
        except:
            return '.jpg'
    
    async def crawl_user_covers(self, uid):
        """爬取指定用户的所有视频封面"""
        try:
            # 初始化浏览器
            await self.initialize_browser()
            
            # 获取用户信息
            user_info = await self.get_user_info(uid)
            if not user_info:
                print(f"无法获取用户 {uid} 的信息")
                return False
            
            user_name = user_info['name']
            print(f"用户: {user_name} (UID: {uid})")
            
            # 获取用户所有视频
            videos = await self.get_user_videos(uid)
            if not videos:
                print("没有找到任何视频")
                return False
            
            # 创建保存目录
            safe_user_name = self.sanitize_filename(user_name)
            save_dir = Path(f"{uid}_{safe_user_name}")
            save_dir.mkdir(exist_ok=True)
            
            print(f"封面将保存到目录: {save_dir}")
            
            # 下载封面
            success_count = 0
            failed_videos = []
            
            with tqdm(total=len(videos), desc="下载封面") as pbar:
                for video in videos:
                    bvid = video['bvid']
                    title = video['title']
                    pic_url = video['pic']
                    
                    if not pic_url:
                        print(f"视频 {bvid} 没有封面URL")
                        failed_videos.append(video)
                        pbar.update(1)
                        continue
                    
                    # 生成文件名
                    safe_title = self.sanitize_filename(title)
                    ext = self.get_image_extension(pic_url)
                    filename = f"{bvid}_{safe_title}{ext}"
                    save_path = save_dir / filename
                    
                    # 检查文件是否已存在
                    if save_path.exists():
                        print(f"文件已存在，跳过: {filename}")
                        success_count += 1
                        pbar.update(1)
                        continue
                    
                    # 下载封面
                    if await self.download_cover(pic_url, save_path):
                        success_count += 1
                        pbar.set_postfix({"成功": success_count, "失败": len(failed_videos)})
                    else:
                        failed_videos.append(video)
                    
                    pbar.update(1)
            
            # 输出结果统计
            print(f"\n下载完成!")
            print(f"总视频数: {len(videos)}")
            print(f"成功下载: {success_count}")
            print(f"失败数量: {len(failed_videos)}")
            
            if failed_videos:
                print("\n失败的视频:")
                for video in failed_videos[:10]:  # 只显示前10个失败的
                    print(f"  - {video['bvid']}: {video['title']}")
                if len(failed_videos) > 10:
                    print(f"  ... 还有 {len(failed_videos) - 10} 个")
            
            # 保存失败记录
            if failed_videos:
                failed_log = save_dir / "failed_downloads.json"
                with open(failed_log, 'w', encoding='utf-8') as f:
                    json.dump(failed_videos, f, ensure_ascii=False, indent=2)
                print(f"失败记录已保存到: {failed_log}")
            
            return True
            
        finally:
            # 确保关闭浏览器
            await self.close_browser()


async def main():
    """主函数"""
    print("🎭 哔哩哔哩视频爬虫 (Playwright版本 - 支持封面和视频下载)")
    print("=" * 65)
    print("\n🌟 功能特色:")
    print("- 🖼️ 封面下载 - 批量下载用户所有视频封面")
    print("- 📺 视频下载 - 支持下载用户所有视频或单个BV号")
    print("- 🎭 真实浏览器 - 使用Playwright降低被检测风险")
    print("- 🛡️ 智能反爬 - 自动处理各种反爬虫限制")
    print("- 📄 分页支持 - 自动处理多页视频获取")
    print("- 🔍 数量校验 - 确保视频收集完整性")
    print("- 🎬 分段合并 - 自动下载并合并视频音频流")
    print("\n⚙️ 当前配置:")
    print(f"- 🕐 请求间隔: {config.REQUEST_DELAY_MIN}-{config.REQUEST_DELAY_MAX}秒")
    print(f"- 📥 下载间隔: {config.DOWNLOAD_DELAY_MIN}-{config.DOWNLOAD_DELAY_MAX}秒")
    print(f"- 🔄 连续请求限制: {config.MAX_CONSECUTIVE_REQUESTS}次")
    print(f"- 💤 休息时间: {config.LONG_BREAK_DURATION}秒")
    print(f"- 📄 分页功能: {'开启' if config.PAGINATION_CONFIG.get('enabled', False) else '关闭'}")
    print(f"- 🔍 数量校验: {'开启' if config.CONTENT_VERIFICATION.get('verify_video_count', False) else '关闭'}")
    print(f"- 📺 视频下载: {'开启' if config.VIDEO_DOWNLOAD_CONFIG.get('enabled', False) else '关闭'}")
    print(f"- 📝 日志级别: {logging.getLevelName(config.LOG_LEVEL)}")
    
    # 初始化日志
    logger.info("程序启动，当前配置已加载")
    logger.debug(f"调试模式已启用，HTML调试: {config.ENABLE_HTML_DEBUG}")
    
    import sys
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='哔哩哔哩视频爬虫 - 支持封面下载和视频下载',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例用法:
  # 下载用户封面（默认）
  python %(prog)s 123456
  
  # 下载用户所有视频
  python %(prog)s 123456 --download-videos
  
  # 下载用户视频，不下载封面
  python %(prog)s 123456 --download-videos --no-covers
  
  # 仅下载封面
  python %(prog)s 123456 --covers-only
  
  # 下载单个BV号视频
  python %(prog)s --bv BV1234567890
  
  # 交互模式
  python %(prog)s
        '''
    )
    
    parser.add_argument('uid', nargs='?', type=int, help='用户UID')
    parser.add_argument('--bv', '--bvid', type=str, help='下载指定BV号的视频')
    parser.add_argument('--download-videos', action='store_true', help='下载用户所有视频')
    parser.add_argument('--covers-only', action='store_true', help='仅下载封面（默认行为）')
    parser.add_argument('--no-covers', action='store_true', help='不下载封面（与--download-videos配合使用）')
    parser.add_argument('--enable-video-download', action='store_true', help='启用视频下载功能')
    
    args = parser.parse_args()
    
    # 处理BV号下载
    if args.bv:
        bvid = args.bv
        if not bvid.startswith('BV'):
            bvid = 'BV' + bvid
        
        print(f"📺 下载单个视频: {bvid}")
        
        crawler = PlaywrightBilibiliCrawler()
        try:
            success = await crawler.download_single_video(bvid)
            if success:
                print("\n🎉 视频下载完成！")
            else:
                print("\n😔 视频下载失败！")
        except KeyboardInterrupt:
            print("\n\n⏹️ 用户中断了程序")
        except Exception as e:
            print(f"\n😱 程序执行出错: {e}")
        return
    
    # 获取UID
    uid = args.uid
    if not uid:
        # 交互模式
        while True:
            uid_input = input("\n🎯 请输入要爬取的用户UID (或者输入 'q' 退出): ").strip()
            if uid_input.lower() == 'q':
                print("🙋‍♂️ 用户取消操作")
                return
            if uid_input.isdigit():
                uid = int(uid_input)
                break
            else:
                print("😅 请输入有效的数字UID")
    
    # 确定操作模式
    download_videos = args.download_videos or args.enable_video_download
    download_covers = not args.no_covers  # 默认下载封面，除非明确指定不下载
    
    # 如果启用了视频下载功能，需要先启用配置
    if download_videos:
        config.VIDEO_DOWNLOAD_CONFIG['enabled'] = True
        print("\n📺 已启用视频下载功能")
    
    # 显示操作信息
    print(f"\n📋 操作模式:")
    print(f"  - 用户UID: {uid}")
    print(f"  - 下载封面: {'是' if download_covers else '否'}")
    print(f"  - 下载视频: {'是' if download_videos else '否'}")
    
    # 确认继续
    action_desc = []
    if download_covers: action_desc.append("封面")
    if download_videos: action_desc.append("视频")
    action_text = "和".join(action_desc) if action_desc else "数据"
    
    confirm = input(f"\n🚀 即将爬取用户 {uid} 的{action_text}，继续吗? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes', '是']:
        print("🙋‍♂️ 用户取消操作")
        return
    
    # 创建爬虫实例并开始爬取
    crawler = PlaywrightBilibiliCrawler()
    
    try:
        if download_videos:
            # 视频下载模式
            success = await crawler.download_user_videos(uid, download_covers=download_covers)
        else:
            # 仅封面下载模式
            success = await crawler.crawl_user_covers(uid)
        
        if success:
            print("\n🎉 任务完成！")
        else:
            print("\n😔 任务失败！")
            print("\n💡 建议:")
            print("1. 检查UID是否正确")
            print("2. 确保网络连接稳定")
            print("3. 如果下载视频，请确保已安装FFmpeg")
            print("4. 稍后再试")
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断了程序")
        print("💾 已下载的文件将保留，下次运行时会自动跳过")
    except Exception as e:
        print(f"\n😱 程序执行出错: {e}")
        print("\n🛠️ 故障排除:")
        print("1. 确保已安装Playwright: pip install playwright")
        print("2. 确保已安装浏览器: playwright install chromium")
        print("3. 如果下载视频，确保已安装FFmpeg")
        print("4. 检查网络连接")
        print("5. 检查是否有足够的磁盘空间")


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())