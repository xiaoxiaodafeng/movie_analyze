from flask import session, render_template, request, redirect, url_for
from backend.db.database import get_comment_movie_data, get_random_comment_data, get_user_by_username, update_user_password, update_user_email
import os
from transformers import pipeline


MODEL_NAME = os.getenv(
    'SENTIMENT_MODEL_NAME',
    'lxyuan/distilbert-base-multilingual-cased-sentiments-student'
)
proxy_address = os.getenv('SENTIMENT_PROXY')
if proxy_address:
    os.environ['HTTP_PROXY'] = proxy_address
    os.environ['HTTPS_PROXY'] = proxy_address

classifier = None
try:
    import torch  # noqa: F401
    classifier = pipeline(
        'sentiment-analysis',
        model=MODEL_NAME,
        return_all_scores=True
    )
except Exception as e:
    print(f'模型加载失败: {e}')
    classifier = None

POSITIVE_HINTS = {
    '好': 1.0,
    '喜欢': 1.2,
    '推荐': 1.4,
    '精彩': 1.2,
    '感动': 1.0,
    '满意': 1.0,
    '值得': 1.1,
    '优秀': 1.3,
    '惊喜': 1.0,
    '完美': 1.2
}

NEGATIVE_HINTS = {
    '差': 1.2,
    '烂': 1.5,
    '失望': 1.3,
    '无聊': 1.1,
    '难看': 1.4,
    '垃圾': 1.6,
    '糟糕': 1.4,
    '后悔': 1.3,
    '尴尬': 1.0,
    '拖沓': 1.0
}

NEGATION_HINTS = ('不', '没', '无', '并不', '不是', '毫无')


def _score_with_model(content):
    if not content or classifier is None:
        return None
    try:
        results = classifier(content)
    except Exception:
        return None

    if not results:
        return None

    raw_scores = results[0]
    if isinstance(raw_scores, dict):
        raw_scores = [raw_scores]

    sentiment_scores = {}
    for result in raw_scores:
        label = str(result.get('label', '')).lower()
        sentiment_scores[label] = float(result.get('score', 0))

    very_negative_score = sentiment_scores.get('very negative', 0)
    negative_score = sentiment_scores.get('negative', 0)
    neutral_score = sentiment_scores.get('neutral', 0)
    positive_score = sentiment_scores.get('positive', 0)
    very_positive_score = sentiment_scores.get('very positive', 0)

    score = (
        1.0 * very_negative_score +
        2.0 * negative_score +
        3.0 * neutral_score +
        5.0 * positive_score +
        5.5 * very_positive_score
    )

    if (positive_score + very_positive_score) > 0.2:
        score += 1.0

    return round(max(1.0, min(5.0, score)), 1)


def _score_with_heuristic(content):
    if not content:
        return 3.0

    text = str(content)
    signal = 0.0

    for word, weight in POSITIVE_HINTS.items():
        if word in text:
            signal += weight
    for word, weight in NEGATIVE_HINTS.items():
        if word in text:
            signal -= weight

    for neg in NEGATION_HINTS:
        for word, weight in POSITIVE_HINTS.items():
            if f'{neg}{word}' in text:
                signal -= weight * 1.3
        for word, weight in NEGATIVE_HINTS.items():
            if f'{neg}{word}' in text:
                signal += weight * 0.8

    score = 3.0 + signal * 0.35
    return round(max(1.0, min(5.0, score)), 1)


def score_sentiment(content):
    model_score = _score_with_model(content)
    if model_score is not None:
        return model_score
    return _score_with_heuristic(content)


