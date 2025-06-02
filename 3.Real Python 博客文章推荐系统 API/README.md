# Real Python 博客文章推荐系统 API (V2.0 - 增强版)

## 项目简介

本项目的核心目的是将 Real Python 博客文章数据，转化为一个能够提供个性化内容推荐的后端服务。这是一个基于 FastAPI 构建的 RESTful API，采用基于内容的推荐算法 (Content-Based Recommendation) 和 TF-IDF 文本特征提取技术，为用户提供与指定文章内容相似的其他文章列表。

## 技术栈

- Python 3.8+
- Pandas: 数据加载、处理与操作。
- NumPy: 高效数值计算。
- scikit-learn: TF-IDF 向量化和余弦相似度计算。
- NLTK: 文本预处理（停用词去除、词形还原）。
- SpaCy: 文本预处理（词形还原、分词）。
- FastAPI: 构建 RESTful API。
- Pydantic: API 数据模型验证。
- Uvicorn: ASGI 服务器，用于运行 FastAPI 应用。

## 数据要求

- **数据源**: `real_python_sentiment_analysis.csv` 文件 (预期由之前的爬虫项目生成，并重命名)。
- **关键数据列**: 必须包含以下列 (或可以被脚本正确解析的类似列名，脚本内部会将它们映射为 `title`, `url`, `content`):
    - 文章标题 (例如: `Title`)
    - 文章URL (例如: `URL`)
    - 文章内容 (例如: `Content`): 必须是文章的完整正文内容。
- **文件位置**: CSV 文件应放置在项目的根目录下 (与 `api` 文件夹同级)。

## 项目结构

```
real_python_recommender_api/
├── api/
│   └── main.py       # FastAPI 应用主文件，包含所有API逻辑和模型加载
├── utils/            # (可选) 辅助模块，例如独立的文本处理器或推荐器逻辑
├── real_python_sentiment_analysis.csv # 数据文件
├── requirements.txt  # 项目依赖
└── README.md         # 项目说明文档
```

## API 接口定义

### 1. 获取推荐文章

- **URL**: `/recommend`
- **方法**: `POST`
- **请求体 (JSON)**:
  ```json
  {
    "article_id": 0,    // (必需) 要获取推荐的文章的唯一ID (整数, 通常是DataFrame的索引)
    "top_n": 5          // (可选) 返回推荐文章的数量 (整数, 默认为5)
  }
  ```
- **成功响应 (200 OK)**:
  ```json
  {
    "message": "成功为文章ID 0 找到 3 篇推荐文章。",
    "recommendations": [
      {
        "article_id": 10,
        "title": "Example Article Title 1",
        "url": "http://example.com/article1"
      },
      {
        "article_id": 25,
        "title": "Another Similar Article",
        "url": "http://example.com/article2"
      }
    ]
  }
  ```
- **错误响应**:
    - `404 Not Found`: 如果提供的 `article_id` 不存在。
      ```json
      {
        "detail": "文章ID 9999 未找到。请提供一个有效的文章ID。"
      }
      ```
    - `503 Service Unavailable`: 如果服务正在初始化或遇到内部错误。
      ```json
      {
        "detail": "推荐服务正在初始化或遇到内部错误，请稍后重试。"
      }
      ```

### 2. API 根路径

- **URL**: `/`
- **方法**: `GET`
- **响应 (200 OK)**:
  ```json
  {
    "message": "Real Python Article Recommendation API v2.0"
  }
  ```

### 3. 健康检查接口

- **URL**: `/health`
- **方法**: `GET`
- **成功响应 (200 OK)**:
  ```json
  {
    "status": "ok",
    "message": "Recommendation service is running and data loaded."
  }
  ```
- **失败响应 (503 Service Unavailable)**:
  ```json
  {
    "status": "error", // 或者直接返回503错误
    "detail": "Recommendation service is still loading data or encountered an error."
  }
  ```

## 如何运行

1.  **克隆/下载项目** (如果适用)。
2.  **创建并激活虚拟环境** (推荐):
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Linux/macOS
    # source venv/bin/activate
    ```
3.  **安装依赖**: 确保你在项目的根目录 (`real_python_recommender_api`)下，并且虚拟环境已激活。
    ```bash
    pip install -r requirements.txt
    ```
    在首次运行时，`api/main.py` 中的代码会自动尝试下载必要的 NLTK 和 SpaCy 数据模型。如果自动下载失败或网络受限，你可能需要手动下载它们：
    ```bash
    python -m spacy download en_core_web_sm
    python -m nltk.downloader stopwords wordnet averaged_perceptron_tagger punkt # punkt可能也需要
    ```
4.  **准备数据文件**: 将包含文章数据的 CSV 文件 (例如 `real_python_courses_analysis.csv`) 复制到项目根目录，并确保其名称为 `real_python_sentiment_analysis.csv`，或者修改 `api/main.py` 中 `pd.read_csv()` 的文件名。
5.  **运行 FastAPI 应用**: 在项目根目录下运行以下命令：
    ```bash
    uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
    ```
    - `api.main`: 指向 `api` 目录下的 `main.py` 文件。
    - `app`: FastAPI 实例的名称。
    - `--reload`: 代码更改后自动重载服务 (方便开发)。
    - `--host 0.0.0.0`: 允许从外部网络访问。
    - `--port 8000`: 指定服务端口。

## 如何测试

应用启动后，可以通过以下方式测试：

1.  **Swagger UI (自动交互式API文档)**:
    在浏览器中打开 `http://127.0.0.1:8000/docs`。你可以在这里直接测试所有 API 接口。

