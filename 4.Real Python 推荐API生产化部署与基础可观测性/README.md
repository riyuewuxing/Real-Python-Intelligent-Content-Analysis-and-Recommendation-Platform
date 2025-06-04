# 📚 Real Python 博客推荐系统：我的生产级部署与基础可观测性
# 📚 Real Python 博客推荐系统：生产级部署与基础可观测性

这是一个基于内容相似度开发的 Real Python 博客文章推荐系统，集成了主题分析仪表盘和智能推荐功能，支持容器化部署和完整的生产环境监控。

## 🌟 项目特色

- **🚀 完整的微服务架构**：使用FastAPI 后端 + Streamlit 前端
- **🐳 多阶段容器化部署**：优化了镜像体积，提高了构建效率
- **📊 集成数据分析**：实现的LDA 主题建模 + 可视化仪表盘
- **🎯 智能推荐**：基于 TF-IDF 和余弦相似度的文章推荐
- **🔧 生产级配置**：配置的Nginx 反向代理、健康检查、自动重启
- **📈 完整可观测性**：搭建的Prometheus + Grafana + AlertManager 监控栈
- **🔍 日志聚合**：集成的Loki + Promtail 集中式日志管理
- **🚨 智能告警**：设计的基于指标的自动告警系统
- **🛡️ 安全配置**：配置的HTTPS 支持、安全头部、非 root 用户运行

## 📁 项目结构

```
.
├── api/                                # FastAPI 后端服务
│   └── main.py                        # API 主程序（含 Prometheus 指标）
├── frontend/                          # Streamlit 前端应用
│   ├── app.py                        # 前端主程序
│   ├── requirements.txt              # 前端依赖
│   └── Dockerfile                    # 前端容器配置
├── nginx/                            # Nginx 配置
│   └── nginx.conf                   # 反向代理配置
├── monitoring/                       # 监控配置
│   ├── prometheus.yml               # Prometheus 配置
│   ├── alertmanager.yml            # 告警管理配置
│   ├── blackbox.yml                # 黑盒监控配置
│   ├── loki-config.yml             # 日志聚合配置
│   ├── promtail-config.yml         # 日志收集配置
│   ├── rules/
│   │   └── alerts.yml              # 告警规则
│   └── grafana/                    # Grafana 配置
│       ├── provisioning/           # 自动配置
│       └── dashboards/             # 预置的仪表盘
├── Dockerfile                        # API 多阶段容器配置
├── docker-compose.yml               # 生产环境编排
├── docker-compose.dev.yml           # 开发环境编排
├── docker-compose.monitoring.yml    # 完整监控栈编排
├── start-dev.ps1                   # Windows 启动脚本
├── start-dev.sh                    # Linux/Mac 启动脚本
├── deploy.sh                       # 生产环境部署脚本
├── requirements.txt                # API 依赖（含监控）
├── real_python_courses_analysis.csv  # 数据文件
├── DEPLOYMENT_GUIDE.md            # 详细部署指南
└── README.md                       # 项目文档
```

## 🛠️ 技术栈

### 后端 (API)
- **FastAPI**: 选择的高性能 Web 框架
- **scikit-learn**: 使用的机器学习库 (TF-IDF, 余弦相似度)
- **NLTK & spaCy**: 采用的自然语言处理工具
- **pandas**: 用于数据处理
- **uvicorn**: 使用的ASGI 服务器
- **prometheus_client**: 集成的监控指标收集

### 前端 (Frontend)
- **Streamlit**: 选择的数据应用框架
- **Plotly**: 用于交互式可视化
- **WordCloud**: 用于词云生成
- **matplotlib**: 用于静态图表

### 基础设施
- **Docker**: 使用的容器化（多阶段构建）
- **Docker Compose**: 采用的服务编排
- **Nginx**: 配置的反向代理和负载均衡

### 监控栈
- **Prometheus**: 用于指标收集和存储
- **Grafana**: 用于监控仪表盘和可视化
- **AlertManager**: 配置的告警管理和通知
- **Node Exporter**: 部署的系统指标收集
- **cAdvisor**: 使用的容器指标收集
- **Blackbox Exporter**: 配置的黑盒监控
- **Loki**: 部署的日志聚合
- **Promtail**: 配置的日志收集

## 🚀 快速开始指南

### 前置要求

- Docker Desktop (Windows/Mac) 或 Docker Engine (Linux)
- Docker Compose
- 至少 4GB 可用内存（完整模式需要 8GB）

### 方法一：使用启动脚本 (推荐)

**Windows:**
```powershell
# 克隆项目
git clone <repository-url>
cd real-python-recommender

# 运行启动脚本
.\start-dev.ps1

# 选择启动模式：
# 1) 基础模式 (API + 前端)
# 2) 完整模式 (包含监控栈)
# 3) 仅监控服务
# 4) 停止所有服务
```

**Linux/Mac:**
```bash
# 克隆项目
git clone <repository-url>
cd real-python-recommender

# 设置脚本权限
chmod +x start-dev.sh

# 启动开发环境
./start-dev.sh
```

### 方法二：手动启动服务