def register_dashboard_routes(app):
    @app.route('/dashboard', methods=['GET', 'POST'])
    def dashboard():
        if 'username' in session:
            # 鑾峰彇骞舵竻闄ession涓殑鎴愬姛淇℃伅
            success = session.pop('success', None)
            
            # 鑾峰彇褰撳墠鍔熻兘
            if request.method == 'POST':
                feature = request.form.get('feature', 'sentiment')
            else:
                feature = request.args.get('feature', 'sentiment')
            
            # 妫€鏌ユ槸鍚︽槸涓汉璁剧疆琛ㄥ崟鎻愪氦
            if request.method == 'POST' and feature == 'settings':
                # 澶勭悊瀵嗙爜淇敼
                if 'new_password' in request.form and 'confirm_password' in request.form:
                    new_password = request.form.get('new_password')
                    confirm_password = request.form.get('confirm_password')
                    
                    if new_password != confirm_password:
                        session['error'] = '两次输入的密码不一致'
                    elif not new_password or len(new_password) < 4:
                        session['error'] = '密码长度不能少于4位'
                    else:
                        user = get_user_by_username(session['username'])
                        if update_user_password(user['id'], new_password):
                            session['success'] = '密码修改成功'
                        else:
                            session['error'] = '密码修改失败'
                # 澶勭悊閭淇敼
                elif 'new_email' in request.form:
                    new_email = request.form.get('new_email')
                    
                    if not new_email or '@' not in new_email:
                        session['error'] = '请输入有效的邮箱地址'
                    else:
                        user = get_user_by_username(session['username'])
                        if update_user_email(user['id'], new_email):
                            session['success'] = '邮箱修改成功'
                        else:
                            session['error'] = '邮箱修改失败，该邮箱可能已被使用'
                # 閲嶅畾鍚戝洖dashboard椤甸潰
                return redirect(url_for('dashboard', feature='settings'))
            
            # 鑾峰彇鏌ヨ鍙傛暟
            if request.method == 'POST':
                page = request.form.get('page', 1, type=int)
                per_page = request.form.get('per_page', 10, type=int)
                direction = request.form.get('direction')
                comment_id = request.form.get('comment_id', '')
                movie_name = request.form.get('movie_name', '')
                jump_page = request.form.get('jump_page', '')
                sample_mode = request.form.get('sample_mode', 'page')
                sample_size = request.form.get('sample_size', 2000, type=int)
                confirm_sample = request.form.get('confirm_sample', False) == 'true'
                reset_metrics = request.form.get('reset_metrics', False) == 'true'
                
                # 濡傛灉闇€瑕侀噸缃甿etrics锛屾竻闄ession涓殑metrics
                if reset_metrics:
                    session.pop('metrics', None)
                
                # 濡傛灉鏄柊鐨勬煡璇紙涓嶆槸缈婚〉鎿嶄綔锛夛紝閲嶇疆椤电爜涓?骞舵竻闄ession涓殑metrics
                if (comment_id or movie_name) and not (direction or jump_page):
                    page = 1
                    session.pop('metrics', None)
                
                # 澶勭悊椤电爜璺宠浆
                elif jump_page and jump_page.isdigit():
                    page = max(1, int(jump_page))
                # 鏍规嵁鏂瑰悜璋冩暣椤电爜
                elif direction == 'prev':
                    page = max(1, page - 1)
                elif direction == 'next':
                    _, total = get_comment_movie_data(page=1, per_page=1, comment_id=comment_id, movie_name=movie_name)
                    total_pages = (total + per_page - 1) // per_page
                    page = min(total_pages, page + 1)
            else:
                # 浠嶶RL鍙傛暟鑾峰彇
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 10, type=int)
                comment_id = request.args.get('comment_id', '')
                movie_name = request.args.get('movie_name', '')
                sample_mode = request.args.get('sample_mode', 'page')
                sample_size = request.args.get('sample_size', 2000, type=int)
                confirm_sample = False
            
            # 鏍规嵁feature鍙傛暟纭畾褰撳墠鍔熻兘
            if feature == 'settings':
                # 涓汉璁剧疆鍔熻兘
                user = get_user_by_username(session['username'])
                return render_template('dashboard.html', 
                                      success=success, 
                                      error=session.pop('error', None),
                                      feature_name='settings',
                                      feature_title='个人设置',
                                      username=user['username'],
                                      email=user['email'])
            else:
                # 鎯呮劅鍒嗘瀽鍔熻兘
                # 闄愬埗姣忛〉琛屾暟涓?0鎴?5
                if per_page not in [10, 15]:
                    per_page = 10
                
                # 鑾峰彇鏁版嵁
                data, total = get_comment_movie_data(page=page, per_page=per_page, comment_id=comment_id, movie_name=movie_name)
                
                # 璁剧疆鏌ヨ缁撴灉鎻愮ず - 浠呭湪鍒濆鏌ヨ鏃舵樉绀猴紝缈婚〉鏃朵笉鏄剧ず
                if request.method == 'POST' and (comment_id or movie_name):
                    # 妫€鏌ユ槸鍚︽槸缈婚〉鎿嶄綔
                    is_pagination = direction is not None or jump_page is not None
                    if not is_pagination:
                        if total > 0:
                            session['alert'] = {'message': f'查询到 {total} 条记录', 'title': '查询成功'}
                        else:
                            session['alert'] = {'message': '未找到匹配的记录', 'title': '提示'}
                
                # 对每条评论进行情感分析
                processed_data = []
                for row in data:
                    row_dict = dict(row)
                    content = row_dict.get('content', '')

                    sentiment_score = score_sentiment(content)
                    row_dict['sentiment_score'] = round(sentiment_score, 1)
                    processed_data.append(row_dict)
                
                # 浣跨敤澶勭悊鍚庣殑鏁版嵁
                data = processed_data
                
                # 浠巗ession涓幏鍙杕etrics锛屽鏋滀笉瀛樺湪鍒欏垵濮嬪寲涓篘one
                metrics = session.get('metrics', None)
                
                if confirm_sample:
                    predicted_positive_threshold = 3.5 if classifier is not None else 3.0
                    if sample_mode == 'random':
                        # 闅忔満鏍锋湰闇€瑕侀噸鏂拌幏鍙栧苟澶勭悊
                        sample_rows = get_random_comment_data(limit=sample_size, comment_id=comment_id, movie_name=movie_name)
                    else:
                        sample_rows = processed_data
                    
                    # 璁＄畻绮剧‘鐜囥€佸彫鍥炵巼鍜孎1鍒嗘暟
                    tp = 0  # True Positive
                    fp = 0  # False Positive
                    fn = 0  # False Negative
                    
                    valid_samples = 0
                    
                    # 瀵规牱鏈泦鍚堣繘琛岄娴嬩笌璁＄畻
                    for item in sample_rows:
                        # 鑾峰彇鐪熷疄璇勫垎鍜岄娴嬫儏鎰熷垎
                        try:
                            # item鍙兘涓哄瓧鍏告垨sqlite3.Row
                            row_dict = dict(item) if not isinstance(item, dict) else item
                            actual_rating = float(row_dict.get('rating', 0)) if row_dict.get('rating') is not None else None
                            predicted_score = row_dict.get('sentiment_score')
                            
                            if predicted_score is None:
                                content = row_dict.get('content', '')
                                predicted_score = score_sentiment(content)
                            
                            if actual_rating is None:
                                continue
                                
                            valid_samples += 1
                            
                            # 以 3.5 作为正向阈值，用于计算准确率/召回率/F1
                            is_actual_positive = (actual_rating >= 3.5)
                            is_predicted_positive = (predicted_score >= predicted_positive_threshold)
                            
                            if is_predicted_positive and is_actual_positive:
                                tp += 1
                            elif is_predicted_positive and not is_actual_positive:
                                fp += 1
                            elif not is_predicted_positive and is_actual_positive:
                                fn += 1
                        except (ValueError, TypeError):
                            continue
                    
                    # 璁＄畻鎸囨爣
                    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
                    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
                    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                    
                    # 鏍煎紡鍖栨寚鏍囦负鐧惧垎姣斿瓧绗︿覆
                    metrics = {
                        'precision': f"{precision:.2%}",
                        'recall': f"{recall:.2%}",
                        'f1_score': f"{f1_score:.2%}",
                        'valid_samples': valid_samples,
                        'sample_desc': '随机样本' if sample_mode == 'random' else '当前页面',
                        'pred_threshold': f"{predicted_positive_threshold:.1f}",
                        'mode': '模型预测' if classifier is not None else '规则兜底'
                    }
                    
                    session['metrics'] = metrics
                
                total_pages = (total + per_page - 1) // per_page
                
                # 瀹氫箟鍒楀悕鏄犲皠
                column_names = {
                    'name': '电影名',
                    'comment_id': '评论ID',
                    'content': '评论内容',
                    'sentiment_score': '情感分',
                    'rating': '标注评分'
                }
                
                # 鑾峰彇骞舵竻闄ession涓殑alert淇℃伅
                alert = session.pop('alert', None)
                
                return render_template('dashboard.html', success=success, 
                                      error=session.pop('error', None),
                                      alert=alert,
                                      feature_name='sentiment',
                                      feature_title='评论情感分析',
                                      data=data, page=page, per_page=per_page, 
                                      total_pages=total_pages, total=total, 
                                      column_names=column_names, metrics=metrics)
        return redirect(url_for('auth'))
