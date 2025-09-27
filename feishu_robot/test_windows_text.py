#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import requests
from datetime import datetime

# 配置
WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/465dfe1a-7f80-48df-aa7f-300d77583d8a"
SCHEDULE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schedule.json")

def load_schedule():
    """加载排班表"""
    try:
        with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
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
    
    print(f"本次值日人员: {member['name']}, 索引: {next_index}")
    
    # 更新排班表状态
    schedule_data["last_index"] = next_index
    schedule_data["last_date"] = datetime.now().strftime("%Y-%m-%d")
    save_schedule(schedule_data)
    
    return member

def send_text_message(member):
    """发送纯文本飞书消息（不使用@功能）"""
    if not member:
        print("没有值日人员信息")
        return False
    
    # 构建消息内容
    content = f"今日卫生值日提醒：@{member['name']}，请记得完成卫生清扫工作！"
    
    # 构建纯文本消息格式
    message = {
        "msg_type": "text",
        "content": {
            "text": "今日卫生值日提醒："+"<at user_id = \""+ member['open_id'] +"\">"+ member['name'] +"</at> 请记得完成卫生清扫工作！"
        }
    }
    
    # 输出消息内容用于测试
    print(f"准备发送纯文本消息: {content}")
    print(f"消息JSON: {json.dumps(message, ensure_ascii=False, indent=2)}")
    
    # 询问是否实际发送
    should_send = input("\n是否实际发送消息到飞书群? (y/n): ").lower() == 'y'
    
    if not should_send:
        print("已取消发送消息")
        return False
    
    # 发送请求
    try:
        print(f"正在发送消息到: {WEBHOOK_URL}")
        response = requests.post(WEBHOOK_URL, json=message)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            resp_data = response.json()
            if resp_data.get("code") == 0:
                print(f"消息发送成功: {content}")
                return True
            else:
                print(f"API返回错误: {resp_data}")
                return False
        else:
            print(f"消息发送失败: HTTP {response.status_code}, {response.text}")
            return False
    except Exception as e:
        print(f"发送消息时出错: {e}")
        return False

def main():
    """主函数"""
    print("飞书值日提醒机器人 Windows测试版（纯文本消息）")
    print("=" * 50)
    
    # 检查排班表是否存在
    schedule_data = load_schedule()
    if not schedule_data:
        print("无法加载排班表，程序退出")
        return
    
    # 显示当前成员列表
    members = schedule_data.get("duty_members", [])
    if not members:
        print("警告：排班表中没有成员信息，请先添加成员")
        return
    
    print("\n当前成员列表:")
    for i, member in enumerate(members):
        print(f"{i+1}. {member['name']} (ID: {member['open_id']})")
    
    print(f"\n上次提醒索引: {schedule_data.get('last_index', -1)}")
    print(f"上次提醒日期: {schedule_data.get('last_date', '无')}")
    
    # 获取并发送消息
    member = get_next_duty_member(schedule_data)
    if member:
        send_text_message(member)
    else:
        print("无法获取值日人员")

if __name__ == "__main__":
    main()
    input("\n按Enter键退出...") 