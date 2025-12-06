#!/usr/bin/env python3
"""
F12 Key Reminder - 监听F12按键并通过邮件发送提醒
"""

import keyboard
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import time
import sys
import os
from pathlib import Path

# 获取配置文件路径
CONFIG_FILE = Path(__file__).parent / "config.ini"


def load_config():
    """加载配置文件"""
    if not CONFIG_FILE.exists():
        print(f"❌ 配置文件不存在: {CONFIG_FILE}")
        print("请先创建 config.ini 文件，参考 config.ini.example")
        sys.exit(1)
    
    config = {}
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    
    return config


def send_email(config, subject, body):
    """
    发送邮件
    
    Args:
        config: 配置字典
        subject: 邮件主题
        body: 邮件内容
    """
    try:
        # 获取邮件配置
        sender_email = config.get('sender_email')
        sender_password = config.get('sender_password')
        smtp_server = config.get('smtp_server', 'smtp.gmail.com')
        smtp_port = int(config.get('smtp_port', 587))
        receiver_email = config.get('receiver_email')
        
        if not all([sender_email, sender_password, receiver_email]):
            print("❌ 邮件配置不完整，请检查 config.ini 文件")
            return False
        
        # 创建邮件
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = receiver_email
        
        # 创建HTML邮件内容
        html = f"""\
        <html>
            <body>
                <h2>F12 按键提醒</h2>
                <p><strong>时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>信息:</strong></p>
                <p>{body}</p>
                <hr>
                <p><small>这是一封自动生成的邮件。</small></p>
            </body>
        </html>
        """
        
        part = MIMEText(html, "html")
        message.attach(part)
        
        # 发送邮件
        print(f"📧 正在发送邮件到 {receiver_email}...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        
        print("✅ 邮件发送成功!")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ 邮件认证失败，请检查发送者邮箱和密码")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP 错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 发送邮件失败: {e}")
        return False


def on_f12_pressed():
    """F12按键回调函数"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n🔔 [F12 按键触发] {timestamp}")
    
    config = load_config()
    subject = "F12 按键提醒"
    body = f"您的电脑在 {timestamp} 按下了 F12 按键。\n请检查您的操作。"
    
    send_email(config, subject, body)


def main():
    """主函数"""
    print("=" * 50)
    print("F12 按键提醒系统")
    print("=" * 50)
    print("正在监听 F12 按键...")
    print("按 Ctrl+C 停止监听\n")
    
    try:
        # 注册F12按键事件
        keyboard.on_press_key('f12', lambda _: on_f12_pressed())
        
        # 保持程序运行
        while True:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\n👋 程序已停止")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
