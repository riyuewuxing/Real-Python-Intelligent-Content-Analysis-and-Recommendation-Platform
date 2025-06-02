# Real Python 智能内容分析与推荐平台

这是一个完整的端到端智能推荐系统项目，专注于Real Python学习内容的智能分析与个性化推荐。项目涵盖了从数据收集、内容分析、算法开发到生产部署的完整机器学习工程流程。

## 🎯 项目概述

本平台通过四个相互关联的子系统，实现了Real Python内容的智能化处理：

- **数据收集层**：自动化网页爬虫获取最新内容
- **分析洞察层**：基于NLP的主题建模和内容分析
- **智能推荐层**：个性化文章推荐算法API
- **生产服务层**：企业级部署与可观测性监控

## 🚀 核心价值

- 📊 **智能内容分析**：使用先进的NLP技术进行主题建模和情感分析
- 🎯 **个性化推荐**：基于内容相似度的智能推荐算法
- 📈 **数据可视化**：交互式仪表盘展示内容分析结果
- 🏭 **生产级部署**：包含容器化、负载均衡、监控的完整DevOps流程

## 📁 项目结构

```
小项目/
├── shared_data/                    # 共享数据目录
│   ├── real_python_courses_analysis.csv      # 课程分析数据
│   └── real_python_sentiment_analysis.csv    # 情感分析数据
├── shared_venv/                    # 统一虚拟环境
├── requirements.txt                # 合并的依赖文件
├── setup_environment.bat          # 环境设置脚本
├── 1.Real Python 网页爬虫/
├── 2.Real Python 博客内容主题分析仪表盘/
├── 3.Real Python 博客文章推荐系统 API/
└── 4.Real Python 推荐API生产化部署与基础可观测性/
```

## 🚀 快速开始

### 1. 环境设置

**方式一：使用批处理脚本（推荐）**
```bash
setup_environment.bat
```

**方式二：手动设置**
```bash
# 创建虚拟环境
python -m venv shared_venv

# 激活虚拟环境 (Windows)
shared_venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 下载Spacy模型
python -m spacy download en_core_web_sm
```

### 2. 运行各个项目

**⚠️ 重要**: 请按以下顺序运行项目，确保数据流程正确：

#### 步骤1: 数据收集（必须首先执行）
```bash
cd "1.Real Python 网页爬虫"
python real_python_scraper.py
```
- **作用**: 生成共享数据文件供后续项目使用
- **配置**: 默认爬取1页（可修改 `MAX_PAGES_TO_SCRAPE` 增加数据量）
- **注意**: 遵守2秒延迟避免对网站造成压力

#### 步骤2: 内容分析仪表盘
```bash
cd "2.Real Python 博客内容主题分析仪表盘"
streamlit run topic_dashboard_enhanced.py
```
- **访问**: http://localhost:8501
- **功能**: 交互式主题建模和可视化分析
- **特色**: 词云生成、趋势分析、置信度评估

#### 步骤3: 基础推荐API
```bash
cd "3.Real Python 博客文章推荐系统 API"
uvicorn api.main:app --reload
```
- **访问**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **测试**: `curl -X POST "http://localhost:8000/recommend" -H "Content-Type: application/json" -d '{"article_id": 0, "top_n": 3}'`

#### 步骤4: 生产级API（含监控）
```bash
cd "4.Real Python 推荐API生产化部署与基础可观测性"
uvicorn api.main:app --reload
```
- **访问**: http://localhost:8000（增强版）
- **监控**: http://localhost:8000/metrics
- **特色**: Prometheus监控和生产级错误处理

**📝 注意事项**:
- 项目3和4使用相同端口(8000)，不能同时运行
- 项目4是项目3的生产增强版本
- 必须先运行步骤1获取数据，其他项目才能正常工作

## 📊 数据说明

### shared_data/
- **real_python_courses_analysis.csv**: 从Real Python网站爬取的文章和课程数据，所有项目共享使用

