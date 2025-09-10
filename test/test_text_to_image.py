#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文件：用于本地调试 TextToImageTool 类

使用方法：
1. 确保已安装所需依赖：pip install -r requirements.txt
2. 设置环境变量或在代码中配置 VolcEngine 凭证
3. 运行测试：python test/test_text_to_image.py
"""

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

from tools.text_to_image import TextToImageTool


class MockRuntime:
    """模拟 runtime 对象"""
    def __init__(self, access_key: str, secret_key: str):
        self.credentials = {
            'volcengine_access_key': access_key,
            'volcengine_secret_key': secret_key
        }
    
    def get(self, key: str):
        return self.credentials.get(key)


class MockSession:
    """模拟 session 对象"""
    def __init__(self):
        pass


def test_text_to_image_basic():
    """基础文生图测试"""
    print("=== 基础文生图测试 ===")
    
    # 配置凭证（请替换为实际的凭证）
    access_key = os.getenv('VOLCENGINE_ACCESS_KEY', 'your_access_key_here')
    secret_key = os.getenv('VOLCENGINE_SECRET_KEY', 'your_secret_key_here')
    
    if access_key == 'your_access_key_here' or secret_key == 'your_secret_key_here':
        print("请设置环境变量 VOLCENGINE_ACCESS_KEY 和 VOLCENGINE_SECRET_KEY")
        print("或者直接在代码中修改 access_key 和 secret_key 的值")
        return
    
    # 创建工具实例
    mock_runtime = MockRuntime(access_key, secret_key)
    mock_session = MockSession()
    tool = TextToImageTool(runtime=mock_runtime, session=mock_session)
    
    # 测试参数
    test_params = {
        'prompt': '一只可爱的小猫咪，坐在花园里，阳光明媚',
        'model_version': '3.1',
        'width': 1024,
        'height': 1024,
        'seed': 42,
        'use_pre_llm': True,
        'use_sr': True,
        'return_url': True
    }
    
    print(f"测试参数: {test_params}")
    print("开始调用工具...")
    
    try:
        # 调用工具
        messages = list(tool._invoke(test_params))
        
        print(f"\n收到 {len(messages)} 条消息:")
        for i, message in enumerate(messages, 1):
            print(f"消息 {i}: {message.type} - {message.message if hasattr(message, 'message') else 'N/A'}")
            
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


def test_text_to_image_with_watermark():
    """带水印的文生图测试"""
    print("\n=== 带水印文生图测试 ===")
    
    # 配置凭证
    access_key = os.getenv('VOLCENGINE_ACCESS_KEY', 'your_access_key_here')
    secret_key = os.getenv('VOLCENGINE_SECRET_KEY', 'your_secret_key_here')
    
    if access_key == 'your_access_key_here' or secret_key == 'your_secret_key_here':
        print("请设置环境变量 VOLCENGINE_ACCESS_KEY 和 VOLCENGINE_SECRET_KEY")
        return
    
    # 创建工具实例
    mock_runtime = MockRuntime(access_key, secret_key)
    mock_session = MockSession()
    tool = TextToImageTool(runtime=mock_runtime, session=mock_session)
    
    # 测试参数（包含水印）
    test_params = {
        'prompt': '美丽的山水风景画，中国风格',
        'model_version': '3.0',
        'width': 512,
        'height': 512,
        'add_logo': True,
        'position': 1,  # 右下角
        'language': 0,  # 中文
        'opacity': 0.8,
        'logo_text_content': 'AI',
        'use_pre_llm': False,
        'use_sr': False,
        'return_url': True,  # 返回base64数据
    }
    
    print(f"测试参数: {test_params}")
    print("开始调用工具...")
    
    try:
        # 调用工具
        messages = list(tool._invoke(test_params))
        
        print(f"\n收到 {len(messages)} 条消息:")
        for i, message in enumerate(messages, 1):
            print(f"消息 {i}: {message.type} - {message.message if hasattr(message, 'message') else 'N/A'}")
            
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


def test_parameter_validation():
    """参数验证测试"""
    print("\n=== 参数验证测试 ===")
    
    # 创建工具实例（无凭证）
    mock_runtime = MockRuntime('', '')  # 空凭证
    mock_session = MockSession()
    tool = TextToImageTool(runtime=mock_runtime, session=mock_session)
    
    # 测试缺少凭证
    print("测试1: 缺少凭证")
    try:
        messages = list(tool._invoke({'prompt': '测试'}))
        print(f"结果: {messages[0].message if messages else 'No messages'}")
    except Exception as e:
        print(f"异常: {str(e)}")
    
    # 测试缺少prompt
    print("\n测试2: 缺少prompt")
    mock_runtime = MockRuntime('test_key', 'test_secret')
    mock_session = MockSession()
    tool = TextToImageTool(runtime=mock_runtime, session=mock_session)
    try:
        messages = list(tool._invoke({}))
        print(f"结果: {messages[0].message if messages else 'No messages'}")
    except Exception as e:
        print(f"异常: {str(e)}")


if __name__ == '__main__':
    print("TextToImageTool 本地调试测试")
    print("=" * 50)
    
    # 运行参数验证测试（不需要真实凭证）
    test_parameter_validation()
    
    # 运行实际API测试（需要真实凭证）
    print("\n" + "=" * 50)
    print("注意：以下测试需要真实的 VolcEngine 凭证")
    print("请设置环境变量或修改代码中的凭证配置")
    print("=" * 50)

    # 从 .env 文件中获取凭证（如果存在）
    load_dotenv()
    access_key = os.getenv('VOLCENGINE_ACCESS_KEY')
    secret_key = os.getenv('VOLCENGINE_SECRET_KEY')
    print(f"从环境变量获取的 VOLCENGINE_ACCESS_KEY: {access_key}")
    print(f"从环境变量获取的 VOLCENGINE_SECRET_KEY: {secret_key}")
    
    if access_key and secret_key:
        print("检测到环境变量中的凭证，可以运行完整测试")
        print("取消注释以下行来运行实际API测试：")
        print("# test_text_to_image_basic()")
        print("# test_text_to_image_with_watermark()")
    else:
        print("未检测到环境变量 VOLCENGINE_ACCESS_KEY 和 VOLCENGINE_SECRET_KEY")
        print("如需运行完整测试，请设置这些环境变量或创建 .env 文件")
    
    # 取消注释以下行来运行实际API测试
    # test_text_to_image_basic()
    test_text_to_image_with_watermark()
    
    print("\n测试完成！")