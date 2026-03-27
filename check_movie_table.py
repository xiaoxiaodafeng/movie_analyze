#!/usr/bin/env python3
"""
检查movies_score_mins表是否存在以及数据是否导入成功
"""

import sqlite3

# 连接到数据库
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

print("检查数据库表...")

# 检查所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("数据库中的表:")
for table in tables:
    print(f"  - {table[0]}")

# 检查movies_score_mins表是否存在
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='movies_score_mins';")
table_exists = cursor.fetchone() is not None

if table_exists:
    print("\nmovies_score_mins表存在")
    
    # 检查表结构
    cursor.execute("PRAGMA table_info(movies_score_mins);")
    columns = cursor.fetchall()
    print("表结构:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # 检查数据行数
    cursor.execute("SELECT COUNT(*) FROM movies_score_mins;")
    row_count = cursor.fetchone()[0]
    print(f"数据行数: {row_count}")
    
    # 显示前10条数据
    print("\n前10条数据:")
    cursor.execute("SELECT * FROM movies_score_mins LIMIT 10;")
    rows = cursor.fetchall()
    for row in rows:
        print(f"  - {row}")
else:
    print("\nmovies_score_mins表不存在")

# 关闭连接
conn.close()