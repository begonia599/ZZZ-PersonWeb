from flask import Flask, jsonify
from flask_cors import CORS

# 创建 Flask 应用实例
app = Flask(__name__)
# 启用 CORS，允许所有来源的请求
CORS(app)

# 定义一个路由，当访问 /api/hello 时触发
@app.route('/api/hello', methods=['GET'])
def hello_world():
    # 返回一个 JSON 响应
    return jsonify({"message": "Hello, World!"})

# 如果直接运行此文件，启动服务器
if __name__ == '__main__':
    # debug=True 会在代码更改时自动重启服务器
    # port=5000 是后端服务器的端口号
    app.run(debug=True, port=5000)