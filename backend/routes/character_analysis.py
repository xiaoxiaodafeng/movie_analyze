from flask import session, render_template, request, redirect, url_for, jsonify
from backend.db.database import search_character_simple, get_character_details


def register_character_analysis_routes(app):
    @app.route('/character_analysis', methods=['GET', 'POST'])
    def character_analysis():
        if 'username' in session:
            # 获取并清除session中的成功信息
            success = session.pop('success', None)
            # 获取查询参数
            if request.method == 'POST':
                # 从表单获取参数
                page = request.form.get('page', 1, type=int)
                per_page = request.form.get('per_page', 10, type=int)
                direction = request.form.get('direction')
                keyword = request.form.get('keyword', '')
                jump_page = request.form.get('jump_page', '')
                
                # 处理页码跳转
                if jump_page and jump_page.isdigit():
                    page = max(1, int(jump_page))
                # 根据方向调整页码
                elif direction == 'prev':
                    page = max(1, page - 1)
                elif direction == 'next':
                    # 先获取总记录数来计算最大页码
                    _, total = search_character_simple(keyword=keyword, page=1, per_page=1)
                    total_pages = (total + per_page - 1) // per_page
                    page = min(total_pages, page + 1)
            else:
                # 从URL参数获取
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 10, type=int)
                keyword = request.args.get('keyword', '')
            
            # 限制每页行数为10或15
            if per_page not in [10, 15]:
                per_page = 10
            
            # 获取数据
            data, total = search_character_simple(keyword=keyword, page=page, per_page=per_page)
            
            # 计算总页数
            total_pages = (total + per_page - 1) // per_page
            
            # 定义列名映射
            column_names = {
                'character_id': '人物ID',
                'character_name': '人物姓名',
                'participation_role': '参与身份',
                'movie_type_count': '参与电影类型数',
                'total_work_count': '总作品数',
                'main_movie_type': '主要电影类型',
                'top_three_types': '前三大类型'
            }
            
            return render_template('character_analysis.html', 
                                  data=data, page=page, per_page=per_page, 
                                  total_pages=total_pages, total=total, 
                                  column_names=column_names, keyword=keyword, 
                                  success=success, alert={})
        return redirect(url_for('auth'))

    @app.route('/character_details/<int:character_id>', methods=['GET'])
    def character_details(character_id):
        """
        获取演员/导演的详细信息API
        :param character_id: 演员/导演的唯一标识
        :return: 演员/导演的详细信息（JSON格式）
        """
        try:
            if 'username' in session:
                details = get_character_details(character_id)
                if details:
                    # 将SQLite行对象转换为字典
                    details_dict = dict(details)
                    # 确保返回的数据是JSON可序列化的
                    return jsonify(details_dict)
                else:
                    return jsonify({'error': '未找到该演员/导演的详细信息'}), 404
            return jsonify({'error': '未登录'}), 401
        except Exception as e:
            print(f"获取演员详情出错: {e}")
            return jsonify({'error': '服务器内部错误'}), 500
