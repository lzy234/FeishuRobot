# 飞书值日提醒机器人 - Windows部署指南

这是一个在Windows环境下运行飞书值日提醒机器人的指南。该机器人可以在Windows系统上定时发送消息，提醒宿舍群中的值日人员。

## 测试结果说明

1. 在测试过程中发现，使用`@`功能时出现了错误：
   - 错误消息：`there is an invalid user resource (at/person) in your card`
   - 原因：飞书机器人需要真实有效的飞书用户ID才能使用@功能

2. 解决方案：
   - 使用纯文本消息，而不使用@功能
   - 或者获取真实的飞书用户ID替换示例中的ID

## Windows环境配置

### 1. 安装Python环境

1. 下载并安装Python 3.8+：https://www.python.org/downloads/windows/
2. 安装依赖包：
   ```
   pip install requests schedule
   ```

### 2. 修改配置文件

1. 编辑`schedule.json`文件，填入正确的成员信息：
   ```json
   {
     "duty_members": [
       {
         "name": "实际成员名1",
         "open_id": "用户真实ID（可选）"
       },
       {
         "name": "实际成员名2",
         "open_id": "用户真实ID（可选）"
       }
     ],
     "last_index": -1,
     "last_date": ""
   }
   ```

### 3. 测试机器人

1. 运行测试脚本：
   ```
   python test_windows_text.py
   ```
   
2. 如果测试成功，将显示"消息发送成功"的提示

## 设置Windows定时任务

### 方法一：使用Windows任务计划程序

1. 打开"任务计划程序"（可在开始菜单中搜索"Task Scheduler"）
2. 点击右侧的"创建基本任务"
3. 输入任务名称，如"飞书值日提醒"
4. 选择"每天"触发
5. 设置开始时间为早上9:00
6. 选择"启动程序"
7. 浏览并选择刚创建的`windows_task.bat`批处理文件
8. 完成设置

### 方法二：使用批处理文件和计划任务

1. 编辑`windows_task.bat`中的Python路径（如果需要）
2. 使用以下命令创建计划任务：

```cmd
schtasks /create /tn "飞书值日提醒" /tr "D:\路径\到\feishu_robot\windows_task.bat" /sc daily /st 09:00:00
```

## 检查和维护

1. 查看任务运行情况：
   ```
   schtasks /query /tn "飞书值日提醒"
   ```

2. 手动运行任务：
   ```
   schtasks /run /tn "飞书值日提醒"
   ```

3. 删除任务：
   ```
   schtasks /delete /tn "飞书值日提醒"
   ```

## 排障指南

1. **脚本无法运行**
   - 检查Python路径是否正确
   - 检查是否以管理员权限运行批处理文件

2. **定时任务未执行**
   - 查看Windows事件查看器中的日志
   - 确保计算机在预定时间处于开机状态
   - 尝试以管理员身份创建任务

3. **消息发送失败**
   - 检查网络连接
   - 验证webhook地址是否正确
   - 确认机器人是否仍在群中

## 注意事项

1. Windows系统需要保持开机状态才能在预定时间执行定时任务
2. 如需使用@功能，必须获取真实的飞书用户ID
3. 机器人webhook地址具有时效性，过期后需要重新生成 