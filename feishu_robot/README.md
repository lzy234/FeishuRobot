# 飞书值日提醒机器人

这是一个简单的飞书机器人，用于每天早上9点自动提醒宿舍群中的值日人员。机器人会按照预设的排班表轮流@不同的成员，提醒他们完成卫生清扫工作。

## 功能特性

- 每天早上9点自动发送提醒
- 轮流提醒功能，按顺序@每个值日人员
- 自动记录上次提醒位置，即使重启也能保持轮转顺序
- 完整的日志记录功能

## 安装步骤

### 1. 准备环境

```bash
# 安装Python依赖
pip3 install requests schedule
```

### 2. 配置排班表

编辑`schedule.json`文件，添加群成员信息：

```json
{
  "duty_members": [
    {
      "name": "成员1",
      "open_id": "ou_xxxxxxxx"  // 需要替换为真实的open_id
    },
    {
      "name": "成员2", 
      "open_id": "ou_yyyyyyyy"
    }
    // 可以继续添加更多成员...
  ],
  "last_index": -1,
  "last_date": ""
}
```

> 注意：`open_id`是飞书用户的唯一标识，需要从飞书获取。

### 3. 配置Webhook

在`main.py`文件中确认webhook地址是否正确：

```python
WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/465dfe1a-7f80-48df-aa7f-300d77583d8a"
```

## 部署方法

### 本地测试运行

```bash
python3 main.py
```

### Linux服务器部署

1. 将程序文件上传到服务器
   
   ```bash
   # 本地操作：打包上传
   scp -r feishu_robot/ user@your-server-ip:/path/to/deploy/
   ```

2. 配置systemd服务
   
   ```bash
   # 复制服务文件
   sudo cp /path/to/deploy/feishu_robot/feishu_duty.service /etc/systemd/system/
   
   # 编辑服务文件，修改用户和路径
   sudo nano /etc/systemd/system/feishu_duty.service
   ```

3. 启动服务
   
   ```bash
   # 重新加载systemd配置
   sudo systemctl daemon-reload
   
   # 启动服务
   sudo systemctl start feishu_duty
   
   # 设置开机自启
   sudo systemctl enable feishu_duty
   ```

4. 检查服务状态
   
   ```bash
   sudo systemctl status feishu_duty
   ```

## 日志查看

日志文件保存在程序运行目录下的`feishu_duty.log`：

```bash
# 查看日志文件
cat feishu_duty.log

# 或者通过systemd查看日志
sudo journalctl -u feishu_duty -f
```

## 常见问题

1. **消息发送失败**
   - 检查webhook地址是否正确
   - 确认机器人是否已添加到目标群

2. **无法找到成员**
   - 检查open_id是否正确
   - 确认成员是否在群中

3. **程序不自动运行**
   - 检查systemd服务状态
   - 查看系统日志是否有错误信息

## 维护与更新

1. **更新排班表**

   直接编辑服务器上的`schedule.json`文件，添加或修改成员信息。

2. **重启服务**

   ```bash
   sudo systemctl restart feishu_duty
   ``` 