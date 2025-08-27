#!/bin/bash

# 🚀 PersonWeb 一键部署脚本
# 适用于已部署旧版本的服务器更新

set -e

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

# 检查是否为root用户或有sudo权限
check_permissions() {
    if [[ $EUID -eq 0 ]]; then
        SUDO=""
        log_info "以root用户运行"
    elif sudo -n true 2>/dev/null; then
        SUDO="sudo"
        log_info "检测到sudo权限"
    else
        log_error "需要root权限或sudo权限来运行此脚本"
        exit 1
    fi
}

# 检查Docker和docker compose
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    # 检查新版本的 docker compose 或旧版本的 docker-compose
    if docker compose version &> /dev/null; then
        DOCKER_COMPOSE="docker compose"
        log_info "检测到新版本 docker compose"
    elif command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
        log_info "检测到旧版本 docker-compose"
    else
        log_error "docker compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    log_success "Docker环境检查通过"
}

# 检查Git
check_git() {
    if ! command -v git &> /dev/null; then
        log_error "Git未安装，请先安装Git"
        exit 1
    fi
    log_success "Git检查通过"
}

# 备份当前配置
backup_config() {
    log_info "备份当前配置文件..."
    
    # 备份站点配置
    if [ -f "site-config.json" ]; then
        cp site-config.json site-config.json.backup
        log_success "已备份 site-config.json"
    fi
    
    # 备份数据库（如果存在）
    if [ -d "backend/instance" ]; then
        cp -r backend/instance backend/instance.backup
        log_success "已备份数据库文件"
    fi
    
    # 备份上传文件（如果存在）
    if [ -d "backend/uploads" ]; then
        cp -r backend/uploads backend/uploads.backup
        log_success "已备份上传文件"
    fi
}

# 停止当前服务
stop_services() {
    log_info "停止当前运行的服务..."
    
    # 停止服务
    $DOCKER_COMPOSE down || true
    
    log_success "服务已停止"
}

# 更新代码
update_code() {
    log_info "更新代码..."
    
    # 检查当前分支
    CURRENT_BRANCH=$(git branch --show-current)
    log_info "当前分支: $CURRENT_BRANCH"
    
    # 拉取最新代码
    git fetch origin
    git pull origin $CURRENT_BRANCH
    
    log_success "代码更新完成"
}

# 恢复配置文件
restore_config() {
    log_info "恢复配置文件..."
    
    # 恢复站点配置
    if [ -f "site-config.json.backup" ]; then
        mv site-config.json.backup site-config.json
        log_success "已恢复 site-config.json"
    else
        # 如果没有备份，检查是否需要创建配置文件
        if [ ! -f "site-config.json" ] && [ -f "site-config.example.json" ]; then
            log_warning "未找到站点配置，使用示例配置"
            cp site-config.example.json site-config.json
        fi
    fi
    
    # 恢复数据库
    if [ -d "backend/instance.backup" ]; then
        rm -rf backend/instance
        mv backend/instance.backup backend/instance
        log_success "已恢复数据库文件"
    fi
    
    # 恢复上传文件
    if [ -d "backend/uploads.backup" ]; then
        rm -rf backend/uploads
        mv backend/uploads.backup backend/uploads
        log_success "已恢复上传文件"
    fi
}

# 清理Docker镜像
clean_docker() {
    log_info "清理旧的Docker镜像..."
    
    # 清理未使用的镜像
    docker image prune -f || true
    
    # 清理未使用的容器
    docker container prune -f || true
    
    log_success "Docker清理完成"
}

# 构建并启动服务
start_services() {
    log_info "构建并启动服务..."
    
    # 检测架构
    ARCH=$(uname -m)
    log_info "检测到架构: $ARCH"
    
    # 构建并启动
    $DOCKER_COMPOSE up --build -d
    
    log_success "服务启动完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 等待服务启动
    sleep 10
    
    # 检查容器状态
    if $DOCKER_COMPOSE ps | grep -q "Up"; then
        log_success "容器运行正常"
    else
        log_warning "部分容器可能未正常启动，请检查日志"
        $DOCKER_COMPOSE ps
    fi
    
    # 检查端口
    if netstat -tuln | grep -q ":5173 "; then
        log_success "前端服务 (端口5173) 运行正常"
    else
        log_warning "前端服务可能未正常启动"
    fi
    
    if netstat -tuln | grep -q ":5000 "; then
        log_success "后端服务 (端口5000) 运行正常"
    else
        log_warning "后端服务可能未正常启动"
    fi
}

# 显示部署信息
show_info() {
    echo ""
    echo "🎉 部署完成！"
    echo ""
    echo "📋 服务信息:"
    echo "  - 前端服务: http://$(hostname -I | awk '{print $1}'):5173"
    echo "  - 后端API: http://$(hostname -I | awk '{print $1}'):5000"
    echo "  - 架构: $(uname -m)"
    echo ""
    echo "🔧 管理命令:"
    echo "  - 查看日志: $DOCKER_COMPOSE logs -f"
    echo "  - 重启服务: $DOCKER_COMPOSE restart"
    echo "  - 停止服务: $DOCKER_COMPOSE down"
    echo ""
    echo "📁 配置文件:"
    echo "  - 站点配置: site-config.json"
    echo "  - 数据库: backend/instance/"
    echo "  - 上传文件: backend/uploads/"
    echo ""
}

# 主函数
main() {
    echo "🚀 PersonWeb 一键部署脚本启动"
    echo "适用于服务器代码更新和重新部署"
    echo ""
    
    # 检查环境
    check_permissions
    check_docker
    check_git
    
    # 备份配置
    backup_config
    
    # 停止服务
    stop_services
    
    # 更新代码
    update_code
    
    # 恢复配置
    restore_config
    
    # 清理Docker
    clean_docker
    
    # 启动服务
    start_services
    
    # 健康检查
    health_check
    
    # 显示信息
    show_info
    
    log_success "部署完成！🎉"
}

# 错误处理
trap 'log_error "部署过程中发生错误，请检查日志"; exit 1' ERR

# 执行主函数
main "$@"
