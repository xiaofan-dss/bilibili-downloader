# -*- coding: utf-8 -*-
"""
FFmpeg 检测和安装助手
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def check_ffmpeg():
    """检查FFmpeg是否已安装 - 使用配置文件的路径"""
    print("🔍 检查FFmpeg安装状态...")
    
    # 导入配置
    try:
        import config
        ffmpeg_config = config.FFMPEG_CONFIG
    except ImportError:
        print("⚠️  无法加载配置文件，使用默认检测")
        ffmpeg_config = {}
    
    # 1. 检查配置中的自定义路径
    custom_path = ffmpeg_config.get('custom_path', '')
    if custom_path:
        print(f"🔍 检查自定义路径: {custom_path}")
        if Path(custom_path).exists():
            print(f"✅ 自定义路径中找到FFmpeg: {custom_path}")
            return custom_path
        else:
            print(f"❌ 自定义路径不存在: {custom_path}")
    
    # 2. 检查PATH中的ffmpeg
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        print(f"✅ 在PATH中找到FFmpeg: {ffmpeg_path}")
        return ffmpeg_path
    
    # 3. 根据平台检查常见路径
    import platform
    system = platform.system().lower()
    
    if system == 'windows':
        search_paths = ffmpeg_config.get('search_paths', {}).get('windows', [
            'ffmpeg.exe',
            r'C:\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files\ffmpeg\bin\ffmpeg.exe', 
            r'C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe'
        ])
    elif system == 'linux':
        search_paths = ffmpeg_config.get('search_paths', {}).get('linux', [
            '/usr/bin/ffmpeg',
            '/usr/local/bin/ffmpeg',
            '/opt/ffmpeg/bin/ffmpeg'
        ])
    elif system == 'darwin':
        search_paths = ffmpeg_config.get('search_paths', {}).get('darwin', [
            '/usr/local/bin/ffmpeg',
            '/opt/homebrew/bin/ffmpeg'
        ])
    else:
        search_paths = ['ffmpeg', './ffmpeg']
    
    print(f"🔍 检查常见安装路径...")
    for path in search_paths:
        if Path(path).exists():
            print(f"✅ 在本地路径找到FFmpeg: {path}")
            return path
    
    print("❌ 未找到FFmpeg")
    return None

def test_ffmpeg(ffmpeg_path):
    """测试FFmpeg是否正常工作"""
    try:
        print(f"🧪 测试FFmpeg功能: {ffmpeg_path}")
        result = subprocess.run([ffmpeg_path, '-version'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            # 提取版本信息
            version_line = result.stdout.split('\n')[0]
            print(f"✅ FFmpeg工作正常: {version_line}")
            return True
        else:
            print(f"❌ FFmpeg测试失败: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ FFmpeg测试超时")
        return False
    except Exception as e:
        print(f"❌ FFmpeg测试异常: {e}")
        return False

def show_installation_guide():
    """显示FFmpeg安装指南"""
    print("\n" + "="*60)
    print("📥 FFmpeg 安装指南")
    print("="*60)
    
    print("\n🪟 Windows 安装方法:")
    print("方法1: 手动安装")
    print("  1. 访问 https://ffmpeg.org/download.html")
    print("  2. 下载 Windows 版本 (选择 'Windows builds by BtbN')")
    print("  3. 解压到 C:\\ffmpeg")
    print("  4. 将 C:\\ffmpeg\\bin 添加到系统 PATH 环境变量")
    print("  5. 重启命令行")
    
    print("\n方法2: 使用包管理器")
    print("  Chocolatey: choco install ffmpeg")
    print("  Scoop: scoop install ffmpeg")
    print("  winget: winget install ffmpeg")
    
    print("\n🐧 Linux 安装方法:")
    print("  Ubuntu/Debian: sudo apt install ffmpeg")
    print("  CentOS/RHEL: sudo yum install ffmpeg")
    print("  Arch: sudo pacman -S ffmpeg")
    
    print("\n🍎 macOS 安装方法:")
    print("  Homebrew: brew install ffmpeg")
    print("  MacPorts: sudo port install ffmpeg")
    
    print("\n⚠️  重要提示:")
    print("  - 安装后需要重新启动命令行")
    print("  - 确保FFmpeg在系统PATH中")
    print("  - 可以运行 'ffmpeg -version' 验证安装")

def check_system_requirements():
    """检查系统要求"""
    print("\n🖥️  系统信息:")
    print(f"  操作系统: {sys.platform}")
    print(f"  Python版本: {sys.version.split()[0]}")
    
    # 检查磁盘空间
    try:
        import shutil
        total, used, free = shutil.disk_usage('.')
        free_gb = free // (1024**3)
        print(f"  可用磁盘空间: {free_gb} GB")
        
        if free_gb < 5:
            print("  ⚠️  磁盘空间不足，建议至少保留5GB空间用于视频下载")
    except:
        pass

def main():
    """主函数"""
    print("🎬 哔哩哔哩视频下载器 - FFmpeg 检测工具")
    print("="*60)
    
    # 检查系统要求
    check_system_requirements()
    
    # 检查FFmpeg
    ffmpeg_path = check_ffmpeg()
    
    if ffmpeg_path:
        # 测试FFmpeg
        if test_ffmpeg(ffmpeg_path):
            print("\n🎉 FFmpeg已正确安装并可正常工作！")
            print("✅ 您可以正常使用视频下载功能")
            
            print(f"\n💡 使用方法:")
            print("  python bilibili_cover_crawler_playwright.py 123456 --download-videos")
        else:
            print("\n⚠️  FFmpeg安装存在问题")
            show_installation_guide()
    else:
        print("\n❌ 未检测到FFmpeg安装")
        show_installation_guide()
        
        print(f"\n🔄 安装完成后，请重新运行此脚本验证:")
        print(f"  python {__file__}")

if __name__ == "__main__":
    main()