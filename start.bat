@echo off
REM F12 按键提醒系统启动脚本（Windows）

setlocal enabledelayedexpansion

REM 获取脚本目录
cd /d "%~dp0"

REM 检查配置文件
if not exist "config.ini" (
    echo ❌ 配置文件不存在！
    echo 请先创建 config.ini 文件：
    echo   copy config.ini.example config.ini
    echo   notepad config.ini
    pause
    exit /b 1
)

REM 检查依赖
python -c "import keyboard" 2>nul
if errorlevel 1 (
    echo 📦 正在安装依赖...
    pip install -r requirements.txt
)

REM 启动程序
echo 🚀 启动 F12 按键提醒系统...
echo.

REM 检查是否是高级版本
if "%1"=="advanced" (
    python f12_reminder_advanced.py
) else (
    python f12_reminder.py
)

pause
