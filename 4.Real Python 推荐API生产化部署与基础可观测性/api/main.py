import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import spacy
import re
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import Response
from pydantic import BaseModel
import uvicorn
import logging
from contextlib import asynccontextmanager # 用于 FastAPi 生命周期事件
import pathlib # <-- 新增导入
import time

# Prometheus 监控相关导入
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 全局变量，用于存储加载的数据和模型
# 它们会在应用启动时加载一次
df = None
tfidf_matrix = None
cosine_sim = None
vectorizer = None
nlp_model = None
stop_words_set = None # Renamed from stop_words to avoid conflict with nltk.corpus.stopwords
lemmatizer = None

# --- Prometheus 监控指标定义 ---
# 请求计数器
REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Total HTTP requests', 
    ['method', 'endpoint', 'status']
)

# 请求延迟直方图
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 
    'HTTP request latency', 
    ['method', 'endpoint']
)

# 推荐请求计数
RECOMMENDATION_REQUESTS = Counter(
    'recommendation_requests_total',
    'Total recommendation requests',
    ['status']
)

# 数据集大小指标
DATASET_SIZE = Gauge(
    'dataset_articles_total',
    'Total number of articles in dataset'
)

# 模型状态指标
MODEL_LOADED = Gauge(
    'model_loaded_status',
    'Whether the ML model is loaded (1) or not (0)'
)

# --- API 请求和响应模型定义 ---
class RecommendationRequest(BaseModel):
    article_id: int
    top_n: int = 5 # 默认推荐5篇

class RecommendedArticle(BaseModel):
    article_id: int
    title: str # Changed from 文章标题 to title
    url: str   # Changed from 文章URL to url
    # similarity_score: float = None # 相似度分数可选

class RecommendationResponse(BaseModel):
    message: str
    recommendations: list[RecommendedArticle]

# --- FastAPI 生命周期事件 (用于在应用启动/关闭时加载/卸载资源) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用程序启动时运行
    logger.info("应用启动中：加载数据和模型...")
    global df, tfidf_matrix, cosine_sim, vectorizer, nlp_model, stop_words_set, lemmatizer

    try:
        # 1. 加载数据
        # Construct the path to the CSV file relative to this script (main.py)
        # main.py is in api/, csv is in the shared_data directory
        try:
            # 尝试Docker路径
            csv_file_path = '/shared_data/real_python_courses_analysis.csv'
            if not pathlib.Path(csv_file_path).exists():
                # 如果Docker路径不存在，使用本地相对路径
                script_dir = pathlib.Path(__file__).parent.resolve()
                project_root = script_dir.parent.parent
                csv_file_path = project_root / 'shared_data' / 'real_python_courses_analysis.csv'
        except:
            # 备用方案：使用相对路径
            script_dir = pathlib.Path(__file__).parent.resolve()
            project_root = script_dir.parent.parent
            csv_file_path = project_root / 'shared_data' / 'real_python_courses_analysis.csv'
        
        logger.info(f"尝试从以下路径加载CSV: {csv_file_path}")
        df = pd.read_csv(csv_file_path)
        # Use actual column names from the CSV: Title, URL, Content
        df = df[['Title', 'URL', 'Content']].dropna(subset=['Content', 'Title'])
        df.rename(columns={'Title': 'title', 'URL': 'url', 'Content': 'content'}, inplace=True) # Rename for internal consistency
        df['article_id'] = df.index # 使用DataFrame索引作为文章ID
        logger.info(f"数据加载成功！共 {len(df)} 篇文章。")

        # 2. 初始化 NLP 工具
        try:
            nlp_model = spacy.load("en_core_web_sm")
        except OSError:
            logger.info("Spacy model 'en_core_web_sm' not found. Downloading...")
            spacy.cli.download("en_core_web_sm")
            nlp_model = spacy.load("en_core_web_sm")
            
        nltk_data_path_configured = False
        try:
            stopwords.words('english') # Check if stopwords are available
            nltk_data_path_configured = True
        except LookupError:
            logger.info("NLTK stopwords not found. Downloading...")
            nltk.download('stopwords')
        try:
            WordNetLemmatizer().lemmatize('test') # Check if wordnet is available
            nltk_data_path_configured = True
        except LookupError:
            logger.info("NLTK WordNet not found. Downloading...")
            nltk.download('wordnet')
        try:
            nltk.pos_tag(['test']) # Check if averaged_perceptron_tagger is available
            nltk_data_path_configured = True
        except LookupError:
            logger.info("NLTK averaged_perceptron_tagger not found. Downloading...")
            nltk.download('averaged_perceptron_tagger')

        stop_words_set = set(stopwords.words('english'))
        lemmatizer = WordNetLemmatizer()

        # 3. 文本预处理
        def preprocess_text_internal(text):
            text = str(text).lower()
            text = re.sub(r'[^a-z\s]', '', text) # Keep spaces for tokenization
            doc = nlp_model(text)
            # Use lemmatization and ensure token.is_alpha and not in stop_words_set
            tokens = [token.lemma_ for token in doc if token.is_alpha and token.text not in stop_words_set and len(token.text) > 2]
            return " ".join(tokens)

        df['processed_content'] = df['content'].apply(preprocess_text_internal) # Use 'content' column
        logger.info("文本预处理完成。")

        # 4. TF-IDF 向量化
        vectorizer = TfidfVectorizer(stop_words='english', max_features=5000) # 限制特征数量
        tfidf_matrix = vectorizer.fit_transform(df['processed_content'])
        logger.info(f"TF-IDF 向量化完成。词汇量: {tfidf_matrix.shape[1]}")

        # 5. 计算余弦相似度矩阵
        logger.info("正在计算余弦相似度矩阵，这可能需要一些时间...")
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        logger.info("余弦相似度矩阵计算完成。")

        # 更新 Prometheus 指标
        DATASET_SIZE.set(len(df))
        MODEL_LOADED.set(1)

    except FileNotFoundError:
        logger.error("错误：'../shared_data/real_python_courses_analysis.csv' 未找到。请确保文件位于共享数据目录且包含 'Content' 列。", exc_info=True)
        raise RuntimeError("必要的数据文件未找到，应用无法启动。")
    except Exception as e:
        logger.error(f"应用启动时发生错误: {e}", exc_info=True)
        raise RuntimeError(f"应用启动失败: {e}")

    yield # 应用启动完成，可以开始处理请求

    # 应用程序关闭时运行 (可选，用于清理资源)
    logger.info("应用关闭中：清理资源...")
    df = None
    tfidf_matrix = None
    cosine_sim = None
    vectorizer = None
    nlp_model = None
    stop_words_set = None
    lemmatizer = None
    # 重置 Prometheus 指标
    MODEL_LOADED.set(0)
    DATASET_SIZE.set(0)
    logger.info("资源清理完成。")

