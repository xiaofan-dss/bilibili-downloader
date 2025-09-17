# 🎭 哔哩哔哩视频爬虫完整文档

> **版本**: v2.0 完整版 | **最后更新**: 2025-09-15  
> **技术栈**: Python 10 + Playwright + aiohttp + FFmpeg

---

## 📑 目录

1. [项目概述](#项目概述)
2. [功能特点](#功能特点)  
3. [版本选择](#版本选择)
4. [快速开始](#快速开始)
5. [详细使用指南](#详细使用指南)
6. [视频下载功能](#视频下载功能)
7. [系统要求](#系统要求)
8. [配置说明](#配置说明)
9. [故障排除](#故障排除)
10. [技术实现](#技术实现)
11. [更新记录](#更新记录)

---

## 🎆 项目概述

这是一个用于爬取哔哩哔哩指定用户所有视频封面和视频的Python程序，提供多个版本供选择。

### 🌟 主要功能

✅ **封面下载** - 批量下载用户所有视频封面  
✅ **视频下载** - 下载用户所有视频或单个BV号视频  
✅ **分页支持** - 自动处理多页视频获取  
✅ **智能反爬** - 使用Playwright降低被检测风险  
✅ **数量校验** - 确保视频收集完整性  
✅ **进度显示** - 实时显示下载进度  
✅ **断点续传** - 跳过已下载的文件  
✅ **错误重试** - 智能重试机制  

---

## 🎭 版本选择

### 🎭 Playwright版本（强烈推荐）
✅ **高成功率**: 使用真实浏览器环境，大幅降低被检测风险  
✅ **更温和的策略**: 请求间隔3-8秒，效率更高  
✅ **智能反反爬**: 自动处理各种限制和检测  
✅ **用户友好**: 一键启动，自动安装依赖  
✅ **完整功能**: 支持封面下载、视频下载、分页处理

**适用场景**: 需要稳定、高效的爬取任务

### 🐌 极限保守版本  
⚠️ **超低速度**: 请求间隔15-30秒，确保绝对安全  
⚠️ **资源占用低**: 仅使用requests库，轻量级  
⚠️ **兼容性好**: 适用于各种环境  

**适用场景**: 对速度要求不高，但需要绝对稳定的场景

### ⏱️ 性能对比

| 特性 | Playwright版本 | 极限保守版本 |
|------|----------------|-----------------|
| 🎯 成功率 | 高 | 中等 |
| ⏰ API请求间隔 | 3-8秒 | 15-30秒 |
| 🔄 连续请求限制 | 8次 | 3次 |
| ⚙️ 启动时间 | 10-15秒 | 即时 |
| 💾 内存占用 | 中等 | 低 |
| 🔧 安装复杂度 | 中等 | 低 |
| 🐋 大用户(1000视频) | 8-12小时 | 30+小时 |

---

## 🚀 快速开始

### 🎭 Playwright版本（推荐）

**Windows用户**:
```bash
# 双击运行或命令行执行
start_playwright.bat

# 或指定UID直接运行
start_playwright.bat 137429365
```

**Linux/Mac用户**:
```bash
# 添加执行权限
chmod +x start_playwright.sh

# 运行脚本
./start_playwright.sh 137429365
```

**手动运行**:
```bash
# 安装依赖
pip install -r requirements.txt
playwright install chromium

# 运行程序
python10 bilibili_cover_crawler_playwright.py
```

### 🐌 极限保守版本

```bash
# 安装依赖
pip install -r requirements.txt

# 运行程序
python bilibili_cover_crawler.py
```

---

## 📖 详细使用指南

### 1. 基础使用（下载封面）
```bash
# 下载用户123456的所有视频封面
python10 bilibili_cover_crawler_playwright.py 123456
```

### 2. 下载视频
```bash
# 下载用户所有视频和封面
python10 bilibili_cover_crawler_playwright.py 123456 --download-videos

# 只下载视频，不下载封面
python10 bilibili_cover_crawler_playwright.py 123456 --download-videos --no-covers
```

### 3. 下载单个视频  
```bash
# 下载指定BV号的视频
python10 bilibili_cover_crawler_playwright.py --bv BV1234567890
```

### 4. 交互模式
```bash
# 启动交互界面选择功能
python10 bilibili_cover_crawler_playwright.py
```

### 🔧 命令行参数详解

| 参数 | 说明 | 示例 |
|------|------|------|
| `uid` | 用户UID（位置参数） | `123456` |
| `--bv` / `--bvid` | 下载指定BV号视频 | `--bv BV1234567890` |
| `--download-videos` | 下载用户所有视频 | `--download-videos` |
| `--covers-only` | 仅下载封面（默认） | `--covers-only` |
| `--no-covers` | 不下载封面 | `--no-covers` |
| `--enable-video-download` | 启用视频下载功能 | `--enable-video-download` |
| `--help` | 显示帮助信息 | `--help` |

### 📊 输出结构

```
项目目录/
├── 123456_用户名/              # 封面下载目录
│   ├── BV1xxx_视频标题.jpg
│   └── failed_downloads.json  # 失败记录
├── downloaded_videos/          # 视频下载目录
│   └── 123456_用户名/
│       ├── covers/            # 封面子目录
│       ├── BV1xxx_视频标题.mp4
│       └── failed_videos.json
└── temp_videos/               # 临时文件
    ├── BV1xxx_video.m4s
    └── BV1xxx_audio.m4s
```

---

## 🎬 视频下载功能

### 🆕 新增功能

✅ **用户所有视频下载** - 下载指定用户的所有视频  
✅ **单个BV号下载** - 下载指定BV号的视频  
✅ **分段下载合并** - 自动下载视频流和音频流并合并  
✅ **封面下载支持** - 可同时下载视频封面  
✅ **进度显示** - 实时显示下载进度  
✅ **完整命令行支持** - 支持多种参数组合，灵活控制下载行为

### 🎯 工作原理

1. **获取视频信息** - 通过B站API获取视频详情
2. **获取播放URL** - 获取DASH格式的视频流地址  
3. **分段下载** - 分别下载视频流和音频流
4. **FFmpeg合并** - 使用FFmpeg将视频和音频合并为MP4
5. **文件整理** - 按用户分类保存到对应目录

### 💡 使用示例

```bash
# 示例1：下载UP主123456的所有封面
python10 bilibili_cover_crawler_playwright.py 123456

# 示例2：下载UP主123456的所有视频和封面
python10 bilibili_cover_crawler_playwright.py 123456 --download-videos

# 示例3：只下载UP主123456的视频，不要封面
python10 bilibili_cover_crawler_playwright.py 123456 --download-videos --no-covers

# 示例4：下载指定的BV号视频
python10 bilibili_cover_crawler_playwright.py --bv BV1xx4y7w147y

# 示例5：交互式选择模式
python10 bilibili_cover_crawler_playwright.py
```

---

## ⚙️ 系统要求

### 必需依赖
- **Python 3.10+**
- **Playwright** - 浏览器自动化
- **aiohttp** - 异步HTTP客户端
- **aiofiles** - 异步文件操作
- **FFmpeg** - 视频合并（仅视频下载需要）
- **tqdm** - 进度条显示

### 完整依赖列表

```bash
# 核心爬虫依赖
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
Pillow==10.0.1
urllib3==2.0.7
tqdm==4.66.1

# Playwright浏览器自动化
playwright==1.40.0

# 异步HTTP和文件操作（新增）
aiohttp==3.9.1
aiofiles==23.2.0

# 数据处理
pandas==2.1.4
numpy==1.24.3

# 配置和工具
pyyaml==6.0.1
chardet==5.2.0

# 日志和调试
coloredlogs==15.0.1
```

### 安装命令
```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装Playwright浏览器
playwright install chromium

# 安装FFmpeg（视频下载必需）
# Windows: 从 https://ffmpeg.org/download.html 下载并添加到PATH
# Linux: sudo apt install ffmpeg
# macOS: brew install ffmpeg
```

---

## 🔧 配置说明

### 基础配置
- `PAGE_SIZE`: 每页获取的视频数量（默认30）
- `DOWNLOAD_TIMEOUT`: 下载超时时间（默认45秒）
- `MAX_RETRIES`: 最大重试次数（默认3次）
- `MAX_FILENAME_LENGTH`: 最大文件名长度（默认100字符）

### 反反爬配置
- `REQUEST_DELAY_MIN/MAX`: API请求延迟范围（默认3-8秒）
- `DOWNLOAD_DELAY_MIN/MAX`: 下载延迟范围（默认2-5秒）
- `MAX_CONSECUTIVE_REQUESTS`: 连续请求最大次数（默认30次）
- `LONG_BREAK_DURATION`: 长时间休息持续时间（默认15秒）
- `ERROR_COOLDOWN`: 出错后冷却时间（默认180秒）

### 视频下载配置
```python
VIDEO_DOWNLOAD_CONFIG = {
    'enabled': False,              # 默认关闭视频下载功能
    'quality': 'high',            # 视频质量：'high', 'medium', 'low'
    'format': 'mp4',              # 输出格式
    'max_concurrent': 2,          # 最大并发下载数
    'segment_timeout': 600,       # 分段下载超时（秒）
    'retry_times': 5,             # 下载重试次数
    'temp_dir': 'temp_videos',    # 临时文件目录
    'output_dir': 'downloaded_videos',  # 输出目录
}
```

### FFmpeg配置
```python
FFMPEG_CONFIG = {
    'enabled': True,                    # 是否启用FFmpeg功能
    'custom_path': '',                  # 自定义FFmpeg路径（优先级最高）
    'timeout': 300,                     # FFmpeg执行超时时间（秒）
    'quality_preset': 'fast',          # 编码预设
    'video_codec': 'copy',              # 视频编解码器：copy（不重编码）
    'audio_codec': 'aac',               # 音频编解码器
    'extra_args': [],                   # 额外的FFmpeg参数
    
    # 跨平台路径检测顺序
    'search_paths': {
        'windows': [
            './bin/ffmpeg.exe',                     # 项目本地FFmpeg（最高优先级）
            'ffmpeg.exe',                           # 当前目录或PATH中
            r'C:\\ffmpeg\\bin\\ffmpeg.exe',         # 常见安装路径
            # ... 更多路径
        ],
        'linux': [
            'ffmpeg',                               # PATH中
            '/usr/bin/ffmpeg',                      # 系统安装
            # ... 更多路径
        ],
        'darwin': [  # macOS
            'ffmpeg',                               # PATH中或Homebrew
            '/usr/local/bin/ffmpeg',                # Homebrew默认
            # ... 更多路径
        ]
    }
}
```

### 分页处理配置
```python
PAGINATION_CONFIG = {
    'enabled': True,                # 启用分页点击
    'smart_stop': True,            # 智能停止：当收集数量达到期望值时自动停止
    'max_pages': 50,               # 最大处理页数限制
    'page_wait_time': 5,           # 页面切换后等待时间（秒）
    'click_delay': 1000,           # 点击延迟（毫秒）
}
```

---

## 🛠️ 故障排除

### 🚨 紧急情况：获取用户信息就失败

#### 🔍 问题分析
当程序在第一步"获取用户信息"就失败时，通常表明：
1. **IP已被标记**: 你的IP地址可能已经被哔哩哔哩的反爬虫系统标记
2. **请求过于频繁**: 最近可能有过多的请求导致临时限制
3. **网络环境问题**: 当前网络环境可能不适合进行爬虫操作
4. **时间段问题**: 当前可能是高峰时段，反爬虫更加严格

#### 🛠️ 解决方案

**立即行动方案**:
1. **🕐 等待冷却** - 停止程序，等待30-60分钟后再试
2. **🌐 更换网络环境** - 使用手机热点、更换WiFi网络、使用VPN
3. **⏰ 选择合适时间** - 避开高峰期（晚上8-11点），推荐深夜或早晨

**配置调整**:
```python
# 进一步增加延迟时间
REQUEST_DELAY_MIN = 30  # 增加到30秒
REQUEST_DELAY_MAX = 60  # 增加到60秒

# 增加预热时间
INITIAL_WARMUP_DELAY = 120  # 增加到2分钟

# 增加错误冷却时间
ERROR_COOLDOWN = 1200  # 增加到20分钟
```

### 常见问题解决

#### Q: 提示"ffmpeg命令未找到"
A: 请安装FFmpeg并添加到系统PATH环境变量
```bash
# Windows下载：https://ffmpeg.org/download.html
# 添加bin目录到系统PATH环境变量

# Linux
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

#### Q: 字符编码问题 (UnicodeDecodeError)
A: 已在最新版本中修复，FFmpeg输出使用UTF-8编码处理

#### Q: 下载失败或被拦截
A: 程序已内置反爬策略，如仍失败可：
- 等待一段时间后重试
- 更换网络环境（如使用手机热点）  
- 选择网络空闲时间段使用

#### Q: 分页功能问题
A: 确保启用分页配置，程序会自动检测并点击"下一页"按钮

#### Q: 用户名获取失败  
A: 程序使用多选择器策略，包括新版页面的`.upinfo-detail__top .nickname`选择器

### FFmpeg相关问题
- **"合并失败"** - 检查FFmpeg版本和视频格式兼容性
- **路径检测失败** - 程序会按优先级搜索多个路径，包括项目本地的`./bin/ffmpeg.exe`

### 存储相关
- **"权限错误"** - 检查输出目录的写入权限
- **"磁盘空间不足"** - 清理磁盘空间或更改输出目录

---

## 💻 技术实现

### 🎭 Playwright优势

**真实浏览器环境**:
- 使用真实的Chromium浏览器，完全模拟人类用户行为
- 支持完整的JavaScript执行和动态内容加载
- 真实的网络指纹和HTTP/2特征
- 自动处理Cookies和会话管理

**智能反反爬**:
- 自动更换User-Agent和请求头
- 动态重建浏览器上下文
- 模拟真实的浏览器会话
- 支持代理和网络配置

### 🔄 分页处理机制

**工作流程**:
```
访问页面 → 收集第1页（滚动） → 点击下一页 → 收集第2页（滚动） → ... → 所有页面完成 → 数量验证
```

**智能停止**: 当收集数量达到期望值时自动停止，避免不必要的等待

### 🎨 封面提取优化

**优先策略**:
1. 检查当前元素是否为 `bili-cover-card__thumbnail`
2. 在子元素中搜索 `bili-cover-card__thumbnail`  
3. 从父元素/兄弟元素获取视频链接和标题
4. 兼容回退：使用通用方法兼容旧版页面

### 🎬 视频下载技术

**DASH流处理**:
- 自动选择最高质量的视频和音频流
- 分段异步下载，提高效率
- FFmpeg无损合并，保证质量

**错误处理**:
- 智能重试机制
- 断点续传支持  
- 完整的日志记录

---

## ⚠️ 使用注意

1. **版权尊重** - 仅用于个人学习研究，请勿商用
2. **网络稳定** - 确保网络连接稳定，避免下载中断
3. **存储空间** - 视频文件较大，确保有足够磁盘空间
4. **下载速度** - 程序内置反爬延迟，下载速度相对较慢
5. **FFmpeg依赖** - 视频下载功能需要安装FFmpeg
6. **合理使用** - 请适度使用，避免对服务器造成过大压力

---

## 🔄 更新记录

### v2.0.0 (完整版) - 2025-09-15
- 🎬 **视频下载功能** - 新增完整的视频下载和FFmpeg合并功能
- 🔧 **字符编码修复** - 解决Windows系统FFmpeg输出的编码问题
- 📁 **FFmpeg路径优化** - 支持项目本地FFmpeg，优先检测`./bin/ffmpeg.exe`
- 📦 **依赖更新** - 新增aiohttp、aiofiles等异步处理库
- 🛠️ **配置完善** - 完善的跨平台FFmpeg配置和错误处理

### v2.0.0 (Playwright版本)
- 🎭 **重大升级**: 集成Playwright浏览器模拟技术
- 🚀 **成功率大幅提高**: 真实浏览器环境，降低被检测风险
- ⚡ **效率大幅提升**: 请求间隔从15-30秒降至3-8秒
- 🔄 **智能上下文更新**: 自动更换浏览器身份
- 🛠️ **一键启动**: 提供自动安装脚本
- 📊 **更温和策略**: 连续请求限制增加到8次
- 📖 **完善文档**: 新增Playwright使用指南

### v1.2.0 (分页支持版)
- 🔄 **分页点击支持** - 自动检测并点击"下一页"按钮
- 📊 **数量校验** - 对比实际收集数量与页面显示总数
- 🎯 **智能停止** - 达到预期数量时自动停止
- 🔍 **用户名选择器更新** - 支持新版页面结构

### v1.1.0 (反反爬优化版)
- 🆕 添加多User-Agent随机轮换
- 🆕 智能随机延迟机制
- 🆕 连续请求限制与长时间休息
- 🆕 反爬检测与自动处理
- 🆕 指数退避重试策略
- 🔧 优化错误处理逻辑

### v1.0.0
- 初始版本发布
- 支持用户视频封面批量下载
- 支持断点续传
- 支持错误重试和失败记录

---

## 📞 技术支持

如遇到问题，请提供：
1. 完整的错误信息截图
2. 使用的命令和参数
3. 目标用户UID
4. 网络环境描述（家庭/公司/移动网络）
5. 使用时间段
6. 系统环境信息

## 💡 使用建议

1. **首次使用** - 建议先用小用户测试，确认程序正常工作
2. **选择合适时间** - 深夜或早晨使用，网络负载小  
3. **分批处理** - 大用户可以分时段处理
4. **保持网络稳定** - 避免在不稳定网络环境下使用
5. **预留足够时间** - 不要在时间紧张时使用
6. **定期更新** - 关注版本更新，获取最新功能和修复

## 📝 免责声明

- 本工具仅用于学习和研究目的
- 请遵守哔哩哔哩的使用条款和robots.txt
- 请勿用于商业用途或侵犯他人权益
- 使用者需自行承担使用风险

## 📄 许可证

MIT License

---

**🎉 享受稳定高效的哔哩哔哩爬虫体验！**

> 文档最后更新：2025-09-15  
> 项目版本：v2.0 完整版  
> 维护状态：积极维护中