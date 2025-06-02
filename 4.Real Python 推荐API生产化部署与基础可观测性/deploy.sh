#!/bin/bash

# Real Python 推荐系统生产环境部署脚本
# 用于在云服务器上快速部署整个应用

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 检查是否为 root 用户
check_root() {
    if [ "$EUID" -eq 0 ]; then
        log_error "请不要以 root 用户运行此脚本"
        exit 1
    fi
}

# 检查操作系统
check_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_info "检测到 Linux 系统"
        if command -v apt-get &> /dev/null; then
            OS="ubuntu"
        elif command -v yum &> /dev/null; then
            OS="centos"
        else
            log_error "不支持的 Linux 发行版"
            exit 1
        fi
    else
        log_error "此脚本仅支持 Linux 系统"
        exit 1
    fi
}

# 安装 Docker
install_docker() {
    log_info "检查 Docker 安装状态..."
    
    if command -v docker &> /dev/null; then
        log_success "Docker 已安装"
        return 0
    fi
    
    log_info "安装 Docker..."
    
    if [ "$OS" == "ubuntu" ]; then
        # Ubuntu/Debian
        sudo apt-get update
        sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    elif [ "$OS" == "centos" ]; then
        # CentOS/RHEL
        sudo yum install -y yum-utils
        sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
        sudo yum install -y docker-ce docker-ce-cli containerd.io
    fi
    
    # 启动 Docker 服务
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # 将当前用户添加到 docker 组
    sudo usermod -aG docker $USER
    
    log_success "Docker 安装完成"
    log_warning "请重新登录以使 docker 组权限生效"
}

# 安装 Docker Compose
install_docker_compose() {
    log_info "检查 Docker Compose 安装状态..."
    
    if command -v docker-compose &> /dev/null; then
        log_success "Docker Compose 已安装"
        return 0
    fi
    
    log_info "安装 Docker Compose..."
    
    # 获取最新版本号
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    
    # 下载并安装
    sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    log_success "Docker Compose 安装完成"
}

# 安装 Nginx
install_nginx() {
    log_info "检查 Nginx 安装状态..."
    
    if command -v nginx &> /dev/null; then
        log_success "Nginx 已安装"
        return 0
    fi
    
    log_info "安装 Nginx..."
    
    if [ "$OS" == "ubuntu" ]; then
        sudo apt-get update
        sudo apt-get install -y nginx
    elif [ "$OS" == "centos" ]; then
        sudo yum install -y nginx
    fi
    
    # 启动 Nginx 服务
    sudo systemctl start nginx
    sudo systemctl enable nginx
    
    log_success "Nginx 安装完成"
}

# 配置防火墙
configure_firewall() {
    log_info "配置防火墙..."
    
    if command -v ufw &> /dev/null; then
        # Ubuntu UFW
        sudo ufw allow ssh
        sudo ufw allow 80/tcp
        sudo ufw allow 443/tcp
        sudo ufw allow 8000/tcp
        sudo ufw allow 8501/tcp
        sudo ufw --force enable
    elif command -v firewall-cmd &> /dev/null; then
        # CentOS/RHEL firewalld
        sudo firewall-cmd --permanent --add-service=ssh
        sudo firewall-cmd --permanent --add-service=http
        sudo firewall-cmd --permanent --add-service=https
        sudo firewall-cmd --permanent --add-port=8000/tcp
        sudo firewall-cmd --permanent --add-port=8501/tcp
        sudo firewall-cmd --reload
    fi
    
    log_success "防火墙配置完成"
}

# 部署应用
deploy_application() {
    log_info "部署应用..."
    
    # 构建并启动服务
    docker-compose build --no-cache
    docker-compose --profile production up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 检查服务状态
    docker-compose ps
    
    # 测试健康检查
    log_info "测试服务健康状态..."
    
    # 测试 API
    if curl -f http://localhost:8000/health; then
        log_success "API 服务正常"
    else
        log_error "API 服务异常"
    fi
    
    # 测试前端
    if curl -f http://localhost:8501/_stcore/health; then
        log_success "前端服务正常"
    else
        log_error "前端服务异常"
    fi
    
    log_success "应用部署完成"
}

# 配置 SSL/HTTPS (可选)
setup_https() {
    read -p "是否配置 HTTPS? (y/n): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        return 0
    fi
    
    read -p "请输入您的域名: " domain
    
    if [ -z "$domain" ]; then
        log_error "域名不能为空"
        return 1
    fi
    
    log_info "安装 Certbot..."
    
    if [ "$OS" == "ubuntu" ]; then
        sudo apt-get install -y snapd
        sudo snap install core; sudo snap refresh core
        sudo snap install --classic certbot
        sudo ln -sf /snap/bin/certbot /usr/bin/certbot
    elif [ "$OS" == "centos" ]; then
        sudo yum install -y epel-release
        sudo yum install -y certbot python3-certbot-nginx
    fi
    
    log_info "获取 SSL 证书..."
    sudo certbot --nginx -d $domain
    
    # 设置自动续期
    echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
    
    log_success "HTTPS 配置完成"
}

# 显示部署信息
show_deployment_info() {
    log_success "========================================="
    log_success "🎉 部署完成！"
    log_success "========================================="
    echo
    log_info "访问地址："
    echo "  📊 前端应用: http://$(curl -s ifconfig.me)"
    echo "  🔌 API 文档: http://$(curl -s ifconfig.me)/docs"
    echo "  ❤️  健康检查: http://$(curl -s ifconfig.me)/health"
    echo
    log_info "常用命令："
    echo "  查看服务状态: docker-compose ps"
    echo "  查看日志:     docker-compose logs -f"
    echo "  停止服务:     docker-compose down"
    echo "  重启服务:     docker-compose restart"
    echo
    log_info "配置文件位置："
    echo "  Nginx:       /etc/nginx/sites-available/default"
    echo "  Docker:      ./docker-compose.yml"
    echo "  应用日志:    docker-compose logs"
}

# 主函数
main() {
    log_info "开始部署 Real Python 推荐系统..."
    
    check_root
    check_os
    install_docker
    install_docker_compose
    install_nginx
    configure_firewall
    deploy_application
    setup_https
    show_deployment_info
    
    log_success "部署脚本执行完成！"
}

# 处理 Ctrl+C
trap 'log_error "部署中断"; exit 1' INT

# 如果直接运行此脚本，则执行主函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi 