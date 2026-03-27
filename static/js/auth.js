// 验证码生成类
class CaptchaGenerator {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.captchaText = '';
        this.generate();
        
        // 点击验证码重新生成
        this.canvas.addEventListener('click', () => this.generate());
    }
    
    async generate() {
        // 清除画布
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        try {
            // 调用后端接口获取验证码
            const response = await fetch('/generate_captcha', { method: 'POST' });
            this.captchaText = await response.text();
            
            // 绘制验证码
            this.drawCaptcha();
        } catch (error) {
            console.error('生成验证码失败:', error);
            // 失败时使用本地生成的验证码
            this.captchaText = this.generateCaptchaText();
            this.drawCaptcha();
        }
        
        return this.captchaText;
    }
    
    generateBackground() {
        // 创建渐变背景
        const gradient = this.ctx.createLinearGradient(0, 0, this.canvas.width, this.canvas.height);
        gradient.addColorStop(0, '#f8f9ff');
        gradient.addColorStop(1, '#e8ecff');
        
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    }
    
    generateCaptchaText() {
        const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjklmnpqrstuvwxyz23456789';
        let text = '';
        for (let i = 0; i < 4; i++) {
            text += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return text;
    }
    
    drawCaptcha() {
        // 生成随机背景
        this.generateBackground();
        
        const fontSize = 20;
        const font = `bold ${fontSize}px Arial, sans-serif`;
        
        this.ctx.font = font;
        this.ctx.textBaseline = 'middle';
        
        // 计算每个字符的位置
        const charWidth = this.canvas.width / this.captchaText.length;
        
        for (let i = 0; i < this.captchaText.length; i++) {
            // 随机深色 - 提高对比度
            const r = Math.floor(Math.random() * 100);
            const g = Math.floor(Math.random() * 100);
            const b = Math.floor(Math.random() * 100);
            this.ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
            
            // 轻微旋转角度
            const angle = (Math.random() - 0.5) * 0.2;
            
            // 绘制字符
            this.ctx.save();
            this.ctx.translate(i * charWidth + charWidth / 2, this.canvas.height / 2);
            this.ctx.rotate(angle);
            this.ctx.fillText(this.captchaText[i], -fontSize / 3, 0);
            this.ctx.restore();
        }
        
        // 添加干扰线
        this.addNoiseLines();
        
        // 添加干扰点
        this.addNoiseDots();
    }
    
    addNoiseLines() {
        // 添加1-2条干扰线
        const lineCount = Math.floor(Math.random() * 2) + 1;
        
        for (let i = 0; i < lineCount; i++) {
            this.ctx.beginPath();
            this.ctx.moveTo(Math.random() * this.canvas.width, Math.random() * this.canvas.height);
            this.ctx.lineTo(Math.random() * this.canvas.width, Math.random() * this.canvas.height);
            
            // 使用淡色干扰线
            const r = Math.floor(Math.random() * 150) + 100;
            const g = Math.floor(Math.random() * 150) + 100;
            const b = Math.floor(Math.random() * 180) + 100;
            this.ctx.strokeStyle = `rgba(${r}, ${g}, ${b}, 0.6)`;
            
            this.ctx.lineWidth = Math.random() * 1 + 0.3;
            this.ctx.stroke();
        }
    }
    
    addNoiseDots() {
        // 添加30-50个干扰点
        const dotCount = Math.floor(Math.random() * 20) + 30;
        
        for (let i = 0; i < dotCount; i++) {
            // 使用淡色干扰点
            const r = Math.floor(Math.random() * 150) + 100;
            const g = Math.floor(Math.random() * 150) + 100;
            const b = Math.floor(Math.random() * 180) + 100;
            this.ctx.fillStyle = `rgba(${r}, ${g}, ${b}, 0.5)`;
            
            // 随机位置
            const x = Math.random() * this.canvas.width;
            const y = Math.random() * this.canvas.height;
            
            // 绘制干扰点
            const size = Math.random() * 1 + 0.2;
            this.ctx.beginPath();
            this.ctx.arc(x, y, size, 0, Math.PI * 2);
            this.ctx.fill();
        }
    }
    
    validate(userInput) {
        return userInput.toLowerCase() === this.captchaText.toLowerCase();
    }
}

