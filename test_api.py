import requests
import json

# API 地址
url = "http://127.0.0.1:5000/api/drive/add"

# 成功的请求数据
success_payload = {
  "set_name": "空洞驰行",
  "position": 1,
  "main_stat_name": "暴击率",
  "substats": ["暴击伤害", "攻击力百分比", "生命值"]
}

# 失败的请求数据 (例如，缺少字段)
failure_payload = {
  "set_name": "空洞驰行",
  "position": 1
  # 缺少 main_stat_name
}

def test_success():
    print("--- 测试成功添加驱动盘 ---")
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(success_payload), headers=headers)

    print(f"状态码: {response.status_code}")
    print(f"响应体: {response.json()}")

def test_failure():
    print("\n--- 测试缺少字段的失败情况 ---")
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(failure_payload), headers=headers)

    print(f"状态码: {response.status_code}")
    print(f"响应体: {response.json()}")

if __name__ == "__main__":
    test_success()
    test_failure()