#!/bin/bash

# 多架构Docker构建脚本
# 支持 ARM64 (如Apple M1/M2, ARM服务器) 和 AMD64 (传统x86服务器)

set -e

echo "🚀 开始多架构Docker构建..."

# 检查Docker buildx是否可用
if ! docker buildx version > /dev/null 2>&1; then
    echo "❌ Docker buildx不可用，请升级Docker到最新版本"
    exit 1
fi

# 创建多架构构建器（如果不存在）
BUILDER_NAME="personweb-builder"
if ! docker buildx ls | grep -q $BUILDER_NAME; then
    echo "📦 创建多架构构建器: $BUILDER_NAME"
    docker buildx create --name $BUILDER_NAME --driver docker-container --bootstrap
fi

# 使用多架构构建器
docker buildx use $BUILDER_NAME

echo "🏗️  构建前端镜像 (ARM64 + AMD64)..."
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    --tag personweb-frontend:latest \
    --file frontend/Dockerfile \
    --load \
    ./frontend

echo "🐍 构建后端镜像 (ARM64 + AMD64)..."
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    --tag personweb-backend:latest \
    --file backend/Dockerfile \
    --load \
    ./backend

echo "✅ 多架构构建完成！"
echo ""
echo "📋 可用镜像:"
docker images | grep personweb

echo ""
echo "🚀 启动服务:"
echo "  开发环境: docker-compose up -d"
echo "  生产环境: docker-compose -f docker-compose.prod.yml up -d"

echo ""
echo "🔍 架构信息:"
echo "  当前架构: $(uname -m)"
echo "  支持架构: linux/amd64, linux/arm64"
echo "  镜像源: 官方源（适合国外服务器）"
echo "  ARM优化: 延长超时时间，减少Worker数量"
