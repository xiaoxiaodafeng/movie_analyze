from flask import session, render_template, request, redirect, url_for, flash
from backend.db.database import get_user_by_username, update_user_password, update_user_email

def register_user_settings_routes(app):
    @app.route('/settings', methods=['GET', 'POST'])
    def settings():
        if 'username' not in session:
            return redirect(url_for('auth'))
        
        username = session['username']
        user = get_user_by_username(username)
        
        if not user:
            return redirect(url_for('auth'))
        
        # 获取并清除session中的成功信息
        success = session.pop('success', None)
        error = session.pop('error', None)
        
        if request.method == 'POST':
            # 处理密码修改
            if 'new_password' in request.form and 'confirm_password' in request.form:
                new_password = request.form.get('new_password')
                confirm_password = request.form.get('confirm_password')
                
                if new_password != confirm_password:
                    session['error'] = '两次输入的密码不一致'
                    return redirect(url_for('settings'))
                
                if not new_password or len(new_password) < 6:
                    session['error'] = '密码长度不能少于6位'
                    return redirect(url_for('settings'))
                
                if update_user_password(user['id'], new_password):
                    session['success'] = '密码修改成功'
                    return redirect(url_for('settings'))
                else:
                    session['error'] = '密码修改失败'
                    return redirect(url_for('settings'))
            
            # 处理邮箱修改
            elif 'new_email' in request.form:
                new_email = request.form.get('new_email')
                
                if not new_email or '@' not in new_email:
                    session['error'] = '请输入有效的邮箱地址'
                    return redirect(url_for('settings'))
                
                if update_user_email(user['id'], new_email):
                    session['success'] = '邮箱修改成功'
                    return redirect(url_for('settings'))
                else:
                    session['error'] = '邮箱修改失败，该邮箱可能已被使用'
                    return redirect(url_for('settings'))
        
        return render_template('settings.html', 
                              success=success, 
                              error=error,
                              username=username,
                              email=user['email'])
    
    @app.route('/change_password', methods=['POST'])
    def change_password():
        return redirect(url_for('settings'))
    
    @app.route('/change_email', methods=['POST'])
    def change_email():
        return redirect(url_for('settings'))