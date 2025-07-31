# 使用官方的 Python LTS Alpine 基础镜像
FROM python:3.11-alpine

# 设置工作目录
WORKDIR /app

# 打印一个触发器，确保每次构建都会执行这一步，而不是使用缓存
RUN echo "Rebuild trigger: $(date +%s)"

# 复制依赖文件
COPY requirements.txt ./

# 安装 Python 依赖
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --no-cache-dir -r requirements.txt --default-timeout=100

# **关键修改：移除复制 Firebase 服务账号密钥文件**
# COPY firebase-service-account.json ./

# 复制所有应用代码到容器
COPY . .

# 设置 FLASK_APP 指向 run.py
ENV FLASK_APP=run.py

# 暴露 Flask 应用的端口
EXPOSE 5000

# 定义容器启动时运行的命令
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:create_app()"]