#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import json
import sys
from typing import List, Optional

from get_user_openid import FeishuUserIdGetter


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="根据手机号码和/或邮箱查询飞书用户ID")
    
    parser.add_argument("-m", "--mobile", action="append", 
                        help="要查询的手机号码，可以多次使用此参数查询多个手机号")
    
    parser.add_argument("-e", "--email", action="append", 
                        help="要查询的邮箱地址，可以多次使用此参数查询多个邮箱")
    
    parser.add_argument("--app-id", 
                        help="飞书应用的App ID，也可通过FEISHU_APP_ID环境变量设置")
    
    parser.add_argument("--app-secret", 
                        help="飞书应用的App Secret，也可通过FEISHU_APP_SECRET环境变量设置")
    
    parser.add_argument("-o", "--output", choices=["json", "table"], default="table",
                        help="输出格式：json或table (默认: table)")
    
    return parser.parse_args()


def print_table(data):
    """以表格形式打印结果"""
    if not data.get("success"):
        print(f"错误: {data.get('error')}")
        return
    
    result_data = data.get("data", {})
    user_list = result_data.get("user_list", [])
    
    if not user_list:
        print("没有找到匹配的用户")
        return
    
    print("\n查询结果:\n" + "-" * 80)
    print(f"{'用户ID':<40} | {'类型':<10} | {'值':<30}")
    print("-" * 80)
    
    for user in user_list:
        user_id = user.get("user_id", "N/A")
        
        if "mobile" in user:
            print(f"{user_id:<40} | {'手机号':<10} | {user.get('mobile', 'N/A'):<30}")
        
        if "email" in user:
            print(f"{user_id:<40} | {'邮箱':<10} | {user.get('email', 'N/A'):<30}")
    
    print("-" * 80)
    
    errors = result_data.get("errors", [])
    if errors:
        print("\n查询错误:")
        for error in errors:
            error_type = "手机号" if "mobile" in error else "邮箱"
            value = error.get("mobile", error.get("email", "N/A"))
            reason = error.get("msg", "未知错误")
            print(f"{error_type}: {value} - {reason}")


def main():
    """主函数"""
    args = parse_args()
    
    # 获取应用凭证
    app_id = args.app_id or os.environ.get("FEISHU_APP_ID")
    app_secret = args.app_secret or os.environ.get("FEISHU_APP_SECRET")
    
    if not app_id or not app_secret:
        print("错误: 请提供App ID和App Secret")
        print("可通过--app-id和--app-secret参数或FEISHU_APP_ID和FEISHU_APP_SECRET环境变量设置")
        return 1
    
    # 检查是否提供了手机号或邮箱
    mobiles = args.mobile
    emails = args.email
    
    if not mobiles and not emails:
        print("错误: 请至少提供一个手机号(--mobile)或邮箱(--email)")
        return 1
    
    try:
        # 初始化工具
        user_getter = FeishuUserIdGetter(app_id, app_secret)
        
        # 查询用户ID
        result = user_getter.get_user_ids_by_mobile_and_email(
            mobiles=mobiles, 
            emails=emails
        )
        
        # 输出结果
        if args.output == "json":
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print_table(result)
        
        # 检查是否成功
        return 0 if result.get("success") else 1
    
    except Exception as e:
        print(f"发生错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 