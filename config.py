# -*- coding: utf-8 -*-
"""
哔哩哔哩封面爬虫配置文件 - Playwright版本
"""

import logging

# 日志级别配置
LOG_LEVEL = logging.ERROR  # 可选: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# 是否启用HTML调试日志
ENABLE_HTML_DEBUG = True  # 是否在DEBUG级别显示HTML内容
HTML_DEBUG_MAX_LENGTH = 10000000  # HTML调试日志的最大长度

# API 相关配置（仅用于下载图片）
BILIBILI_API_BASE = "https://api.bilibili.com"
USER_SPACE_API = "https://api.bilibili.com/x/space/arc/search"  # 不再使用
USER_INFO_API = "https://api.bilibili.com/x/space/acc/info"      # 不再使用

# 页面爬取相关配置
USER_SPACE_URL = "https://space.bilibili.com/{uid}/upload/video"  # 用户视频页面
USER_SPACE_BASE = "https://space.bilibili.com/{uid}"       # 用户主页

# Playwright 浏览器配置
PLAYWRIGHT_CONFIG = {
    'headless': True,  # 改为非无头模式，便于调试
    'slow_mo': 2000,   # 增加操作间隔到2秒
    'timeout': 120000,  # 增加页面加载超时到2分钟
    'viewport': {'width': 1920, 'height': 1080},  # 视窗大小
    'user_agent': None,  # 将动态设置
    'ignore_https_errors': True,
    'java_script_enabled': True
}

# 浏览器启动参数 - 更真实的浏览器环境
BROWSER_ARGS = [
    '--no-sandbox',
    '--disable-setuid-sandbox', 
    '--disable-dev-shm-usage',
    '--disable-background-timer-throttling',
    '--disable-backgrounding-occluded-windows',
    '--disable-renderer-backgrounding',
    '--disable-features=TranslateUI',
    '--disable-extensions',
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-default-apps',
    '--disable-blink-features=AutomationControlled',  # 隐藏自动化标识
    '--disable-web-security',  # 禁用web安全限制
    '--allow-running-insecure-content',  # 允许不安全内容
    '--disable-features=VizDisplayCompositor'  # 禁用显示合成器
]

# 请求头配置 - 更多User-Agent和更真实的浏览器环境
USER_AGENTS = [
    # Chrome Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    # Firefox Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0',
    # Edge Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
    # Chrome macOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    # Safari macOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    # Chrome Linux
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    # Firefox Linux
    'Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:119.0) Gecko/20100101 Firefox/119.0'
]

