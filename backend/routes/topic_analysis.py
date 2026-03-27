from flask import session, render_template, request, redirect, url_for
from backend.db.database import get_comment_movie_data
from backend.analysis.lda_analysis import analyze_topics

def register_topic_analysis_routes(app):
    @app.route('/topic_analysis', methods=['GET', 'POST'])
    def topic_analysis():
        if 'username' not in session:
            return redirect(url_for('auth'))
        
        lda_result = None
        error = None
        
        if request.method == 'POST':
            # 获取查询参数
            movie_name = request.form.get('movie_name', '')
            
            try:
                # 获取所有匹配的评论数据（限制最大数量）
                data, total = get_comment_movie_data(
                    page=1, 
                    per_page=1000,  # 限制最多1000条评论
                    movie_name=movie_name
                )
                
                if total == 0:
                    session['alert'] = {'message': '未找到匹配的评论数据', 'title': '提示'}
                elif total < 10:
                    session['alert'] = {'message': '评论数量不足，无法进行主题分析（至少需要10条评论）', 'title': '提示'}
                else:
                    # 提取评论内容（使用索引访问，因为SELECT顺序固定）
                    comments = []
                    for row in data:
                        try:
                            # SELECT name, comment_id, content, rating
                            # content是第3个字段，索引为2
                            content_val = row[2]
                            if content_val and content_val.strip():
                                comments.append(content_val.strip())
                        except (IndexError, TypeError):
                            # 如果索引访问失败，尝试按名称访问
                            try:
                                # sqlite3.Row支持按名称访问，大小写不敏感
                                content_val = row['content']
                                if content_val and content_val.strip():
                                    comments.append(content_val.strip())
                            except (KeyError, IndexError):
                                # 最后尝试大写名称
                                try:
                                    content_val = row['CONTENT']
                                    if content_val and content_val.strip():
                                        comments.append(content_val.strip())
                                except (KeyError, IndexError):
                                    # 所有方法都失败，跳过这条记录
                                    print(f"无法提取评论内容: {row}")
                                    continue
                    
                    if not comments:
                        session['alert'] = {'message': '未找到有效的评论内容', 'title': '提示'}
                    else:
                        # 执行LDA主题分析
                        lda_result = analyze_topics(
                            comments, 
                            max_texts=1000,  # 限制分析数据量
                            auto_k=True,     # 自动选择最佳主题数
                            top_n=10,        # 每个主题显示10个关键词
                            use_ner=True     # 启用命名实体识别
                        )
                        
                        if not lda_result:
                            session['alert'] = {'message': '主题分析失败，请检查评论数据', 'title': '错误'}
            except Exception as e:
                error = str(e)
                session['alert'] = {'message': f'主题分析出错: {error}', 'title': '错误'}
        
        # 获取并清除session中的alert信息
        alert = session.pop('alert', None)
        
        return render_template('topic_analysis.html', lda_result=lda_result, alert=alert)