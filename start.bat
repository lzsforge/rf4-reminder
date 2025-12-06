@echo off
REM F12 按键提醒启动脚本（Windows）
setlocal enabledelayedexpansion

cd /d "%~dp0"

REM 配置检查
if not exist "config.ini" (
    echo ❌ 配置文件不存在！
    echo 请先创建 config.ini（可从 config.ini.example 复制）
    pause
    exit /b 1
)

REM 依赖检查
python -c "import importlib.util,sys;sys.exit(0 if importlib.util.find_spec('keyboard') else 1)" 2>nul
if errorlevel 1 (
    echo 📦 正在安装依赖...
    pip install -r requirements.txt
)

echo 🚀 启动 F12 按键提醒...
python f12_email_reminder.py

pause
