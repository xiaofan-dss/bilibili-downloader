#!/bin/bash

echo "🎭 哔哩哔哩封面爬虫 - Playwright版本启动器"
echo "================================================"
echo ""

# 检查python10是否存在
if ! command -v python10 &> /dev/null; then
    echo "❌ 未找到python10命令"
    echo "💡 请确保Python已正确安装并添加到PATH"
    echo "💡 或者尝试使用: python3 bilibili_cover_crawler_playwright.py"
    exit 1
fi

# 检查Playwright是否已安装
if ! python10 -c "import playwright" &> /dev/null; then
    echo "❌ 未检测到Playwright"
    echo "📦 正在安装依赖包..."
    python10 -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
    
    echo "🌐 正在安装Playwright浏览器..."
    python10 -m playwright install chromium
    if [ $? -ne 0 ]; then
        echo "❌ 浏览器安装失败"
        exit 1
    fi
fi

echo "✅ 环境检查完成，启动爬虫程序..."
echo "🌐 此版本直接从用户空间页面获取视频信息，更加稳定！"
echo ""

# 启动Playwright版本的爬虫
if [ $# -eq 0 ]; then
    python10 bilibili_cover_crawler_playwright.py
else
    python10 bilibili_cover_crawler_playwright.py $1
fi