# 📚 Real Python 博客推荐系统：生产级部署与基础可观测性

一个基于内容相似度的 Real Python 博客文章推荐系统，集成了主题分析仪表盘和智能推荐功能，支持容器化部署和完整的生产环境监控。

## 🌟 项目特色

- **🚀 完整的微服务架构**：FastAPI 后端 + Streamlit 前端
- **🐳 多阶段容器化部署**：优化镜像体积，提高构建效率
- **📊 集成数据分析**：LDA 主题建模 + 可视化仪表盘
- **🎯 智能推荐**：基于 TF-IDF 和余弦相似度的文章推荐
- **🔧 生产级配置**：Nginx 反向代理、健康检查、自动重启
- **📈 完整可观测性**：Prometheus + Grafana + AlertManager 监控栈
- **🔍 日志聚合**：Loki + Promtail 集中式日志管理
- **🚨 智能告警**：基于指标的自动告警系统
- **🛡️ 安全配置**：HTTPS 支持、安全头部、非 root 用户运行

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
│       └── dashboards/             # 预置仪表盘
├── Dockerfile                        # API 多阶段容器配置
├── docker-compose.yml               # 生产环境编排
├── docker-compose.dev.yml           # 开发环境编排
├── docker-compose.monitoring.yml    # 完整监控栈编排
├── start-dev.ps1                   # Windows 启动脚本
├── start-dev.sh                    # Linux/Mac 启动脚本
├── deploy.sh                       # 生产环境部署脚本
├── requirements.txt                # API 依赖（含监控）
├── real_python_sentiment_analysis.csv  # 数据文件
├── DEPLOYMENT_GUIDE.md            # 详细部署指南
└── README.md                       # 项目文档
```

## 🛠️ 技术栈

### 后端 (API)
- **FastAPI**: 高性能 Web 框架
- **scikit-learn**: 机器学习库 (TF-IDF, 余弦相似度)
- **NLTK & spaCy**: 自然语言处理
- **pandas**: 数据处理
- **uvicorn**: ASGI 服务器
- **prometheus_client**: 监控指标收集

### 前端 (Frontend)
- **Streamlit**: 数据应用框架
- **Plotly**: 交互式可视化
- **WordCloud**: 词云生成
- **matplotlib**: 静态图表

### 基础设施
- **Docker**: 容器化（多阶段构建）
- **Docker Compose**: 服务编排
- **Nginx**: 反向代理和负载均衡

### 监控栈
- **Prometheus**: 指标收集和存储
- **Grafana**: 监控仪表盘和可视化
- **AlertManager**: 告警管理和通知
- **Node Exporter**: 系统指标收集
- **cAdvisor**: 容器指标收集
- **Blackbox Exporter**: 黑盒监控
- **Loki**: 日志聚合
- **Promtail**: 日志收集

## 🚀 快速开始

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

### 方法二：手动启动

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

启动成功后，可以通过以下地址访问：

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
- 查看数据集统计信息
- 文章长度分布图表
- 数据质量检查

### 2. 主题分析仪表盘
- **LDA 主题建模**: 发现文章主要主题
- **交互式可视化**: 主题权重分布图
- **词云生成**: 各主题关键词可视化
- **参数调节**: 动态调整主题数量

### 3. 智能推荐器
- **实时推荐**: 输入文章ID获取相似文章
- **API状态监控**: 实时检查后端服务状态
- **批量测试**: 随机测试多篇文章推荐效果
- **结果展示**: 推荐文章标题、链接和相似度

### 4. 监控仪表盘
- **系统监控**: CPU、内存、磁盘使用率
- **应用监控**: API 响应时间、错误率、请求量
- **容器监控**: Docker 容器资源使用情况
- **告警管理**: 自动告警和通知

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
ls -la real_python_sentiment_analysis.csv

# 修复权限
chmod 644 real_python_sentiment_analysis.csv
```

### 调试模式

```bash
# 启动单个服务调试
docker-compose up api  # 不使用 -d 参数

# 进入容器内部调试
docker exec -it real-python-api /bin/bash

# 查看实时日志
docker-compose logs -f --tail=100
```

## 🔄 维护与更新

### 常用维护命令

```bash
# 查看服务状态
docker-compose ps

# 查看资源使用
docker stats

# 清理无用镜像
docker system prune -f

# 备份重要数据
docker-compose exec prometheus tar czf /tmp/backup.tar.gz /prometheus
```

### 更新流程

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 重新构建镜像
docker-compose build --no-cache

# 3. 重启服务
docker-compose up -d

# 4. 验证更新
curl http://localhost:8000/health
```

## 🚀 性能优化

### API 优化
- 增加 worker 进程数量
- 启用响应缓存
- 优化数据预处理流程

### 监控优化
- 调整指标收集间隔
- 配置数据保留策略
- 优化告警规则

### 资源优化
- 设置合理的资源限制
- 启用镜像缓存
- 使用多阶段构建减小镜像体积

## 📚 文档链接

- [详细部署指南](./DEPLOYMENT_GUIDE.md)
- [API 在线文档](http://localhost:8000/docs)
- [监控仪表盘](http://localhost:3000)

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [Real Python](https://realpython.com/) - 优质的 Python 教程内容
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [Streamlit](https://streamlit.io/) - 快速构建数据应用
- [Prometheus](https://prometheus.io/) - 监控和告警系统
- [Grafana](https://grafana.com/) - 监控数据可视化

---

## 📞 技术支持

如果您在使用过程中遇到任何问题，请：

1. 查看 [故障排除](#故障排除) 部分
2. 阅读 [详细部署指南](./DEPLOYMENT_GUIDE.md)
3. 提交 [GitHub Issue](https://github.com/your-repo/issues)
4. 联系项目维护者

**祝您使用愉快！** 🎉 