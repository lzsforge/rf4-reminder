# F12 邮件提醒系统

按下 F12（真实按键或程序模拟）时自动发送邮件提醒，并提供一个可视化控制面板方便配置和监控。

## 主要功能
- 全局监听 F12，真实/模拟按键都会触发
- SMTP 邮件提醒，支持自定义主题和内容模板（`{timestamp}`、`{source}` 占位符）
- 速率限制（最小间隔、每分钟上限）防止邮件轰炸
- 可视化界面：开始/停止监听、模拟一次 F12、发送测试邮件、实时日志
- 可选附带系统信息、提示音、日志文件滚动保存

## 环境准备
1. Python 3.8+
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
   > 第一次运行 `start.bat` 也会自动安装 `keyboard`。

## 配置
1. 复制并修改邮箱配置：
   ```bash
   copy config.ini.example config.ini
   ```
   按照文件里的注释填写发件人、授权码/密码、SMTP 服务器、端口、收件人。
2. （可选）高级配置 `advanced_config.json`：
   - `subject`：邮件主题
   - `custom_message`：内容模板，可用 `{timestamp}`、`{source}`
   - `rate_limit_seconds`：两次邮件的最小间隔（秒）
   - `max_emails_per_minute`：每分钟最多发送数量
   - `include_system_info`：是否附带系统信息
   - `play_sound`：触发时播放提示音
   - `log_to_file`：将日志写入 `logs/f12_reminder.log`

## 运行
- 直接启动 GUI：
  ```bash
  python f12_email_reminder.py
  ```
- Windows 启动脚本：
  ```bash
  start.bat gui
  ```

界面中可以：
- 「开始监听」/「停止监听」控制全局监听
- 「模拟一次 F12」验证触发逻辑
- 「发送测试邮件」快速检查 SMTP 配置
- 「保存配置」写回 `config.ini` 和 `advanced_config.json`

## 常见问题
- 全局键盘监听可能需要在 Windows 以管理员权限运行。
- 如果邮件发送失败，检查发件邮箱的 SMTP/授权码设置及网络连通性。
- 如被速率限制拦截，请调整高级配置里的间隔和上限。***
