# 快速开始

## 1️⃣ 安装依赖

```bash
pip install -r requirements.txt
```

## 2️⃣ 配置邮箱

### 第一步：复制配置文件
```bash
cp config.ini.example config.ini
```

### 第二步：编辑配置文件
根据你的邮箱服务商填写以下信息：

```ini
sender_email=your_email@example.com      # 你的邮箱
sender_password=your_app_password        # 密码或应用密码
smtp_server=smtp.example.com             # SMTP服务器
smtp_port=587                            # SMTP端口（通常是587或465）
receiver_email=receiver@example.com      # 接收邮箱（可以和发送者相同）
```

### 常见邮箱配置

| 邮箱 | SMTP服务器 | 端口 | 密码类型 |
|------|-----------|------|--------|
| **Gmail** | smtp.gmail.com | 587 | [应用密码](https://myaccount.google.com/apppasswords) |
| **QQ邮箱** | smtp.qq.com | 587 | [授权码](https://mail.qq.com/) |
| **163邮箱** | smtp.163.com | 587 | [授权码](https://mail.163.com/) |
| **Outlook** | smtp-mail.outlook.com | 587 | 密码或应用密码 |

## 3️⃣ 运行程序

### 基础版本（推荐新手）
```bash
python3 f12_reminder.py
```

### 高级版本（支持日志和限流）
```bash
python3 f12_reminder_advanced.py
```

### 使用启动脚本
```bash
# Linux/Mac
chmod +x start.sh
./start.sh

# Windows
start.bat
```

## 4️⃣ 测试

1. 运行程序后，会显示"正在监听 F12 按键..."
2. 按下 F12 键
3. 应该收到邮件提醒
4. 按 Ctrl+C 停止程序

## 📋 文件说明

| 文件 | 说明 |
|------|------|
| `f12_reminder.py` | 基础版程序（推荐） |
| `f12_reminder_advanced.py` | 高级版本（支持日志、限流等） |
| `config.ini.example` | 配置文件示例 |
| `config.ini` | 你的配置（需要自己创建） |
| `requirements.txt` | 依赖列表 |
| `examples.py` | 使用示例代码 |
| `SETUP_GUIDE.md` | 详细配置指南 |

## 🚀 后台运行

### Linux/Mac
```bash
nohup python3 f12_reminder.py > f12_reminder.log 2>&1 &
```

### Windows
```bash
pythonw f12_reminder.py
```

## ❓ 常见问题

### 邮件认证失败
- 检查邮箱和密码是否正确
- 确保使用了应用密码（如Gmail）或授权码（如QQ邮箱）
- 检查SMTP服务器和端口是否正确

### Windows 无法检测按键
- 以**管理员权限**运行程序

### Linux/Mac 权限错误
- 使用 `sudo python3 f12_reminder.py`

### 找不到 config.ini
```bash
cp config.ini.example config.ini
# 然后编辑 config.ini
```

## 📚 更多信息

详见 `SETUP_GUIDE.md` 了解更多配置选项和使用方式。

## 🔒 安全提示

⚠️ **重要**：
- 不要将 `config.ini` 上传到公开仓库
- 使用应用专用密码或授权码，而不是邮箱主密码
- 定期更新密码

---

**祝使用愉快！** 🎉
