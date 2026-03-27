// 设置页面的JavaScript

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 获取表单元素
    const changePasswordForm = document.getElementById('changePasswordForm');
    const changeEmailForm = document.getElementById('changeEmailForm');
    
    // 密码修改表单提交事件处理
    if (changePasswordForm) {
        changePasswordForm.addEventListener('submit', function(e) {
            const newPassword = document.getElementById('new_password');
            const confirmPassword = document.getElementById('confirm_password');
            
            // 表单验证
            if (newPassword.value !== confirmPassword.value) {
                alert('两次输入的密码不一致');
                e.preventDefault(); // 阻止表单提交
                return false;
            }
            
            if (newPassword.value.length < 6) {
                alert('密码长度不能少于6位');
                e.preventDefault(); // 阻止表单提交
                return false;
            }
            
            // 可以添加更多密码强度验证
            // 例如：至少包含一个字母和一个数字
            const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$/;
            if (!passwordRegex.test(newPassword.value)) {
                alert('密码必须包含至少一个字母和一个数字');
                e.preventDefault(); // 阻止表单提交
                return false;
            }
            
            // 表单验证通过，允许提交
            return true;
        });
    }
    
    // 邮箱修改表单提交事件处理
    if (changeEmailForm) {
        changeEmailForm.addEventListener('submit', function(e) {
            const newEmail = document.getElementById('new_email');
            
            // 邮箱格式验证
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(newEmail.value)) {
                alert('请输入有效的邮箱地址');
                e.preventDefault(); // 阻止表单提交
                return false;
            }
            
            // 表单验证通过，允许提交
            return true;
        });
    }
    
    // 密码输入框交互
    const newPasswordInput = document.getElementById('new_password');
    if (newPasswordInput) {
        newPasswordInput.addEventListener('focus', function() {
            // 可以添加密码输入提示
        });
        
        newPasswordInput.addEventListener('input', function() {
            // 实时验证密码强度
            const password = this.value;
            const strengthIndicator = document.createElement('div');
            strengthIndicator.className = 'password-strength';
            
            // 简单的密码强度检查
            if (password.length < 6) {
                strengthIndicator.textContent = '密码强度：弱';
                strengthIndicator.style.color = '#e74c3c';
            } else if (password.length < 10) {
                strengthIndicator.textContent = '密码强度：中';
                strengthIndicator.style.color = '#f39c12';
            } else {
                strengthIndicator.textContent = '密码强度：强';
                strengthIndicator.style.color = '#2ecc71';
            }
            
            // 移除旧的强度指示器
            const oldIndicator = this.parentNode.querySelector('.password-strength');
            if (oldIndicator) {
                oldIndicator.remove();
            }
            
            // 添加新的强度指示器
            this.parentNode.appendChild(strengthIndicator);
        });
    }
    
    // 添加页面加载动画效果
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.3s ease-in-out';
    setTimeout(() => {
        document.body.style.opacity = '1';
    }, 100);
});

// 密码可见性切换功能（可选扩展）
function togglePasswordVisibility() {
    const passwordInput = document.getElementById('new_password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    
    if (passwordInput && confirmPasswordInput) {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        confirmPasswordInput.setAttribute('type', type);
        
        // 切换图标
        const toggleBtn = this;
        toggleBtn.textContent = type === 'password' ? '显示密码' : '隐藏密码';
    }
}