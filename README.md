# F12 按键提醒系统

一个监听F12按键（真实按键或程序模拟）并通过邮件发送提醒的Python程序。

## 功能特性

- 🔔 实时监听F12按键（真实按键和程序模拟都可以检测）
- 📧 自动发送邮件提醒
- ⚙️ 支持多种邮箱服务商
- 🎯 简单易用的配置系统

## 安装

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置邮箱

根据你的邮箱服务商进行配置，参考 `config.ini.example` 文件中的示例。

### 3. 创建配置文件

```bash
cp config.ini.example config.ini
nano config.ini
```

必须配置的参数：

```ini
sender_email=your_email@gmail.com          # 发送方邮箱
sender_password=your_app_password          # 邮箱密码或应用密码
smtp_server=smtp.gmail.com                 # SMTP服务器
smtp_port=587                              # SMTP端口
receiver_email=receiver@gmail.com          # 接收方邮箱
```

## 使用

### 基础运行

```bash
python3 f12_reminder.py
```

### 后台运行（Linux/Mac）

```bash
nohup python3 f12_reminder.py > f12_reminder.log 2>&1 &
```

### 后台运行（Windows）

```bash
pythonw f12_reminder.py
```

## 常见问题

### Linux/Mac 中出现权限错误

```bash
sudo python3 f12_reminder.py
```

### 邮件认证失败

- 检查邮箱地址和密码
- 确保SMTP服务器和端口正确
- 使用应用密码而不是主密码

### Windows 需要管理员权限

以管理员身份运行程序。

## 安全建议

⚠️ **重要**：
- 不要提交 `config.ini` 到版本控制
- 使用应用专用密码
- 限制文件权限：`chmod 600 config.ini`

## 文件说明

- `f12_reminder.py` - 主程序文件
- `config.ini.example` - 配置文件示例
- `config.ini` - 你的配置文件（需要自己创建）
- `requirements.txt` - Python依赖列表