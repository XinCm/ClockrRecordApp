"""
配置管理
"""
import configparser
import os

class AppConfig:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_file = "config.ini"
        self.load_config()
    
    def load_config(self):
        """加载配置"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')
        else:
            self.create_default_config()
    
    def create_default_config(self):
        """创建默认配置"""
        self.config['DEFAULT'] = {
            'database_path': 'data/clock_in.db',
            'auto_save': 'true',
            'backup_days': '7'
        }
        self.save_config()
    
    def save_config(self):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)