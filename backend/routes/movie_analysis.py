from flask import session, render_template, request, redirect, url_for, jsonify
from backend.db.database import get_movie_languages_data, get_movie_regions_data, get_movie_years_data, get_movie_score_duration_data, get_movie_score_genres_data

def register_movie_analysis_routes(app):
    """注册电影数据分析路由"""
    
    @app.route('/movie_analysis', methods=['GET'])
    def movie_analysis():
        """电影数据分析主页面（包含三个图表）"""
        if 'username' not in session:
            return redirect(url_for('auth'))
        
        try:
            # 语言和地区分布默认显示前15条
            show_all_languages = False
            show_all_regions = False
            # 年份分布始终显示所有数据
            show_all_years = True
            # 获取用户选择的电影类型
            selected_genre = request.args.get('selected_genre', '')
            
            # 获取所有三个图表所需的数据
            
            # 1. 语言分布数据（饼图）
            languages_data = get_movie_languages_data(limit=None if show_all_languages else 15)
            processed_languages = {}
            for row in languages_data:
                languages = row['LANGUAGES']
                count = row['count']
                
                if '/' in languages:
                    language_list = [l.strip() for l in languages.split('/') if l.strip()]
                    for language in language_list:
                        processed_languages[language] = processed_languages.get(language, 0) + count
                else:
                    language = languages.strip()
                    if language:
                        processed_languages[language] = processed_languages.get(language, 0) + count
            
            sorted_languages = sorted(processed_languages.items(), key=lambda x: x[1], reverse=True)
            if not show_all_languages:
                sorted_languages = sorted_languages[:15]
            languages_labels = [item[0] for item in sorted_languages]
            languages_data = [item[1] for item in sorted_languages]
            
            # 2. 地区分布数据（条形图）
            regions_data = get_movie_regions_data(limit=None if show_all_regions else 15)
            processed_regions = {}
            for row in regions_data:
                regions = row['REGIONS']
                count = row['count']
                
                if '/' in regions:
                    region_list = [r.strip() for r in regions.split('/') if r.strip()]
                    for region in region_list:
                        processed_regions[region] = processed_regions.get(region, 0) + count
                else:
                    region = regions.strip()
                    if region:
                        processed_regions[region] = processed_regions.get(region, 0) + count
            
            sorted_regions = sorted(processed_regions.items(), key=lambda x: x[1], reverse=True)
            if not show_all_regions:
                sorted_regions = sorted_regions[:15]
            regions_labels = [item[0] for item in sorted_regions]
            regions_data = [item[1] for item in sorted_regions]
            
            # 3. 年份分布数据（柱形图）
            years_data = get_movie_years_data(limit=None)
            
            # 处理年份数据
            processed_years = []
            for row in years_data:
                year = row['YEAR']
                count = row['count']
                
                # 转换年份为字符串，处理None和0的情况
                year_str = str(year) if year is not None and year != 0 else '未知年份'
                processed_years.append((year_str, count))
            
            # 按年份排序（从早到晚）
            sorted_years = sorted(processed_years, key=lambda x: int(x[0]) if x[0].isdigit() else 0)
            
            # 提取标签和数据（始终显示所有年份）
            sorted_years_labels = [item[0] for item in sorted_years]
            sorted_years_counts = [item[1] for item in sorted_years]
            
            # 4. 电影评分与电影时长关系数据（散点图）
            score_duration_result = get_movie_score_duration_data()
            score_duration_data = score_duration_result['raw_data']
            score_duration_analysis = score_duration_result['analysis']
            
            # 处理散点图数据
            score_duration_points = []
            for row in score_duration_data:
                score = row['DOUBAN_SCORE']
                duration = row['MINS']
                name = row['NAME']
                score_duration_points.append({
                    'x': float(duration),  # 确保时长是浮点数
                    'y': float(score),     # 确保评分是浮点数
                    'name': name           # 电影名称（用于tooltip）
                })
            
            # 提取分析结果
            duration_buckets = score_duration_analysis['duration_buckets']
            correlation = score_duration_analysis['correlation']
            trend_line = score_duration_analysis['trend_line']
            outliers = score_duration_analysis['outliers']
            
            # 5. 电影评分与电影类型关系数据（柱状图）
            score_genres_data = get_movie_score_genres_data()
            
            # 处理类型数据，计算每个类型的平均评分
            genres_scores = {}
            genres_counts = {}
            
            for row in score_genres_data:
                score = float(row['DOUBAN_SCORE'])
                genres_str = row['GENRES']
                
                # 分割类型
                genres_list = [genre.strip() for genre in genres_str.split('/') if genre.strip()]
                
                for genre in genres_list:
                    if genre not in genres_scores:
                        genres_scores[genre] = 0.0
                        genres_counts[genre] = 0
                    
                    genres_scores[genre] += score
                    genres_counts[genre] += 1
            
            # 过滤掉电影部数少于10部的类型
            filtered_genres = {genre: count for genre, count in genres_counts.items() if count >= 10}
            
            # 计算过滤后的类型的平均评分
            genres_avg_scores = {}
            for genre in filtered_genres:
                genres_avg_scores[genre] = genres_scores[genre] / genres_counts[genre]
            
            # 按平均评分排序
            sorted_genres = sorted(genres_avg_scores.items(), key=lambda x: x[1], reverse=True)
            
            # 提取类型标签和平均评分
            genres_labels = [item[0] for item in sorted_genres]
            genres_avg_scores_data = [round(item[1], 2) for item in sorted_genres]
            genres_counts_data = [genres_counts[genre] for genre in genres_labels]  # 只包含过滤后的类型的数量
            
            # 处理特定类型电影的评分散点图数据
            genre_ratings_points = []
            if selected_genre:
                # 获取所有电影数据
                all_movies_data = get_movie_score_genres_data()
                
                # 筛选出用户选择类型的电影
                for row in all_movies_data:
                    score = float(row['DOUBAN_SCORE'])
                    genres_str = row['GENRES']
                    name = row['NAME']
                    
                    # 检查电影是否属于选中的类型
                    genres_list = [genre.strip() for genre in genres_str.split('/') if genre.strip()]
                    if selected_genre in genres_list:
                        # 使用电影在类型列表中的索引作为X轴值
                        # 这样可以在散点图中显示该类型电影的评分分布
                        genre_ratings_points.append({
                            'x': len(genre_ratings_points),  # 简单使用索引作为X轴
                            'y': score,                     # 评分作为Y轴
                            'name': name                    # 电影名称（用于tooltip）
                        })
                

            

            
            return render_template('movie_analysis.html', 
                                  # 语言分布数据
                                  languages_labels=languages_labels,
                                  languages_data=languages_data,
                                  # 地区分布数据
                                  regions_labels=regions_labels,
                                  regions_data=regions_data,
                                  # 年份分布数据
                                  years_labels=sorted_years_labels,
                                  years_data=sorted_years_counts,
                                  # 评分与时长关系数据
                                  score_duration_points=score_duration_points,
                                  duration_buckets=duration_buckets,
                                  correlation=correlation,
                                  trend_line=trend_line,
                                  outliers=outliers,
                                  # 评分与类型关系数据
                                  genres_labels=genres_labels,
                                  genres_avg_scores=genres_avg_scores_data,
                                  genres_counts=genres_counts_data,
                                  # 特定类型电影评分数据
                                  genre_ratings_points=genre_ratings_points,
                                  selected_genre=selected_genre,
                                  feature_name='movie_analysis',
                                  feature_title='电影数据分析',
                                  # 图表显示选项
                                  show_all_languages=show_all_languages,
                                  show_all_regions=show_all_regions,
                                  show_all_years=show_all_years)
            
        except Exception as e:
            return render_template('movie_analysis.html', 
                                  languages_labels=[],
                                  languages_data=[],
                                  regions_labels=[],
                                  regions_data=[],
                                  years_labels=[],
                                  years_data=[],
                                  score_duration_points=[],
                                  duration_buckets=[],
                                  correlation=0,
                                  trend_line=None,
                                  outliers=[],
                                  genres_labels=[],
                                  genres_avg_scores=[],
                                  genres_counts=[],
                                  genre_ratings_points=[],
                                  selected_genre='',
                                  feature_name='movie_analysis',
                                  feature_title='电影数据分析',
                                  error='获取数据失败')
    
    @app.route('/api/movie_analysis/genre_ratings', methods=['GET'])
    def get_genre_ratings_data():
        """获取特定类型电影的评分数据（AJAX端点）"""
        try:
            # 获取用户选择的电影类型
            selected_genre = request.args.get('selected_genre', '')
            
            # 处理特定类型电影的评分散点图数据
            genre_ratings_points = []
            if selected_genre:
                # 获取所有电影数据
                all_movies_data = get_movie_score_genres_data()
                
                # 筛选出用户选择类型的电影
                for row in all_movies_data:
                    score = float(row['DOUBAN_SCORE'])
                    genres_str = row['GENRES']
                    name = row['NAME']
                    
                    # 检查电影是否属于选中的类型
                    genres_list = [genre.strip() for genre in genres_str.split('/') if genre.strip()]
                    if selected_genre in genres_list:
                        genre_ratings_points.append({
                            'x': len(genre_ratings_points),  # 使用索引作为X轴
                            'y': score,                     # 评分作为Y轴
                            'name': name                    # 电影名称
                        })
            
            # 返回JSON响应
            return jsonify({
                'success': True,
                'data': {
                    'points': genre_ratings_points,
                    'selectedGenre': selected_genre
                }
            })
        except Exception as e:
            # 返回错误响应
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500