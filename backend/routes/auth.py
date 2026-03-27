from flask import request, session, redirect, url_for, render_template
from backend.utils.utils import generate_captcha, hash_password
from backend.db.database import get_user_by_username, create_user

def register_auth_routes(app):
    @app.route('/auth', methods=['GET', 'POST'])
    def auth():
        # 获取并清除session中的错误和成功信息
        error = session.pop('error', None)
        success = session.pop('success', None)
        # 获取并清除session中的用户名（仅用于表单回显，不影响登录状态）
        username = session.pop('username', None)  # 这里用pop可以确保只显示一次
        # 获取并清除session中的活跃标签页信息
        active_tab = session.pop('active_tab', 'login')  # 默认显示登录标签页
        return render_template('auth.html', error=error, success=success, username=username, active_tab=active_tab)
    
    @app.route('/login', methods=['POST'])
    def login():
        username = request.form['username']
        password = request.form['password']
        captcha = request.form['captcha']
        
        # 验证验证码
        if captcha.lower() != session.get('captcha', '').lower():
            session['error'] = '验证码错误'
            session['username'] = username  # 保存用户名到session
            return redirect(url_for('auth'))
        
        user = get_user_by_username(username)
        
        if user and hash_password(password) == user['password']:
            # 检查是否勾选了"记住我"
            remember = request.form.get('remember')
            if remember:
                session.permanent = True
            else:
                session.permanent = False
            session['username'] = username
            session['success'] = '登录成功'
            return redirect(url_for('dashboard'))
        else:
            session['error'] = '账号或密码错误'
            session['username'] = username  # 保存用户名到session
            return redirect(url_for('auth'))
    
    @app.route('/register', methods=['POST'])
    def register():
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']
        
        if password != confirm_password:
            session['error'] = '两次输入的密码不一致'
            session['active_tab'] = 'register'  # 保存当前标签页
            session['username'] = username  # 保存用户名到session
            return redirect(url_for('auth'))
        
        hashed_password = hash_password(password)
        
        if create_user(username, hashed_password, email):
            session['success'] = '注册成功，请登录'
            session['active_tab'] = 'login'  # 注册成功后切换到登录标签页
            return redirect(url_for('auth'))
        else:
            session['error'] = '用户名或邮箱已存在'
            session['active_tab'] = 'register'  # 保存当前标签页
            session['username'] = username  # 保存用户名到session
            return redirect(url_for('auth'))
    
    @app.route('/logout')
    def logout():
        session.pop('username', None)
        return redirect(url_for('auth'))
    
    @app.route('/generate_captcha', methods=['POST'])
    def generate_captcha_route():
        captcha = generate_captcha()
        session['captcha'] = captcha
        return captcha