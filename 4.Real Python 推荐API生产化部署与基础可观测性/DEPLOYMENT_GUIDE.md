# 📚 Real Python 推荐系统部署指南

本文档提供了完整的部署指南，涵盖从开发环境到生产环境的所有部署场景。

## 📋 目录

- [快速开始](#快速开始)
- [环境要求](#环境要求)
- [开发环境部署](#开发环境部署)
- [生产环境部署](#生产环境部署)
- [监控配置](#监控配置)
- [故障排除](#故障排除)
- [维护与更新](#维护与更新)

## 🚀 快速开始

### Windows 用户

```powershell
# 1. 克隆项目
git clone <repository-url>
cd real-python-recommender

# 2. 启动开发环境
.\start-dev.ps1
```

### Linux/Mac 用户

```bash
# 1. 克隆项目
git clone <repository-url>
cd real-python-recommender

# 2. 设置脚本权限
chmod +x start-dev.sh
chmod +x deploy.sh

# 3. 启动开发环境
./start-dev.sh
```

## 🛠️ 环境要求

### 基础要求

- **Docker**: >= 20.10.0
- **Docker Compose**: >= 2.0.0
- **操作系统**: 
  - Linux (Ubuntu 18.04+, CentOS 7+)
  - macOS 10.14+
  - Windows 10 Pro/Enterprise (带 WSL2)

### 硬件要求

| 部署模式 | CPU | 内存 | 存储 |
|---------|-----|------|------|
| 基础模式 | 2 核 | 4GB | 10GB |
| 完整模式 | 4 核 | 8GB | 20GB |
| 生产环境 | 8 核 | 16GB | 50GB |

### 网络端口

| 服务 | 端口 | 描述 |
|-----|------|------|
| Streamlit 前端 | 8501 | Web 界面 |
| FastAPI 后端 | 8000 | API 服务 |
| Nginx | 80/443 | 反向代理 |
| Prometheus | 9090 | 监控数据收集 |
| Grafana | 3000 | 监控仪表盘 |
| AlertManager | 9093 | 告警管理 |

## 💻 开发环境部署

### 方法一：使用启动脚本（推荐）

#### Windows

```powershell
# 启动完整开发环境
.\start-dev.ps1

# 选择启动模式：
# 1) 基础模式 (API + 前端)
# 2) 完整模式 (包含监控)
# 3) 仅监控服务
# 4) 停止所有服务
```

#### Linux/Mac

```bash
# 启动完整开发环境
./start-dev.sh

# 选择相应的启动模式
```

### 方法二：手动启动

```bash
# 基础模式
docker-compose -f docker-compose.dev.yml up -d

# 完整模式（包含监控）
docker-compose -f docker-compose.monitoring.yml up -d

# 仅启动特定服务
docker-compose up -d api frontend
```

### 验证部署

访问以下地址验证服务正常运行：

- **前端应用**: http://localhost:8501
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **监控指标**: http://localhost:8000/metrics

## 🏭 生产环境部署

### 云服务器准备

1. **购买云服务器**（推荐配置：4核8GB）
2. **配置安全组**：开放端口 22, 80, 443, 8000, 8501
3. **生成SSH密钥对**并配置到服务器

### 自动化部署

```bash
# 1. 上传项目到服务器
scp -r -i your-key.pem ./real-python-recommender ubuntu@<server-ip>:/home/ubuntu/

# 2. 连接到服务器
ssh -i your-key.pem ubuntu@<server-ip>

# 3. 运行自动部署脚本
cd /home/ubuntu/real-python-recommender
chmod +x deploy.sh
./deploy.sh
```

### 手动部署步骤

#### 1. 安装基础环境

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 重启以应用用户组更改
sudo reboot
```

#### 2. 部署应用

```bash
# 构建并启动生产环境
docker-compose --profile production up -d

# 检查服务状态
docker-compose ps
```

#### 3. 配置 Nginx 和 HTTPS

```bash
# 安装 Nginx
sudo apt install nginx -y

# 配置 Nginx（可选，如果使用独立 Nginx）
sudo cp nginx/nginx.conf /etc/nginx/sites-available/real-python-recommender
sudo ln -s /etc/nginx/sites-available/real-python-recommender /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# 安装 SSL 证书（如果有域名）
sudo apt install snapd
sudo snap install --classic certbot
sudo certbot --nginx -d your-domain.com
```

## 📊 监控配置

### 启动完整监控栈

```bash
# 启动所有监控服务
docker-compose -f docker-compose.monitoring.yml up -d

# 验证监控服务
curl http://localhost:9090/-/healthy  # Prometheus
curl http://localhost:3000/api/health # Grafana
```

### Grafana 配置

1. **访问 Grafana**: http://localhost:3000
2. **登录**: admin / admin123
3. **导入仪表盘**: 
   - 预置仪表盘会自动加载
   - 或手动导入 `monitoring/grafana/dashboards/` 下的文件

### 告警配置

编辑 `monitoring/alertmanager.yml` 配置告警接收方式：

```yaml
# 邮件告警示例
receivers:
- name: 'email-alert'
  email_configs:
  - to: 'admin@example.com'
    subject: '[Alert] {{ .GroupLabels.alertname }}'
    body: |
      {{ range .Alerts }}
      Alert: {{ .Annotations.summary }}
      Description: {{ .Annotations.description }}
      {{ end }}
```

## 🔧 故障排除

### 常见问题

#### 1. 容器启动失败

```bash
# 查看容器日志
docker-compose logs <service-name>

# 查看所有服务状态
docker-compose ps

# 重启特定服务
docker-compose restart <service-name>
```

#### 2. 端口冲突

```bash
# 检查端口占用
netstat -tlnp | grep <port>

# 修改 docker-compose.yml 中的端口映射
ports:
  - "8502:8501"  # 将前端改为8502端口
```

#### 3. 内存不足

```bash
# 检查系统资源
free -h
df -h

# 限制容器资源使用
deploy:
  resources:
    limits:
      memory: 512M
```

#### 4. API 无法访问数据文件

```bash
# 检查文件权限
ls -la real_python_sentiment_analysis.csv

# 修复权限
chmod 644 real_python_sentiment_analysis.csv
```

### 调试模式

```bash
# 启动单个服务进行调试
docker-compose up api  # 不使用 -d 参数

# 进入容器调试
docker exec -it real-python-api /bin/bash

# 查看详细日志
docker-compose logs -f --tail=100 api
```

## 🔄 维护与更新

### 日常维护

```bash
# 查看服务状态
docker-compose ps

# 查看资源使用
docker stats

# 清理无用镜像
docker system prune -f

# 备份数据
docker-compose exec prometheus tar czf /tmp/prometheus-backup.tar.gz /prometheus
```

### 更新应用

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

### 数据备份

```bash
# 备份 Prometheus 数据
docker cp prometheus:/prometheus ./prometheus-backup

# 备份 Grafana 数据
docker cp grafana:/var/lib/grafana ./grafana-backup

# 创建完整备份脚本
cat << 'EOF' > backup.sh
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p ./backups/$DATE

# 备份配置文件
cp -r monitoring ./backups/$DATE/
cp docker-compose*.yml ./backups/$DATE/

# 备份数据
docker cp prometheus:/prometheus ./backups/$DATE/prometheus-data
docker cp grafana:/var/lib/grafana ./backups/$DATE/grafana-data

echo "备份完成: ./backups/$DATE"
EOF

chmod +x backup.sh
```

### 性能优化

#### 1. API 优化

```python
# 增加 workers 数量
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### 2. 数据库优化

```bash
# 如果使用数据库，添加连接池配置
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
```

#### 3. 缓存配置

```yaml
# 添加 Redis 缓存服务
redis:
  image: redis:alpine
  container_name: redis
  ports:
    - "6379:6379"
```

### 监控告警配置

```yaml
# 添加自定义告警规则
- alert: HighAPILatency
  expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "API 响应延迟过高"
    description: "95% 的请求响应时间超过 1 秒"
```

## 🚀 高级配置

### 多环境部署

创建不同环境的配置文件：

```bash
# 开发环境
docker-compose -f docker-compose.dev.yml up -d

# 测试环境
docker-compose -f docker-compose.test.yml up -d

# 生产环境
docker-compose -f docker-compose.prod.yml up -d
```

### 集群部署

```yaml
# docker-compose.cluster.yml
version: '3.8'
services:
  api:
    deploy:
      replicas: 3
      placement:
        constraints:
          - node.role == worker
```

### CI/CD 集成

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production
on:
  push:
    branches: [ main ]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to server
        run: |
          ssh user@server 'cd /app && git pull && docker-compose up -d --build'
```

---

## 📞 技术支持

如遇到问题，请：

1. 查看 [故障排除](#故障排除) 部分
2. 检查项目 Issues
3. 联系技术支持团队

**祝您部署顺利！** 🎉 