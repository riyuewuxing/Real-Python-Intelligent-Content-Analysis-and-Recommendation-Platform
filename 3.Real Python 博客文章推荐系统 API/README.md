# Real Python 博客文章推荐系统 API (V2.0 - 增强版)

## 项目简介

此项目的核心是将 Real Python 博客文章数据，转化为一个能够提供个性化内容推荐的后端服务。这是一个基于 FastAPI 构建的 RESTful API，采用基于内容的推荐算法 (Content-Based Recommendation) 和 TF-IDF 文本特征提取技术，为用户提供与指定文章内容相似的其他文章列表。

## 技术栈

- Python 3.8+
- Pandas: 用于数据加载、处理与操作。
- NumPy: 用于高效数值计算。
- scikit-learn: 用于TF-IDF 向量化和余弦相似度计算。
- NLTK: 用于文本预处理（停用词去除、词形还原）。
- SpaCy: 用于文本预处理（词形还原、分词）。
- FastAPI: 用于构建 RESTful API。
- Pydantic: 用于API 数据模型验证。
- Uvicorn: 用作ASGI 服务器，用于运行 FastAPI 应用。

## 数据要求

- **数据源**: `real_python_courses_analysis.csv` 文件 (之前的爬虫项目生成)。
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
├── utils/            # (可选) 可能添加的辅助模块，例如独立的文本处理器或推荐器逻辑
├── real_python_courses_analysis.csv # 数据文件
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
4.  **准备数据文件**: 将包含文章数据的 CSV 文件 (例如 `real_python_courses_analysis.csv`) 复制到项目根目录，并确保其名称为 `real_python_courses_analysis.csv`，或者修改 `api/main.py` 中 `pd.read_csv()` 的文件名。
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
    except json.JSONDecodeError:
        print(f"错误响应 (非JSON): {response_invalid.text}")
    ```

## 核心算法说明

### 基于内容的推荐算法
推荐系统采用以下步骤：

1. **文本预处理**: 对文章内容进行清洗、分词、去停用词等处理
2. **特征提取**: 使用TF-IDF向量化将文本转换为数值特征
3. **相似度计算**: 使用余弦相似度计算文章间的相似性
4. **推荐生成**: 返回与目标文章最相似的N篇文章

### 算法优势
- **冷启动友好**: 算法不依赖用户行为数据
- **可解释性强**: 可以明确知道推荐的原因（内容相似）
- **实时性好**: 算法计算速度快，适合实时推荐

## 性能说明

- **启动时间**: 首次启动时需要加载和处理数据，可能需要几十秒
- **响应时间**: 数据加载完成后，单次推荐请求通常在100ms内完成
- **内存使用**: 系统内存使用量取决于文章数量，通常在几百MB到几GB之间

## 故障排除

### 常见问题

1. **依赖安装失败**
   - 确保Python版本为3.8+
   - 建议使用虚拟环境避免依赖冲突

2. **数据文件找不到**
   - 确保CSV文件路径正确
   - 检查文件名是否匹配代码中的设置

3. **服务启动失败**
   - 检查端口8000是否被占用
   - 查看错误日志确定具体问题

## 未来改进计划

计划在未来版本中添加：

- **混合推荐算法**: 结合协同过滤和内容推荐
- **多语言支持**: 支持中文等其他语言的文章推荐
- **个性化推荐**: 基于用户历史行为的个性化推荐
- **推荐解释**: 提供推荐理由和置信度
- **缓存优化**: 添加Redis缓存提高响应速度
- **A/B测试**: 支持不同推荐算法的效果对比

---

**注意**: 这是一个学习项目，主要用于展示推荐系统的基本原理和实现方法。在生产环境中使用时，建议进行更多的性能优化和安全考虑。 