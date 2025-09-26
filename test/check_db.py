import sqlite3

# 连接到 SQLite 数据库
conn = sqlite3.connect('../data/clock_in.db')
cursor = conn.cursor()

# 查询所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# 查询表的结构
table_name = 'clock_records'
cursor.execute(f"PRAGMA table_info({table_name});")
columns = cursor.fetchall()
print(f"Columns in {table_name}:", columns)

# 查询表中的数据
cursor.execute(f"SELECT * FROM {table_name};")
rows = cursor.fetchall()
for row in rows:
    print(row)

# 关闭连接
conn.close()