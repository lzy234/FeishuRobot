https://open.feishu.cn/open-apis/bot/v2/hook/465dfe1a-7f80-48df-aa7f-300d77583d8a
这是我的飞书宿舍群中自定义机器人的webhook地址

我要实现一个功能，通过机器人在宿舍群里发消息@来提醒当天卫生值日的人。
由于自定义机器人无法获取任何群成员的信息，我会把排班表以json的格式给你，你需要的是帮我写一个程序能够每天早上9点发消息提醒

## 实现步骤

### 1. 环境准备
- Python 3.8+
- 必要的Python库：
  - requests：用于发送HTTP请求到飞书API
  - schedule：用于实现定时任务
  - json：处理JSON数据
  - datetime：处理日期和时间

### 2. 数据格式设计
排班表JSON格式建议如下（仅包含成员ID的简单列表）：
```json
{
  "duty_members": [
    {
      "name": "张三",
      "open_id": "ou_xxxxxxxxxxxxxxxx"
    },
    {
      "name": "李四", 
      "open_id": "ou_yyyyyyyyyyyyyyyy"
    },
    {
      "name": "王五",
      "open_id": "ou_zzzzzzzzzzzzzzzz"
    }
    // 更多成员...
  ],
  "last_index": 0,  // 上次提醒到的成员索引，用于记录轮转状态
  "last_date": "2025-09-30"  // 上次提醒的日期
}
```

### 3. 程序架构
程序主要包含以下几个部分：
1. 配置管理：读取webhook地址和排班表
2. 轮转逻辑：实现按顺序轮流提醒的机制
3. 消息发送：构建消息格式，调用飞书API
4. 定时任务：设置每天早上9点定时执行

### 4. 飞书API调用
- 使用飞书自定义机器人API发送消息
- 消息格式支持@特定人员
- 错误处理与重试机制

### 5. 代码实现示例
```python
import requests
import json
import schedule
import time
from datetime import datetime

# 配置
WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/465dfe1a-7f80-48df-aa7f-300d77583d8a"
SCHEDULE_FILE = "schedule.json"

def load_schedule():
    """加载排班表"""
    try:
        with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # 如果文件不存在，创建初始排班表
        print("排班表文件不存在，将创建初始文件")
        initial_schedule = {
            "duty_members": [],  # 需手动添加成员信息
            "last_index": -1,
            "last_date": ""
        }
        save_schedule(initial_schedule)
        return initial_schedule
    except Exception as e:
        print(f"加载排班表失败: {e}")
        return None

def save_schedule(schedule_data):
    """保存排班表"""
    try:
        with open(SCHEDULE_FILE, 'w', encoding='utf-8') as f:
            json.dump(schedule_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存排班表失败: {e}")
        return False

def get_next_duty_member(schedule_data):
    """获取下一个值日人员（轮流机制）"""
    members = schedule_data.get("duty_members", [])
    if not members:
        print("排班表中没有成员")
        return None
    
    # 获取上次索引，默认为-1
    last_index = schedule_data.get("last_index", -1)
    
    # 计算下一个索引（循环）
    next_index = (last_index + 1) % len(members)
    member = members[next_index]
    
    # 更新排班表状态
    schedule_data["last_index"] = next_index
    schedule_data["last_date"] = datetime.now().strftime("%Y-%m-%d")
    save_schedule(schedule_data)
    
    return member

def send_message(member):
    """发送飞书消息"""
    if not member:
        print("没有值日人员信息")
        return
    
    # 构建消息内容
    content = f"今日卫生值日提醒：{member['name']}，请记得完成卫生清扫工作！"
    
    # 构建消息格式（使用@功能）
    message = {
        "msg_type": "interactive",
        "card": {
            "config": {
                "wide_screen_mode": True
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "content": content,
                        "tag": "plain_text"
                    }
                },
                {
                    "tag": "div",
                    "text": {
                        "content": f"<at id={member['open_id']}></at>",
                        "tag": "lark_md"
                    }
                }
            ]
        }
    }
    
    # 发送请求
    try:
        response = requests.post(WEBHOOK_URL, json=message)
        if response.status_code == 200:
            print(f"消息发送成功: {content}")
        else:
            print(f"消息发送失败: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"发送消息时出错: {e}")

def daily_reminder():
    """每日提醒任务"""
    print(f"执行每日提醒任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    schedule_data = load_schedule()
    if schedule_data:
        member = get_next_duty_member(schedule_data)
        if member:
            send_message(member)

def main():
    """主函数"""
    print("启动卫生值日提醒程序...")
    
    # 设置每天早上9点执行
    schedule.every().day.at("09:00").do(daily_reminder)
    
    # 首次启动时立即执行一次（可选）
    # daily_reminder()
    
    # 持续运行
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次

if __name__ == "__main__":
    main()
```

### 6. Linux服务器部署步骤
1. **上传代码到服务器**：
   ```bash
   # 本地操作：将代码打包并上传到服务器
   scp -r feishu_robot/ user@your-server-ip:/path/to/deploy/
   ```

2. **安装依赖**：
   ```bash
   # 服务器上操作
   cd /path/to/deploy/feishu_robot/
   pip3 install requests schedule
   ```

3. **创建排班表**：
   ```bash
   # 创建一个初始的排班表JSON文件
   cat > schedule.json << EOF
   {
     "duty_members": [
       {"name": "成员1", "open_id": "ou_xxxxxxxx"},
       {"name": "成员2", "open_id": "ou_yyyyyyyy"},
       {"name": "成员3", "open_id": "ou_zzzzzzzz"}
     ],
     "last_index": -1,
     "last_date": ""
   }
   EOF
   ```

4. **使用systemd创建服务**：
   ```bash
   # 创建服务文件
   sudo nano /etc/systemd/system/feishu_duty.service
   ```
   
   文件内容：
   ```
   [Unit]
   Description=Feishu Duty Reminder
   After=network.target

   [Service]
   User=your-username
   WorkingDirectory=/path/to/deploy/feishu_robot/
   ExecStart=/usr/bin/python3 /path/to/deploy/feishu_robot/main.py
   Restart=always
   RestartSec=5
   StandardOutput=journal
   StandardError=journal

   [Install]
   WantedBy=multi-user.target
   ```

5. **启动并设置开机自启**：
   ```bash
   # 重新加载systemd配置
   sudo systemctl daemon-reload
   
   # 启动服务
   sudo systemctl start feishu_duty
   
   # 设置开机自启
   sudo systemctl enable feishu_duty
   
   # 检查服务状态
   sudo systemctl status feishu_duty
   ```

6. **查看日志**：
   ```bash
   # 查看服务日志
   sudo journalctl -u feishu_duty -f
   ```

### 7. 维护说明
1. **更新排班表**：
   - 直接编辑服务器上的`schedule.json`文件
   - 注意保持正确的JSON格式

2. **监控与维护**：
   - 定期检查服务状态：`sudo systemctl status feishu_duty`
   - 检查日志确保正常运行：`sudo journalctl -u feishu_duty --since="24 hours ago"`
   - 如遇问题可重启服务：`sudo systemctl restart feishu_duty`

3. **服务器维护**：
   - 确保服务器时间同步准确，避免定时任务错误
   - 监控服务器资源使用情况，确保稳定运行

### 8. 后续优化方向
1. 添加简单的Web界面，方便管理排班表
2. 增加临时跳过功能
3. 支持多群组管理
4. 添加备份与恢复机制
5. 提供值日完成确认功能