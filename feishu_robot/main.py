#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import schedule
import time
import logging
from datetime import datetime
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("feishu_duty.log", encoding='utf-8')
    ]
)
logger = logging.getLogger("feishu_duty")

# 配置
WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/465dfe1a-7f80-48df-aa7f-300d77583d8a"
SCHEDULE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schedule.json")

def load_schedule():
    """加载排班表"""
    try:
        with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # 如果文件不存在，创建初始排班表
        logger.warning("排班表文件不存在，将创建初始文件")
        initial_schedule = {
            "duty_members": [],  # 需手动添加成员信息
            "last_index": -1,
            "last_date": ""
        }
        save_schedule(initial_schedule)
        return initial_schedule
    except Exception as e:
        logger.error(f"加载排班表失败: {e}")
        return None

def save_schedule(schedule_data):
    """保存排班表"""
    try:
        with open(SCHEDULE_FILE, 'w', encoding='utf-8') as f:
            json.dump(schedule_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"保存排班表失败: {e}")
        return False

def get_next_duty_member(schedule_data):
    """获取下一个值日人员（轮流机制）"""
    members = schedule_data.get("duty_members", [])
    if not members:
        logger.warning("排班表中没有成员")
        return None
    
    # 获取上次索引，默认为-1
    last_index = schedule_data.get("last_index", -1)
    
    # 计算下一个索引（循环）
    next_index = (last_index + 1) % len(members)
    member = members[next_index]
    
    logger.info(f"今日值日人员: {member['name']}, 索引: {next_index}")
    
    # 更新排班表状态
    schedule_data["last_index"] = next_index
    schedule_data["last_date"] = datetime.now().strftime("%Y-%m-%d")
    save_schedule(schedule_data)
    
    return member

def send_message(member):
    """发送飞书消息"""
    if not member:
        logger.warning("没有值日人员信息")
        return False
    
    # 构建消息内容
    content = f"今日卫生值日提醒：{member['name']}，请记得完成卫生清扫工作！"
    
    # 构建消息格式（使用@功能）
    message = {
        "msg_type": "text",
        "content": {
            "text": "今日卫生值日提醒："+"<at user_id = \""+ member['open_id'] +"\">"+ member['name'] +"</at> 请记得完成卫生清扫工作！"
        }
    }
    
    # 发送请求
    try:
        response = requests.post(WEBHOOK_URL, json=message)
        if response.status_code == 200:
            resp_data = response.json()
            if resp_data.get("code") == 0:
                logger.info(f"消息发送成功: {content}")
                return True
            else:
                logger.error(f"API返回错误: {resp_data}")
                return False
        else:
            logger.error(f"消息发送失败: HTTP {response.status_code}, {response.text}")
            return False
    except Exception as e:
        logger.error(f"发送消息时出错: {e}")
        return False

def daily_reminder():
    """每日提醒任务"""
    logger.info(f"执行每日提醒任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    schedule_data = load_schedule()
    if schedule_data:
        member = get_next_duty_member(schedule_data)
        if member:
            if send_message(member):
                logger.info("今日提醒发送完成")
            else:
                logger.error("今日提醒发送失败")
        else:
            logger.error("无法获取值日人员")
    else:
        logger.error("无法加载排班表")

def main():
    """主函数"""
    logger.info("启动卫生值日提醒程序...")
    
    # 检查排班表是否存在
    schedule_data = load_schedule()
    if not schedule_data:
        logger.error("无法加载排班表，程序退出")
        return
    
    if not schedule_data.get("duty_members"):
        logger.warning("排班表中没有成员信息，请先添加成员")
    
    # 设置每天早上9点执行
    schedule.every().day.at("09:00").do(daily_reminder)
    logger.info("已设置每天早上9点发送提醒")
    
    # 持续运行
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error(f"程序运行错误: {e}")

if __name__ == "__main__":
    main() 