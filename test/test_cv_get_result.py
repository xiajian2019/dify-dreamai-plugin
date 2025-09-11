#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文件：用于本地调试 CVGetResultTool 类

使用方法：
1. 确保已安装所需依赖：pip install -r requirements.txt
2. 设置环境变量或在代码中配置 VolcEngine 凭证
3. 运行测试：python test/test_cv_get_result.py
"""

import json
import os
import sys
from unittest.mock import Mock

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        """如果没有安装python-dotenv，提供一个空的实现"""
        pass

from http.client import HTTPConnection

# 启用 http.client 的调试
HTTPConnection.debuglevel = 1

# 可选：配置 logging 以获取更结构化的输出，否则调试信息会直接打印到 stderr
import logging
logging.basicConfig(level=logging.DEBUG)

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.cv_get_result import CVGetResultTool


class MockRuntime:
    """模拟运行时环境"""
    def __init__(self, access_key: str, secret_key: str):
        self.credentials = {
            'volcengine_access_key': access_key,
            'volcengine_secret_key': secret_key
        }
    
    def get(self, key: str):
        return self.credentials.get(key)


class MockSession:
    """模拟会话对象"""
    def __init__(self):
        self.user_id = "test_user"


def test_cv_get_result_specific_task():
    """测试指定的task_id和req_key"""
    print("\n测试指定任务结果查询...")
    
    # 从环境变量获取凭证
    access_key = os.getenv('VOLCENGINE_ACCESS_KEY')
    secret_key = os.getenv('VOLCENGINE_SECRET_KEY')
    
    if not access_key or not secret_key:
        print("警告：未找到 VolcEngine 凭证，使用模拟凭证")
        access_key = "test_access_key"
        secret_key = "test_secret_key"
    
    # 创建模拟对象
    mock_runtime = MockRuntime(access_key, secret_key)
    mock_session = MockSession()
    
    # 创建工具实例
    tool = CVGetResultTool(runtime=mock_runtime, session=mock_session)
    
    # 测试参数（使用指定的task_id和req_key）
    # test_params = {
    #     'task_id': '13611150795167972662',
    #     'req_key': 'jimeng_i2i_v30'
    # }
    
    # 测试参数（使用指定的task_id和req_key）
    test_params = {
        'task_id': '3035337728219037513',
        'req_key': 'jimeng_t2v_v30'
    }
    
    print(f"测试参数: {test_params}")
    
    # 执行工具
    try:
        messages = list(tool._invoke(test_params))
        print(f"\n收到 {len(messages)} 条消息:")
        for i, msg in enumerate(messages):
            print(f"消息 {i+1}: {msg}")
    except Exception as e:
        print(f"执行失败: {e}")


def test_cv_get_result_with_req_json():
    """测试带req_json参数的任务结果查询"""
    print("\n测试带req_json参数的任务结果查询...")
    
    # 从环境变量获取凭证
    access_key = os.getenv('VOLCENGINE_ACCESS_KEY')
    secret_key = os.getenv('VOLCENGINE_SECRET_KEY')
    
    if not access_key or not secret_key:
        print("警告：未找到 VolcEngine 凭证，使用模拟凭证")
        access_key = "test_access_key"
        secret_key = "test_secret_key"
    
    # 创建模拟对象
    mock_runtime = MockRuntime(access_key, secret_key)
    mock_session = MockSession()
    
    # 创建工具实例
    tool = CVGetResultTool(runtime=mock_runtime, session=mock_session)
    
    # 测试参数（包含req_json）
    req_json_data = {
        "return_url": True,
        "logo_info": {
            "add_logo": True,
            "position": 0,
            "language": 0,
            "opacity": 0.8,
            "logo_text_content": "AI Generated"
        }
    }
    
    test_params = {
        'task_id': '13611150795167972662',
        'req_key': 'jimeng_i2i_v30',
        'req_json': json.dumps(req_json_data)
    }
    
    print(f"测试参数: {test_params}")
    
    # 执行工具
    try:
        messages = list(tool._invoke(test_params))
        print(f"\n收到 {len(messages)} 条消息:")
        for i, msg in enumerate(messages):
            print(f"消息 {i+1}: {msg}")
    except Exception as e:
        print(f"执行失败: {e}")


def test_req_json_validation():
    """测试req_json参数验证"""
    print("\n测试req_json参数验证...")
    
    # 创建模拟对象
    mock_runtime = MockRuntime("test_key", "test_secret")
    mock_session = MockSession()
    
    # 创建工具实例
    tool = CVGetResultTool(runtime=mock_runtime, session=mock_session)
    
    # 测试无效的JSON格式
    test_params = {
        'task_id': '13611150795167972662',
        'req_key': 'jimeng_i2i_v30',
        'req_json': '{invalid json}'
    }
    
    print("测试无效JSON格式...")
    try:
        messages = list(tool._invoke(test_params))
        print(f"收到 {len(messages)} 条消息:")
        for i, msg in enumerate(messages):
            print(f"消息 {i+1}: {msg}")
    except Exception as e:
        print(f"执行失败: {e}")


def test_parameter_validation():
    """测试参数验证"""
    print("\n测试参数验证...")
    
    # 创建模拟对象（使用空凭证测试参数验证）
    mock_runtime = MockRuntime("", "")
    mock_session = MockSession()
    
    # 创建工具实例
    tool = CVGetResultTool(runtime=mock_runtime, session=mock_session)
    
    # 测试用例
    test_cases = [
        ({}, "缺少所有必需参数"),
        ({'task_id': '123'}, "缺少req_key参数"),
        ({'req_key': 'test'}, "缺少task_id参数"),
    ]
    
    for params, description in test_cases:
        print(f"\n测试: {description}")
        print(f"参数: {params}")
        try:
            messages = list(tool._invoke(params))
            if messages:
                print(f"结果: {messages[0]}")
        except Exception as e:
            print(f"异常: {e}")


if __name__ == '__main__':
    print("CVGetResultTool 本地调试测试")
    print("=" * 50)
    
    # 先运行参数验证测试（不需要真实凭证）
    test_parameter_validation()
    
    # 运行req_json参数验证测试
    test_req_json_validation()
    
    print("\n" + "=" * 50)
    print("注意：以下测试需要真实的 VolcEngine 凭证")
    print("请设置环境变量或修改代码中的凭证配置")
    print("=" * 50)
    
    # 加载环境变量
    load_dotenv()
    access_key = os.getenv('VOLCENGINE_ACCESS_KEY')
    secret_key = os.getenv('VOLCENGINE_SECRET_KEY')
    print(f"从环境变量获取的 VOLCENGINE_ACCESS_KEY: {access_key}")
    print(f"从环境变量获取的 VOLCENGINE_SECRET_KEY: {secret_key}")
    
    if access_key and secret_key:
        print("检测到环境变量中的凭证，运行指定任务测试")
        test_cv_get_result_specific_task()
    else:
        print("未检测到环境变量 VOLCENGINE_ACCESS_KEY 和 VOLCENGINE_SECRET_KEY")
        print("如需运行完整测试，请设置这些环境变量或创建 .env 文件")
        print("取消注释以下行来运行实际API测试：")
        print("# test_cv_get_result_specific_task()")
    
    print("\n测试完成！")