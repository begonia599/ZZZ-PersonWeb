# 使用官方的 Node.js LTS Alpine 基础镜像
FROM node:lts-alpine

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 package-lock.json (或 yarn.lock)
COPY package*.json ./

# **关键修改：设置 npm 镜像源**
RUN npm config set registry https://registry.npmmirror.com/

# 安装前端依赖
RUN npm install

# 复制前端应用的其余代码
COPY . .

# 构建 Vue 应用 (在开发模式下，通常不需要在 Dockerfile 中构建，因为会挂载本地代码)
# 但为了确保生产部署的 Dockerfile 完整性，我们暂时保留
# RUN npm run build

# 暴露前端服务端口
EXPOSE 5173

# 定义容器启动时运行的命令
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

