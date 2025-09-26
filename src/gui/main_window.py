"""
主窗口界面
"""
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os
from core.clock_manager import ClockManager

class ClockInApp:
    def __init__(self, root, config):
        self.root = root
        self.config = config
        self.clock_manager = ClockManager()
        self.rest_periods = self.load_rest_periods()  # 加载保存的休息时间段
        
        self.setup_window()
        self.create_widgets()
        self.refresh_display()
    
    def setup_window(self):
        """设置窗口属性"""
        self.root.title("智能打卡机")
        self.root.geometry("900x700+200+100")
        self.root.resizable(True, True)
        self.root.minsize(800, 700)
        
        # 设置图标
        try:
            self.root.iconbitmap("resources/icons/clock.ico")
        except:
            pass
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def create_widgets(self):
        """创建界面控件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        tab_control = ttk.Notebook(self.root)
        # 标题
        title_label = ttk.Label(main_frame, text="智能打卡系统", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 当前时间显示
        self.create_time_display(main_frame, row=1)

        # 休息时间段设置按钮
        self.create_settings_button(main_frame, row=2)
        
        # 最后打卡时间显示
        self.create_last_clock_display(main_frame, row=3)
        
        # 快速打卡按钮区域
        self.create_quick_buttons(main_frame, row=4)
        
        # 自定义时间打卡区域
        self.create_custom_section(main_frame, row=5)

        # 打卡统计区
        self.create_monthly_average_display(main_frame, row=6)
        
        # 更新时间显示
        self.update_time_display()

    def create_last_clock_display(self, parent, row):
        """创建最后打卡时间显示区域"""
        last_clock_frame = ttk.LabelFrame(parent, text="最后打卡时间", padding="10")
        last_clock_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        last_clock_frame.columnconfigure(1, weight=1)
        
        # 最后上班时间
        ttk.Label(last_clock_frame, text="最后上班时间:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W)
        self.last_in_var = tk.StringVar(value="暂无记录")
        last_in_label = ttk.Label(last_clock_frame, textvariable=self.last_in_var, 
                                 font=("Arial", 10, "bold"), foreground="green")
        last_in_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # 最后下班时间
        ttk.Label(last_clock_frame, text="最后下班时间:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.last_out_var = tk.StringVar(value="暂无记录")
        last_out_label = ttk.Label(last_clock_frame, textvariable=self.last_out_var, 
                                  font=("Arial", 10, "bold"), foreground="red")
        last_out_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))

    def create_settings_button(self, parent, row):
        """创建休息时间段设置按钮"""

        button_frame = ttk.LabelFrame(parent, text="设置", padding="10")
        button_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        self.rest_btn = ttk.Button(button_frame, text="设置休息时间段", 
                                      command=self.show_rest_settings)
        self.rest_btn.pack(side=tk.LEFT, padx=5)

        self.check_btn = ttk.Button(button_frame, text="查询月份", 
                                      command=self.show_check_settings)
        self.check_btn.pack(side=tk.LEFT, padx=5)

        # 刷新按钮
        self.refresh_btn = ttk.Button(button_frame, text="刷新数据", 
                                command=self.refresh_monthly_display)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)


    def show_check_settings(self):
        """显示查询设置窗口"""
        # 创建设置窗口
        settings_window = tk.Toplevel(self.root)
        settings_window.title("月份查询设置")
        settings_window.geometry("300x200")
        settings_window.resizable(False, False)
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # 居中显示
        self.center_window(settings_window)
        
        # 主框架
        main_frame = ttk.Frame(settings_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 年份选择
        ttk.Label(main_frame, text="选择年份:").grid(row=0, column=0, sticky=tk.W, pady=5)
        year_var = tk.StringVar(value=str(datetime.now().year))
        year_combo = ttk.Combobox(main_frame, textvariable=year_var, 
                                values=['全部'] + [str(year) for year in range(2020, 2031)], 
                                width=10)
        year_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=10)
        
        # 月份选择
        ttk.Label(main_frame, text="选择月份:").grid(row=1, column=0, sticky=tk.W, pady=5)
        month_var = tk.StringVar(value='全部')
        month_combo = ttk.Combobox(main_frame, textvariable=month_var, 
                                values=['全部'] + [f"{month:02d}" for month in range(1, 13)], 
                                width=10)
        month_combo.grid(row=1, column=1, sticky=tk.W, pady=5, padx=10)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        def confirm_query():
            """确认查询"""
            year = year_var.get() if year_var.get() != '全部' else None
            month = month_var.get() if month_var.get() != '全部' else None
            settings_window.destroy()
            self.show_monthly_records(year, month)
            
        # 确认按钮
        confirm_btn = ttk.Button(button_frame, text="确认查询", command=confirm_query)
        confirm_btn.pack(side=tk.LEFT, padx=10)
            
        # 取消按钮
        cancel_btn = ttk.Button(button_frame, text="取消", command=settings_window.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=10)
            
        # 绑定回车键确认
        settings_window.bind('<Return>', lambda e: confirm_query())

    def execute_monthly_query(self, year=None, month=None):
        """执行月份查询，显示每日打卡详情"""
        try:
            # 清空现有数据
            for item in self.monthly_tree.get_children():
                self.monthly_tree.delete(item)
            
            # 确定查询的月份
            if year and month:
                # 具体的年月
                target_month = f"{year}-{month}"
            elif year:
                # 某一年，默认显示当前月份或第一个有数据的月份
                current_date = datetime.now()
                target_month = f"{year}-{current_date.month:02d}"
            elif month:
                # 某个月份，默认显示当前年份
                current_date = datetime.now()
                target_month = f"{current_date.year}-{month}"
            else:
                # 全部，默认显示当前月份
                current_date = datetime.now()
                target_month = f"{current_date.year}-{current_date.month:02d}"
            
            # 获取该月份的所有打卡记录
            daily_stats = self.clock_manager.get_daily_statistics(target_month, self.rest_periods)
            
            if not daily_stats:
                self.summary_var.set(f"{target_month} 没有找到打卡记录")
                messagebox.showinfo("提示", f"{target_month} 没有找到打卡记录！")
                return
            
            # 显示每日统计结果
            total_days = 0
            total_hours = 0.0
            
            for day_stat in daily_stats:
                self.monthly_tree.insert("", tk.END, values=(
                    day_stat['date'],
                    day_stat['first_in'],
                    day_stat['last_out'],
                    f"{day_stat['work_hours']:.2f}",
                    day_stat['remark']
                ))
                
                if day_stat['work_hours'] > 0:
                    total_days += 1
                    total_hours += day_stat['work_hours']
            
            # 计算平均工时
            avg_hours = total_hours / total_days if total_days > 0 else 0
            
            # 更新统计摘要
            summary_text = (f"{target_month}统计: {total_days}个工作日, "
                        f"总工时: {total_hours:.2f}小时, 平均: {avg_hours:.2f}小时/天")
            self.summary_var.set(summary_text)
            
            messagebox.showinfo("查询完成", f"{target_month} 共找到 {len(daily_stats)} 天的打卡记录")
            
        except Exception as e:
            self.summary_var.set("查询失败，请检查数据")
            messagebox.showerror("错误", f"查询失败: {e}")

    def show_monthly_records(self, year, month):
        """显示月度打卡记录和统计数据"""
        # 获取打卡记录
        records = self.get_monthly_records(year, month)
        
        # 计算统计数据
        total_days = len(records)
        total_hours = sum(record['hours'] for record in records)
        average_hours = total_hours / total_days if total_days > 0 else 0
        
        # 创建显示窗口
        display_window = tk.Toplevel(self.root)
        display_window.title(f"{year}年{month}月打卡记录")
        display_window.geometry("600x400")
        display_window.resizable(False, False)
        display_window.transient(self.root)
        display_window.grab_set()
        
        # 居中显示
        self.center_window(display_window)
        
        # 主框架
        main_frame = ttk.Frame(display_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 树形视图显示打卡记录
        tree = ttk.Treeview(main_frame, columns=("日期", "工时"), show="headings")
        tree.heading("日期", text="日期")
        tree.heading("上班时间", text="上班时间")
        tree.heading("下班时间", text="下班时间")
        tree.heading("工时", text="工时")
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscroll=scrollbar.set)
        
        # 添加数据到树形视图
        for record in records:
            tree.insert("", "end", values=(record['date'], record['hours']))
        
        # 统计数据
        stats_frame = ttk.Frame(display_window, padding=10)
        stats_frame.pack(pady=10)
        
        ttk.Label(stats_frame, text=f"总天数: {total_days}").grid(row=0, column=0, padx=10)
        ttk.Label(stats_frame, text=f"总工时: {total_hours:.2f} 小时").grid(row=0, column=1, padx=10)
        ttk.Label(stats_frame, text=f"平均每日工时: {average_hours:.2f} 小时").grid(row=0, column=2, padx=10)


    def get_monthly_records(self, year, month):
        """查询月份统计"""
        try:
            if not year and month != '全部':
                messagebox.showwarning("警告", "请选择年份！")
                return
            
            # 获取统计信息
            monthly_stats = self.clock_manager.get_monthly_statistics(
                year if year else None, 
                month if month != '全部' else None,
                self.rest_periods
            )
            
            if not monthly_stats:
                messagebox.showinfo("提示", "没有找到相关统计信息！")
                return
            
            messagebox.showinfo("完成", f"共找到 {len(monthly_stats)} 个月的统计信息")
            
        except Exception as e:
            messagebox.showerror("错误", f"查询失败: {e}")

    def refresh_monthly_display(self):
        """刷新月份统计显示"""
        # 获取当前显示的数据并重新查询
        try:
            # 这里可以添加逻辑来判断当前显示的是什么数据，然后重新查询
            # 暂时简单重新查询所有数据
            self.execute_monthly_query(None, None)
        except Exception as e:
            messagebox.showerror("错误", f"刷新失败: {e}")

    def center_window(self, window):
        """窗口居中显示"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry('{}x{}+{}+{}'.format(width, height, x, y))


    def create_monthly_average_display(self, parent, row):
        """创建月平均时间显示区域"""
        monthly_frame = ttk.LabelFrame(parent, text="本月工作统计", padding="10")
        monthly_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        monthly_frame.columnconfigure(0, weight=1)
        monthly_frame.rowconfigure(0, weight=1)
        
        
        # 本月统计信息
        stats_frame = ttk.Frame(monthly_frame)
        stats_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(stats_frame, text="本月工作日数:").grid(row=0, column=0, sticky=tk.W)
        self.month_days_var = tk.StringVar(value="0")
        ttk.Label(stats_frame, textvariable=self.month_days_var, font=("Arial", 10, "bold")).grid(row=0, column=1, sticky=tk.W, padx=(5, 20))
        
        ttk.Label(stats_frame, text="总工时:").grid(row=0, column=2, sticky=tk.W)
        self.month_total_var = tk.StringVar(value="0小时")
        ttk.Label(stats_frame, textvariable=self.month_total_var, font=("Arial", 10, "bold")).grid(row=0, column=3, sticky=tk.W, padx=(5, 20))
        
        ttk.Label(stats_frame, text="平均每日:").grid(row=0, column=4, sticky=tk.W)
        self.month_avg_var = tk.StringVar(value="0小时")
        ttk.Label(stats_frame, textvariable=self.month_avg_var, font=("Arial", 10, "bold")).grid(row=0, column=5, sticky=tk.W, padx=5)
        
        # 创建Treeview显示每日详情
        columns = ("日期", "上班时间", "下班时间", "工作时长(小时)")
        self.daily_tree = ttk.Treeview(monthly_frame, columns=columns, show="tree headings", height=8)
        
        # 设置列属性
        self.daily_tree.column("#0", width=0, stretch=tk.NO)
        self.daily_tree.column("日期", width=100, anchor=tk.CENTER)
        self.daily_tree.column("上班时间", width=100, anchor=tk.CENTER)
        self.daily_tree.column("下班时间", width=100, anchor=tk.CENTER)
        self.daily_tree.column("工作时长(小时)", width=120, anchor=tk.CENTER)
        
        # 设置列标题
        for col in columns:
            self.daily_tree.heading(col, text=col)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(monthly_frame, orient=tk.VERTICAL, command=self.daily_tree.yview)
        self.daily_tree.configure(yscrollcommand=scrollbar.set)
        
        self.daily_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))

    def create_status_bar(self, parent, row):
        """创建状态栏"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                                relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(fill=tk.X)

    def refresh_display(self):
        """刷新所有显示"""
        print(f"update_last_clock_times")
        self.update_last_clock_times()
        self.refresh_monthly_display()
        print(f"refresh_monthly_display")

    def update_last_clock_times(self):
        """更新最后打卡时间显示"""
        last_in = self.clock_manager.get_last_clock_in()
        last_out = self.clock_manager.get_last_clock_out()
        
        if last_in:
            self.last_in_var.set(f"{last_in['date']} {last_in['time']}")
        else:
            self.last_in_var.set("暂无记录")
        
        if last_out:
            self.last_out_var.set(f"{last_out['date']} {last_out['time']}")
        else:
            self.last_out_var.set("暂无记录")

    def refresh_monthly_display(self):
        """刷新本月统计显示"""
        print(f"monthly_stats")
        try:
            # 清空现有记录
            print(f"monthly_stats")
            for item in self.daily_tree.get_children():
                self.daily_tree.delete(item)
            
            # 计算本月统计数据
            monthly_stats = self.clock_manager.calculate_monthly_statistics(rest_periods=self.rest_periods)
            print(f"monthly_stats {monthly_stats}")
            
            # 更新统计信息
            self.month_days_var.set(str(monthly_stats['total_days']))
            self.month_total_var.set(f"{monthly_stats['total_hours']:.2f}小时")
            self.month_avg_var.set(f"{monthly_stats['average_hours']:.2f}小时")
            
            # 显示每日详情
            for work_day in monthly_stats['work_days']:
                # 获取当天的上班下班时间
                records = work_day['records']
                in_times = [r['time'] for r in records if r['type'] == 'in']
                out_times = [r['time'] for r in records if r['type'] == 'out']
                
                first_in = in_times[0] if in_times else "无记录"
                last_out = out_times[-1] if out_times else "无记录"
                
                self.daily_tree.insert("", tk.END, values=(
                    work_day['date'],
                    first_in,
                    last_out,
                    f"{work_day['hours']:.2f}"
                ))
        except Exception as e:
            print(f"刷新本月统计显示时出错: {e}")




    def show_rest_settings(self):
        """显示设置休息时间段的界面"""
        self.rest_window = tk.Toplevel(self.root)
        self.rest_window.title("设置休息时间段")
        self.rest_window.geometry("500x500")
        self.rest_window.resizable(False, False)
        
        # 使窗口模态
        self.rest_window.transient(self.root)
        self.rest_window.grab_set()
        
        # 创建设置界面的控件
        settings_frame = ttk.Frame(self.rest_window, padding="15")
        settings_frame.pack(fill=tk.BOTH, expand=True)
        settings_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(settings_frame, text="设置休息时间段", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 15))
        
        # 说明文字
        info_label = ttk.Label(settings_frame, 
                              text="可以设置多个休息时间段，系统会自动扣除休息时间计算实际工作时间",
                              wraplength=400)
        info_label.grid(row=1, column=0, columnspan=4, pady=(0, 15))
        
        # 输入区域
        input_frame = ttk.Frame(settings_frame)
        input_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        # 开始时间输入
        ttk.Label(input_frame, text="开始时间 (HH:MM):").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.start_time_entry = ttk.Entry(input_frame, width=10)
        self.start_time_entry.grid(row=0, column=1, sticky=tk.W, padx=5)
        self.start_time_entry.insert(0, "12:00")
        
        # 结束时间输入
        ttk.Label(input_frame, text="结束时间 (HH:MM):").grid(row=0, column=2, sticky=tk.W, padx=(20, 5))
        self.end_time_entry = ttk.Entry(input_frame, width=10)
        self.end_time_entry.grid(row=0, column=3, sticky=tk.W, padx=5)
        self.end_time_entry.insert(0, "13:00")
        
        # 添加按钮
        add_btn = ttk.Button(input_frame, text="添加休息时间段", 
                           command=self.add_rest_period)
        add_btn.grid(row=1, column=0, columnspan=4, pady=10)

        # 休息时间段列表
        list_frame = ttk.LabelFrame(settings_frame, text="当前休息时间段", padding="10")
        list_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.rest_tree = ttk.Treeview(list_frame, columns=("开始时间", "结束时间", "时长(分钟)"), 
                               show="tree headings", height=8)
        self.rest_tree.column("#0", width=0, stretch=tk.NO)
        self.rest_tree.column("开始时间", width=100, anchor=tk.CENTER)
        self.rest_tree.column("结束时间", width=100, anchor=tk.CENTER)
        self.rest_tree.column("时长(分钟)", width=100, anchor=tk.CENTER)
        
        for col in ("开始时间", "结束时间", "时长(分钟)"):
            self.rest_tree.heading(col, text=col)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.rest_tree.yview)
        self.rest_tree.configure(yscrollcommand=scrollbar.set)
        
        self.rest_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 按钮区域
        button_frame = ttk.Frame(settings_frame)
        button_frame.grid(row=4, column=0, columnspan=4, pady=10)
        
        # 删除选中按钮
        delete_btn = ttk.Button(button_frame, text="删除选中", 
                              command=self.delete_selected_rest)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        # 清空所有按钮
        clear_btn = ttk.Button(button_frame, text="清空所有", 
                             command=self.clear_all_rest)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # 保存按钮
        save_btn = ttk.Button(button_frame, text="保存设置", 
                            command=self.save_rest_settings)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # 取消按钮
        cancel_btn = ttk.Button(button_frame, text="取消", 
                              command=self.rest_window.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # 加载现有休息时间段到树形视图
        self.load_rest_to_tree()

    def add_rest_period(self):
        """添加休息时间段"""
        start_time = self.start_time_entry.get().strip()
        end_time = self.end_time_entry.get().strip()
        
        if not start_time or not end_time:
            messagebox.showwarning("警告", "请输入开始时间和结束时间！")
            return
        
        # 验证时间格式
        try:
            start_dt = datetime.strptime(start_time, "%H:%M")
            end_dt = datetime.strptime(end_time, "%H:%M")
            
            if start_dt >= end_dt:
                messagebox.showwarning("警告", "开始时间必须早于结束时间！")
                return
                
        except ValueError:
            messagebox.showerror("错误", "时间格式不正确，请使用HH:MM格式！")
            return
        
        # 计算时长（分钟）
        duration = (end_dt - start_dt).seconds // 60
        
        # 添加到数据列表
        self.rest_periods.append({
            'start': start_time,
            'end': end_time,
            'duration': duration
        })
        
        # 更新树形视图
        self.rest_tree.insert("", tk.END, values=(start_time, end_time, duration))
        
        # 清空输入框
        self.start_time_entry.delete(0, tk.END)
        self.end_time_entry.delete(0, tk.END)
        
        messagebox.showinfo("成功", f"已添加休息时间段: {start_time} - {end_time} ({duration}分钟)")

    def delete_selected_rest(self):
        """删除选中的休息时间段"""
        selected = self.rest_tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的休息时间段！")
            return
        
        # 从数据列表中删除
        for item in selected:
            values = self.rest_tree.item(item)['values']
            start_time = values[0]
            end_time = values[1]
            
            # 从rest_periods中删除对应的项
            self.rest_periods = [period for period in self.rest_periods 
                               if not (period['start'] == start_time and period['end'] == end_time)]
            
            # 从树形视图中删除
            self.rest_tree.delete(item)
        
        messagebox.showinfo("成功", "已删除选中的休息时间段")

    def clear_all_rest(self):
        """清空所有休息时间段"""
        if not messagebox.askyesno("确认", "确定要清空所有休息时间段吗？"):
            return
        
        # 清空数据列表
        self.rest_periods.clear()
        
        # 清空树形视图
        for item in self.rest_tree.get_children():
            self.rest_tree.delete(item)
        
        messagebox.showinfo("成功", "已清空所有休息时间段")

    def load_rest_to_tree(self):
        """加载现有休息时间段到树形视图"""
        for period in self.rest_periods:
            start_time = period['start']
            end_time = period['end']
            duration = period.get('duration', 0)
            
            self.rest_tree.insert("", tk.END, values=(start_time, end_time, duration))

    def save_rest_settings(self):
        """保存休息时间段设置"""
        # 保存到文件
        if self.save_rest_periods(self.rest_periods):
            messagebox.showinfo("成功", "休息时间段设置已保存！")
            self.rest_window.destroy()
            self.update_rest_count()
            self.refresh_monthly_display()
        else:
            messagebox.showerror("错误", "保存失败！")

    def load_rest_periods(self):
        """加载保存的休息时间段"""
        rest_file = "data/rest_periods.json"
        if os.path.exists(rest_file):
            try:
                with open(rest_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载休息时间段失败: {e}")
        return []

    def save_rest_periods(self, periods):
        """保存休息时间段到文件"""
        os.makedirs("data", exist_ok=True)
        rest_file = "data/rest_periods.json"
        try:
            with open(rest_file, 'w', encoding='utf-8') as f:
                json.dump(periods, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存休息时间段失败: {e}")
            return False

    def update_rest_count(self):
        """更新休息时间段数量显示"""
        count = len(self.rest_periods)
        self.rest_count_var.set(f"已设置 {count} 个休息时间段")

    def calculate_monthly_average(self):
        """计算每个月的平均工作时间（示例数据）"""
        # 这里需要连接数据库获取真实数据
        # 暂时返回示例数据
        return {
            "2024-01": {"total_hours": 160.5, "average": 8.03, "days": 20},
            "2024-02": {"total_hours": 152.0, "average": 7.60, "days": 20},
            "2024-03": {"total_hours": 168.2, "average": 8.41, "days": 20}
        }

    def create_time_display(self, parent, row):
        """创建时间显示区域"""
        time_frame = ttk.Frame(parent)
        time_frame.grid(row=row, column=0, columnspan=3, pady=10)
        
        self.time_var = tk.StringVar()
        time_label = ttk.Label(time_frame, textvariable=self.time_var, 
                              font=("Arial", 14), foreground="blue")
        time_label.pack()
        
        self.date_var = tk.StringVar()
        date_label = ttk.Label(time_frame, textvariable=self.date_var,
                              font=("Arial", 12))
        date_label.pack()
    
    def create_quick_buttons(self, parent, row):
        """创建快速打卡按钮"""
        button_frame = ttk.LabelFrame(parent, text="快速打卡", padding="10")
        button_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # 上班打卡按钮
        self.clock_in_btn = ttk.Button(button_frame, text="上班打卡 (IN)", 
                                      command=self.clock_in)
        self.clock_in_btn.pack(side=tk.LEFT, padx=5)
        
        # 下班打卡按钮
        self.clock_out_btn = ttk.Button(button_frame, text="下班打卡 (OUT)", 
                                       command=self.clock_out)
        self.clock_out_btn.pack(side=tk.LEFT, padx=5)

    def create_custom_section(self, parent, row):
        """创建自定义时间打卡区域"""
        custom_frame = ttk.LabelFrame(parent, text="自定义时间打卡", padding="10")
        custom_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=0)
        # custom_frame.columnconfigure(0, weight=1)
        # custom_frame.columnconfigure(1, weight=1)
        # custom_frame.columnconfigure(2, weight=1)
        # custom_frame.columnconfigure(3, weight=1)
        # custom_frame.columnconfigure(4, weight=1)
        # custom_frame.columnconfigure(5, weight=1)
        
        # 获取当前日期时间
        now = datetime.now()
        
        # 创建年份下拉框
        self.year_combobox = ttk.Combobox(custom_frame, width=5)
        self.year_combobox['values'] = list(range(now.year - 5, now.year + 6))  # 当前年份前后5年
        self.year_combobox.current(5)  # 默认选中当前年份
        self.year_combobox.grid(row=0, column=0, padx=5, pady=5)
        
        # 创建月份下拉框
        self.month_combobox = ttk.Combobox(custom_frame, width=5)
        self.month_combobox['values'] = list(range(1, 13))  # 1到12月
        self.month_combobox.current(now.month - 1)
        self.month_combobox.grid(row=0, column=1, padx=5, pady=5)
        
        # 创建日期下拉框
        self.day_combobox = ttk.Combobox(custom_frame, width=5)
        self.day_combobox['values'] = list(range(1, 32))  # 1到31日
        self.day_combobox.current(now.day - 1)
        self.day_combobox.grid(row=0, column=2, padx=5, pady=5)
        
        # 创建小时下拉框
        self.hour_combobox = ttk.Combobox(custom_frame, width=5)
        self.hour_combobox['values'] = list(range(24))  # 0到23小时
        self.hour_combobox.current(now.hour)
        self.hour_combobox.grid(row=0, column=3, padx=5, pady=5)
        
        # 创建分钟下拉框
        self.minute_combobox = ttk.Combobox(custom_frame, width=5)
        self.minute_combobox['values'] = list(range(60))  # 0到59分钟
        self.minute_combobox.current(now.minute)
        self.minute_combobox.grid(row=0, column=4, padx=5, pady=5)
        
        # # 创建秒下拉框
        # self.second_combobox = ttk.Combobox(custom_frame, width=5)
        # self.second_combobox['values'] = list(range(60))  # 0到59秒
        # self.second_combobox.current(now.second)
        # self.second_combobox.grid(row=0, column=5, padx=5, pady=5)
        
        # 类型选择
        type_frame = ttk.Frame(custom_frame)
        type_frame.grid(row=0, column=6, columnspan=6, sticky=tk.W, padx=(20, 5))
        self.record_type_var = tk.StringVar(value="in")
        ttk.Radiobutton(type_frame, text="上班(IN)", variable=self.record_type_var, value="in").pack(side=tk.LEFT)
        ttk.Radiobutton(type_frame, text="下班(OUT)", variable=self.record_type_var, value="out").pack(side=tk.LEFT, padx=5)
        
        # 自定义打卡按钮
        custom_btn = ttk.Button(custom_frame, text="自定义打卡", command=self.custom_clock)
        # custom_btn.grid(row=3, column=0, columnspan=6, pady=5, padx=20, sticky=(tk.W, tk.E))
        custom_btn.grid(row=0, column=7, padx=320, pady=5)
        
    def query_monthly_statistics(self):
        """查询月份统计"""
        try:
            year = self.year_var.get()
            month = self.month_var.get()
            
            if not year and month != '全部':
                messagebox.showwarning("警告", "请选择年份！")
                return
            
            # 清空现有数据
            for item in self.monthly_tree.get_children():
                self.monthly_tree.delete(item)
            
            # 获取统计信息
            monthly_stats = self.clock_manager.get_monthly_statistics(
                year if year else None, 
                month if month != '全部' else None,
                self.rest_periods
            )
            
            if not monthly_stats:
                messagebox.showinfo("提示", "没有找到相关统计信息！")
                return
            
            # 显示统计结果
            for stat in monthly_stats:
                self.monthly_tree.insert("", tk.END, values=(
                    stat['month'],
                    stat['work_days'],
                    f"{stat['total_hours']:.2f}",
                    f"{stat['avg_hours']:.2f}",
                    stat['remark']
                ))
            
            messagebox.showinfo("完成", f"共找到 {len(monthly_stats)} 个月的统计信息")
            
        except Exception as e:
            messagebox.showerror("错误", f"查询失败: {e}")

    def refresh_monthly_statistics(self):
        """刷新月份统计"""
        self.query_monthly_statistics()

    def export_monthly_statistics(self):
        """导出月份统计到CSV文件"""
        try:
            # 获取当前显示的数据
            items = self.monthly_tree.get_children()
            if not items:
                messagebox.showwarning("警告", "没有数据可导出！")
                return
            
            filename = f"月度统计_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # 写入表头
                writer.writerow(["月份", "工作日数", "总工时(小时)", "平均每日工时(小时)", "备注"])
                
                # 写入数据
                for item in items:
                    values = self.monthly_tree.item(item)['values']
                    writer.writerow(values)
            
            messagebox.showinfo("成功", f"统计信息已导出到: {filename}")
            
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {e}")

    def create_monthly_statistics_tab(self, tab_control):
        """创建月份统计标签页"""
        monthly_tab = ttk.Frame(tab_control)
        tab_control.add(monthly_tab, text="月份统计")
        
        # 创建主框架
        main_frame = ttk.Frame(monthly_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 查询条件区域 - 第0行
        query_frame = ttk.LabelFrame(main_frame, text="查询条件", padding=10)
        query_frame.grid(row=0, column=0, sticky=tk.EW, padx=5, pady=5)
        
        # 年份选择
        ttk.Label(query_frame, text="年份:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.year_var = tk.StringVar(value=str(datetime.now().year))
        year_combobox = ttk.Combobox(query_frame, textvariable=self.year_var, 
                                    values=[str(year) for year in range(2020, 2031)], width=10)
        year_combobox.grid(row=0, column=1, padx=5, pady=5)
        
        # 月份选择
        ttk.Label(query_frame, text="月份:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.month_var = tk.StringVar(value='全部')
        month_combobox = ttk.Combobox(query_frame, textvariable=self.month_var, 
                                    values=['全部'] + [f"{month:02d}" for month in range(1, 13)], width=10)
        month_combobox.grid(row=0, column=3, padx=5, pady=5)
        
        # 按钮区域 - 第1行
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        # 查询按钮
        query_btn = ttk.Button(button_frame, text="查询统计", command=self.query_monthly_statistics)
        query_btn.grid(row=0, column=0, padx=5)
        
        # 刷新按钮
        refresh_btn = ttk.Button(button_frame, text="刷新", command=self.refresh_monthly_statistics)
        refresh_btn.grid(row=0, column=1, padx=5)
        
        # 统计结果显示区域 - 第2行
        stats_frame = ttk.LabelFrame(main_frame, text="月份统计结果", padding=10)
        stats_frame.grid(row=2, column=0, sticky=tk.NSEW, padx=5, pady=5)
        
        # 配置网格权重，使统计区域可以扩展
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_rowconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(0, weight=1)
        
        # 创建Treeview显示月份统计
        columns = ("月份", "工作日数", "总工时", "平均每日工时", "备注")
        self.monthly_tree = ttk.Treeview(stats_frame, columns=columns, show="tree headings", height=15)
        
        # 设置列宽
        self.monthly_tree.column("月份", width=100, anchor=tk.CENTER)
        self.monthly_tree.column("工作日数", width=80, anchor=tk.CENTER)
        self.monthly_tree.column("总工时", width=100, anchor=tk.CENTER)
        self.monthly_tree.column("平均每日工时", width=100, anchor=tk.CENTER)
        self.monthly_tree.column("备注", width=150, anchor=tk.W)
        
        # 设置表头
        self.monthly_tree.heading("月份", text="月份")
        self.monthly_tree.heading("工作日数", text="工作日数")
        self.monthly_tree.heading("总工时", text="总工时(小时)")
        self.monthly_tree.heading("平均每日工时", text="平均每日(小时)")
        self.monthly_tree.heading("备注", text="备注")
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=self.monthly_tree.yview)
        self.monthly_tree.configure(yscrollcommand=scrollbar.set)
        
        # 使用grid布局
        self.monthly_tree.grid(row=0, column=0, sticky=tk.NSEW)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
        
        # 底部信息区域 - 第3行
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=3, column=0, sticky=tk.EW, padx=5, pady=5)
        
        # 统计摘要信息
        self.summary_var = tk.StringVar(value="请点击查询按钮查看统计信息")
        summary_label = ttk.Label(info_frame, textvariable=self.summary_var, foreground="blue")
        summary_label.pack(side=tk.LEFT)
        
        return monthly_tab

    def update_time_display(self):
        """更新时间显示"""
        now = datetime.now()
        self.time_var.set(f"当前时间: {now.strftime('%H:%M:%S')}")
        self.date_var.set(f"当前日期: {now.strftime('%Y年%m月%d日 %A')}")
        self.root.after(1000, self.update_time_display)
    
    def clock_in(self):
        """上班打卡"""
        if self.clock_manager.clock_in("快速上班打卡"):
            self.refresh_display()
        else:
            messagebox.showerror("错误", "打卡失败！")
    
    def clock_out(self):
        """下班打卡"""
        if self.clock_manager.clock_out("快速下班打卡"):
            self.refresh_display()
        else:
            messagebox.showerror("错误", "打卡失败！")

    def custom_clock(self):
        """自定义时间打卡"""
        
        # 获取年月日时分秒
        year = self.year_combobox.get()
        month = self.month_combobox.get()
        day = self.day_combobox.get()
        hour = self.hour_combobox.get()
        minute = self.minute_combobox.get()
        second = 0
        
        # 组合日期时间字符串
        custom_time = f"{year}-{month}-{day} {hour}:{minute}:{second}"

        try:
            # 尝试解析时间，验证格式是否正确
            datetime.strptime(custom_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            messagebox.showwarning("警告", "时间格式不正确！请使用 YYYY-MM-DD HH:MM:SS 格式")
            return
        
        record_type = self.record_type_var.get()
        notes = "自定义打卡"

        print(f"sss{custom_time} {record_type} {notes}")
        
        if not custom_time:
            messagebox.showwarning("警告", "请输入时间！")
            return
        
        if self.clock_manager.custom_clock(custom_time, record_type, notes):
            self.refresh_display()
        else:
            messagebox.showerror("错误", "打卡失败！请检查时间格式")