# 初始化 FastAPI 应用，并将生命周期事件传入
app = FastAPI(
    title="Real Python 文章推荐 API",
    description="基于内容相似度的 Real Python 博客文章推荐服务。",
    version="2.0.0",
    lifespan=lifespan # 注册生命周期事件
)

# --- 添加 Prometheus 监控中间件 ---
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start_time = time.time()
    
    # 获取请求信息
    method = request.method
    endpoint = request.url.path
    
    # 调用下一个中间件/路由处理器
    response = await call_next(request)
    
    # 计算处理时间
    process_time = time.time() - start_time
    
    # 更新指标
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=response.status_code).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(process_time)
    
    return response

# --- 推荐函数 ---
def get_recommendations_logic(article_id: int, top_n: int = 5, sim_threshold: float = 0.05):
    if df is None or cosine_sim is None:
        logger.error("数据或相似度矩阵未加载。")
        return []

    if article_id not in df['article_id'].values:
        logger.warning(f"推荐逻辑：文章ID {article_id} 未找到。")
        return []

    idx = df[df['article_id'] == article_id].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    filtered_scores = [
        s for s in sim_scores
        if s[0] != idx and s[1] > sim_threshold
    ]

    if not filtered_scores:
        logger.info(f"文章ID {article_id} 未找到高于阈值 ({sim_threshold}) 的推荐。")
        return []

    article_indices = [i[0] for i in filtered_scores[0:top_n]]
    
    # Prepare data for RecommendedArticle model (title, url, article_id)
    recommendations_data = []
    for i in article_indices:
        recommendations_data.append({
            "article_id": df.loc[i, 'article_id'],
            "title": df.loc[i, 'title'], # Use renamed 'title'
            "url": df.loc[i, 'url']      # Use renamed 'url'
        })
    return recommendations_data

# --- API 接口 (Endpoint) ---
@app.post("/recommend", response_model=RecommendationResponse, status_code=status.HTTP_200_OK, summary="根据文章ID获取推荐文章")
async def recommend_articles(request: RecommendationRequest):
    logger.info(f"收到推荐请求：文章ID={request.article_id}, 推荐数量={request.top_n}")

    if df is None or cosine_sim is None:
        logger.error("API 收到请求但核心数据/模型未加载。")
        RECOMMENDATION_REQUESTS.labels(status="error").inc()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="推荐服务正在初始化或遇到内部错误，请稍后重试。"
        )

    if request.article_id not in df['article_id'].values:
        logger.warning(f"请求的文章ID {request.article_id} 未找到。")
        RECOMMENDATION_REQUESTS.labels(status="not_found").inc()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文章ID {request.article_id} 未在数据集中找到。"
        )

    try:
        recommendations = get_recommendations_logic(request.article_id, request.top_n)
        if not recommendations:
            logger.info(f"未找到文章ID {request.article_id} 的推荐内容。")
            RECOMMENDATION_REQUESTS.labels(status="no_recommendations").inc()
            return RecommendationResponse(
                message=f"未找到文章ID {request.article_id} 的推荐内容，或所有相似文章均低于阈值。",
                recommendations=[]
            )
        
        logger.info(f"成功为文章ID {request.article_id} 找到 {len(recommendations)} 条推荐。")
        RECOMMENDATION_REQUESTS.labels(status="success").inc()
        return RecommendationResponse(
            message="成功获取推荐",
            recommendations=recommendations
        )
    except Exception as e:
        logger.error(f"处理文章ID {request.article_id} 的推荐请求时发生未知错误: {e}", exc_info=True)
        RECOMMENDATION_REQUESTS.labels(status="error").inc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="处理推荐请求时发生内部服务器错误。"
        )

@app.get("/", summary="API 根路径")
async def root():
    return {"message": "欢迎使用 Real Python 文章推荐 API! 访问 /docs 查看 API 文档。"}

@app.get("/health", summary="健康检查接口")
async def health_check():
    # 简单的健康检查，可以根据需要扩展，例如检查数据库连接、模型加载状态等
    if df is not None and cosine_sim is not None:
        return {"status": "ok", "message": "API 运行正常，数据和模型已加载。"}
    else:
        return {"status": "error", "message": "API 遇到问题，核心数据或模型未加载。"}

# --- Prometheus 指标端点 ---
@app.get("/metrics", summary="Prometheus 监控指标")
async def metrics():
    """返回 Prometheus 格式的监控指标"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# --- 直接运行脚本进行本地测试 (可选) ---
if __name__ == "__main__":
    logger.info("尝试以本地开发模式启动 Uvicorn 服务器...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info") 