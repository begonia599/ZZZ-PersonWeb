# 时区统一更新总结

## 更新时间：2025-10-25

## 问题描述
打卡工具的日期显示正确，但时间始终显示为 8:00，原因是服务器使用的是 UTC 时间或数据库服务器时间，而不是北京时间（UTC+8）。

## 解决方案
将所有后端代码中的时间处理统一改为使用北京时间（UTC+8）。

## 更新的文件列表

### 1. 数据库模型文件（Models）
以下所有模型文件都已更新为使用北京时间：

- **backend/models/checkin.py**
  - `CheckinTask` 模型的 `created_at` 和 `updated_at` 字段
  - `CheckinRecord` 模型的 `created_at` 字段

- **backend/models/blog.py**
  - `Post` 模型的 `created_at` 和 `updated_at` 字段

- **backend/models/travel_photo.py**
  - `TravelPhoto` 模型的 `created_at` 和 `updated_at` 字段

- **backend/models/metrics.py**
  - `WebsiteMetrics` 模型的 `startup_time` 和 `last_updated` 字段

- **backend/models/set_type.py**
  - `SetType` 模型的 `created_at` 字段

- **backend/models/stat_type.py**
  - `StatType` 模型的 `created_at` 字段

- **backend/models/drive_piece.py**
  - `DrivePiece` 模型的 `created_at` 和 `updated_at` 字段
  - `DrivePieceSubstat` 模型的 `created_at` 字段

- **backend/models/upgrade_record.py**
  - `UpgradeRecord` 模型的 `created_at` 和 `updated_at` 字段

### 2. 路由文件（Routes）

- **backend/checkin_app/routes.py**
  - 已使用北京时区函数 `get_beijing_date()` 进行日期处理

- **backend/metrics_app/routes.py**
  - 所有使用 `datetime.utcnow()` 的地方改为 `get_beijing_now()`
  - 包括访问统计、网站运行时间等功能

- **backend/drive_app/routes.py**
  - 统计数据的 `last_updated` 时间戳改为使用北京时间

### 3. 应用配置文件

- **backend/run.py**
  - `init-metrics` 命令中的时间初始化改为使用北京时间

- **backend/migrate_complete.py**
  - 备份文件名的时间戳改为使用北京时间

## 技术实现

在每个文件中都添加了以下代码来定义北京时区：

```python
from datetime import datetime, timedelta, timezone

# 北京时区（UTC+8）
BEIJING_TZ = timezone(timedelta(hours=8))

def get_beijing_now():
    """获取北京时间的当前时间"""
    return datetime.now(BEIJING_TZ)
```

## 变更前后对比

### 变更前
- 使用 `db.func.now()` - 获取数据库服务器时间
- 使用 `db.func.current_timestamp()` - 获取数据库当前时间戳
- 使用 `datetime.utcnow()` - 获取 UTC 时间
- 使用 `datetime.now()` - 获取系统本地时间（不带时区信息）

### 变更后
- 统一使用 `get_beijing_now()` 函数
- 该函数返回带有北京时区（UTC+8）信息的 datetime 对象

## 影响范围

### 现有数据
- **不会影响**已存在的数据库记录
- 已有的时间戳保持不变

### 新数据
- 所有**新创建**的记录将使用北京时间
- 所有**更新**的记录的 `updated_at` 字段将使用北京时间

## 测试建议

### 1. 测试打卡功能
```bash
# 创建一个新的打卡任务并执行打卡
# 检查打卡记录的创建时间是否显示正确的北京时间
```

### 2. 测试博客功能
```bash
# 创建或更新一篇博客文章
# 检查创建时间和更新时间是否为北京时间
```

### 3. 测试访问统计
```bash
# 访问网站首页，触发访问统计
# 检查 last_updated 时间是否为北京时间
```

### 4. 查看数据库
```bash
# 连接到 SQLite 数据库
sqlite3 instance/checkin.db
SELECT * FROM checkin_records ORDER BY created_at DESC LIMIT 1;
# 检查时间字段是否正确
```

## 注意事项

1. **数据库中的时间格式**
   - 时间在数据库中存储时会包含时区信息
   - ISO 格式示例：`2025-10-25T14:30:00+08:00`

2. **前端显示**
   - 前端接收到的时间字符串已包含时区信息
   - JavaScript 的 `Date` 对象会自动处理时区转换

3. **时区一致性**
   - 确保所有新记录都使用北京时间
   - 现有数据的时区可能不同，需要在显示时注意

4. **数据迁移**
   - 如果需要，可以创建迁移脚本将现有数据的时间转换为北京时区
   - 但通常不必要，因为新数据会自动使用正确的时区

## 部署步骤

1. **重启后端服务**
   ```bash
   cd /opt/ZZZ-PersonWeb/backend
   # 停止现有服务
   pkill -f "flask run" 或停止 gunicorn
   
   # 启动服务
   flask run 或使用 gunicorn
   ```

2. **验证更新**
   - 创建新的打卡记录
   - 检查时间显示是否正确

3. **监控日志**
   - 检查应用日志，确保没有时区相关的错误

## 回滚方案

如果发现问题需要回滚：

1. 使用 git 恢复到之前的版本
2. 或者手动将所有 `get_beijing_now` 替换回 `db.func.now()` 或 `datetime.utcnow`

## 完成状态

✅ 所有数据库模型已更新
✅ 所有路由文件已更新
✅ 所有工具脚本已更新
✅ 无 linter 错误
✅ 时区统一为北京时间（UTC+8）

---

**更新完成！现在服务器的所有时间都以北京时间为标准。**