# 基础请求头模板 (更真实的浏览器行为)
BASE_HEADERS_TEMPLATES = [
    # Chrome 模板
    {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    },
    # Firefox 模板
    {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1'
    },
    # Safari 模板
    {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
]

# 下载配置
DOWNLOAD_TIMEOUT = 45
MAX_RETRIES = 3  # 减少重试次数，避免频繁请求
RETRY_DELAY = 10  # 重试间隔（秒）- 大幅增加
RETRY_BACKOFF = 3  # 重试退避倍数 - 增加

# 文件配置
ALLOWED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.webp']
MAX_FILENAME_LENGTH = 100  # 最大文件名长度

# 爬取配置（Playwright模式 - 更温和的策略）
PAGE_SIZE = 30  # 每页获取的视频数量（Playwright可以适当放宽）
REQUEST_DELAY_MIN = 3  # 最小请求间隔（秒）- 由于Playwright更真实，可以减少
REQUEST_DELAY_MAX = 8  # 最大请求间隔（秒）
DOWNLOAD_DELAY_MIN = 2  # 下载间隔最小值（秒）
DOWNLOAD_DELAY_MAX = 5  # 下载间隔最大值（秒）

# 反反爬配置（Playwright模式 - 更均衡的策略）
MAX_CONSECUTIVE_REQUESTS = 30  # 连续请求最大次数（适当增加）
LONG_BREAK_DURATION = 15  # 长时间休息持续时间（秒）- 2分钟
ERROR_COOLDOWN = 180  # 出错后冷却时间（秒）- 3分钟
INITIAL_WARMUP_DELAY = 3  # 启动预热延迟（秒）- 减少到30秒
REQUEST_FAILURE_PENALTY = 10  # 请求失败惩罚时间（秒）- 2分钟
FIRST_REQUEST_DELAY = 1  # 首次请求额外延迟（秒）- 减少到10秒

# 页面操作配置
PAGE_LOAD_TIMEOUT = 30000  # 页面加载超时(毫秒)
ELEMENT_WAIT_TIMEOUT = 15000  # 元素等待超时(毫秒)
SCROLL_DELAY = 1500  # 滚动延迟(毫秒) - 增加以模拟真实用户
CLICK_DELAY = 800   # 点击延迟(毫秒)
SCROLL_STEP = 800   # 每次滚动距离(像素)
MAX_SCROLL_ATTEMPTS = 100  # 最大滚动次数 - 增加以获取更多视频

# JavaScript完全加载等待配置
WAIT_FOR_LOAD_STATES = [
    'domcontentloaded',  # DOM内容加载完成
    'networkidle'        # 网络空闲(500ms内无网络活动)
]
ADDITIONAL_WAIT_TIME = 5  # 额外等待时间(秒) - 确保JS完全执行
MAX_WAIT_ATTEMPTS = 3     # 最大等待重试次数

# 页面内容验证
CONTENT_VERIFICATION = {
    'check_video_elements': True,    # 检查是否有视频元素
    'min_video_count': 0,           # 最少视频数量（改为0，允许空页面）
    'check_user_info': True,        # 检查用户信息
    'retry_on_empty': False,        # 内容为空时不重试（可能是正常的空页面）
    'strict_error_check': False,    # 不使用严格的错误检查
    'verify_video_count': True      # 验证视频数量是否与页面显示一致
}

# 视频数量验证配置
VIDEO_COUNT_VERIFICATION = {
    'check_pagination': True,       # 检查分页信息
    'pagination_selectors': [       # 分页信息选择器
        '.vui_pagenation-go__count',    # "共 X 页 / Y 个"
        '.pagination-info',
        '.page-info',
        '.total-count'
    ],
    'count_pattern': r'共\s*(\d+)\s*页\s*/\s*(\d+)\s*个',  # 提取总数的正则
    'tolerance_ratio': 0.1,         # 允许的误差比例（10%）
    'min_expected_count': 1         # 期望的最小视频数量
}

# 分页操作配置
PAGINATION_CONFIG = {
    'enabled': True,                # 启用分页点击
    'smart_stop': True,            # 智能停止：当收集数量达到期望值时自动停止
    'max_pages': 50,               # 最大处理页数限制
    'page_wait_time': 5,           # 页面切换后等待时间（秒）
    'click_delay': 1000,           # 点击延迟（毫秒）
    'next_page_selectors': [       # 下一页按钮选择器
        '.vui_pagenation--btn-side:has-text("下一页")',  # "下一页"按钮
        '.vui_button:has-text("下一页")',
        'button:has-text("下一页")',
        '.pagination-next',
        '.next-page',
        '.page-next',
        'a:has-text("下一页")',
        '[aria-label="下一页"]',
        '.vui_pagenation--btn-side'    # 通用的分页侧边按钮
    ]
}

# 视频元素选择器（按优先级排序）
VIDEO_SELECTORS = [
    '.bili-video-card',             # B站新版视频卡片
    '.bili-cover-card__thumbnail',  # B站封面卡片缩略图
    '.small-item',                  # B站常用的小卡片
    '.video-item',                  # 视频项目
    '.list-item',                   # 列表项
    '.video',                       # 通用视频元素
    'a[href*="/video/BV"]'          # 包含BV号的链接
]

# 用户名选择器（按优先级排序）
USER_NAME_SELECTORS = [
    '.nickname',               # 昵称选择器（最高优先级）
    '.upinfo-detail__top .nickname',   # 新版页面用户信息区域的昵称
    '.h-name',                # 旧版新版页面用户名
    '.username',             # 经典用户名选择器
    '.info .name',           # 信息区域的名称
    '.user-info .username',  # 用户信息用户名
    '.user-info-title',      # 用户信息标题
    '.user-name',            # 用户名称
    'h1.username',           # H1标签用户名
    '.space-info .info .name', # 空间信息名称
    '.username-wrap .username' # 用户名包装器
]

# 视频标题选择器（按优先级排序）
TITLE_SELECTORS = [
    '.bili-video-card__title',      # B站新版视频卡片标题
    '.bili-video-card__title a',    # B站新版视频卡片标题链接
    '.bili-cover-card__title',      # B站封面卡片标题
    '.title',
    '.video-title',
    'a[title]',
    '.name',
    '.video-name',
    'h3',
    '.title-text'
]

# 图片选择器（按优先级排序）
IMAGE_SELECTORS = [
    '.bili-cover-card__thumbnail img',  # B站新版封面卡片内的图片
    '.bili-cover-card__thumbnail picture img',  # 如果使用picture标签
    'img',
    '.cover img',
    '.pic img',
    '.video-cover img'
]

# 兼容性配置 - 保持向后兼容
VIDEO_CARD_SELECTOR = '.small-item, .video-item'  # 视频卡片选择器（旧版本兼容）
USER_NAME_SELECTOR = '.username, .info .name'     # 用户名选择器（旧版本兼容）
NO_MORE_DATA_SELECTOR = '.no-more'  # 没有更多数据的选择器

# 视频下载配置
VIDEO_DOWNLOAD_CONFIG = {
    'enabled': False,              # 默认关闭视频下载功能
    'quality': 'high',            # 视频质量：'high', 'medium', 'low'
    'format': 'mp4',              # 输出格式
    'max_concurrent': 2,          # 最大并发下载数（降低以防止被检测）
    'segment_timeout': 600,       # 分段下载超时（秒）- 增加超时时间
    'retry_times': 5,             # 下载重试次数 - 增加重试
    'retry_delay': [3, 8, 15],    # 重试延迟阶段（秒）
    'temp_dir': 'temp_videos',    # 临时文件目录
    'output_dir': 'downloaded_videos',  # 输出目录
    
    # 反爬虫配置 - 使用更通用的浏览器标识和行为模拟
    'user_agents': [
        # 主流浏览器User-Agent轮换 - 使用最新稳定版本
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ],
    
    # 通用请求头模板 - 模拟真实浏览器行为
    'headers_templates': [
        # 通用模板1 - 适合大多数场景
        {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site'
        },
        # 通用模板2 - 视频请求专用
        {
            'Accept': 'video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'identity;q=1, *;q=0',
            'Range': 'bytes=0-',
            'Connection': 'keep-alive'
        },
        # 通用模板3 - API请求专用
        {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': 'https://www.bilibili.com',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site'
        }
    ],
    
    # 通用反爬策略配置 - 防止被检测和拦截
    'anti_crawl': {
        'request_delay_min': 2,          # 最小请求间隔（秒）- 模拟人类行为
        'request_delay_max': 6,          # 最大请求间隔（秒）
        'max_consecutive': 3,            # 连续请求最大次数 - 避免频繁请求
        'cooldown_time': 180,            # 冷却时间（秒）- 防止触发限制
        'rotate_headers': True,          # 轮换请求头 - 模拟不同浏览器
        'rotate_user_agent': True,       # 轮换User-Agent - 避免识别
        'random_delay': True,            # 启用随机延迟 - 更自然的请求间隔
        'session_rotation': True,        # 会话轮换 - 定期更换连接
        'max_retry_attempts': 3,         # 最大重试次数
        'backoff_factor': 2.0,           # 退避因子 - 重试间隔递增
        'respect_rate_limit': True,      # 遵守速率限制
        'adaptive_delay': True           # 自适应延迟 - 根据响应时间调整
    },
    
    # 通用Referer配置 - 随机选择更真实
    'referers': [
        'https://www.bilibili.com/',
        'https://space.bilibili.com/',
        'https://www.bilibili.com/video/',
        'https://search.bilibili.com/'
    ]
}

# 视频API配置
VIDEO_API_CONFIG = {
    'play_url_api': 'https://api.bilibili.com/x/player/playurl',
    'video_info_api': 'https://api.bilibili.com/x/web-interface/view',
    'required_params': {
        'fnval': 16,    # 获取MP4格式
        'fnver': 0,
        'fourk': 1      # 支持4K
    }
}

# FFmpeg配置 - 跨平台路径支持
FFMPEG_CONFIG = {
    'enabled': True,                    # 是否启用FFmpeg功能
    'custom_path': '',                  # 自定义FFmpeg路径（优先级最高）
    'timeout': 300,                     # FFmpeg执行超时时间（秒）
    'quality_preset': 'fast',          # 编码预设：ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
    'video_codec': 'copy',              # 视频编解码器：copy（不重编码），libx264, libx265等
    'audio_codec': 'aac',               # 音频编解码器：aac, mp3, copy等
    'extra_args': ['-strict', 'experimental'],  # 额外的FFmpeg参数
    
    # 跨平台路径检测顺序
    'search_paths': {
        'windows': [
            './bin/ffmpeg.exe',                     # 项目本地FFmpeg（最高优先级）
            'ffmpeg.exe',                           # 当前目录或PATH中
            r'C:\ffmpeg\bin\ffmpeg.exe',            # 常见安装路径
            r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe',
            r'D:\ffmpeg\bin\ffmpeg.exe',
            './ffmpeg.exe',                         # 相对路径
            './tools/ffmpeg.exe'
        ],
        'linux': [
            'ffmpeg',                               # PATH中
            '/usr/bin/ffmpeg',                      # 系统安装
            '/usr/local/bin/ffmpeg',                # 本地安装
            '/opt/ffmpeg/bin/ffmpeg',               # 可选安装
            '/snap/bin/ffmpeg',                     # Snap安装
            './ffmpeg',                             # 相对路径
            './bin/ffmpeg'
        ],
        'darwin': [  # macOS
            'ffmpeg',                               # PATH中或Homebrew
            '/usr/local/bin/ffmpeg',                # Homebrew默认
            '/opt/homebrew/bin/ffmpeg',             # Apple Silicon Homebrew
            '/usr/bin/ffmpeg',                      # 系统安装
            '/Applications/ffmpeg',                 # 应用程序目录
            './ffmpeg',                             # 相对路径
            './bin/ffmpeg'
        ]
    },
    
    # 安装指南链接
    'install_guides': {
        'windows': 'https://ffmpeg.org/download.html#build-windows',
        'linux': 'https://ffmpeg.org/download.html#build-linux', 
        'darwin': 'https://ffmpeg.org/download.html#build-mac'
    }
}