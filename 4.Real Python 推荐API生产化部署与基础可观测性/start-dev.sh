#!/bin/bash

# Real Python 推荐系统开发环境启动脚本 (Linux/Mac)
# 功能：快速启动开发环境，包含完整的监控栈

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 项目信息
PROJECT_NAME="Real Python 推荐系统"
VERSION="2.0.0"

echo -e "${BLUE}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    📚 Real Python 博客推荐系统                               ║
║    🚀 生产级部署与基础可观测性                               ║
║                                                              ║
║    版本: 2.0.0                                               ║
║    包含: FastAPI + Streamlit + Nginx + 完整监控栈           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# 检查系统依赖
check_dependencies() {
    log_step "检查系统依赖..."
    
    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装。请先安装 Docker。"
        log_info "安装命令: curl -fsSL https://get.docker.com | sh"
        exit 1
    fi
    
    # 检查 Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose 未安装。"
        exit 1
    fi
    
    # 检查 Docker 是否运行
    if ! docker info &> /dev/null; then
        log_error "Docker 服务未运行。请启动 Docker 服务。"
        log_info "启动命令: sudo systemctl start docker"
        exit 1
    fi
    
    log_success "所有依赖检查通过！"
}

# 选择启动模式
select_mode() {
    echo
    log_step "选择启动模式："
    echo "  1) 🚀 基础模式 (API + 前端)"
    echo "  2) 📊 完整模式 (包含监控栈)"
    echo "  3) 🔧 仅监控服务"
    echo "  4) 🛑 停止所有服务"
    echo
    
    while true; do
        read -p "请选择模式 [1-4]: " choice
        case $choice in
            1)
                MODE="basic"
                break
                ;;
            2)
                MODE="full"
                break
                ;;
            3)
                MODE="monitoring"
                break
                ;;
            4)
                MODE="stop"
                break
                ;;
            *)
                log_warning "请选择有效选项 (1-4)"
                ;;
        esac
    done
}

# 停止服务
stop_services() {
    log_step "停止所有服务..."
    
    # 停止不同的compose文件
    if [ -f "docker-compose.yml" ]; then
        docker-compose down -v 2>/dev/null || true
    fi
    
    if [ -f "docker-compose.dev.yml" ]; then
        docker-compose -f docker-compose.dev.yml down -v 2>/dev/null || true
    fi
    
    if [ -f "docker-compose.monitoring.yml" ]; then
        docker-compose -f docker-compose.monitoring.yml down -v 2>/dev/null || true
    fi
    
    # 清理无用的容器和网络
    docker system prune -f &>/dev/null || true
    
    log_success "所有服务已停止！"
}

# 启动基础服务
start_basic() {
    log_step "启动基础服务 (API + 前端)..."
    
    if [ -f "docker-compose.dev.yml" ]; then
        docker-compose -f docker-compose.dev.yml up -d --build
    else
        docker-compose up -d --build api frontend
    fi
}

# 启动完整服务
start_full() {
    log_step "启动完整服务 (包含监控栈)..."
    
    if [ -f "docker-compose.monitoring.yml" ]; then
        docker-compose -f docker-compose.monitoring.yml up -d --build
    else
        log_error "监控配置文件不存在！"
        exit 1
    fi
}

# 启动仅监控服务
start_monitoring() {
    log_step "启动监控服务..."
    
    if [ -f "docker-compose.monitoring.yml" ]; then
        docker-compose -f docker-compose.monitoring.yml up -d prometheus grafana alertmanager node-exporter cadvisor
    else
        log_error "监控配置文件不存在！"
        exit 1
    fi
}

# 等待服务启动
wait_for_services() {
    log_step "等待服务启动完成..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo -n "."
        sleep 2
        
        # 检查基础服务
        if [ "$MODE" = "basic" ] || [ "$MODE" = "full" ]; then
            if curl -s http://localhost:8000/health > /dev/null 2>&1; then
                break
            fi
        fi
        
        # 检查监控服务
        if [ "$MODE" = "monitoring" ] || [ "$MODE" = "full" ]; then
            if curl -s http://localhost:9090 > /dev/null 2>&1; then
                break
            fi
        fi
        
        ((attempt++))
    done
    
    echo
    
    if [ $attempt -gt $max_attempts ]; then
        log_warning "服务启动可能需要更多时间，请稍后检查"
    else
        log_success "服务启动完成！"
    fi
}