2.  **ReDoc (备选API文档)**:
    在浏览器中打开 `http://127.0.0.1:8000/redoc`。

3.  **使用 `curl` 或 API 测试工具 (如 Postman, Insomnia)**:
    例如，测试推荐接口:
    ```bash
    curl -X 'POST' \
      'http://127.0.0.1:8000/recommend' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{ 
        "article_id": 0, 
        "top_n": 3 
      }'
    ```
    (请确保 `article_id: 0` 是一个有效的数据行索引)

4.  **使用 Python `requests` 库 (示例脚本)**:

    ```python
    import requests
    import json

    api_url = "http://127.0.0.1:8000/recommend"
    
    # 假设 article_id 0 存在
    payload = {"article_id": 0, "top_n": 3}

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status() # 如果状态码是 4xx 或 5xx，则引发 HTTPError
        print("推荐结果:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 错误: {http_err}")
        try:
            print(f"错误详情: {response.json()}")
        except json.JSONDecodeError:
            print(f"错误详情 (非JSON): {response.text}")
    except requests.exceptions.RequestException as req_err:
        print(f"请求错误: {req_err}")

    # 测试无效 ID
    payload_invalid = {"article_id": 999999, "top_n": 3}
    try:
        response_invalid = requests.post(api_url, json=payload_invalid)
        print(f"\n测试无效ID ({payload_invalid['article_id']}) 状态码: {response_invalid.status_code}")
        print(json.dumps(response_invalid.json(), indent=2, ensure_ascii=False))
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")

    # 测试健康检查
    health_url = "http://127.0.0.1:8000/health"
    try:
        health_response = requests.get(health_url)
        health_response.raise_for_status()
        print(f"\n健康检查结果 ({health_url}):")
        print(json.dumps(health_response.json(), indent=2, ensure_ascii=False))
    except requests.exceptions.RequestException as e:
        print(f"健康检查失败: {e}")
    ```

## 核心亮点与实现细节

- **高效数据加载与预处理**: 应用启动时一次性加载和处理所有数据及模型，避免了每次请求的重复计算。
- **文本特征提取**: 使用 TF-IDF 将文本内容转化为数值向量，便于计算相似度。
- **内容相似度计算**: 采用余弦相似度来衡量文章之间的内容相似性。
- **RESTful API**: 基于 FastAPI 构建，自动生成 OpenAPI (Swagger & ReDoc) 文档。
- **数据验证**: 使用 Pydantic 模型进行请求和响应数据的自动验证和序列化。
- **NLP 处理**: 集成了 SpaCy 和 NLTK 进行文本的词形还原和停用词去除，以提高特征质量。
- **配置化与模块化**: 代码结构清晰，易于理解和扩展。
- **错误处理**: 对常见的错误情况（如文件未找到、文章ID无效）进行了处理，并返回有意义的错误信息。
- **异步处理**: FastAPI 默认支持异步请求处理，为未来扩展高并发场景奠定基础。

## 未来展望

- **更复杂的推荐算法**: 探索协同过滤、混合推荐模型或基于深度学习的推荐算法 (如使用 Sentence Transformers 获取更优的文本嵌入)。
- **用户行为数据集成**: 引入用户阅读历史、评分等行为数据，实现更个性化的推荐。
- **持久化存储**: 将预计算的相似度矩阵或推荐结果存入数据库 (如 Redis, PostgreSQL) 以加速查询，特别是对于大规模数据集。
- **近似最近邻 (ANN) 搜索**: 对于海量文章，使用 FAISS, Annoy 等库实现 ANN 搜索，以在可接受的精度损失下大幅提升大规模相似度查询效率。
- **配置管理**: 将文件路径、模型参数等配置移至环境变量或配置文件 (`.env`)。
- **单元测试与集成测试**: 为核心逻辑和 API 端点编写测试用例。
- **Docker 容器化**: 将应用打包成 Docker 镜像，方便部署和管理。
- **CI/CD 流水线**: 建立自动化构建、测试和部署流程。
- **更精细的文本预处理**: 根据数据特点调整预处理步骤，例如处理特定领域的术语、命名实体识别等。
- **API 认证与授权**: 为 API 添加安全机制。

## 贡献

欢迎提出问题、报告BUG或贡献代码。

---

祝您使用愉快！ 