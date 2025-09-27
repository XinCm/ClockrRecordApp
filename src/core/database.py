"""
数据库管理模块
"""
import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "data/clock_in.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建打卡记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clock_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_date TEXT NOT NULL,
                record_time TEXT NOT NULL,
                record_type TEXT NOT NULL,
                record_datetime TEXT NOT NULL,
                notes TEXT,
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON clock_records(record_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_datetime ON clock_records(record_datetime)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_type ON clock_records(record_type)')
        
        conn.commit()
        conn.close()


    def add_clock_record(self, record_time: str, record_type: str, notes: str = "") -> bool:
        """添加打卡记录，支持仅时间部分的输入"""
        try:
            record_datetime = record_time
            
            # 解析record_datetime为datetime对象
            record_datetime_obj = datetime.strptime(record_datetime, "%Y-%m-%d %H:%M:%S")
            print(f"record_datetime_obj {record_datetime_obj}")
            record_date = record_datetime_obj.strftime("%Y-%m-%d")
            print(f"record_date {record_date}")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查当天是否已经存在该类型的打卡记录
            cursor.execute('''
                SELECT id FROM clock_records 
                WHERE record_date = ? AND record_type = ?
                ORDER BY record_datetime DESC 
                LIMIT 1
            ''', (record_date, record_type))
            
            existing_record = cursor.fetchone()
            
            if existing_record:
                # 如果存在，更新该记录
                cursor.execute('''
                    UPDATE clock_records 
                    SET record_time = ?, record_datetime = ?, notes = ?
                    WHERE id = ?
                ''', (record_time, record_datetime, notes, existing_record[0]))
            else:
                # 如果不存在，插入新记录
                cursor.execute('''
                    INSERT INTO clock_records 
                    (record_date, record_time, record_type, record_datetime, notes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (record_date, record_time, record_type, record_datetime, notes))
            
            print(f"database {record_time} {record_type}")
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"添加记录失败: {e}")
            return False
    
    def get_today_records(self) -> List[Dict]:
        """获取今天的打卡记录"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            return self.get_date_records(today)
        except Exception as e:
            print(f"查询今日记录失败: {e}")
            return []
    
    def get_date_records(self, date_str: str) -> List[Dict]:
        """获取指定日期的记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT record_time, record_type, record_datetime, notes 
                FROM clock_records 
                WHERE record_date = ? 
                ORDER BY record_datetime
            ''', (date_str,))
            
            records = []
            for row in cursor.fetchall():
                records.append({
                    'time': row[0],
                    'type': row[1],
                    'datetime': row[2],
                    'notes': row[3] or ''
                })
            print(f"获取到的记录: {records}")
            conn.close()
            return records
            
        except Exception as e:
            print(f"查询日期记录失败: {e}")
            return []
    
    def get_last_clock_time(self, record_type: str) -> Optional[Dict]:
        """获取最后一次指定类型的打卡时间"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT record_date, record_time, record_datetime, notes
                FROM clock_records 
                WHERE record_type = ? 
                ORDER BY record_datetime DESC 
                LIMIT 1
            ''', (record_type,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                print(f"获取到的结果: {result}")

                return {
                    'date': result[0],
                    'time': result[1],
                    'datetime': result[2],
                    'notes': result[3] or ''
                }
            return None
            
        except Exception as e:
            print(f"查询最后打卡时间失败: {e}")
            return None
    
    def get_monthly_records(self, year: int = None, month: int = None) -> List[Dict]:
        """获取指定年月的所有记录"""
        try:
            # 如果 year 或 month 为 None，使用当前年月
            now = datetime.now()
            if year is None:
                year = now.year
            if month is None:
                month = now.month
            year = int(year)
            month = int(month)
            month_str = f"{year:04d}-{month:02d}"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT record_date, record_time, record_type, record_datetime, notes
                FROM clock_records 
                WHERE record_date LIKE ? 
                ORDER BY record_datetime
            ''', (f"{month_str}%",))
            
            records = []
            for row in cursor.fetchall():
                records.append({
                    'date': row[0],
                    'time': row[1],
                    'type': row[2],
                    'datetime': row[3],
                    'notes': row[4] or ''
                })
            
            conn.close()
            return records
            
        except Exception as e:
            print(f"查询月度记录失败: {e}")
            return []
    
    def get_all_records(self) -> List[Dict]:
        """获取所有记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT record_date, record_time, record_type, record_datetime, notes
                FROM clock_records 
                ORDER BY record_datetime
            ''')
            
            records = []
            for row in cursor.fetchall():
                records.append({
                    'date': row[0],
                    'time': row[1],
                    'type': row[2],
                    'datetime': row[3],
                    'notes': row[4] or ''
                })
            
            conn.close()
            return records
            
        except Exception as e:
            print(f"查询所有记录失败: {e}")
            return []