```bash
# 基础模式：启动 API 和前端
docker-compose -f docker-compose.dev.yml up --build -d

# 完整模式：启动所有服务（包含监控）
docker-compose -f docker-compose.monitoring.yml up --build -d

# 生产模式：包含 Nginx 反向代理
docker-compose --profile production up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 访问应用

启动成功后，可以通过以下地址访问服务：

#### 基础服务
- **📊 Streamlit 前端**: http://localhost:8501
- **🔌 API 文档**: http://localhost:8000/docs
- **❤️ 健康检查**: http://localhost:8000/health
- **📈 API 指标**: http://localhost:8000/metrics

#### 监控服务（完整模式）
- **📊 Grafana 仪表盘**: http://localhost:3000 (admin/admin123)
- **🔍 Prometheus**: http://localhost:9090
- **🚨 AlertManager**: http://localhost:9093
- **📋 Node Exporter**: http://localhost:9100
- **🐳 cAdvisor**: http://localhost:8080

## 🎯 功能使用指南

### 1. 数据概览
- 查看提供的数据集统计信息
- 制作的文章长度分布图表
- 实现的数据质量检查

### 2. 主题分析仪表盘
- **LDA 主题建模**: 发现文章主要主题
- **交互式可视化**: 制作的主题权重分布图
- **词云生成**: 生成的各主题关键词可视化
- **参数调节**: 提供的动态调整主题数量功能

### 3. 智能推荐器
- **实时推荐**: 输入文章ID获取推荐的相似文章
- **API状态监控**: 实时检查后端服务状态
- **批量测试**: 提供的随机测试多篇文章推荐效果
- **结果展示**: 展示推荐文章标题、链接和相似度

### 4. 监控仪表盘
- **系统监控**: 监控的CPU、内存、磁盘使用率
- **应用监控**: 监控的API 响应时间、错误率、请求量
- **容器监控**: 监控的Docker 容器资源使用情况
- **告警管理**: 设置的自动告警和通知

## 🔧 高级配置

### 生产环境部署

详细的生产环境部署指南请参阅 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

```bash
# 快速部署到云服务器
scp -r ./real-python-recommender ubuntu@<server-ip>:/home/ubuntu/
ssh ubuntu@<server-ip>
cd /home/ubuntu/real-python-recommender
chmod +x deploy.sh
./deploy.sh
```

### 环境变量配置

```bash
# API 配置
PYTHONPATH=/app
NLTK_DATA=/home/appuser/nltk_data
ENVIRONMENT=production

# 前端配置
API_BASE_URL=http://api:8000
STREAMLIT_SERVER_PORT=8501

# 监控配置
PROMETHEUS_RETENTION=30d
GRAFANA_ADMIN_PASSWORD=your_secure_password
```

### 资源限制配置

```yaml
# 在 docker-compose.yml 中调整资源限制
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
    reservations:
      memory: 1G
      cpus: '0.5'
```

## 📊 API 接口文档

### 推荐接口

**POST** `/recommend`

请求体：
```json
{
  "article_id": 10,
  "top_n": 5
}
```

响应：
```json
{
  "message": "推荐成功",
  "recommendations": [
    {
      "article_id": 25,
      "title": "Python Decorators",
      "url": "https://realpython.com/python-decorators/"
    }
  ]
}
```

### 健康检查

**GET** `/health`

响应：
```json
{
  "status": "ok",
  "message": "API 运行正常，数据和模型已加载。"
}
```

### 监控指标

**GET** `/metrics`

返回 Prometheus 格式的监控指标：
- `http_requests_total`: HTTP 请求总数
- `http_request_duration_seconds`: 请求延迟分布
- `recommendation_requests_total`: 推荐请求统计
- `dataset_articles_total`: 数据集文章数量
- `model_loaded_status`: 模型加载状态

## 🔍 监控与告警

### 内置监控指标

- **系统指标**: CPU、内存、磁盘、网络使用率
- **应用指标**: API 响应时间、错误率、吞吐量
- **业务指标**: 推荐成功率、用户行为统计
- **容器指标**: Docker 容器资源使用情况

### 预置告警规则

- API 服务不可用
- 响应时间过长（>2秒）
- 错误率过高（>10%）
- 系统资源使用率过高（>85%）
- 磁盘空间不足（<15%）
- 容器重启频率过高

### Grafana 仪表盘

预置了完整的监控仪表盘，包括：
- API 性能监控
- 系统资源监控
- 推荐服务业务监控
- 告警状态概览

## 🔧 故障排除

### 常见问题

#### 1. 容器启动失败
```bash
# 查看详细日志
docker-compose logs -f <service-name>

# 重启特定服务
docker-compose restart <service-name>
```

#### 2. 端口冲突
```bash
# 检查端口占用
netstat -tlnp | grep <port>

# 修改端口映射
ports:
  - "8502:8501"  # 修改外部端口
```

#### 3. 内存不足
```bash
# 检查系统资源
docker stats

# 调整资源限制
deploy:
  resources:
    limits:
      memory: 512M
```

#### 4. 数据文件访问权限
```bash
# 检查文件权限
ls -la real_python_courses_analysis.csv

# 修复权限
chmod 644 real_python_courses_analysis.csv
```

### 调试模式

```