import sqlite3
import os
import csv

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    ''')
    
    # 创建电影评论表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comment_movie (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            movie_id INTEGER NOT NULL,
            comment_id INTEGER NOT NULL UNIQUE,
            content TEXT,
            rating REAL
        )
    ''')
    
    conn.commit()
    conn.close()

def import_comment_movie_data():
    # 检查文件是否存在
    csv_path = os.path.join('movies_data', 'comment_movie.csv')
    if not os.path.exists(csv_path):

        return True
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查是否已经导入过数据
        cursor.execute('SELECT COUNT(*) FROM comment_movie')
        count = cursor.fetchone()[0]
        if count > 0:

            conn.close()
            return True
        
        # 读取CSV文件并导入数据
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            row_count = 0
            
            for row in reader:
                try:
                    # 转换数据类型
                    movie_id = int(row['MOVIE_ID'])
                    comment_id = int(row['COMMENT_ID'])
                    rating = float(row['RATING']) if row['RATING'] else None
                    
                    # 插入数据
                    cursor.execute('''
                        INSERT INTO comment_movie (name, movie_id, comment_id, content, rating)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (row['NAME'], movie_id, comment_id, row['CONTENT'], rating))
                    
                    row_count += 1
                    
                except ValueError as e:

                    continue
                except sqlite3.IntegrityError:
                    # 忽略重复的comment_id
                    continue
        
        conn.commit()

        conn.close()
        return True
        
    except Exception as e:

        if 'conn' in locals():
            conn.close()
        return False

def get_comment_movie_data(page=1, per_page=10, comment_id=None, movie_name=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 构建查询条件
    conditions = []
    params = []
    
    if comment_id is not None and comment_id != '':
        try:
            conditions.append('comment_id = ?')
            params.append(int(comment_id))
        except ValueError:
            pass  # 如果comment_id不是有效数字，忽略此条件
    
    if movie_name is not None and movie_name != '':
        conditions.append('name LIKE ?')
        params.append(f'%{movie_name}%')
    
    # 构建WHERE子句
    where_clause = 'WHERE ' + ' AND '.join(conditions) if conditions else ''
    
    # 查询总记录数
    count_query = f'SELECT COUNT(*) FROM comment_movie {where_clause}'
    cursor.execute(count_query, params)
    total = cursor.fetchone()[0]
    
    # 计算偏移量
    offset = (page - 1) * per_page
    
    # 查询当前页数据
    data_query = f'''
        SELECT name, comment_id, content, rating 
        FROM comment_movie 
        {where_clause}
        LIMIT ? OFFSET ?
    '''
    cursor.execute(data_query, params + [per_page, offset])
    
    data = cursor.fetchall()
    conn.close()
    
    return data, total

def get_random_comment_data(limit=2000, comment_id=None, movie_name=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 构建查询条件
    conditions = []
    params = []
    
    if comment_id is not None and comment_id != '':
        try:
            conditions.append('comment_id = ?')
            params.append(int(comment_id))
        except ValueError:
            pass
    
    if movie_name is not None and movie_name != '':
        conditions.append('name LIKE ?')
        params.append(f'%{movie_name}%')
    
    where_clause = 'WHERE ' + ' AND '.join(conditions) if conditions else ''
    
    query = f'''
        SELECT name, comment_id, content, rating
        FROM comment_movie
        {where_clause}
        ORDER BY RANDOM()
        LIMIT ?
    '''
    cursor.execute(query, params + [int(limit)])
    data = cursor.fetchall()
    conn.close()
    return data

def get_user_by_username(username):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

def get_user_by_email(email):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return user

def create_user(username, password, email):
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                     (username, password, email))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# 用户设置相关函数
def update_user_password(user_id, new_password):
    conn = get_db_connection()
    try:
        conn.execute('UPDATE users SET password = ? WHERE id = ?',
                     (new_password, user_id))
        conn.commit()
        return True
    except Exception as e:

        return False
    finally:
        conn.close()

def update_user_email(user_id, new_email):
    conn = get_db_connection()
    try:
        conn.execute('UPDATE users SET email = ? WHERE id = ?',
                     (new_email, user_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # 邮箱已存在
        return False
    except Exception as e:

        return False
    finally:
        conn.close()

# 演员导演画像查询函数
def search_character_simple(keyword=None, page=1, per_page=10):
    """
    模糊查询演员导演的简单画像信息
    :param keyword: 搜索关键词，用于模糊匹配人物姓名
    :param page: 当前页码
    :param per_page: 每页显示的记录数
    :return: 查询结果列表和总记录数
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 构建查询条件
    conditions = []
    params = []
    
    if keyword is not None and keyword != '':
        conditions.append('character_name LIKE ?')
        params.append(f'%{keyword}%')
    
    # 构建WHERE子句
    where_clause = 'WHERE ' + ' AND '.join(conditions) if conditions else ''
    
    # 查询总记录数
    count_query = f'SELECT COUNT(*) FROM character_simple_analysis {where_clause}'
    cursor.execute(count_query, params)
    total = cursor.fetchone()[0]
    
    # 计算偏移量
    offset = (page - 1) * per_page
    
    # 查询当前页数据
    data_query = f'''
        SELECT * 
        FROM character_simple_analysis 
        {where_clause}
        ORDER BY character_id
        LIMIT ? OFFSET ?
    '''
    cursor.execute(data_query, params + [per_page, offset])
    
    data = cursor.fetchall()
    conn.close()
    
    return data, total

# 获取演员导演详细信息函数
def get_character_details(character_id):
    """
    根据character_id获取演员导演的详细信息
    :param character_id: 演员导演的唯一标识
    :return: 演员导演的详细信息
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 查询详细信息
    cursor.execute('''
        SELECT * 
        FROM character_analysis 
        WHERE character_id = ?
    ''', (character_id,))
    
    data = cursor.fetchone()
    conn.close()
    
    return data

# 评论时间段可视化相关函数

def get_comments_by_year(year=None):
    """
    查询按年份统计的评论数据
    :param year: 可选，指定年份进行过滤
    :return: 评论数据列表
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if year:
        try:
            # 尝试转换为整数，确保与数据库字段类型匹配
            cursor.execute('SELECT * FROM comments_by_year WHERE year = ?', (int(year),))
        except ValueError:
            # 如果转换失败，使用原字符串
            cursor.execute('SELECT * FROM comments_by_year WHERE year = ?', (year,))
    else:
        cursor.execute('SELECT * FROM comments_by_year')
    
    data = cursor.fetchall()
    conn.close()
    return data

def get_comments_by_month(year=None, month=None):
    """
    查询按月份统计的评论数据
    :param year: 可选，指定年份进行过滤
    :param month: 可选，指定月份进行过滤
    :return: 评论数据列表
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    conditions = []
    params = []
    
    if year:
        conditions.append('year = ?')
        try:
            # 尝试转换为整数，确保与数据库字段类型匹配
            params.append(int(year))
        except ValueError:
            # 如果转换失败，使用原字符串
            params.append(year)
    
    if month:
        conditions.append('month = ?')
        try:
            # 尝试转换为整数，确保与数据库字段类型匹配
            params.append(int(month))
        except ValueError:
            # 如果转换失败，使用原字符串
            params.append(month)
    
    where_clause = 'WHERE ' + ' AND '.join(conditions) if conditions else ''
    
    query = f'SELECT * FROM comments_by_month {where_clause} ORDER BY year, month'
    cursor.execute(query, params)
    
    data = cursor.fetchall()
    conn.close()
    return data

def get_month_hour_comments(year=None, month=None, hour_range=None):
    """
    查询按月小时统计的评论数据
    :param year: 可选，指定年份进行过滤
    :param month: 可选，指定月份进行过滤
    :param hour_range: 可选，指定小时范围进行过滤
    :return: 评论数据列表
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    conditions = []
    params = []
    
    if year:
        conditions.append('year = ?')
        try:
            # 尝试转换为整数，确保与数据库字段类型匹配
            params.append(int(year))
        except ValueError:
            # 如果转换失败，使用原字符串
            params.append(year)
        
    if month:
        conditions.append('month = ?')
        try:
            # 尝试转换为整数，确保与数据库字段类型匹配
            params.append(int(month))
        except ValueError:
            # 如果转换失败，使用原字符串
            params.append(month)
    
    if hour_range:
        conditions.append('hour_range = ?')
        params.append(hour_range)
    
    where_clause = 'WHERE ' + ' AND '.join(conditions) if conditions else ''
    
    query = f'SELECT * FROM month_hour_comments {where_clause} ORDER BY year, month, hour_range'
    cursor.execute(query, params)
    
    data = cursor.fetchall()
    conn.close()
    return data

def get_year_hour_comments(year=None, hour_range=None):
    """
    查询按年小时统计的评论数据
    :param year: 可选，指定年份进行过滤
    :param hour_range: 可选，指定小时范围进行过滤
    :return: 评论数据列表
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    conditions = []
    params = []
    
    if year:
        conditions.append('year = ?')
        try:
            # 尝试转换为整数，确保与数据库字段类型匹配
            params.append(int(year))
        except ValueError:
            # 如果转换失败，使用原字符串
            params.append(year)
    
    if hour_range:
        conditions.append('hour_range = ?')
        params.append(hour_range)
    
    where_clause = 'WHERE ' + ' AND '.join(conditions) if conditions else ''
    
    query = f'SELECT * FROM year_hour_comments {where_clause} ORDER BY year, hour_range'
    cursor.execute(query, params)
    
    data = cursor.fetchall()
    conn.close()
    return data

def get_all_years():
    """
    获取所有可用的年份列表
    :return: 年份列表
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 从comments_by_year表获取所有年份
    try:
        cursor.execute('SELECT DISTINCT year FROM comments_by_year ORDER BY year')
        rows = cursor.fetchall()
        years = [str(row[0]) if row[0] is not None else '' for row in rows]
    except Exception:
        # 如果查询失败，返回空列表
        years = []
    
    conn.close()
    return years

def get_all_months():
    """
    获取所有月份列表
    :return: 月份列表
    """
    return [str(i).zfill(2) for i in range(1, 13)]  # 返回01-12

def get_all_hours():
    """
    获取所有小时范围列表
    :return: 小时范围列表
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 从year_hour_comments表获取所有小时范围
    try:
        cursor.execute('SELECT DISTINCT hour_range FROM year_hour_comments ORDER BY hour_range')
        rows = cursor.fetchall()
        hours = [str(row[0]) if row[0] is not None else '' for row in rows]
    except Exception:
        # 如果查询失败，返回默认的小时列表
        hours = [f"{i:02d}" for i in range(24)]
    
    conn.close()
    return hours

# 电影数据分析相关函数

def get_movie_languages_data(limit=None):
    """
    获取电影语言分布数据
    :param limit: 返回前N条数据，如果为None则返回所有数据
    :return: 语言分布数据列表
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    if limit is None:
        cursor.execute('SELECT LANGUAGES, COUNT(*) as count FROM movie GROUP BY LANGUAGES ORDER BY count DESC')
    else:
        cursor.execute('SELECT LANGUAGES, COUNT(*) as count FROM movie GROUP BY LANGUAGES ORDER BY count DESC LIMIT ?', (limit,))
    data = cursor.fetchall()
    conn.close()
    return data

def get_movie_regions_data(limit=None):
    """
    获取电影地区分布数据
    :param limit: 返回前N条数据，如果为None则返回所有数据
    :return: 地区分布数据列表
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    if limit is None:
        cursor.execute('SELECT REGIONS, COUNT(*) as count FROM movie GROUP BY REGIONS ORDER BY count DESC')
    else:
        cursor.execute('SELECT REGIONS, COUNT(*) as count FROM movie GROUP BY REGIONS ORDER BY count DESC LIMIT ?', (limit,))
    data = cursor.fetchall()
    conn.close()
    return data

def get_movie_years_data(limit=None):
    """
    获取电影年份分布数据
    :param limit: 返回前N条数据，如果为None则返回所有数据
    :return: 年份分布数据列表
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    if limit is None:
        cursor.execute('SELECT YEAR, COUNT(*) as count FROM movie GROUP BY YEAR ORDER BY YEAR DESC')
    else:
        cursor.execute('SELECT YEAR, COUNT(*) as count FROM movie GROUP BY YEAR ORDER BY YEAR DESC LIMIT ?', (limit,))
    data = cursor.fetchall()
    conn.close()
    return data

def get_movie_score_duration_data():
    """
    获取电影评分和时长数据，用于散点图分析，过滤掉时长超过1000分钟的电影
    :return: 包含原始数据和分析结果的字典
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取原始数据，过滤掉评分超过10分的电影（这些可能是数据错误）
    cursor.execute('SELECT DOUBAN_SCORE, MINS, NAME FROM movies_score_mins WHERE DOUBAN_SCORE IS NOT NULL AND MINS IS NOT NULL AND MINS <= 1000 AND DOUBAN_SCORE <= 10 ORDER BY NAME')
    raw_data = cursor.fetchall()
    
    conn.close()
    
    # 进行深入分析
    analysis_result = analyze_score_duration_relationship(raw_data)
    
    return {
        'raw_data': raw_data,
        'analysis': analysis_result
    }


def analyze_score_duration_relationship(data):
    """
    深入分析电影评分与时长的关系
    :param data: 原始评分和时长数据
    :return: 分析结果字典
    """
    if not data:
        return {
            'duration_buckets': [],
            'correlation': 0,
            'trend_line': None,
            'outliers': []
        }
    
    # 1. 按时长区间分组统计
    duration_buckets = {
        '0-60分钟': [],
        '61-90分钟': [],
        '91-120分钟': [],
        '121-150分钟': [],
        '151-180分钟': [],
        '181+分钟': []
    }
    
    # 提取评分和时长列表用于后续计算
    scores = []
    durations = []
    
    for row in data:
        score = float(row['DOUBAN_SCORE'])
        duration = float(row['MINS'])
        name = row['NAME']
        
        scores.append(score)
        durations.append(duration)
        
        # 分配到不同的时长区间
        if duration <= 60:
            duration_buckets['0-60分钟'].append({'score': score, 'name': name})
        elif duration <= 90:
            duration_buckets['61-90分钟'].append({'score': score, 'name': name})
        elif duration <= 120:
            duration_buckets['91-120分钟'].append({'score': score, 'name': name})
        elif duration <= 150:
            duration_buckets['121-150分钟'].append({'score': score, 'name': name})
        elif duration <= 180:
            duration_buckets['151-180分钟'].append({'score': score, 'name': name})
        else:
            duration_buckets['181+分钟'].append({'score': score, 'name': name})
    
    # 计算每个时长区间的统计信息
    bucket_stats = []
    for bucket, movies in duration_buckets.items():
        if movies:
            avg_score = sum(m['score'] for m in movies) / len(movies)
            count = len(movies)
            bucket_stats.append({
                'bucket': bucket,
                'avg_score': round(avg_score, 2),
                'count': count,
                'movies': movies
            })
    
    # 2. 计算相关系数
    correlation = calculate_correlation(scores, durations)
    
    # 3. 计算趋势线
    trend_line = calculate_linear_regression(scores, durations)
    
    # 4. 识别异常值（使用Z-score方法）
    outliers = identify_outliers(scores, durations, data)
    
    return {
        'duration_buckets': bucket_stats,
        'correlation': round(correlation, 4),
        'trend_line': trend_line,
        'outliers': outliers
    }


def calculate_correlation(x, y):
    """
    计算皮尔逊相关系数
    :param x: x值列表
    :param y: y值列表
    :return: 相关系数
    """
    if len(x) != len(y) or len(x) == 0:
        return 0
    
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_x2 = sum(i*i for i in x)
    sum_y2 = sum(i*i for i in y)
    sum_xy = sum(i*j for i, j in zip(x, y))
    
    numerator = n * sum_xy - sum_x * sum_y
    denominator = ((n * sum_x2 - sum_x**2) * (n * sum_y2 - sum_y**2)) ** 0.5
    
    if denominator == 0:
        return 0
    
    return numerator / denominator


def calculate_linear_regression(x, y):
    """
    计算线性回归（趋势线）
    :param x: x值列表（时长）
    :param y: y值列表（评分）
    :return: 包含斜率、截距和预测值的字典
    """
    if len(x) != len(y) or len(x) == 0:
        return None
    
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(i*j for i, j in zip(x, y))
    sum_x2 = sum(i*i for i in x)
    
    denominator = n * sum_x2 - sum_x**2
    if denominator == 0:
        return None
    
    slope = (n * sum_xy - sum_x * sum_y) / denominator
    intercept = (sum_y - slope * sum_x) / n
    
    # 计算趋势线上的点
    min_x = min(x)
    max_x = max(x)
    trend_points = [
        {'x': min_x, 'y': slope * min_x + intercept},
        {'x': max_x, 'y': slope * max_x + intercept}
    ]
    
    return {
        'slope': round(slope, 4),
        'intercept': round(intercept, 4),
        'equation': f'y = {round(slope, 4)}x + {round(intercept, 4)}',
        'points': trend_points
    }


def identify_outliers(x, y, original_data, threshold=2):
    """
    使用Z-score方法识别异常值
    :param x: x值列表（时长）
    :param y: y值列表（评分）
    :param original_data: 原始数据列表，包含电影名称
    :param threshold: Z-score阈值，默认2
    :return: 异常值列表
    """
    if len(x) != len(y) or len(x) == 0:
        return []
    
    # 计算平均评分，排除评分超过10分的电影
    valid_scores = [score for score in y if score <= 10]
    if not valid_scores:
        return []
        
    avg_score = sum(valid_scores) / len(valid_scores)
    std_score = (sum((score - avg_score) ** 2 for score in valid_scores) / len(valid_scores)) ** 0.5
    
    outliers = []
    
    for i in range(len(x)):
        score = y[i]
        duration = x[i]
        row = original_data[i]
        
        # 跳过评分超过10分的电影，这些可能是数据错误
        if score > 10:
            continue
        
        # 计算Z-score
        if std_score > 0:
            z_score = (score - avg_score) / std_score
        else:
            z_score = 0
        
        # 识别异常值
        if abs(z_score) > threshold:
            outliers.append({
                'name': row['NAME'],
                'score': score,
                'duration': duration,
                'z_score': round(z_score, 2)
            })
    
    return outliers

def get_movie_score_genres_data():
    """
    获取电影评分和类型数据，用于分析评分与类型的关系
    :return: 电影评分和类型数据列表
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT DOUBAN_SCORE, GENRES, NAME FROM movies_douban_genres WHERE DOUBAN_SCORE IS NOT NULL AND GENRES IS NOT NULL ORDER BY NAME')
    data = cursor.fetchall()
    conn.close()
    return data

def import_csv_data_from_directory(directory):
    """
    导入目录下所有CSV文件到SQLite数据库，表名以文件名命名
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 确保目录存在
    if not os.path.exists(directory):

        conn.close()
        return False
    
    try:
        # 获取目录下所有CSV文件
        csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
        
        for csv_file in csv_files:
            file_path = os.path.join(directory, csv_file)
            table_name = os.path.splitext(csv_file)[0]  # 去除.csv扩展名作为表名
            

            
            # 读取CSV文件
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader)  # 获取头部信息
                
                # 根据头部创建表结构
                columns = []
                for i, header in enumerate(headers):
                    # 处理列名中的特殊字符
                    clean_header = header.replace(' ', '_').replace('-', '_').replace('.', '_')
                    if i == 0:
                        # MOVIE_ID作为主键，设置为INTEGER类型
                        columns.append(f"{clean_header} INTEGER PRIMARY KEY")
                    elif clean_header in ['DOUBAN_SCORE', 'MINS']:
                        # DOUBAN_SCORE和MINS字段设置为REAL类型
                        columns.append(f"{clean_header} REAL")
                    else:
                        # 其他字段设置为TEXT类型
                        columns.append(f"{clean_header} TEXT")
                
                create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
                cursor.execute(create_table_sql)

                
                # 导入数据
                insert_sql = f"INSERT OR REPLACE INTO {table_name} VALUES ({', '.join(['?' for _ in headers])})"
                row_count = 0
                
                for row in reader:
                    cursor.execute(insert_sql, row)
                    row_count += 1
                

        
        conn.commit()

        return True
    
    except Exception as e:

        conn.rollback()
        return False
    
    finally:
        conn.close()
