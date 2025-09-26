"""
日志工具
"""
import logging
import os
from datetime import datetime

def setup_logging():
    """设置日志"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, f"clock_in_{datetime.now().strftime('%Y%m%d')}.log")),
            logging.StreamHandler()
        ]
    )