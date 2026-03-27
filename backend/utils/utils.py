import hashlib
import random
import string

def hash_password(password):
    """对密码进行MD5哈希处理"""
    return hashlib.md5(password.encode()).hexdigest()

def generate_captcha(length=4):
    """生成指定长度的验证码，包含大小写字母和数字"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))