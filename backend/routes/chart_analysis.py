from flask import session, render_template, request, redirect, url_for
from backend.db.database import (
    get_comments_by_year, 
    get_comments_by_month, 
    get_month_hour_comments, 
    get_year_hour_comments,
    get_all_years,
    get_all_months,
    get_all_hours
)

def register_chart_analysis_routes(app):
    @app.route('/chart_analysis', methods=['GET', 'POST'])
    def chart_analysis():
        if 'username' not in session:
            return redirect(url_for('auth'))
        
        # 获取所有可用的年份、月份和小时选项
        all_years = get_all_years()
        all_months = get_all_months()
        all_hours = get_all_hours()
        
        # 获取各个图表的筛选参数，优先从表单获取，否则保持当前状态
        # 第一个图表：无筛选条件，始终查询所有年份数据
        comments_by_year_data = get_comments_by_year(None)
        
        # 初始化所有筛选参数
        month_year = None
        month_hour_year = None
        month_hour_month = None
        year_hour_year = None
        scroll_target = None
        
        # 从请求中获取所有可能的筛选参数
        if request.method == 'POST':
            month_year = request.form.get('month_year')
            month_hour_year = request.form.get('month_hour_year')
            month_hour_month = request.form.get('month_hour_month')
            year_hour_year = request.form.get('year_hour_year')
            scroll_target = request.form.get('scroll_target')
        
        # 确保参数类型正确
        month_year = month_year if month_year != '' else None
        month_hour_year = month_hour_year if month_hour_year != '' else None
        month_hour_month = month_hour_month if month_hour_month != '' else None
        year_hour_year = year_hour_year if year_hour_year != '' else None
        allowed_targets = {'yearChart', 'monthChart', 'monthHourChart', 'yearHourChart'}
        scroll_target = scroll_target if scroll_target in allowed_targets else None
        
        # 查询数据
        comments_by_month_data = get_comments_by_month(month_year, None)
        month_hour_data = get_month_hour_comments(month_hour_year, month_hour_month)
        year_hour_data = get_year_hour_comments(year_hour_year)
        
        # 将sqlite3.Row对象转换为字典，确保JSON可序列化
        comments_by_year_data = [dict(row) for row in comments_by_year_data]
        comments_by_month_data = [dict(row) for row in comments_by_month_data]
        month_hour_data = [dict(row) for row in month_hour_data]
        year_hour_data = [dict(row) for row in year_hour_data]
        
        # 格式化数据供前端图表使用，确保所有数据都是JSON可序列化的类型
        # 1. 按年份统计的数据（折线图）- 无筛选条件
        year_labels = []
        year_values = []
        for row in comments_by_year_data:
                try:
                    year = str(row.get('year', ''))
                    count = int(row.get('comments_count', 0)) if row.get('comments_count') else 0
                    if year:
                        year_labels.append(year)
                        year_values.append(count)
                except (ValueError, TypeError):
                    continue
        year_chart_data = {
            'labels': year_labels,
            'values': year_values
        }
        
        # 2. 按月份统计的数据 - 仅年份筛选
        month_labels = []
        month_values = []
        
        # 如果选择了特定年份，确保显示1-12月的数据
        if month_year:
            # 创建一个字典来存储每个月的数据
            month_data_dict = {}
            for i in range(1, 13):
                month_data_dict[f"{i:02d}"] = 0  # 初始化所有月份为0
            
            # 填充数据库中的数据
            for row in comments_by_month_data:
                try:
                    # 获取数据库中的年份和月份，处理不同类型
                    db_year = row.get('year', '')
                    db_month = row.get('month', '')
                    
                    # 确保年份比较时类型一致
                    year_match = False
                    if isinstance(db_year, int):
                        year_match = db_year == int(month_year)
                    else:
                        year_match = str(db_year) == month_year
                    
                    # 处理月份格式，无论是整数还是字符串
                    if isinstance(db_month, int):
                        month_key = f"{db_month:02d}"
                    else:
                        month_key = str(db_month).zfill(2)
                    
                    # 获取评论数量
                    count = int(row.get('comments_count', 0)) if row.get('comments_count') else 0
                    
                    # 更新对应月份的数据
                    if year_match and month_key in month_data_dict:
                        month_data_dict[month_key] = count
                except (ValueError, TypeError):
                    continue
            
            # 生成图表数据，确保1-12月都有数据
            for month in sorted(month_data_dict.keys()):
                month_labels.append(f"{month_year}-{month}")
                month_values.append(month_data_dict[month])
        else:
            # 如果没有选择年份，显示所有年份的月份数据
            for row in comments_by_month_data:
                try:
                    year = str(row.get('year', ''))
                    month = str(row.get('month', '')).zfill(2)  # 确保月份是两位数
                    count = int(row.get('comments_count', 0)) if row.get('comments_count') else 0
                    if year and month:
                        month_labels.append(f"{year}-{month}")
                        month_values.append(count)
                except (ValueError, TypeError):
                    continue
        
        month_chart_data = {
            'labels': month_labels,
            'values': month_values
        }
        
        # 3. 按月小时统计的数据 - 年份和月份筛选
        month_hour_labels = []
        month_hour_values = []
        
        # 确保显示00到23小时的数据
        # 创建一个字典来存储每个小时的数据，使用完整时间段作为键
        hour_data_dict = {}
        for i in range(24):
            hour_data_dict[f"{i:02d}:00 - {i+1:02d}:00"] = 0  # 初始化所有小时为0
        
        # 填充数据库中的数据
        if month_hour_year:
            for row in month_hour_data:
                try:
                    hour_range = str(row.get('hour_range', ''))  # 使用完整的时间段格式
                    count = int(row.get('total_comments', 0)) if row.get('total_comments') else 0
                    
                    # 尝试匹配小时范围格式
                    if hour_range in hour_data_dict:
                        # 如果格式完全匹配，直接使用
                        hour_data_dict[hour_range] = count
                    else:
                        # 尝试解析小时范围，提取起始小时
                        try:
                            # 处理格式如"10"或"10:00"的情况
                            if hour_range.isdigit():
                                hour = int(hour_range)
                            else:
                                # 处理格式如"10:00"的情况
                                hour = int(hour_range.split(':')[0])
                            
                            # 确保小时在0-23范围内
                            if 0 <= hour < 24:
                                key = f"{hour:02d}:00 - {hour+1:02d}:00"
                                hour_data_dict[key] = count
                        except (ValueError, IndexError):
                            # 如果解析失败，跳过此数据
                            continue
                except (ValueError, TypeError):
                    # 跳过无效数据
                    continue
        
        # 生成图表数据，确保00-23小时都有数据
        for hour in sorted(hour_data_dict.keys()):
            month_hour_labels.append(hour)
            month_hour_values.append(hour_data_dict[hour])
        
        month_hour_chart_data = {
            'labels': month_hour_labels,
            'values': month_hour_values
        }
        
        # 4. 按年小时统计的数据 - 年份筛选
        year_hour_labels = []
        year_hour_values = []
        
        # 确保显示00到23小时的数据
        # 创建一个字典来存储每个小时的数据，使用完整时间段作为键
        hour_data_dict = {}
        for i in range(24):
            hour_data_dict[f"{i:02d}:00 - {i+1:02d}:00"] = 0  # 初始化所有小时为0
        
        # 填充数据库中的数据
        if year_hour_year:
            for row in year_hour_data:
                try:
                    hour_range = str(row.get('hour_range', ''))  # 使用完整的时间段格式
                    count = int(row.get('total_comments', 0)) if row.get('total_comments') else 0
                    
                    # 尝试匹配小时范围格式
                    if hour_range in hour_data_dict:
                        # 如果格式完全匹配，直接使用
                        hour_data_dict[hour_range] = count
                    else:
                        # 尝试解析小时范围，提取起始小时
                        try:
                            # 处理格式如"10"或"10:00"的情况
                            if hour_range.isdigit():
                                hour = int(hour_range)
                            else:
                                # 处理格式如"10:00"的情况
                                hour = int(hour_range.split(':')[0])
                            
                            # 确保小时在0-23范围内
                            if 0 <= hour < 24:
                                key = f"{hour:02d}:00 - {hour+1:02d}:00"
                                hour_data_dict[key] = count
                        except (ValueError, IndexError):
                            # 如果解析失败，跳过此数据
                            continue
                except (ValueError, TypeError):
                    # 跳过无效数据
                    continue
        
        # 生成图表数据，确保00-23小时都有数据
        for hour in sorted(hour_data_dict.keys()):
            year_hour_labels.append(hour)
            year_hour_values.append(hour_data_dict[hour])
        
        year_hour_chart_data = {
            'labels': year_hour_labels,
            'values': year_hour_values
        }
        
        return render_template(
            'chart_analysis.html',
            all_years=all_years,
            all_months=all_months,
            all_hours=all_hours,
            month_year=month_year,
            month_hour_year=month_hour_year,
            month_hour_month=month_hour_month,
            year_hour_year=year_hour_year,
            scroll_target=scroll_target,
            year_chart_data=year_chart_data,
            month_chart_data=month_chart_data,
            month_hour_chart_data=month_hour_chart_data,
            year_hour_chart_data=year_hour_chart_data
        )
