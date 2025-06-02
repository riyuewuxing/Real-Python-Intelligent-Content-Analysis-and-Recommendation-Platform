# --- Stage 1: Build Environment ---
FROM python:3.9-slim-buster as builder

# 设置环境变量，避免 Python 缓存和日志缓冲
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV BLIS_ARCH=generic

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制并安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 下载 NLTK 和 SpaCy 语料库和模型
RUN python -m nltk.downloader stopwords wordnet averaged_perceptron_tagger
RUN python -m spacy download en_core_web_sm

# --- Stage 2: Production Environment ---
FROM python:3.9-slim-buster

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/home/appuser/.local/lib/python3.9/site-packages:/app
ENV BLIS_ARCH=generic

# 安装运行时依赖（仅包含必要的依赖）
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 创建非 root 用户
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup --no-create-home appuser && \
    mkdir -p /home/appuser/nltk_data && \
    mkdir -p /app

# 从 builder 阶段复制安装的依赖
COPY --from=builder --chown=appuser:appgroup /root/.local /home/appuser/.local
COPY --from=builder --chown=appuser:appgroup /root/nltk_data /home/appuser/nltk_data

# 设置环境变量（在复制依赖之后）
ENV PATH=/home/appuser/.local/bin:$PATH
ENV NLTK_DATA=/home/appuser/nltk_data

# 复制应用程序代码
COPY --chown=appuser:appgroup . /app

# 设置工作目录和用户
WORKDIR /app
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["/home/appuser/.local/bin/uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
