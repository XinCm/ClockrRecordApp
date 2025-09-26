#!/usr/bin/env python3
"""
打卡机应用 - 主程序入口
"""
import sys
import os
import tkinter as tk

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui.main_window import ClockInApp
from core.config import AppConfig
from utils.logger import setup_logging

def main():
    """主函数"""
    try:
        # 初始化配置和日志
        config = AppConfig()
        setup_logging()
        
        # 创建主窗口
        root = tk.Tk()
        app = ClockInApp(root, config)
        
        # 启动应用
        root.mainloop()
        
    except Exception as e:
        print(f"应用启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()