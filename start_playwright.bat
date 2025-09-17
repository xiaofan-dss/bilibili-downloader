@echo off
chcp 65001 >nul
echo 🎭 哔哩哔哩封面爬虫 - Playwright版本启动器
echo ================================================
echo.

REM 检查python10是否存在
python10 --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到python10命令
    echo 💡 请确保Python已正确安装并添加到PATH
    echo 💡 或者尝试使用: python bilibili_cover_crawler_playwright.py
    pause
    exit /b 1
)

REM 检查Playwright是否已安装
python10 -c "import playwright" >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到Playwright
    echo 📦 正在安装依赖包...
    python10 -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
    
    echo 🌐 正在安装Playwright浏览器...
    python10 -m playwright install chromium
    if errorlevel 1 (
        echo ❌ 浏览器安装失败
        pause
        exit /b 1
    )
)

echo ✅ 环境检查完成，启动爬虫程序...
echo 🌐 此版本直接从用户空间页面获取视频信息，更加稳定！
echo 🎯 支持滚动加载，可获取用户所有视频封面！
echo 🎨 优先使用 bili-cover-card__thumbnail 获取封面！
echo.

REM 启动Playwright版本的爬虫
if "%~1"=="" (
    python10 bilibili_cover_crawler_playwright.py
) else (
    python10 bilibili_cover_crawler_playwright.py %1
)

pause