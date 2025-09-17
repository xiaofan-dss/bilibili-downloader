# -*- coding: utf-8 -*-
"""
哔哩哔哩用户视频封面爬虫
功能：获取指定用户的所有视频封面，按照BV号和标题保存到以用户ID和用户名命名的文件夹中
"""

import os
import re
import time
import json
import random
import requests
from urllib.parse import urlparse
from pathlib import Path
from tqdm import tqdm
import config


class BilibiliCoverCrawler:
    """哔哩哔哩封面爬虫类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.request_count = 0  # 请求计数器
        self.last_request_time = 0  # 上次请求时间
        self.failure_count = 0  # 连续失败计数
        self.last_error_time = 0  # 上次错误时间
        self.is_first_request = True  # 是否是首次请求
        self.update_headers()
        print(f"\n🌡️ 初始化爬虫(极限保守模式)，预热等待 {config.INITIAL_WARMUP_DELAY} 秒...")
        with tqdm(total=config.INITIAL_WARMUP_DELAY, desc="预热中", unit="s") as pbar:
            for i in range(config.INITIAL_WARMUP_DELAY):
                time.sleep(1)
                pbar.update(1)
        
    def update_headers(self):
        """更新请求头，随机选择User-Agent和匹配的请求头模板"""
        # 随机选择User-Agent
        user_agent = random.choice(config.USER_AGENTS)
        
        # 根据User-Agent类型选择相应的请求头模板
        if 'Chrome' in user_agent and 'Edg' not in user_agent:
            headers_template = config.BASE_HEADERS_TEMPLATES[0]  # Chrome
        elif 'Firefox' in user_agent:
            headers_template = config.BASE_HEADERS_TEMPLATES[1]  # Firefox
        elif 'Safari' in user_agent and 'Chrome' not in user_agent:
            headers_template = config.BASE_HEADERS_TEMPLATES[2]  # Safari
        else:
            headers_template = config.BASE_HEADERS_TEMPLATES[0]  # 默认Chrome
        
        # 构建完整的请求头
        headers = headers_template.copy()
        headers['User-Agent'] = user_agent
        headers['Referer'] = 'https://www.bilibili.com/'
        
        # 随机添加一些可选头
        if random.random() < 0.5:
            headers['Cache-Control'] = random.choice(['no-cache', 'max-age=0', 'no-store'])
        if random.random() < 0.3:
            headers['Pragma'] = 'no-cache'
        if random.random() < 0.4:
            headers['DNT'] = '1'
        
        self.session.headers.update(headers)
        print(f"🔄 更新请求头: {user_agent[:50]}...")
    
    def smart_delay(self, is_api_request=False):
        """智能延迟机制"""
        # 首次请求的额外延迟
        if self.is_first_request:
            print(f"\n🔥 首次请求，额外等待 {config.FIRST_REQUEST_DELAY} 秒...")
            time.sleep(config.FIRST_REQUEST_DELAY)
            self.is_first_request = False
        
        # 检查是否需要长时间休息
        if self.request_count > 0 and self.request_count % config.MAX_CONSECUTIVE_REQUESTS == 0:
            print(f"\n💤 已连续请求 {config.MAX_CONSECUTIVE_REQUESTS} 次，休息 {config.LONG_BREAK_DURATION} 秒...")
            with tqdm(total=config.LONG_BREAK_DURATION, desc="休息中", unit="s") as pbar:
                for i in range(config.LONG_BREAK_DURATION):
                    time.sleep(1)
                    pbar.update(1)
            self.update_headers()  # 更新请求头
            self.failure_count = 0  # 重置失败计数
        
        # 如果最近有错误，增加额外延迟
        if self.last_error_time > 0:
            time_since_error = time.time() - self.last_error_time
            if time_since_error < config.REQUEST_FAILURE_PENALTY:
                remaining_penalty = config.REQUEST_FAILURE_PENALTY - time_since_error
                if remaining_penalty > 0:
                    print(f"⚠️ 距离上次错误太近，额外等待 {remaining_penalty:.1f} 秒...")
                    time.sleep(remaining_penalty)
        
        # 计算基础延迟时间
        if is_api_request:
            base_delay = random.uniform(config.REQUEST_DELAY_MIN, config.REQUEST_DELAY_MAX)
        else:
            base_delay = random.uniform(config.DOWNLOAD_DELAY_MIN, config.DOWNLOAD_DELAY_MAX)
        
        # 根据失败次数增加延迟
        if self.failure_count > 0:
            penalty_multiplier = 1 + (self.failure_count * 0.8)  # 增加惩罚倍数
            base_delay *= penalty_multiplier
            print(f"😨 由于失败次数 ({self.failure_count})，延迟增加到 {base_delay:.1f} 秒")
        
        # 确保与上次请求的间隔
        elapsed = time.time() - self.last_request_time
        if elapsed < base_delay:
            actual_wait = base_delay - elapsed
            print(f"⏳ 等待 {actual_wait:.1f} 秒...")
            time.sleep(actual_wait)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def handle_request_error(self, error, attempt):
        """处理请求错误"""
        error_str = str(error)
        self.failure_count += 1
        self.last_error_time = time.time()
        
        # 检测各种反爬错误
        anti_crawl_keywords = [
            "请求过于频繁", "429", "Too Many Requests", 
            "rate limit", "Rate Limited", "访问频繁",
            "Too fast", "slow down", "限制"
        ]
        
        is_anti_crawl = any(keyword in error_str for keyword in anti_crawl_keywords)
        
        if is_anti_crawl:
            # 逐渐增加冷却时间
            cooldown = config.ERROR_COOLDOWN * (attempt + 1) * (1 + self.failure_count * 0.5)
            print(f"\n⚠️ 检测到反爬措施: {error_str}")
            print(f"🧊 冷却 {cooldown:.0f} 秒 (第{attempt+1}次重试，连续失败{self.failure_count}次)...")
            
            # 进度条显示冷却进度
            with tqdm(total=int(cooldown), desc="冷却中", unit="s") as pbar:
                for i in range(int(cooldown)):
                    time.sleep(1)
                    pbar.update(1)
            
            self.update_headers()  # 更新请求头
            
            # 如果失败次数过多，增加额外延迟
            if self.failure_count >= 3:
                extra_delay = 60 * self.failure_count
                print(f"失败次数过多，额外等待 {extra_delay} 秒...")
                time.sleep(extra_delay)
            
            return True
        
        return False
        
    def sanitize_filename(self, filename):
        """清理文件名，移除不允许的字符"""
        # 移除Windows不允许的字符
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # 移除控制字符
        filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
        # 限制长度
        if len(filename) > config.MAX_FILENAME_LENGTH:
            filename = filename[:config.MAX_FILENAME_LENGTH]
        return filename.strip()
    
    def get_user_info(self, uid):
        """获取用户信息"""
        for attempt in range(config.MAX_RETRIES):
            try:
                self.smart_delay(is_api_request=True)
                
                params = {
                    'mid': uid,
                    'jsonp': 'jsonp'
                }
                
                response = self.session.get(
                    config.USER_INFO_API, 
                    params=params, 
                    timeout=config.DOWNLOAD_TIMEOUT
                )
                response.raise_for_status()
                
                data = response.json()
                if data.get('code') == 0:
                    user_data = data.get('data', {})
                    self.failure_count = 0  # 成功后重置失败计数
                    return {
                        'name': user_data.get('name', f'用户_{uid}'),
                        'uid': uid
                    }
                else:
                    print(f"获取用户信息失败: {data.get('message', '未知错误')}")
                    return None
                    
            except Exception as e:
                if self.handle_request_error(e, attempt):
                    continue
                if attempt < config.MAX_RETRIES - 1:
                    delay = config.RETRY_DELAY * (config.RETRY_BACKOFF ** attempt)
                    print(f"获取用户信息失败，{delay}秒后重试: {e}")
                    time.sleep(delay)
                else:
                    print(f"获取用户信息时发生错误: {e}")
                    return None
    
    def get_user_videos(self, uid):
        """获取用户所有视频信息"""
        videos = []
        page = 1
        
        print(f"开始获取用户 {uid} 的视频列表...")
        
        while True:
            success = False
            for attempt in range(config.MAX_RETRIES):
                try:
                    self.smart_delay(is_api_request=True)
                    
                    params = {
                        'mid': uid,
                        'ps': config.PAGE_SIZE,
                        'pn': page,
                        'order': 'pubdate',
                        'jsonp': 'jsonp'
                    }
                    
                    response = self.session.get(
                        config.USER_SPACE_API, 
                        params=params, 
                        timeout=config.DOWNLOAD_TIMEOUT
                    )
                    response.raise_for_status()
                    
                    data = response.json()
                    if data.get('code') != 0:
                        error_msg = data.get('message', '未知错误')
                        if "请求过于频繁" in error_msg or "429" in error_msg:
                            if self.handle_request_error(error_msg, attempt):
                                continue
                        print(f"API错误: {error_msg}")
                        return videos
                    
                    page_data = data.get('data', {})
                    page_list = page_data.get('list', {})
                    vlist = page_list.get('vlist', [])
                    
                    if not vlist:
                        success = True
                        break
                    
                    # 成功获取数据后重置失败计数
                    if self.failure_count > 0:
                        print(f"成功获取数据，重置失败计数 ({self.failure_count} -> 0)")
                        self.failure_count = 0
                    
                    for video in vlist:
                        video_info = {
                            'bvid': video.get('bvid', ''),
                            'title': video.get('title', ''),
                            'pic': video.get('pic', ''),
                            'created': video.get('created', 0)
                        }
                        videos.append(video_info)
                    
                    print(f"已获取第 {page} 页，共 {len(vlist)} 个视频")
                    
                    # 检查是否还有更多页
                    page_info = page_list.get('page', {})
                    if page * config.PAGE_SIZE >= page_info.get('count', 0):
                        success = True
                        break
                        
                    page += 1
                    success = True
                    break
                    
                except Exception as e:
                    if self.handle_request_error(e, attempt):
                        continue
                    if attempt < config.MAX_RETRIES - 1:
                        delay = config.RETRY_DELAY * (config.RETRY_BACKOFF ** attempt)
                        print(f"获取第 {page} 页视频列表失败，{delay}秒后重试: {e}")
                        time.sleep(delay)
                    else:
                        print(f"获取第 {page} 页视频列表时发生错误: {e}")
                        return videos
            
            if not success:
                print(f"获取第 {page} 页失败，停止爬取")
                break
        
        print(f"总共获取到 {len(videos)} 个视频")
        return videos
    
    def download_cover(self, pic_url, save_path):
        """下载单个封面图片"""
        for attempt in range(config.MAX_RETRIES):
            try:
                self.smart_delay(is_api_request=False)
                
                # 确保URL是完整的
                if pic_url.startswith('//'):
                    pic_url = 'https:' + pic_url
                elif pic_url.startswith('/'):
                    pic_url = 'https://i0.hdslb.com' + pic_url
                
                response = self.session.get(
                    pic_url, 
                    timeout=config.DOWNLOAD_TIMEOUT,
                    stream=True
                )
                response.raise_for_status()
                
                # 创建目录
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                
                # 保存文件
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                # 成功下载后重置失败计数
                if self.failure_count > 0:
                    self.failure_count = max(0, self.failure_count - 1)
                
                return True
                
            except Exception as e:
                if self.handle_request_error(e, attempt):
                    continue
                if attempt < config.MAX_RETRIES - 1:
                    delay = config.RETRY_DELAY * (config.RETRY_BACKOFF ** attempt)
                    print(f"下载失败，{delay}秒后第 {attempt + 2} 次重试: {e}")
                    time.sleep(delay)
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
    
    def crawl_user_covers(self, uid):
        """爬取指定用户的所有视频封面"""
        # 获取用户信息
        user_info = self.get_user_info(uid)
        if not user_info:
            print(f"无法获取用户 {uid} 的信息")
            return False
        
        user_name = user_info['name']
        print(f"用户: {user_name} (UID: {uid})")
        
        # 获取用户所有视频
        videos = self.get_user_videos(uid)
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
                if self.download_cover(pic_url, save_path):
                    success_count += 1
                    pbar.set_postfix({"成功": success_count, "失败": len(failed_videos)})
                else:
                    failed_videos.append(video)
                
                pbar.update(1)
                # 智能延迟已在download_cover中处理
        
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


def main():
    """主函数"""
    print("🧑‍💻 哔哩哔哩用户视频封面爬虫 (极限保守模式)")
    print("=" * 55)
    print("\n⚠️  重要提示:")
    print("- 🐌 该程序采用极限保守模式，请求间隔非常长")
    print("- ⏰ API请求间隔: 15-30秒，图片下载间隔: 5-12秒")
    print("- 💤 每3次请求后休息5分钟，遇错冷却10分钟")
    print("- 🔥 启动预热1分钟，首次请求额外等待30秒")
    print("- 🌙 强烈建议在深夜或早晨等网络空闲时间段使用")
    print("\n📋 时间预估:")
    print("- 🐣 小用户(50个视频): 约1-2小时")
    print("- 🐧 中等用户(200个视频): 约6-8小时")
    print("- 🐋 大用户(1000个视频): 约30+小时")
    print("\n🔍 如果程序仍然失败，可能需要:")
    print("- ☕ 等待30分钟后再试")
    print("- 🌐 更换网络环境(如使用手机热点)")
    print("- 🕰️ 选择不同的时间段试试\n")
    
    import sys
    # 支持命令行参数
    if len(sys.argv) > 1:
        try:
            uid = int(sys.argv[1])
        except ValueError:
            print("🙅 错误: 无效的UID参数")
            return
    else:
        # 获取用户输入
        while True:
            uid_input = input("🎯 请输入要爬取的用户UID (或者输入 'q' 退出): ").strip()
            if uid_input.lower() == 'q':
                print("🙋‍♂️ 用户取消操作")
                return
            if uid_input.isdigit():
                uid = int(uid_input)
                break
            else:
                print("🙅 请输入有效的数字UID")
    
    # 确认继续
    confirm = input(f"\n🚀 即将开始爬取用户 {uid} 的视频封面，这可能需要非常长的时间，继续吗? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes', '是']:
        print("🙋‍♂️ 用户取消操作")
        return
    
    # 创建爬虫实例并开始爬取
    crawler = BilibiliCoverCrawler()
    
    try:
        success = crawler.crawl_user_covers(uid)
        if success:
            print("\n🎉 爬取完成！")
        else:
            print("\n😔 爬取失败！")
            print("\n💡 建议:")
            print("1. 等待30-60分钟后再试")
            print("2. 更换网络环境(如使用手机热点)")
            print("3. 选择不同的时间段(如深夜或早晨)")
            print("4. 检查网络连接是否稳定")
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断了程序")
        print("💾 已下载的文件将保留，下次运行时会自动跳过")
    except Exception as e:
        print(f"\n😱 程序执行出错: {e}")
        print("\n🛠️ 故障排除:")
        print("1. 检查网络连接")
        print("2. 检查UID是否正确")
        print("3. 检查是否有足够的磁盘空间")
        print("4. 联系技术支持")


if __name__ == "__main__":
    main()