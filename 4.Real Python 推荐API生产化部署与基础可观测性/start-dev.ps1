# Real Python 推荐系统开发环境启动脚本
Write-Host "🚀 启动 Real Python 推荐系统开发环境..." -ForegroundColor Green

# 检查Docker是否运行
try {
    docker version | Out-Null
    Write-Host "✅ Docker 服务正在运行" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker 服务未运行，请先启动 Docker Desktop" -ForegroundColor Red
    exit 1
}

# 检查docker-compose是否可用
try {
    docker-compose version | Out-Null
    Write-Host "✅ Docker Compose 可用" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose 不可用" -ForegroundColor Red
    exit 1
}

# 停止可能存在的旧容器
Write-Host "🛑 停止旧容器..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml down

# 构建并启动服务
Write-Host "🔨 构建并启动服务..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml up --build -d

# 等待服务启动
Write-Host "⏳ 等待服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 检查服务状态
Write-Host "📊 检查服务状态..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml ps

# 显示访问信息
Write-Host ""
Write-Host "🎉 启动完成！访问地址：" -ForegroundColor Green
Write-Host "  📊 Streamlit 前端: http://localhost:8501" -ForegroundColor Cyan
Write-Host "  🔌 API 文档: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  ❤️  健康检查: http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 查看日志命令:" -ForegroundColor Yellow
Write-Host "  docker-compose -f docker-compose.dev.yml logs -f"
Write-Host ""
Write-Host "🛑 停止服务命令:" -ForegroundColor Yellow
Write-Host "  docker-compose -f docker-compose.dev.yml down" 