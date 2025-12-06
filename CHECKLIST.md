# ✅ 安装和配置检查清单

## 安装前检查

- [ ] Python 3.6+ 已安装（运行 `python3 --version` 验证）
- [ ] pip 已安装（运行 `pip --version` 验证）
- [ ] 能访问互联网（用于安装依赖和发送邮件）
- [ ] 有一个电子邮件账户（Gmail、QQ、163等）

## 安装步骤检查

- [ ] 克隆或下载项目到本地
- [ ] 进入项目目录：`cd /workspaces/rf4-reminder`
- [ ] 安装依赖：`pip install -r requirements.txt`
- [ ] 复制配置文件：`cp config.ini.example config.ini`

## 邮箱配置检查（选择适用的）

### Gmail 配置
- [ ] 访问 https://myaccount.google.com/security
- [ ] 启用"两步验证"
- [ ] 访问 https://myaccount.google.com/apppasswords
- [ ] 生成应用密码（16位）
- [ ] 复制应用密码到 `config.ini`
- [ ] 在 `config.ini` 中设置：
  ```ini
  sender_email=your_email@gmail.com
  sender_password=生成的16位密码
  smtp_server=smtp.gmail.com
  smtp_port=587
  receiver_email=your_email@gmail.com
  ```

### QQ邮箱 配置
- [ ] 访问 https://mail.qq.com/
- [ ] 进入设置 > 账户
- [ ] 启用"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
- [ ] 生成授权码（16位）
- [ ] 复制授权码到 `config.ini`
- [ ] 在 `config.ini` 中设置：
  ```ini
  sender_email=你的QQ号@qq.com
  sender_password=生成的授权码
  smtp_server=smtp.qq.com
  smtp_port=587
  receiver_email=你的QQ号@qq.com
  ```

### 163邮箱 配置
- [ ] 访问 https://mail.163.com/
- [ ] 进入设置 > POP3/SMTP/IMAP
- [ ] 启用 SMTP 服务
- [ ] 生成授权码
- [ ] 复制授权码到 `config.ini`
- [ ] 在 `config.ini` 中设置：
  ```ini
  sender_email=your_email@163.com
  sender_password=生成的授权码
  smtp_server=smtp.163.com
  smtp_port=587
  receiver_email=your_email@163.com
  ```

### Outlook/Office365 配置
- [ ] 访问 https://account.microsoft.com/
- [ ] 如启用双因素认证，生成应用密码
- [ ] 复制密码到 `config.ini`
- [ ] 在 `config.ini` 中设置：
  ```ini
  sender_email=your_email@outlook.com
  sender_password=你的密码或应用密码
  smtp_server=smtp-mail.outlook.com
  smtp_port=587
  receiver_email=your_email@outlook.com
  ```

## 首次运行检查

### 基础版本
- [ ] 运行：`python3 f12_reminder.py`
- [ ] 看到 "正在监听 F12 按键..." 消息
- [ ] 按下 F12 键
- [ ] 收到邮件提醒（通常1-5秒内）
- [ ] 按 Ctrl+C 停止程序

### 高级版本（可选）
- [ ] 运行：`python3 f12_reminder_advanced.py`
- [ ] 查看日志：`tail -f logs/f12_reminder_*.log`
- [ ] 测试按 F12 键
- [ ] 按 Ctrl+C 停止程序

## 安全检查

- [ ] 编辑了 `config.ini` 文件（不是使用示例）
- [ ] 验证 `config.ini` 在 `.gitignore` 中（保护密码）
- [ ] 设置文件权限：`chmod 600 config.ini`（Linux/Mac）
- [ ] 没有将 `config.ini` 提交到版本控制
- [ ] 使用的是应用密码或授权码，而不是邮箱主密码

## 常见问题解决检查

如果遇到以下问题，按步骤检查：

### 找不到 config.ini
- [ ] 运行：`cp config.ini.example config.ini`
- [ ] 验证文件已创建：`ls -la config.ini`

### 找不到 keyboard 模块
- [ ] 运行：`pip install keyboard`
- [ ] 验证安装：`python3 -c "import keyboard; print('OK')"`

### 邮件认证失败
- [ ] 验证 `sender_email` 正确性
- [ ] 验证密码/应用密码正确性
- [ ] 验证 SMTP 服务器地址
- [ ] 验证 SMTP 端口（通常587）
- [ ] 验证邮箱已启用 SMTP 服务
- [ ] 尝试在其他客户端登录验证凭证

### Windows 无法检测按键
- [ ] 以**管理员权限**运行命令提示符或PowerShell
- [ ] 重新运行程序

### Linux/Mac 权限错误
- [ ] 运行：`sudo python3 f12_reminder.py`
- [ ] 如果仍有问题，可能需要更改 uinput 权限

## 后续配置检查（可选）

### 后台运行
- [ ] Linux/Mac：`nohup python3 f12_reminder.py > f12_reminder.log 2>&1 &`
- [ ] Windows：`pythonw f12_reminder.py`

### 开机自启
- [ ] Windows：配置任务计划程序
- [ ] Linux：配置 systemd 服务
- [ ] Mac：配置 LaunchAgent

### 自定义配置（高级版）
- [ ] 编辑 `advanced_config.json`
- [ ] 调整速率限制和其他参数

## 文档阅读检查

- [ ] 已读 `QUICKSTART.md`（快速开始）
- [ ] 已读 `README.md`（项目说明）
- [ ] 已读 `SETUP_GUIDE.md`（详细配置）- 遇到问题时参考

## 最终验证

- [ ] 程序可以成功启动
- [ ] 能检测到 F12 按键
- [ ] 能成功发送邮件
- [ ] 邮件内容包含时间戳
- [ ] 可以正常停止（Ctrl+C）

---

## ✅ 完成！

如果所有检查项都已勾选，说明你已经成功安装和配置了 F12 按键提醒系统！

### 下一步：

1. 根据需要配置后台运行
2. 阅读详细指南了解更多功能
3. 查看 `examples.py` 了解如何在自己的代码中集成

### 需要帮助？

- 查看 `SETUP_GUIDE.md` 的常见问题部分
- 检查邮箱服务商的官方文档
- 查看日志文件：`logs/f12_reminder_*.log`

---

**祝使用愉快！** 🎉
