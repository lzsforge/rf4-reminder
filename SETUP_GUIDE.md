# F12 按键提醒系统 - 完整配置指南

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置邮箱

复制配置文件示例并进行编辑：

```bash
cp config.ini.example config.ini
# 编辑 config.ini，填入你的邮箱信息
```

### 3. 运行程序

```bash
python3 f12_reminder.py
```

---

## 邮箱服务商配置详解

### Gmail

1. 访问 [Google 账户安全设置](https://myaccount.google.com/security)
2. 启用"两步验证"（如未启用）
3. 访问 [App Passwords](https://myaccount.google.com/apppasswords)
4. 选择"应用" = "邮件"，"设备" = "Windows 电脑"（或其他）
5. 生成16位密码，复制到 `config.ini`

**config.ini 配置**：

```ini
sender_email=your_email@gmail.com
sender_password=你生成的16位密码
smtp_server=smtp.gmail.com
smtp_port=587
receiver_email=receiver@gmail.com
```

### QQ邮箱

1. 登录 [QQ邮箱](https://mail.qq.com/)
2. 点击 "设置" -> "账户"
3. 找到 "POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
4. 点击 "开启"
5. 在"生成授权码"部分生成一个16位授权码
6. 复制授权码到 `config.ini`

**config.ini 配置**：

```ini
sender_email=你的QQ号@qq.com
sender_password=你生成的授权码
smtp_server=smtp.qq.com
smtp_port=587
receiver_email=receiver@qq.com
```

### 163邮箱

1. 登录 [163邮箱](https://mail.163.com/)
2. 点击 "设置" -> "POP3/SMTP/IMAP"
3. 在"SMTP服务"部分点击"开启"
4. 生成授权码（或使用邮箱密码）
5. 复制到 `config.ini`

**config.ini 配置**：

```ini
sender_email=your_email@163.com
sender_password=你的授权码或密码
smtp_server=smtp.163.com
smtp_port=587
receiver_email=receiver@163.com
```

### Outlook / Office365

1. 访问 [Microsoft 账户安全设置](https://account.microsoft.com/security)
2. 如启用了双因素认证，需在 "应用密码" 生成一个专用密码
3. 复制密码到 `config.ini`

**config.ini 配置**：

```ini
sender_email=your_email@outlook.com
sender_password=你的密码或应用密码
smtp_server=smtp-mail.outlook.com
smtp_port=587
receiver_email=receiver@outlook.com
```

### 其他邮箱服务

| 邮箱服务 | SMTP 服务器 | 端口 | 是否需要授权码 |
|---------|-----------|------|------------|
| 新浪邮箱 | smtp.sina.com | 25/465 | 是 |
| 腾讯企业邮 | smtp.exmail.qq.com | 587 | 是 |
| 126邮箱 | smtp.126.com | 587 | 是 |
| 搜狐邮箱 | smtp.sohu.com | 25 | 否 |

---

## 运行方式

### 方式1：直接运行

```bash
# Linux/Mac
python3 f12_reminder.py

# Windows
python f12_reminder.py
```

### 方式2：使用启动脚本

```bash
# Linux/Mac
chmod +x start.sh
./start.sh

# Windows
start.bat
```

### 方式3：高级版本（支持日志、速率限制等）

```bash
python3 f12_reminder_advanced.py
```

### 方式4：后台运行（Linux/Mac）

```bash
# 使用 nohup
nohup python3 f12_reminder.py > f12_reminder.log 2>&1 &

# 使用 screen
screen -S f12_monitor
python3 f12_reminder.py
# 按 Ctrl+A，然后按 D 来分离窗口

# 使用 tmux
tmux new-session -d -s f12_monitor python3 f12_reminder.py
```

### 方式5：Windows 后台运行

```batch
# 使用 pythonw（无黑窗口）
pythonw f12_reminder.py

# 或创建快捷方式指向：
pythonw.exe "C:\path\to\f12_reminder.py"
```

### 方式6：Linux/Mac 开机自启

创建 systemd 服务文件 `/etc/systemd/system/f12-reminder.service`：

```ini
[Unit]
Description=F12 Key Reminder
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/python3 /path/to/f12_reminder.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用服务：

```bash
sudo systemctl enable f12-reminder
sudo systemctl start f12-reminder
sudo systemctl status f12-reminder
```

### 方式7：Windows 任务计划程序

1. 打开"任务计划程序"
2. 右键 -> "创建基本任务"
3. 名称：`F12 Key Reminder`
4. 触发器：选择"启动时"
5. 操作：
   - 程序/脚本：`C:\path\to\pythonw.exe`
   - 参数：`f12_reminder.py`
   - 起始位置：`C:\path\to\project`
6. 勾选"以最高权限运行"
7. 完成

---

## 常见问题解决

### 1. "Permission denied" 错误（Linux/Mac）

**问题**：运行时出现权限错误

**解决**：
```bash
# 方法1：使用 sudo
sudo python3 f12_reminder.py

# 方法2：添加执行权限
chmod +x f12_reminder.py
sudo ./f12_reminder.py
```

### 2. "Keyboard module not found" 错误

**问题**：模块未安装

**解决**：
```bash
pip install keyboard
# 或
pip install -r requirements.txt
```

### 3. "Authentication failed" 邮件错误

**问题**：邮箱认证失败

**解决步骤**：
- 检查 `sender_email` 和 `sender_password` 是否正确
- 确认已启用 SMTP 服务
- 检查是否使用了应用密码（某些邮箱需要）
- 尝试使用 `telnet` 测试连接：
  ```bash
  telnet smtp.gmail.com 587
  ```

### 4. "Connection refused" 错误

**问题**：无法连接到 SMTP 服务器

**解决**：
- 检查网络连接
- 检查 SMTP 服务器和端口是否正确
- 确认防火墙未阻止端口
- 尝试其他端口（如465而不是587）

### 5. Windows 无法检测按键

**问题**：程序运行但无法检测F12按键

**解决**：
- 以**管理员权限**运行程序
- 尝试在全屏应用（如游戏）中测试
- 某些应用可能会拦截按键事件

### 6. Linux 中的 "Permission denied"

**问题**：即使 sudo 也无法正确监听

**解决**：
```bash
# 可能是 X11/Wayland 问题，尝试：
sudo python3 f12_reminder.py

# 或检查是否需要按键权限
sudo usermod -a -G input $USER
# 注销并重新登录后尝试
```

---

## 日志和调试

### 查看高级版本日志

高级版本会自动在 `logs/` 目录生成日志文件：

```bash
# 查看最新日志
tail -f logs/f12_reminder_*.log

# 查看所有日志
cat logs/*.log
```

### 测试邮件发送

创建 `test_email.py`：

```python
from f12_reminder import EmailSender, load_config

config = load_config()
sender = EmailSender(config)

if sender.validate():
    sender.send("测试邮件", "这是测试邮件。")
else:
    print("配置不完整")
```

运行：
```bash
python3 test_email.py
```

---

## 安全建议

⚠️ **重要安全提示**：

1. **保护 config.ini**
   ```bash
   # 限制文件权限
   chmod 600 config.ini
   
   # 从版本控制中排除
   echo "config.ini" >> .gitignore
   ```

2. **使用应用专用密码**
   - Gmail：使用"应用密码"而不是主密码
   - QQ邮箱、163等：使用"授权码"而不是邮箱密码

3. **定期更新密码**
   - 每3-6个月更新一次应用密码
   - 如果泄露，立即更改

4. **避免在代码中硬编码密码**
   - 始终使用配置文件
   - 考虑使用环境变量：
   ```bash
   export F12_EMAIL=your_email@gmail.com
   export F12_PASSWORD=your_password
   ```

5. **监控异常活动**
   - 定期检查邮箱登录活动
   - 启用双因素认证

---

## 脚本示例

### 示例1：在自己的代码中集成

```python
from f12_reminder import EmailSender, load_config
import keyboard
import time

config = load_config()
sender = EmailSender(config)

def on_f12():
    sender.send("F12 按键提醒", "按键被按下！")

keyboard.on_press_key('f12', lambda _: on_f12())

while True:
    time.sleep(0.1)
```

### 示例2：发送自定义邮件

```python
from f12_reminder import EmailSender, load_config

config = load_config()
sender = EmailSender(config)

sender.send(
    subject="自定义主题",
    body="这是自定义邮件内容"
)
```

### 示例3：使用高级功能

```bash
python3 f12_reminder_advanced.py
```

编辑 `advanced_config.json` 来自定义行为。

---

## 联系和支持

如有问题或建议，欢迎提交 Issue 或 Pull Request。
