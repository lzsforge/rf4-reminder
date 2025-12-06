#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI-based F12 email reminder.

Listens for F12 key presses (physical or programmatic) and sends email notifications.
Includes a Tkinter control panel to configure SMTP settings, rate limiting, logging,
and quick actions (start/stop/test/simulate).
"""

import configparser
import json
import logging
from logging.handlers import RotatingFileHandler
import queue
import smtplib
import threading
import time
from datetime import datetime
from pathlib import Path
import platform
import socket

import keyboard
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Paths and defaults
BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.ini"
ADVANCED_CONFIG_PATH = BASE_DIR / "advanced_config.json"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

DEFAULT_MAIL_CONFIG = {
    "sender_email": "",
    "sender_password": "",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": "587",
    "receiver_email": "",
}

DEFAULT_ADVANCED_CONFIG = {
    "subject": "F12 按键提醒",
    "custom_message": "您的电脑在 {timestamp} 触发了 F12 按键（来源：{source}）。",
    "rate_limit_seconds": 5,
    "max_emails_per_minute": 10,
    "include_system_info": False,
    "play_sound": False,
    "log_to_file": True,
}


class RateLimiter:
    """Simple rate limiter to avoid spamming emails."""

    def __init__(self, min_interval=5, max_per_minute=10):
        self.min_interval = min_interval
        self.max_per_minute = max_per_minute
        self.events = []
        self.lock = threading.Lock()

    def allow(self) -> bool:
        now = time.time()
        with self.lock:
            self.events = [t for t in self.events if now - t < 60]
            if self.events and now - self.events[-1] < self.min_interval:
                return False
            if len(self.events) >= self.max_per_minute:
                return False
            self.events.append(now)
            return True


class EmailSender:
    """SMTP email sender."""

    def __init__(self, mail_config: dict, advanced_config: dict, logger: logging.Logger):
        self.mail_config = mail_config
        self.advanced_config = advanced_config
        self.logger = logger

    def _build_body(self, timestamp: str, source: str, extra: str = "") -> str:
        template = self.advanced_config.get("custom_message") or DEFAULT_ADVANCED_CONFIG["custom_message"]
        body = template.format(timestamp=timestamp, source=source)
        if extra:
            body += f"\n\n{extra}"
        return body

    def _build_system_info(self) -> str:
        info_lines = [
            f"系统: {platform.system()} {platform.release()} ({platform.version()})",
            f"主机名: {socket.gethostname()}",
            f"用户: {self._safe_username()}",
        ]
        return "\n".join(info_lines)

    @staticmethod
    def _safe_username() -> str:
        try:
            import getpass

            return getpass.getuser()
        except Exception:
            return "未知"

    def send_email(self, timestamp: str, source: str) -> bool:
        sender_email = self.mail_config.get("sender_email", "")
        sender_password = self.mail_config.get("sender_password", "")
        receiver_email = self.mail_config.get("receiver_email", "")
        smtp_server = self.mail_config.get("smtp_server", "smtp.gmail.com")
        smtp_port = int(self.mail_config.get("smtp_port", "587") or 587)

        if not all([sender_email, sender_password, receiver_email]):
            self.logger.error("邮件配置不完整，无法发送。")
            return False

        subject = self.advanced_config.get("subject") or DEFAULT_ADVANCED_CONFIG["subject"]
        extra = self._build_system_info() if self.advanced_config.get("include_system_info") else ""
        body = self._build_body(timestamp, source, extra)

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = receiver_email

        html = f"""
        <html>
            <body>
                <h2>{subject}</h2>
                <p>{body.replace(chr(10), '<br>')}</p>
                <p><small>时间: {timestamp}</small></p>
            </body>
        </html>
        """
        message.attach(MIMEText(html, "html"))

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, message.as_string())
            self.logger.info("邮件发送成功 -> %s", receiver_email)
            return True
        except smtplib.SMTPAuthenticationError:
            self.logger.error("SMTP 认证失败，请检查账号或授权码。")
        except Exception as exc:
            self.logger.error("发送邮件失败: %s", exc)
        return False


class QueueHandler(logging.Handler):
    """Logging handler that writes messages into a queue for the UI."""

    def __init__(self, log_queue: queue.Queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        self.log_queue.put(msg)


class F12ReminderApp(tk.Tk):
    """Main Tkinter application."""

    def __init__(self):
        super().__init__()
        self.title("F12 邮件提醒")
        self.geometry("950x650")

        self.mail_config = self.load_mail_config()
        self.advanced_config = self.load_advanced_config()
        self.rate_limiter = RateLimiter(
            self.advanced_config.get("rate_limit_seconds", 5),
            self.advanced_config.get("max_emails_per_minute", 10),
        )

        self.log_queue: queue.Queue = queue.Queue()
        self.logger = self._setup_logging()
        self.email_sender = EmailSender(self.mail_config, self.advanced_config, self.logger)
        self.listener_handle = None
        self.trigger_count = 0
        self.last_trigger = "-"
        self.last_email = "-"

        self._build_ui()
        self.after(200, self._poll_log_queue)

    # ----------------- Config -----------------
    def load_mail_config(self) -> dict:
        config = DEFAULT_MAIL_CONFIG.copy()
        if not CONFIG_PATH.exists():
            return config
        parser = configparser.ConfigParser()
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        if "[mail]" not in content.lower():
            # backward compatible simple key=value file
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    if key in config:
                        config[key] = value.strip()
            return config
        parser.read_string(content)
        if parser.has_section("mail"):
            for key in config:
                if parser.has_option("mail", key):
                    config[key] = parser.get("mail", key)
        return config

    def save_mail_config(self):
        lines = [f"{key}={self.mail_config.get(key, '')}" for key in DEFAULT_MAIL_CONFIG]
        CONFIG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.logger.info("邮件配置已保存到 %s", CONFIG_PATH)

    def load_advanced_config(self) -> dict:
        config = DEFAULT_ADVANCED_CONFIG.copy()
        if ADVANCED_CONFIG_PATH.exists():
            try:
                loaded = json.loads(ADVANCED_CONFIG_PATH.read_text(encoding="utf-8"))
                config.update(loaded)
            except Exception as exc:
                print(f"无法读取高级配置，已使用默认值: {exc}")
        return config

    def save_advanced_config(self):
        ADVANCED_CONFIG_PATH.write_text(
            json.dumps(self.advanced_config, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self.logger.info("高级配置已保存到 %s", ADVANCED_CONFIG_PATH)

    # ----------------- Logging -----------------
    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger("f12_reminder")
        logger.setLevel(logging.INFO)
        logger.handlers.clear()

        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        queue_handler = QueueHandler(self.log_queue)
        queue_handler.setFormatter(formatter)
        logger.addHandler(queue_handler)

        if self.advanced_config.get("log_to_file", True):
            file_handler = RotatingFileHandler(
                LOG_DIR / "f12_reminder.log", maxBytes=500_000, backupCount=3, encoding="utf-8"
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger

    def _poll_log_queue(self):
        while not self.log_queue.empty():
            msg = self.log_queue.get()
            self.log_widget.configure(state="normal")
            self.log_widget.insert(tk.END, msg + "\n")
            self.log_widget.yview_moveto(1.0)
            self.log_widget.configure(state="disabled")
        self.after(300, self._poll_log_queue)

    # ----------------- UI -----------------
    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        style = ttk.Style(self)
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))

        top_frame = ttk.Frame(self, padding=12)
        top_frame.grid(row=0, column=0, sticky="ew")
        top_frame.columnconfigure(4, weight=1)

        self.status_label = ttk.Label(top_frame, text="监听状态: 未启动", foreground="#a33")
        self.status_label.grid(row=0, column=0, sticky="w", padx=(0, 12))
        self.last_trigger_label = ttk.Label(top_frame, text="最后触发: -")
        self.last_trigger_label.grid(row=0, column=1, sticky="w", padx=6)
        self.last_email_label = ttk.Label(top_frame, text="最后发送: -")
        self.last_email_label.grid(row=0, column=2, sticky="w", padx=6)
        self.counter_label = ttk.Label(top_frame, text="累计触发: 0")
        self.counter_label.grid(row=0, column=3, sticky="w", padx=6)

        actions = ttk.Frame(top_frame)
        actions.grid(row=0, column=4, sticky="e")
        self.start_btn = ttk.Button(actions, text="开始监听", style="Accent.TButton", command=self.start_listening)
        self.start_btn.grid(row=0, column=0, padx=4)
        self.stop_btn = ttk.Button(actions, text="停止监听", command=self.stop_listening, state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=4)
        self.sim_btn = ttk.Button(actions, text="模拟一次 F12", command=lambda: self.on_f12(source="界面模拟"))
        self.sim_btn.grid(row=0, column=2, padx=4)
        self.test_btn = ttk.Button(actions, text="发送测试邮件", command=self.send_test_email)
        self.test_btn.grid(row=0, column=3, padx=4)

        separator = ttk.Separator(self)
        separator.grid(row=1, column=0, sticky="ew", padx=6, pady=4)

        settings_frame = ttk.LabelFrame(self, text="邮件配置", padding=12)
        settings_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=6)
        for i in range(4):
            settings_frame.columnconfigure(i, weight=1)

        self.sender_email_var = tk.StringVar(value=self.mail_config["sender_email"])
        self.sender_pwd_var = tk.StringVar(value=self.mail_config["sender_password"])
        self.smtp_server_var = tk.StringVar(value=self.mail_config["smtp_server"])
        self.smtp_port_var = tk.StringVar(value=self.mail_config["smtp_port"])
        self.receiver_var = tk.StringVar(value=self.mail_config["receiver_email"])

        ttk.Label(settings_frame, text="发件人邮箱").grid(row=0, column=0, sticky="w")
        ttk.Entry(settings_frame, textvariable=self.sender_email_var).grid(row=1, column=0, sticky="ew", padx=4)
        ttk.Label(settings_frame, text="授权码/密码").grid(row=0, column=1, sticky="w")
        self.pwd_entry = ttk.Entry(settings_frame, textvariable=self.sender_pwd_var, show="*")
        self.pwd_entry.grid(row=1, column=1, sticky="ew", padx=4)
        self.show_pwd_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            settings_frame,
            text="显示密码",
            variable=self.show_pwd_var,
            command=self._toggle_password,
        ).grid(row=1, column=2, sticky="w")

        ttk.Label(settings_frame, text="SMTP 服务器").grid(row=2, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(settings_frame, textvariable=self.smtp_server_var).grid(row=3, column=0, sticky="ew", padx=4)
        ttk.Label(settings_frame, text="SMTP 端口").grid(row=2, column=1, sticky="w", pady=(8, 0))
        ttk.Entry(settings_frame, textvariable=self.smtp_port_var).grid(row=3, column=1, sticky="ew", padx=4)
        ttk.Label(settings_frame, text="收件人邮箱").grid(row=2, column=2, sticky="w", pady=(8, 0))
        ttk.Entry(settings_frame, textvariable=self.receiver_var).grid(row=3, column=2, sticky="ew", padx=4)

        ttk.Button(settings_frame, text="保存配置", command=self._save_config).grid(row=3, column=3, padx=4)

        advanced_frame = ttk.LabelFrame(self, text="高级选项", padding=12)
        advanced_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=6)
        for i in range(4):
            advanced_frame.columnconfigure(i, weight=1)

        self.subject_var = tk.StringVar(value=self.advanced_config.get("subject", DEFAULT_ADVANCED_CONFIG["subject"]))
        self.message_var = tk.StringVar(
            value=self.advanced_config.get("custom_message", DEFAULT_ADVANCED_CONFIG["custom_message"])
        )
        self.rate_limit_var = tk.IntVar(value=self.advanced_config.get("rate_limit_seconds", 5))
        self.max_per_min_var = tk.IntVar(value=self.advanced_config.get("max_emails_per_minute", 10))
        self.include_sys_var = tk.BooleanVar(value=self.advanced_config.get("include_system_info", False))
        self.log_to_file_var = tk.BooleanVar(value=self.advanced_config.get("log_to_file", True))
        self.play_sound_var = tk.BooleanVar(value=self.advanced_config.get("play_sound", False))

        ttk.Label(advanced_frame, text="邮件主题").grid(row=0, column=0, sticky="w")
        ttk.Entry(advanced_frame, textvariable=self.subject_var).grid(row=1, column=0, sticky="ew", padx=4)
        ttk.Label(advanced_frame, text="内容模板（可用 {timestamp} / {source}）").grid(row=0, column=1, sticky="w")
        ttk.Entry(advanced_frame, textvariable=self.message_var).grid(row=1, column=1, sticky="ew", padx=4, columnspan=2)

        ttk.Label(advanced_frame, text="最小间隔(秒)").grid(row=2, column=0, sticky="w", pady=(8, 0))
        ttk.Spinbox(advanced_frame, from_=0, to=300, textvariable=self.rate_limit_var, width=8).grid(
            row=3, column=0, sticky="w", padx=4
        )
        ttk.Label(advanced_frame, text="每分钟上限").grid(row=2, column=1, sticky="w", pady=(8, 0))
        ttk.Spinbox(advanced_frame, from_=1, to=100, textvariable=self.max_per_min_var, width=8).grid(
            row=3, column=1, sticky="w", padx=4
        )

        ttk.Checkbutton(advanced_frame, text="包含系统信息", variable=self.include_sys_var).grid(
            row=3, column=2, sticky="w"
        )
        ttk.Checkbutton(advanced_frame, text="写入日志文件", variable=self.log_to_file_var).grid(
            row=3, column=3, sticky="w"
        )
        ttk.Checkbutton(advanced_frame, text="触发时播放提示音", variable=self.play_sound_var).grid(
            row=3, column=4, sticky="w"
        )

        log_frame = ttk.LabelFrame(self, text="运行日志", padding=8)
        log_frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=6)
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)

        self.log_widget = scrolledtext.ScrolledText(log_frame, state="disabled", font=("Consolas", 10))
        self.log_widget.grid(row=0, column=0, sticky="nsew")

        footer = ttk.Frame(self, padding=8)
        footer.grid(row=5, column=0, sticky="ew")
        ttk.Label(
            footer,
            text="温馨提示：需要在后台常驻。确保安装 keyboard 库并允许管理员全局键盘监听。",
            foreground="#555",
        ).grid(row=0, column=0, sticky="w")

    def _toggle_password(self):
        self.pwd_entry.configure(show="" if self.show_pwd_var.get() else "*")

    def _save_config(self):
        self.mail_config.update(
            {
                "sender_email": self.sender_email_var.get().strip(),
                "sender_password": self.sender_pwd_var.get().strip(),
                "smtp_server": self.smtp_server_var.get().strip(),
                "smtp_port": self.smtp_port_var.get().strip(),
                "receiver_email": self.receiver_var.get().strip(),
            }
        )
        self.advanced_config.update(
            {
                "subject": self.subject_var.get().strip() or DEFAULT_ADVANCED_CONFIG["subject"],
                "custom_message": self.message_var.get().strip() or DEFAULT_ADVANCED_CONFIG["custom_message"],
                "rate_limit_seconds": int(self.rate_limit_var.get() or 0),
                "max_emails_per_minute": int(self.max_per_min_var.get() or 1),
                "include_system_info": bool(self.include_sys_var.get()),
                "log_to_file": bool(self.log_to_file_var.get()),
                "play_sound": bool(self.play_sound_var.get()),
            }
        )
        self.rate_limiter = RateLimiter(
            self.advanced_config["rate_limit_seconds"], self.advanced_config["max_emails_per_minute"]
        )
        self.save_mail_config()
        self.save_advanced_config()
        self.logger.info("配置已保存，速率限制已更新。")

    # ----------------- Core logic -----------------
    def start_listening(self):
        if self.listener_handle:
            return
        try:
            self.listener_handle = keyboard.on_press_key("f12", lambda _: self.on_f12(source="键盘事件"))
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.status_label.configure(text="监听状态: 运行中", foreground="#2a8f3c")
            self.logger.info("开始监听 F12 (物理按键和程序模拟都会触发)")
        except Exception as exc:
            messagebox.showerror("无法启动监听", f"监听失败：{exc}\n请确认已安装 keyboard 库，并以管理员权限运行。")
            self.logger.error("监听失败: %s", exc)

    def stop_listening(self):
        if self.listener_handle:
            try:
                keyboard.unhook(self.listener_handle)
            except Exception:
                pass
            self.listener_handle = None
            self.logger.info("已停止监听 F12。")
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_label.configure(text="监听状态: 未启动", foreground="#a33")

    def on_f12(self, source: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.trigger_count += 1
        self.last_trigger = timestamp
        self.counter_label.configure(text=f"累计触发: {self.trigger_count}")
        self.last_trigger_label.configure(text=f"最后触发: {timestamp}")
        self.logger.info("检测到 F12 触发（来源: %s）", source)

        if not self.rate_limiter.allow():
            self.logger.warning("触发过于频繁，已根据速率限制跳过邮件发送。")
            return

        if self.advanced_config.get("play_sound"):
            self._play_beep()

        threading.Thread(target=self._send_email_async, args=(timestamp, source), daemon=True).start()

    def _send_email_async(self, timestamp: str, source: str):
        success = self.email_sender.send_email(timestamp, source)
        if success:
            self.last_email = timestamp
            self.last_email_label.configure(text=f"最后发送: {timestamp}")
        else:
            self.logger.error("发送失败，请检查配置。")

    def _play_beep(self):
        try:
            import winsound

            winsound.Beep(900, 160)
        except Exception:
            pass

    def send_test_email(self):
        self.on_f12(source="测试按钮")
        messagebox.showinfo("测试邮件", "已触发一次模拟 F12，将按照当前配置发送邮件。")

    def on_close(self):
        self.stop_listening()
        self.destroy()


def main():
    app = F12ReminderApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()


if __name__ == "__main__":
    main()
