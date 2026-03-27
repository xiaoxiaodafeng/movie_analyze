# 腾讯视频影视作品数据分析系统 · 技术文档

## 项目简介
- 基于 Flask 的 Web 应用，提供评论数据的情感分析、主题分析、时间分布可视化，以及演员/导演画像查询。
- 数据使用 SQLite 单文件数据库。
- NLP 采用 Transformers 文本情感模型（推荐 PyTorch 后端）与 Jieba 分词；主题模型采用 Scikit‑Learn LDA。

## 技术栈
- 后端：Flask
- 数据库：SQLite（标准库 sqlite3）
- NLP/ML：Transformers + PyTorch、Jieba、Scikit‑Learn、NumPy
- 前端：Jinja2 模板 + 原生 JS + Chart.js（CDN）

## 运行环境
- 操作系统：Windows 10/11
- Python：建议 3.9（当前仓库含 cpython‑39 的 .pyc）
- 浏览器：Chrome/Edge；Chart.js 通过 CDN 加载

## 依赖与版本
- Flask==3.0.0
- transformers==4.44.2
- torch==2.2.0（CPU 版）
- torchvision==0.17.0（可选）
- torchaudio==2.2.0（可选）
- jieba==0.42.1
- scikit-learn==1.4.2
- numpy==1.26.4
- 可选：tensorflow-cpu==2.12.1（仅在明确需要 TF 后端时）
- 可选：pillow==10.3.0（若涉及图片处理）

## 安装指南（PowerShell）
```bash
# 1) 创建并激活虚拟环境
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2) 升级 pip
pip install --upgrade pip

# 3) 安装 Web 与 NLP/ML 依赖（推荐 PyTorch CPU 后端）
pip install Flask==3.0.0
pip install transformers==4.44.2
pip install --index-url https://download.pytorch.org/whl/cpu torch==2.2.0 torchvision==0.17.0 torchaudio==2.2.0
pip install jieba==0.42.1 scikit-learn==1.4.2 numpy==1.26.4

# 4) 可选：如需 TensorFlow 后端（Windows 更建议使用 CPU 版）
pip install tensorflow-cpu==2.12.1
```

## 环境变量（建议）
为避免 Transformers 在导入 pipelines 时自动加载 TensorFlow/JAX，推荐只启用 PyTorch：
```bash
# 当前会话
set TRANSFORMERS_NO_TF=1
set TRANSFORMERS_NO_JAX=1

# 或永久（需重启终端生效）
setx TRANSFORMERS_NO_TF 1
setx TRANSFORMERS_NO_JAX 1
```

## 启动与访问
```bash
python e:\movie_analyze\main.py
```
- 默认开启调试模式；登录后在左侧菜单进入各功能页面。

## 核心模块与代码位置
- 入口与路由注册：[main.py](file:///e:/movie_analyze/main.py)
- 评论情感分析与指标计算：[dashboard.py](file:///e:/movie_analyze/backend/routes/dashboard.py)
- 主题分析路由：[topic_analysis.py](file:///e:/movie_analyze/backend/routes/topic_analysis.py)
- 时间段统计路由：[chart_analysis.py](file:///e:/movie_analyze/backend/routes/chart_analysis.py)
- 演员/导演画像查询路由：[character_analysis.py](file:///e:/movie_analyze/backend/routes/character_analysis.py)
- LDA 分析与词云生成：[lda_analysis.py](file:///e:/movie_analyze/backend/analysis/lda_analysis.py)
- 数据访问：
  - 连接/建表：[database.py](file:///e:/movie_analyze/backend/db/database.py#L5-L38)
  - 分页查询：[get_comment_movie_data](file:///e:/movie_analyze/backend/db/database.py#L97-L139)
  - 随机抽样查询：[get_random_comment_data](file:///e:/movie_analyze/backend/db/database.py#L140-L172)

## 数据与数据库
- 数据表：`comment_movie(name, movie_id, comment_id, content, rating)`
- 初始化与导入：
  - 初始化表结构：`init_db()`（应用启动时调用）
  - 可选导入 CSV：`import_comment_movie_data()`（位于 movies_data/comment_movie.csv）

## 情感分析与指标计算
- 模型：`lxyuan/distilbert-base-multilingual-cased-sentiments-student`
- 评分映射：very negative→[1.0, 1.99]，negative→[2.0, 2.99]，neutral→[3.0, 3.99]，positive→[4.0, 4.99]，very positive→5.0
- 正向定义：`rating ≥ 4.0` 与 `sentiment_score ≥ 4.0`
- 指标：Precision、Recall、F1‑Score、有效样本数
- 样本来源与样本量：
  - 表单参数：`sample_mode ∈ {page, random}`，`sample_size ∈ [100, 10000]`，默认 2000
  - 随机抽样由后端通过 `ORDER BY RANDOM() LIMIT ?` 获取
- 计算逻辑位置：[dashboard.py](file:///e:/movie_analyze/backend/routes/dashboard.py#L122-L181)

## 主题分析
- 分词：Jieba，支持停用词与实体增强
- 模型：Scikit‑Learn LDA（自动主题数可选）
- 输出：主题列表、主题分布图、加权词云、困惑度与连贯性指标
- 入口调用：[topic_analysis.py](file:///e:/movie_analyze/backend/routes/topic_analysis.py#L39-L76) → [lda_analysis.py](file:///e:/movie_analyze/backend/analysis/lda_analysis.py)

## 评论时间段可视化
- 维度：年、月、小时
- 渲染：Chart.js（CDN）
- 数据源函数见：[chart_analysis.py](file:///e:/movie_analyze/backend/routes/chart_analysis.py)

## 演员/导演画像查询
- 支持关键词搜索、分页与详情弹窗（含图表）
- 模板与脚本：`character_analysis.html`、`character_analysis.js`
- 后端查询：`search_character_simple` 等数据访问函数

## 常见问题与建议
- Windows 上导入 Transformers 触发 TensorFlow 导入导致 DLL 初始化失败：
  - 设置 `TRANSFORMERS_NO_TF=1` 与 `TRANSFORMERS_NO_JAX=1`，仅使用 PyTorch 后端。
  - 如必须使用 TensorFlow，请严格匹配 Python 与系统要求，优先安装 `tensorflow-cpu`。
- Pip 提示 “No matching distribution found for tensorflow”：
  - 检查 Python 版本与系统架构是否符合分发要求；在 Windows/CPU 环境推荐使用 `tensorflow-cpu`。
- 版本兼容建议：
  - 在 Python 3.9 环境下固定 `numpy==1.26.4` 与 `scikit-learn==1.4.2` 稳定性更好。

## 版本管理与后续优化建议
- 将依赖固化到 `requirements.txt`，并使用一致的 Python 次版本。
- 如需 GPU：切换到支持的 CUDA/PyTorch 版本，并在安装文档中补充对应索引源与驱动要求。
- 指标计算支持异步任务与进度提示，避免大样本阻塞页面。

