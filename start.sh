#!/bin/bash

# F12 按键提醒系统启动脚本

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查配置文件
if [ ! -f "config.ini" ]; then
    echo "❌ 配置文件不存在！"
    echo "请先创建 config.ini 文件："
    echo "  cp config.ini.example config.ini"
    echo "  nano config.ini"
    exit 1
fi

# 检查依赖
if ! python3 -c "import keyboard" 2>/dev/null; then
    echo "📦 正在安装依赖..."
    pip install -r requirements.txt
fi

# 启动程序
echo "🚀 启动 F12 按键提醒系统..."
echo ""

# 检查是否是高级版本
if [ "$1" == "advanced" ]; then
    python3 f12_reminder_advanced.py
else
    python3 f12_reminder.py
fi
