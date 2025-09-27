"""
打卡管理逻辑
"""
from datetime import datetime, timedelta
from .database import DatabaseManager

class ClockManager:
    def __init__(self):
        self.db = DatabaseManager()
    
    def clock_in(self, notes: str = "") -> bool:
        """上班打卡"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.db.add_clock_record(current_time, "in", notes)
    
    def clock_out(self, notes: str = "") -> bool:
        """下班打卡"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.db.add_clock_record(current_time, "out", notes)
    
    def custom_clock(self, custom_time: str, record_type: str, notes: str = "") -> bool:
        """自定义时间打卡"""
        try:
            if record_type == "in":
                return self.db.add_clock_record(custom_time, "in", notes)
            else:
                print(f"{record_type}")
                return self.db.add_clock_record(custom_time, "out", notes)
        except ValueError:
            print(f"custom_clock err")
            return False
    
    def get_last_clock_in(self):
        """获取最后一次上班打卡时间"""
        return self.db.get_last_clock_time("in")
    
    def get_last_clock_out(self):
        """获取最后一次下班打卡时间"""
        return self.db.get_last_clock_time("out")
    
    def get_today_summary(self) -> dict:
        """获取今日打卡摘要"""
        records = self.db.get_today_records()
        
        in_times = [r['time'] for r in records if r['type'] == 'in']
        out_times = [r['time'] for r in records if r['type'] == 'out']
        
        return {
            'total_records': len(records),
            'in_count': len(in_times),
            'out_count': len(out_times),
            'first_in': in_times[0] if in_times else None,
            'last_out': out_times[-1] if out_times else None,
            'records': records
        }
    
    def _subtract_rest_time(self, total_hours: float, start_dt: datetime, end_dt: datetime, rest_periods: list) -> float:
        """扣除休息时间（接收和返回都是小时单位）"""
        work_hours = total_hours
        
        for rest in rest_periods:
            try:
                rest_start_str = rest['start']
                rest_end_str = rest['end']
                
                # 解析休息时间
                rest_start_time = datetime.strptime(rest_start_str, "%H:%M").time()
                rest_end_time = datetime.strptime(rest_end_str, "%H:%M").time()
                
                # 创建完整的datetime对象
                rest_start_dt = datetime.combine(start_dt.date(), rest_start_time)
                rest_end_dt = datetime.combine(start_dt.date(), rest_end_time)
                
                # 如果结束时间小于开始时间，说明跨天了
                if rest_end_dt < rest_start_dt:
                    rest_end_dt += timedelta(days=1)
                
                # 计算休息时间与工作时间的重叠部分
                overlap_start = max(start_dt, rest_start_dt)
                overlap_end = min(end_dt, rest_end_dt)
                
                if overlap_end > overlap_start:
                    rest_hours = (overlap_end - overlap_start).total_seconds() / 3600  # 转换为小时
                    work_hours -= rest_hours
                    print(f"扣除休息时间: {rest_start_str}-{rest_end_str}, 时长: {rest_hours:.2f}小时")
                    
            except Exception as e:
                print(f"计算休息时间错误: {e}")
                continue
        
        return max(0, work_hours)
    
    def calculate_daily_work_time(self, date_str: str, rest_periods: list = None) -> float:
        """计算某天的工作时长（小时）"""
        try:
            records = self.db.get_date_records(date_str)
            print(f"计算日期 {date_str} 的工作时长，找到 {len(records)} 条记录")
            
            if len(records) < 2:
                print(f"记录不足2条，返回0")
                return 0.0
            
            # 获取当天的所有in和out记录
            in_records = [r for r in records if r['type'] == 'in']
            out_records = [r for r in records if r['type'] == 'out']
            
            print(f"上班记录: {len(in_records)} 条，下班记录: {len(out_records)} 条")
            
            if not in_records or not out_records:
                print(f"缺少上班或下班记录")
                return 0.0
            
            # 使用第一个in和最后一个out计算总时长
            first_in_record = in_records[0]
            last_out_record = out_records[-1]
            
            print(f"第一条上班记录: {first_in_record}")
            print(f"最后一条下班记录: {last_out_record}")
            
            # 统一处理日期时间格式（处理格式不一致的问题）
            def normalize_datetime(dt_str):
                """标准化日期时间格式"""
                # 处理月份和日期为单位数的情况（如 2025-9-25 -> 2025-09-25）
                parts = dt_str.split(' ')
                if len(parts) == 2:
                    date_part, time_part = parts
                    # 标准化日期部分
                    date_parts = date_part.split('-')
                    if len(date_parts) == 3:
                        year, month, day = date_parts
                        month = month.zfill(2)  # 月份补零
                        day = day.zfill(2)      # 日期补零
                        normalized_date = f"{year}-{month}-{day}"
                        return f"{normalized_date} {time_part}"
                return dt_str
            
            # 优先使用record_datetime字段，如果没有则使用record_time
            first_in_str = first_in_record.get('datetime') or first_in_record.get('time', '')
            last_out_str = last_out_record.get('datetime') or last_out_record.get('time', '')
            
            if not first_in_str or not last_out_str:
                print(f"时间字符串为空")
                return 0.0
            
            # 标准化时间格式
            first_in_str = normalize_datetime(first_in_str)
            last_out_str = normalize_datetime(last_out_str)
            
            print(f"标准化后的上班时间: {first_in_str}")
            print(f"标准化后的下班时间: {last_out_str}")
            
            # 解析时间
            first_in = datetime.strptime(first_in_str, "%Y-%m-%d %H:%M:%S")
            last_out = datetime.strptime(last_out_str, "%Y-%m-%d %H:%M:%S")
            
            if last_out <= first_in:
                print(f"下班时间早于或等于上班时间")
                return 0.0
            
            total_seconds = (last_out - first_in).total_seconds()
            total_hours = total_seconds / 3600
            
            print(f"扣除休息前总时长: {total_hours:.2f} 小时")
            
            # 扣除休息时间
            if rest_periods:
                total_hours = self._subtract_rest_time(total_hours, first_in, last_out, rest_periods)
                print(f"扣除休息后总时长: {total_hours:.2f} 小时")
            
            return total_hours
            
        except Exception as e:
            print(f"计算每日工时错误: {e}")
            import traceback
            traceback.print_exc()
            return 0.0
    
    def get_monthly_statistics(self, year: str = None, month: str = None, rest_periods: list = None) -> list:
        """获取月份统计信息"""
        try:
            records = self.db.get_monthly_records(year, month)
            if records is None:
                return []
            return records
        except Exception as e:
            print(f"获取月份统计失败: {e}")
            return []

    def _get_monthly_remark(self, work_days, avg_hours):
        """获取月份备注信息"""
        if work_days == 0:
            return "无打卡记录"
        elif work_days < 10:
            return "工作日较少"
        elif avg_hours > 10:
            return "工时较长"
        elif avg_hours < 6:
            return "工时较短"
        else:
            return "正常"
    
    def calculate_monthly_statistics(self, year: int = None, month: int = None, rest_periods: list = None) -> dict:
        """计算月度统计"""
        print(f"计算 {year}年{month}月 的统计，休息时间段: {rest_periods}")
        now = datetime.now()
        if year is None:
            year = now.year
        if month is None:
            month = now.month
        
        records = self.db.get_monthly_records(year, month)
        print(f"找到 {len(records)} 条记录")
        
        if not records:
            return {
                'year': year,
                'month': month,
                'total_days': 0,
                'total_hours': 0.0,
                'average_hours': 0.0,
                'work_days': []
            }
        
        # 按日期分组
        daily_records = {}
        for record in records:
            date_str = record['date']
            if date_str not in daily_records:
                daily_records[date_str] = []
            daily_records[date_str].append(record)
        
        print(f"有记录的日期: {list(daily_records.keys())}")
        
        # 计算每天的工作时长
        work_days = []
        total_hours = 0.0
        
        for date_str, day_records in daily_records.items():
            print(f"计算日期 {date_str} 的工作时长")
            daily_hours = self.calculate_daily_work_time(date_str, rest_periods)
            print(f"日期 {date_str} 工作时长: {daily_hours:.2f} 小时")
            
            if daily_hours > 0:
                work_days.append({
                    'date': date_str,
                    'hours': daily_hours,
                    'records': day_records
                })
                total_hours += daily_hours
        
        total_days = len(work_days)
        average_hours = total_hours / total_days if total_days > 0 else 0.0
        
        print(f"月度统计结果: {total_days}天, {total_hours:.2f}小时, 平均{average_hours:.2f}小时/天")
        
        return {
            'year': year,
            'month': month,
            'total_days': total_days,
            'total_hours': total_hours,
            'average_hours': average_hours,
            'work_days': work_days
        }
    
    def get_all_records(self):
        """获取所有记录"""
        return self.db.get_all_records()