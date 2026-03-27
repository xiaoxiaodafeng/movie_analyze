import jieba
import jieba.posseg as pseg
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np
import re
import math
from collections import defaultdict

# 提前初始化jieba分词器
jieba.initialize()

# 停用词表（扩展版领域特定停用词表）
STOPWORDS = set([
    '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也',
    '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '还',
    '那', '他', '来', '对', '们', '多', '下', '后', '做', '现', '以', '之', '于', '中', '为',
    '个', '用', '大', '这是', '从', '里', '与', '地', '得', '而', '天', '地', '人', '神', '鬼',
    '电影', '影片', '看了', '觉得', '非常', '不错', '很好', '推荐', '精彩', '喜欢', '真的',
    '剧情', '演员', '导演', '故事', '演技', '特效', '画面', '音乐', '节奏', '台词', '角色',
    '场景', '镜头', '结局', '开始', '过程', '结束', '感觉', '方面', '部分', '这个', '那个',
    '还有', '其实', '但是', '不过', '所以', '因为', '虽然', '但是', '如果', '就是', '只是',
    '还是', '可能', '应该', '大概', '好像', '似乎', '确实', '完全', '绝对', '一定', '肯定',
    '非常', '极其', '特别', '尤其', '十分', '很', '太', '挺', '颇', '相当', '稍微', '略微',
    '有点', '有些', '几乎', '差不多', '简直', '根本', '完全', '彻底', '丝毫', '简直', '幸亏',
    '幸好', '幸亏', '幸亏', '不幸', '可惜', '不幸', '无奈', '无法', '不得不', '只好', '只能',
    '必须', '不得不', '不能', '不会', '不敢', '不想', '不要', '不想要', '不愿意', '不可能',
    '不应该', '不合适', '不舒服', '不开心', '不喜欢', '不满意', '不赞同', '不同意', '不理解',
    '不明白', '不清楚', '不记得', '不认识', '不知道', '不懂得', '不了解', '不熟悉', '不适应',
    '不习惯', '不适合', '不喜欢', '不讨厌', '不反感', '不介意', '不关心', '不注意', '不重视',
    '不认真', '不仔细', '不小心', '不努力', '不勤奋', '不刻苦', '不坚持', '不持久', '不耐心',
    '不细心', '不谨慎', '不勇敢', '不坚强', '不自信', '不自卑', '不骄傲', '不谦虚', '不诚实',
    '不守信', '不负责', '不担当', '不合作', '不配合', '不支持', '不反对', '不参与', '不干涉',
    '不介入', '不影响', '不干扰', '不破坏', '不损害', '不伤害', '不侵犯', '不违反', '不违法',
    '不犯罪', '不道德', '不伦理', '不合适', '不恰当', '不准确', '不正确', '不真实', '不客观',
    '不公正', '不公平', '不合理', '不科学', '不严谨', '不严密', '不完整', '不全面', '不系统',
    '不专业', '不熟练', '不精通', '不了解', '不知道', '不明白', '不清楚', '不记得', '不认识',
    '不懂得', '不理解', '不掌握', '不控制', '不管理', '不经营', '不运作', '不操作', '不使用',
    '不利用', '不开发', '不研究', '不探索', '不创新', '不创造', '不发明', '不设计', '不规划',
    '不计划', '不安排', '不组织', '不协调', '不合作', '不配合', '不支持', '不反对', '不参与',
    '不干涉', '不介入', '不影响', '不干扰', '不破坏', '不损害', '不伤害', '不侵犯', '不违反',
    '不违法', '不犯罪', '不道德', '不伦理', '不合适', '不恰当', '不准确', '不正确', '不真实',
    '不客观', '不公正', '不公平', '不合理', '不科学', '不严谨', '不严密', '不完整', '不全面',
    '不系统', '不专业', '不熟练', '不精通'
])