// 标签页切换功能
function setupTabSwitching() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    const titleElement = document.querySelector('.auth-header h1');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');
            
            // 更新按钮状态
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // 更新内容显示
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === targetTab) {
                    content.classList.add('active');
                }
            });
            
            // 更新标题
            if (titleElement) {
                titleElement.textContent = targetTab === 'login' ? '用户登录' : '用户注册';
            }
        });
    });
}

// 自定义提示框功能
function showCustomAlert(message, title = '提示') {
    return new Promise((resolve) => {
        const customAlert = document.getElementById('customAlert');
        const alertTitle = document.getElementById('alertTitle');
        const alertMessage = document.getElementById('alertMessage');
        const alertConfirm = document.getElementById('alertConfirm');
        const alertClose = document.getElementById('alertClose');
        
        // 检查DOM元素是否存在
        if (!customAlert || !alertTitle || !alertMessage || !alertConfirm || !alertClose) {
            console.error('自定义提示框DOM元素未找到');
            alert(message);
            resolve();
            return;
        }
        
        // 设置提示内容
        alertTitle.textContent = title;
        alertMessage.textContent = message;
        
        // 显示提示框
        customAlert.classList.add('show');
        document.body.style.overflow = 'hidden';
        
        // 确认按钮点击事件
        const confirmHandler = () => {
            customAlert.classList.remove('show');
            document.body.style.overflow = 'auto';
            resolve();
        };
        
        // 关闭按钮点击事件
        const closeHandler = () => {
            customAlert.classList.remove('show');
            document.body.style.overflow = 'auto';
            resolve();
        };
        
        // 背景点击事件
        const backgroundHandler = (e) => {
            if (e.target === customAlert) {
                customAlert.classList.remove('show');
                document.body.style.overflow = 'auto';
                resolve();
            }
        };
        
        // 添加事件监听器
        alertConfirm.addEventListener('click', confirmHandler);
        alertClose.addEventListener('click', closeHandler);
        customAlert.addEventListener('click', backgroundHandler);
        
        // ESC键关闭
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                closeHandler();
            }
        };
        document.addEventListener('keydown', escHandler);
        
        // 3秒后自动关闭提示框
        setTimeout(() => {
            closeHandler();
        }, 3000);
        
        // 清理事件监听器
        setTimeout(() => {
            alertConfirm.removeEventListener('click', confirmHandler);
            alertClose.removeEventListener('click', closeHandler);
            customAlert.removeEventListener('click', backgroundHandler);
            document.removeEventListener('keydown', escHandler);
        }, 4000); // 4秒后自动清理（确保在关闭动画完成后清理）
    });
}

// 初始化函数
document.addEventListener('DOMContentLoaded', async () => {
    // 初始化验证码（仅在登录页面有验证码canvas时执行）
    const loginCaptchaCanvas = document.getElementById('loginCaptchaCanvas');
    if (loginCaptchaCanvas) {
        window.loginCaptcha = new CaptchaGenerator('loginCaptchaCanvas');
        
        // 设置刷新按钮
        const refreshBtn = document.getElementById('refreshLoginCaptcha');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', async () => {
                await loginCaptcha.generate();
            });
        }
    }
    
    // 设置标签页切换（仅在登录页面有标签页时执行）
    const tabButtons = document.querySelectorAll('.tab-btn');
    if (tabButtons.length > 0) {
        setupTabSwitching();
    }
    
    // 检查是否有注册成功消息（仅在登录/注册页面执行）
    const successElement = document.querySelector('.success-message');
    if (successElement && successElement.textContent.includes('注册成功')) {
        // 显示自定义提示框
        await showCustomAlert('注册成功', '成功');
        
        // 切换到登录标签页
        const loginTabBtn = document.querySelector('[data-tab="login"]');
        if (loginTabBtn) {
            loginTabBtn.click();
        }
        
        // 清除成功消息
        successElement.remove();
    }
    
    // 设置错误信息自动消失（仅在登录/注册页面执行）
    const errorMessages = document.querySelectorAll('.error-message');
    errorMessages.forEach(error => {
        setTimeout(() => {
            error.classList.add('fade-out');
            // 动画完成后移除元素
            setTimeout(() => {
                error.remove();
            }, 500); // 与CSS过渡时间一致
        }, 5000); // 5秒后开始消失
    });
});