## 🛠️ 子系统详情

### 1. 数据收集层 - Real Python 网页爬虫
- **核心功能**: 自动化采集Real Python网站的文章、教程和课程信息
- **技术栈**: Python爬虫、数据清洗、CSV数据导出
- **输出**: 结构化数据为后续分析提供数据基础

### 2. 分析洞察层 - 博客内容主题分析仪表盘  
- **核心功能**: 基于机器学习的内容主题建模和可视化分析
- **技术栈**: Streamlit, NLTK, SpaCy, LDA主题建模, scikit-learn
- **特色**: 交互式数据探索、主题趋势分析、内容分布洞察
- **访问**: http://localhost:8501

### 3. 智能推荐层 - 博客文章推荐系统 API
- **核心功能**: 基于内容相似度的智能推荐算法服务
- **技术栈**: FastAPI, TF-IDF向量化, 余弦相似度计算
- **特色**: RESTful API设计、实时推荐、算法可解释性
- **访问**: http://localhost:8000

### 4. 生产服务层 - 推荐API生产化部署与基础可观测性
- **核心功能**: 企业级API服务部署、监控告警、性能优化
- **技术栈**: Docker容器化, Nginx负载均衡, Prometheus监控, Grafana可视化
- **特色**: 高可用架构、自动化部署、全链路监控
- **访问**: http://localhost:8000 (生产环境)

## 🔧 环境要求

- Python 3.8+
- 所有依赖已在 `requirements.txt` 中列出

## 📝 更新日志

### 文件夹整理 (最新)
- ✅ 统一虚拟环境：所有项目共享一个虚拟环境
- ✅ 共享数据目录：消除重复的CSV文件
- ✅ 合并依赖文件：统一的requirements.txt
- ✅ 路径更新：所有项目代码已更新为使用共享数据路径
- ✅ 清理冗余：删除重复的requirements文件和旧虚拟环境

## 💡 使用提示

1. **首次使用**: 运行 `setup_environment.bat` 进行环境初始化
2. **切换项目**: 确保虚拟环境已激活，然后进入对应项目目录
3. **数据更新**: 如需更新数据，运行项目1的爬虫脚本
4. **环境问题**: 如遇到依赖问题，可删除 `shared_venv` 文件夹重新运行设置脚本

## 🏗️ 技术架构特色

### 端到端机器学习工程
- **数据管道**: 爬虫 → 数据处理 → 特征工程 → 模型训练
- **服务化架构**: 微服务API设计、容器化部署
- **DevOps实践**: 自动化部署、监控告警、日志分析

### 现代技术栈集成
- **前端**: Streamlit数据应用 + 现代Web界面
- **后端**: FastAPI高性能异步框架
- **机器学习**: scikit-learn + NLTK + SpaCy NLP工具链
- **运维**: Docker + Nginx + Prometheus监控栈

### 可扩展设计
- 模块化架构支持独立开发和部署
- 统一数据接口便于功能扩展
- 标准化API设计支持多客户端接入

## 🎓 学习价值

这个项目是学习现代机器学习工程实践的绝佳案例，涵盖：

- **数据工程**: 网页爬虫、数据清洗、ETL流程
- **机器学习**: NLP处理、主题建模、推荐算法
- **软件工程**: API设计、测试、文档化
- **DevOps工程**: 容器化、监控、自动化部署
- **产品思维**: 用户体验、性能优化、可扩展性

## 🤝 技术支持

如遇到问题，请检查：
1. Python版本是否符合要求 (3.8+)
2. 虚拟环境是否正确激活
3. 依赖是否完整安装
4. 数据文件路径是否正确
5. 端口是否被占用 (8000, 8501)

---

**项目亮点**: 这是一个真实的端到端机器学习产品，从概念到生产的完整实现，展示了现代AI应用开发的最佳实践。 