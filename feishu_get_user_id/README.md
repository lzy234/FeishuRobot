# 飞书用户ID获取工具

这个工具可以根据用户的手机号码和/或邮箱地址查询飞书用户的OpenID。

## 环境要求

- Python 3.7 或更高版本
- lark-oapi 包（飞书开放平台SDK）

## 安装依赖

```bash
pip install lark-oapi -U
```

## 使用前准备

使用前，您需要：

1. 在[飞书开发者后台](https://open.feishu.cn/app)创建一个企业自建应用
2. 获取应用的App ID和App Secret
3. 为应用添加以下权限：
   - 获取用户 ID（`contact:user.id:readonly`）

## 使用方法

### 设置环境变量

```bash
# Windows
set FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxx
set FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxx

# Linux/Mac
export FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxx
export FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxx
```

### 使用示例

```python
from get_user_openid import FeishuUserIdGetter

# 初始化工具
app_id = "cli_xxxxxxxxxxxxxxxx"  # 替换为您的App ID
app_secret = "xxxxxxxxxxxxxxxxxxxxxx"  # 替换为您的App Secret
user_getter = FeishuUserIdGetter(app_id, app_secret)

# 通过手机号查询
result = user_getter.get_user_ids_by_mobile_and_email(mobiles=["13800138000"])
print(result)

# 通过邮箱查询
result = user_getter.get_user_ids_by_mobile_and_email(emails=["example@example.com"])
print(result)

# 同时通过手机号和邮箱查询
result = user_getter.get_user_ids_by_mobile_and_email(
    mobiles=["13800138000"], 
    emails=["example@example.com"]
)
print(result)
```

### 直接运行脚本

设置好环境变量后，可以直接运行脚本进行测试：

```bash
python get_user_openid.py
```

### 使用命令行工具

我们还提供了一个方便的命令行工具：

```bash
# 通过手机号查询
python cli.py -m 13800138000

# 通过邮箱查询
python cli.py -e example@example.com

# 同时查询多个手机号和邮箱
python cli.py -m 13800138000 -m 13900139000 -e example@example.com -e test@example.com

# 指定输出格式为JSON
python cli.py -m 13800138000 -o json

# 直接指定App ID和App Secret（不推荐，建议使用环境变量）
python cli.py -m 13800138000 --app-id cli_xxx --app-secret xxx
```

## 返回结果示例

成功时：

```json
{
  "success": true,
  "data": {
    "user_list": [
      {
        "user_id": "ou_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "mobile": "13800138000"
      },
      {
        "user_id": "ou_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "email": "example@example.com"
      }
    ],
    "errors": []
  }
}
```

失败时：

```json
{
  "success": false,
  "error": "获取用户ID失败: 99901, auth failed"
}
``` 