class LDAnalysis:
    def __init__(self, max_iter=25, learning_offset=500., doc_topic_prior=0.02, topic_word_prior=0.02):
        self.max_iter = max_iter
        self.learning_offset = learning_offset
        self.doc_topic_prior = doc_topic_prior
        self.topic_word_prior = topic_word_prior
        
    def preprocess_text(self, text, pos_filter=True, frequency_filter=None, use_ner=False):
        # 去除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 去除标点符号和特殊字符
        text = re.sub(r'[^一-龥\s]', '', text)
        
        # 去除数字
        text = re.sub(r'\d+', '', text)
        
        # 去除英文
        text = re.sub(r'[a-zA-Z]+', '', text)
        
        # 中文分词
        if pos_filter:
            words = pseg.cut(text)
            # 保留名词、动词、形容词
            filtered_words = [word for word, pos in words 
                           if len(word) > 1 and pos in ['n', 'vn', 'v', 'a', 'ad', 'an', 'ag', 'al']]
        else:
            filtered_words = jieba.lcut(text)
            filtered_words = [word for word in filtered_words if len(word) > 1]
        
        # 去停用词
        filtered_words = [word for word in filtered_words if word not in STOPWORDS]
        
        # 命名实体识别优化
        if use_ner and filtered_words:
            try:
                import jieba.analyse
                keywords = jieba.analyse.extract_tags(' '.join(filtered_words), topK=20, withWeight=False)
                important_entities = [keyword for keyword in keywords if keyword in filtered_words and len(keyword) > 2]
                if important_entities:
                    filtered_words = important_entities + [word for word in filtered_words if word not in important_entities][:30]
            except Exception as e:
                pass
        
        # 词频过滤
        if frequency_filter:
            word_counts = defaultdict(int)
            for word in filtered_words:
                word_counts[word] += 1
            
            filtered_words = [word for word in filtered_words 
                           if frequency_filter['min'] <= word_counts[word] <= frequency_filter['max']]
        
        return filtered_words
    
    def _calculate_coherence_score(self, topics, vectorizer, texts):
        # 简化版连贯性计算
        total_coherence = 0.0
        num_topics = len(topics)
        
        for topic in topics:
            topic_words = [word for word, _ in topic]
            topic_coherence = 0.0
            num_word_pairs = 0
            
            for i in range(len(topic_words)):
                for j in range(i+1, len(topic_words)):
                    word1 = topic_words[i]
                    word2 = topic_words[j]
                    
                    # 计算共同出现次数
                    co_occurrence = 0
                    for text in texts:
                        if word1 in text and word2 in text:
                            co_occurrence += 1
                    
                    if co_occurrence > 0:
                        topic_coherence += math.log((co_occurrence + 1.0) / len(texts))
                        num_word_pairs += 1
            
            if num_word_pairs > 0:
                total_coherence += topic_coherence / num_word_pairs
        
        return total_coherence / num_topics if num_topics > 0 else 0.0
    
    def _calculate_topic_diversity(self, topics, top_n=10):
        # 计算主题多样性
        all_words = set()
        total_words = 0
        
        for topic in topics:
            topic_words = [word for word, _ in topic[:top_n]]
            all_words.update(topic_words)
            total_words += len(topic_words)
        
        return len(all_words) / total_words if total_words > 0 else 0.0
    
    def calculate_perplexity(self, lda_model, count_matrix):
        # 计算困惑度
        try:
            perplexity = lda_model.perplexity(count_matrix)
            return perplexity
        except Exception as e:
            print(f"计算困惑度出错: {e}")
            return 0.0
    
    def train_model(self, texts, num_topics=None, auto_k=True, min_k=3, max_k=8, top_n=10, use_ner=False):
        # 文本预处理
        processed_texts = [' '.join(self.preprocess_text(text, use_ner=use_ner)) for text in texts]
        
        # 过滤空文本
        processed_texts = [text for text in processed_texts if text.strip()]
        if not processed_texts:
            return None
        
        # 构建词袋模型
        vectorizer = CountVectorizer(
            max_df=0.85,
            min_df=5,
            max_features=3000,
            token_pattern=r'\b\w+\b'
        )
        
        count_matrix = vectorizer.fit_transform(processed_texts)
        feature_names = vectorizer.get_feature_names_out()
        
        # 自动选择最佳主题数
        best_num_topics = num_topics
        best_coherence = -float('inf')
        best_perplexity = float('inf')
        best_lda_model = None
        best_topics = None  # 保存最佳模型的主题词列表
        
        if auto_k and num_topics is None:
            for k in range(min_k, max_k + 1):
                lda = LatentDirichletAllocation(
                    n_components=k,
                    max_iter=self.max_iter,
                    learning_offset=self.learning_offset,
                    doc_topic_prior=self.doc_topic_prior,
                    topic_word_prior=self.topic_word_prior,
                    random_state=42,
                    n_jobs=-1
                )
                
                lda.fit(count_matrix)
                
                # 获取当前迭代的主题词
                current_topics = []
                for topic_idx, topic in enumerate(lda.components_):
                    topic_words = [(feature_names[i], float(topic[i])) for i in topic.argsort()[:-top_n - 1:-1]]
                    current_topics.append(topic_words)
                
                # 计算连贯性分数
                coherence = self._calculate_coherence_score(current_topics, vectorizer, processed_texts)
                
                # 计算困惑度
                perplexity = self.calculate_perplexity(lda, count_matrix)
                
                # 选择最佳模型（基于连贯性分数，困惑度辅助）
                if coherence > best_coherence or (coherence == best_coherence and perplexity < best_perplexity):
                    best_coherence = coherence
                    best_perplexity = perplexity
                    best_num_topics = k
                    best_lda_model = lda
                    best_topics = current_topics.copy()  # 保存最佳模型的主题词列表
        else:
            # 使用指定的主题数
            best_num_topics = num_topics or 5
            best_lda_model = LatentDirichletAllocation(
                n_components=best_num_topics,
                max_iter=self.max_iter,
                learning_offset=self.learning_offset,
                doc_topic_prior=self.doc_topic_prior,
                topic_word_prior=self.topic_word_prior,
                random_state=42,
                n_jobs=-1
            )
            best_lda_model.fit(count_matrix)
            
            # 获取主题词
            best_topics = []
            for topic_idx, topic in enumerate(best_lda_model.components_):
                topic_words = [(feature_names[i], float(topic[i])) for i in topic.argsort()[:-top_n - 1:-1]]
                best_topics.append(topic_words)
            
            # 计算连贯性和困惑度
            best_coherence = self._calculate_coherence_score(best_topics, vectorizer, processed_texts)
            best_perplexity = self.calculate_perplexity(best_lda_model, count_matrix)
        
        if best_lda_model is None:
            return None
        
        # 获取文档主题分布
        doc_topic_dist = best_lda_model.transform(count_matrix)
        
        # 计算主题分布
        topic_distribution = np.sum(doc_topic_dist, axis=0)
        topic_distribution = [int(count) for count in topic_distribution]
        
        # 计算主题相似度矩阵
        topic_similarity_matrix = np.zeros((best_num_topics, best_num_topics))
        for i in range(best_num_topics):
            for j in range(best_num_topics):
                # 余弦相似度
                a = best_lda_model.components_[i]
                b = best_lda_model.components_[j]
                similarity = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
                topic_similarity_matrix[i][j] = float(similarity)
        
        # 生成加权词云数据
        word_cloud_data = []
        word_weights = defaultdict(float)
        
        for topic_idx, topic in enumerate(best_lda_model.components_):
            for word_idx, weight in enumerate(topic):
                word = feature_names[word_idx]
                word_weights[word] += float(weight)
        
        # 归一化权重并转换为词云数据
        max_weight = max(word_weights.values()) if word_weights else 1
        for word, weight in word_weights.items():
            # 控制词云大小范围在12-36px
            size = 12 + (weight / max_weight) * 24
            word_cloud_data.append({"word": word, "size": round(size, 2)})
        
        # 按权重排序
        word_cloud_data.sort(key=lambda x: x["size"], reverse=True)
        
        # 构建结果对象
        result = {
            "num_topics": best_num_topics,
            "num_documents": len(processed_texts),
            "vocab_size": len(feature_names),
            "topics": [],
            "perplexity": best_perplexity,
            "coherence_score": best_coherence,
            "diversity": self._calculate_topic_diversity(best_topics),
            "topic_distribution": topic_distribution,
            "topic_similarity_matrix": topic_similarity_matrix.tolist(),
            "word_cloud_data": word_cloud_data[:100]  # 只保留前100个词
        }
        
        # 添加主题词
        for topic_idx, topic_words in enumerate(best_topics):
            topic_obj = {
                "id": topic_idx + 1,
                "words": [
                    {"word": word, "weight": weight}
                    for word, weight in topic_words
                ]
            }
            result["topics"].append(topic_obj)
        
        return result

def analyze_topics(texts, max_texts=1000, **kwargs):
    # 限制分析数据量
    if len(texts) > max_texts:
        texts = texts[:max_texts]
    
    lda_analyzer = LDAnalysis()
    return lda_analyzer.train_model(texts, **kwargs)