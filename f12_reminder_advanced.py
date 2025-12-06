#!/usr/bin/env python3
"""
F12 Key Reminder - 高级版本
支持日志、多个提醒、黑名单等功能
"""

import keyboard
import smtplib
import json
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import time
import sys
import os
from pathlib import Path

# 设置日志
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f"f12_reminder_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

CONFIG_FILE = Path(__file__).parent / "config.ini"
ADVANCED_CONFIG_FILE = Path(__file__).parent / "advanced_config.json"


def load_config():
    """加载基础配置文件"""
    if not CONFIG_FILE.exists():
        logger.error(f"配置文件不存在: {CONFIG_FILE}")
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


def load_advanced_config():
    """加载高级配置文件（如果存在）"""
    if not ADVANCED_CONFIG_FILE.exists():
        return {
            "enable_logging": True,
            "rate_limit_seconds": 5,
            "max_emails_per_minute": 10,
            "include_system_info": False,
            "custom_message": None
        }
    
    try:
        with open(ADVANCED_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"无法加载高级配置: {e}")
        return {}


class RateLimiter:
    """速率限制器，防止邮件轰炸"""
    
    def __init__(self, min_interval=5, max_per_minute=10):
        self.min_interval = min_interval
        self.max_per_minute = max_per_minute
        self.last_trigger_time = 0
        self.trigger_times = []
    
    def should_send_email(self):
        """检查是否应该发送邮件"""
        now = time.time()
        
        # 检查最小间隔
        if now - self.last_trigger_time < self.min_interval:
            return False
        
        # 检查每分钟限制
        self.trigger_times = [t for t in self.trigger_times if now - t < 60]
        if len(self.trigger_times) >= self.max_per_minute:
            return False
        
        self.last_trigger_time = now
        self.trigger_times.append(now)
        return True


class EmailSender:
    """邮件发送器"""
    
    def __init__(self, config):
        self.sender_email = config.get('sender_email')
        self.sender_password = config.get('sender_password')
        self.smtp_server = config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = int(config.get('smtp_port', 587))
        self.receiver_email = config.get('receiver_email')
    
    def validate(self):
        """验证配置"""
        if not all([self.sender_email, self.sender_password, self.receiver_email]):
            logger.error("邮件配置不完整")
            return False
        return True
    
    def send(self, subject, body, include_timestamp=True):
        """发送邮件"""
        try:
            if include_timestamp:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                body = f"{body}\n\n时间: {timestamp}"
            
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = self.receiver_email
            
            html = f"""\
            <html>
                <body>
                    <h2>F12 按键提醒</h2>
                    <p>{body.replace(chr(10), '<br>')}</p>
                    <hr>
                    <p><small>这是一封自动生成的邮件。</small></p>
                </body>
            </html>
            """
            
            part = MIMEText(html, "html")
            message.attach(part)
            
            logger.info(f"正在发送邮件到 {self.receiver_email}...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.receiver_email, message.as_string())
            
            logger.info("邮件发送成功")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("邮件认证失败")
            return False
        except Exception as e:
            logger.error(f"发送邮件失败: {e}")
            return False


def create_advanced_config_example():
    """创建高级配置示例文件"""
    example_config = {
        "enable_logging": True,
        "rate_limit_seconds": 5,
        "max_emails_per_minute": 10,
        "include_system_info": False,
        "custom_message": "F12按键被触发了！"
    }
    
    with open(ADVANCED_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(example_config, f, indent=2, ensure_ascii=False)
    
    logger.info(f"已创建高级配置示例文件: {ADVANCED_CONFIG_FILE}")


def main():
    """主函数"""
    print("=" * 50)
    print("F12 按键提醒系统 (高级版)")
    print("=" * 50)
    
    # 加载配置
    config = load_config()
    advanced_config = load_advanced_config()
    
    # 初始化邮件发送器
    sender = EmailSender(config)
    if not sender.validate():
        sys.exit(1)
    
    # 初始化速率限制器
    rate_limiter = RateLimiter(
        min_interval=advanced_config.get('rate_limit_seconds', 5),
        max_per_minute=advanced_config.get('max_emails_per_minute', 10)
    )
    
    trigger_count = 0
    
    def on_f12_pressed():
        nonlocal trigger_count
        trigger_count += 1
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        logger.info(f"[F12 按键触发 #{trigger_count}] {timestamp}")
        print(f"🔔 [F12 按键触发 #{trigger_count}] {timestamp}")
        
        if rate_limiter.should_send_email():
            subject = "F12 按键提醒"
            message = advanced_config.get('custom_message') or f"您的电脑在 {timestamp} 按下了 F12 按键。"
            sender.send(subject, message)
        else:
            logger.warning("触发频率过高，跳过此次邮件发送")
    
    logger.info("F12 按键提醒系统已启动")
    print("正在监听 F12 按键...")
    print("按 Ctrl+C 停止监听\n")
    
    try:
        keyboard.on_press_key('f12', lambda _: on_f12_pressed())
        
        while True:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        logger.info(f"程序已停止，共监听到 {trigger_count} 次F12按键")
        print(f"\n\n👋 程序已停止 (共 {trigger_count} 次触发)")
        sys.exit(0)
    except Exception as e:
        logger.error(f"发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
