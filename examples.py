#!/usr/bin/env python3
"""
F12 按键提醒系统 - 使用示例
演示如何在你的代码中使用此系统
"""

import keyboard
from datetime import datetime
import time


def example_1_basic_f12_detection():
    """示例1：基础的F12按键检测"""
    print("\n=== 示例1：基础F12按键检测 ===")
    print("监听F12按键，按Ctrl+C停止\n")
    
    def on_f12():
        print(f"[{datetime.now().strftime('%H:%M:%S')}] F12 按键被按下！")
    
    keyboard.on_press_key('f12', lambda _: on_f12())
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n已停止")


def example_2_multiple_hotkeys():
    """示例2：监听多个按键"""
    print("\n=== 示例2：监听多个热键 ===")
    print("监听 F12 和 F11 按键，按Ctrl+C停止\n")
    
    def on_f12():
        print(f"[{datetime.now().strftime('%H:%M:%S')}] F12 按键被按下！")
    
    def on_f11():
        print(f"[{datetime.now().strftime('%H:%M:%S')}] F11 按键被按下！")
    
    keyboard.on_press_key('f12', lambda _: on_f12())
    keyboard.on_press_key('f11', lambda _: on_f11())
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n已停止")


def example_3_custom_hotkey():
    """示例3：自定义热键组合"""
    print("\n=== 示例3：自定义热键组合 ===")
    print("监听 Ctrl+F12 组合键，按Ctrl+C停止\n")
    
    def on_custom():
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Ctrl+F12 被按下！")
    
    keyboard.add_hotkey('ctrl+f12', on_custom)
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n已停止")


def example_4_trigger_key_press():
    """示例4：在代码中模拟按键"""
    print("\n=== 示例4：模拟F12按键 ===")
    
    def on_f12():
        print(f"[{datetime.now().strftime('%H:%M:%S')}] F12 按键被检测到（包括模拟的）")
    
    keyboard.on_press_key('f12', lambda _: on_f12())
    
    print("设置监听器...")
    time.sleep(1)
    
    print("2秒后将模拟按下F12...")
    time.sleep(2)
    
    print("正在模拟按下F12...")
    keyboard.press_and_release('f12')
    
    time.sleep(1)
    print("模拟完成")


def example_5_with_logging():
    """示例5：带日志的版本"""
    print("\n=== 示例5：带日志的F12监听 ===")
    print("监听F12按键并记录日志，按Ctrl+C停止\n")
    
    # 创建日志文件
    log_file = "f12_events.log"
    
    def log_event(message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + "\n")
    
    def on_f12():
        log_event("F12 按键被按下")
    
    keyboard.on_press_key('f12', lambda _: on_f12())
    log_event("开始监听F12按键")
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        log_event("停止监听")
        print(f"\n已停止，日志已保存到 {log_file}")


def main():
    """主菜单"""
    print("\n" + "="*50)
    print("F12 按键提醒系统 - 使用示例")
    print("="*50)
    print("\n选择要运行的示例：")
    print("1. 基础F12按键检测")
    print("2. 监听多个热键")
    print("3. 自定义热键组合")
    print("4. 模拟F12按键")
    print("5. 带日志的F12监听")
    print("0. 退出")
    
    choice = input("\n请选择 (0-5): ").strip()
    
    examples = {
        '1': example_1_basic_f12_detection,
        '2': example_2_multiple_hotkeys,
        '3': example_3_custom_hotkey,
        '4': example_4_trigger_key_press,
        '5': example_5_with_logging,
    }
    
    if choice in examples:
        examples[choice]()
    elif choice == '0':
        print("再见！")
    else:
        print("❌ 无效选择")


if __name__ == "__main__":
    main()
