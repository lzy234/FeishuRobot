#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from typing import List, Optional, Dict, Any
import json

from lark_oapi.api.contact.v3.resource.user import BatchGetIdUserRequest
from lark_oapi import Client

class FeishuUserIdGetter:
    """飞书用户ID获取工具"""
    
    def __init__(self, app_id: str, app_secret: str):
        """
        初始化飞书API客户端
        
        Args:
            app_id: 飞书应用的App ID
            app_secret: 飞书应用的App Secret
        """
        # 创建客户端
        self.client = Client.builder().app_id(app_id).app_secret(app_secret).build()
    
    def get_user_ids_by_mobile_and_email(self, 
                                         mobiles: List[str] = None, 
                                         emails: List[str] = None) -> Dict[str, Any]:
        """
        根据手机号和邮箱获取用户ID
        
        Args:
            mobiles: 手机号列表
            emails: 邮箱列表
            
        Returns:
            包含用户ID信息的字典
        """
        if not mobiles and not emails:
            raise ValueError("手机号和邮箱至少需要提供一项")
        
        # 创建请求
        request = BatchGetIdUserRequest.builder().build()
        request_body = {}
        
        # 添加手机号
        if mobiles:
            request_body["mobiles"] = mobiles
        
        # 添加邮箱
        if emails:
            request_body["emails"] = emails
        
        # 设置请求体
        request.body = request_body
        
        # 发送请求
        response = self.client.contact.v3.user.batch_get_id(request)
        
        # 处理响应
        if not response.success():
            error_msg = f"获取用户ID失败: {response.code}, {response.msg}"
            print(error_msg)
            return {"success": False, "error": error_msg}
        
        # 将响应对象转换为字典
        result_dict = {}
        if hasattr(response.data, "user_list"):
            user_list = []
            for user in response.data.user_list:
                user_dict = {}
                
                if hasattr(user, "user_id"):
                    user_dict["user_id"] = user.user_id
                
                if hasattr(user, "mobile"):
                    user_dict["mobile"] = user.mobile
                
                if hasattr(user, "email"):
                    user_dict["email"] = user.email
                
                user_list.append(user_dict)
            
            result_dict["user_list"] = user_list
        
        if hasattr(response.data, "errors"):
            errors_list = []
            for error in response.data.errors:
                error_dict = {}
                
                if hasattr(error, "msg"):
                    error_dict["msg"] = error.msg
                
                if hasattr(error, "mobile"):
                    error_dict["mobile"] = error.mobile
                
                if hasattr(error, "email"):
                    error_dict["email"] = error.email
                
                errors_list.append(error_dict)
            
            result_dict["errors"] = errors_list
        
        return {
            "success": True,
            "data": result_dict
        }


def main():
    """主函数示例"""
    # 从环境变量获取应用凭证
    app_id = os.environ.get("FEISHU_APP_ID")
    app_secret = os.environ.get("FEISHU_APP_SECRET")
    
    if not app_id or not app_secret:
        print("请设置环境变量 FEISHU_APP_ID 和 FEISHU_APP_SECRET")
        return
    
    # 创建工具实例
    user_getter = FeishuUserIdGetter(app_id, app_secret)
    
    # 示例：查询手机号对应的用户ID
    mobiles = ["13800138000"]
    result = user_getter.get_user_ids_by_mobile_and_email(mobiles=mobiles)
    
    # 打印结果
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 示例：查询邮箱对应的用户ID
    emails = ["example@example.com"]
    result = user_getter.get_user_ids_by_mobile_and_email(emails=emails)
    
    # 打印结果
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 示例：同时查询手机号和邮箱对应的用户ID
    result = user_getter.get_user_ids_by_mobile_and_email(mobiles=mobiles, emails=emails)
    
    # 打印结果
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main() 