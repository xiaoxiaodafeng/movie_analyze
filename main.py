from flask import Flask, redirect, url_for
from datetime import timedelta
from backend.db.database import init_db, import_comment_movie_data
from backend.routes.auth import register_auth_routes
from backend.routes.dashboard import register_dashboard_routes
from backend.routes.topic_analysis import register_topic_analysis_routes
from backend.routes.chart_analysis import register_chart_analysis_routes
from backend.routes.character_analysis import register_character_analysis_routes
from backend.routes.user_settings import register_user_settings_routes
from backend.routes.movie_analysis import register_movie_analysis_routes

# 创建Flask应用实例
app = Flask(__name__)

# 配置应用
app.secret_key = 'your_secret_key_here'  # 用于加密会话
app.permanent_session_lifetime = timedelta(days=7)  # 长期会话有效期7天

# 注册路由模块
register_auth_routes(app)
register_dashboard_routes(app)
register_topic_analysis_routes(app)
register_chart_analysis_routes(app)
register_character_analysis_routes(app)
register_user_settings_routes(app)
register_movie_analysis_routes(app)

# 定义根路径路由
@app.route('/')
def index():
    return redirect(url_for('auth'))

if __name__ == '__main__':
    # 初始化数据库
    init_db()
    # 导入电影评论数据 - 暂时注释以加快启动速度
    # import_comment_movie_data()
    # 启动应用
    app.run(debug=True)