# 显示服务状态
show_status() {
    log_step "检查服务状态..."
    
    echo
    echo "=== 容器状态 ==="
    if command -v docker-compose &> /dev/null; then
        docker-compose ps 2>/dev/null || docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    else
        docker compose ps 2>/dev/null || docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    fi
}

# 显示访问信息
show_access_info() {
    echo
    log_success "🎉 ${PROJECT_NAME} 启动完成！"
    echo
    echo "=== 📱 访问地址 ==="
    
    if [ "$MODE" = "basic" ] || [ "$MODE" = "full" ]; then
        echo -e "  📊 ${CYAN}Streamlit 前端:${NC}     http://localhost:8501"
        echo -e "  🔌 ${CYAN}API 文档:${NC}          http://localhost:8000/docs"
        echo -e "  ❤️  ${CYAN}健康检查:${NC}          http://localhost:8000/health"
        echo -e "  📈 ${CYAN}API 指标:${NC}          http://localhost:8000/metrics"
    fi
    
    if [ "$MODE" = "monitoring" ] || [ "$MODE" = "full" ]; then
        echo -e "  📊 ${CYAN}Grafana 仪表盘:${NC}    http://localhost:3000 (admin/admin123)"
        echo -e "  🔍 ${CYAN}Prometheus:${NC}        http://localhost:9090"
        echo -e "  🚨 ${CYAN}AlertManager:${NC}      http://localhost:9093"
        echo -e "  📋 ${CYAN}Node Exporter:${NC}     http://localhost:9100"
        echo -e "  🐳 ${CYAN}cAdvisor:${NC}          http://localhost:8080"
    fi
    
    echo
    echo "=== 🛠️  常用命令 ==="
    echo "  查看日志:     docker-compose logs -f"
    echo "  查看状态:     docker-compose ps"
    echo "  重启服务:     docker-compose restart"
    echo "  停止服务:     $0 (选择停止模式)"
    echo "  进入容器:     docker exec -it <container_name> /bin/bash"
    echo
    echo "=== 📚 更多信息 ==="
    echo "  项目文档:     README.md"
    echo "  API 文档:     http://localhost:8000/docs"
    echo "  技术支持:     https://github.com/your-repo"
}

# 健康检查
health_check() {
    if [ "$MODE" = "stop" ]; then
        return
    fi
    
    log_step "执行健康检查..."
    
    local failed_services=""
    
    # 检查基础服务
    if [ "$MODE" = "basic" ] || [ "$MODE" = "full" ]; then
        if ! curl -s http://localhost:8000/health | grep -q "ok"; then
            failed_services="${failed_services}API "
        fi
        
        if ! curl -s http://localhost:8501/_stcore/health > /dev/null 2>&1; then
            failed_services="${failed_services}Frontend "
        fi
    fi
    
    # 检查监控服务
    if [ "$MODE" = "monitoring" ] || [ "$MODE" = "full" ]; then
        if ! curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
            failed_services="${failed_services}Prometheus "
        fi
        
        if ! curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
            failed_services="${failed_services}Grafana "
        fi
    fi
    
    if [ -n "$failed_services" ]; then
        log_warning "以下服务可能存在问题: $failed_services"
        log_info "请检查日志: docker-compose logs -f"
    else
        log_success "所有服务健康检查通过！"
    fi
}

# 主函数
main() {
    # 检查是否在正确目录
    if [ ! -f "README.md" ] || [ ! -f "docker-compose.yml" ]; then
        log_error "请在项目根目录下运行此脚本"
        exit 1
    fi
    
    check_dependencies
    select_mode
    
    case $MODE in
        "basic")
            stop_services
            start_basic
            wait_for_services
            ;;
        "full")
            stop_services
            start_full
            wait_for_services
            ;;
        "monitoring")
            stop_services
            start_monitoring
            wait_for_services
            ;;
        "stop")
            stop_services
            exit 0
            ;;
    esac
    
    show_status
    health_check
    show_access_info
}

# 信号处理
trap 'echo -e "\n${YELLOW}启动过程被中断${NC}"; exit 1' INT TERM

# 运行主函数
main "$@" 