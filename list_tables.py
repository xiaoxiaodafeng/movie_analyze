#!/usr/bin/env python3
# 查询数据库中的所有表名

import sqlite3

if __name__ == '__main__':
    try:
        # 连接到数据库
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # 查询所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = cursor.fetchall()
        
        print("数据库中的表：")
        for table in tables:
            print(f"- {table[0]}")
            
            # 可选：显示表结构
            cursor.execute(f"PRAGMA table_info({table[0]});")
            columns = cursor.fetchall()
            print("  表结构：")
            for column in columns:
                print(f"  - {column[1]} ({column[2]})")
            print()
        
    except Exception as e:
        print(f"查询表名时出错: {e}")
    finally:
        conn.close()
