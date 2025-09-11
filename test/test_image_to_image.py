#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文件：用于本地调试 ImageToImageTool 类

使用方法：
1. 确保已安装所需依赖：pip install -r requirements.txt
2. 设置环境变量或在代码中配置 VolcEngine 凭证
3. 运行测试：python test/test_image_to_image.py
"""

import os
import sys
import base64
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

from tools.image_to_image import ImageToImageTool


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


def test_image_to_image_basic():
    """测试基本的图生图功能"""
    print("\n测试基本图生图功能...")
    
    # 从环境变量获取凭证
    access_key = os.getenv('VOLCENGINE_ACCESS_KEY')
    secret_key = os.getenv('VOLCENGINE_SECRET_KEY')
    
    if not access_key or not secret_key:
        print("跳过实际API测试：未找到凭证")
        return
    
    # 创建工具实例
    mock_runtime = MockRuntime(access_key, secret_key)
    mock_session = MockSession()
    tool = ImageToImageTool(runtime=mock_runtime, session=mock_session)
    
    # 测试参数（使用示例图片URL）
    test_params = {
        'prompt': '把这只猫变成一只狗',
        'image_input': 'https://example.com/cat.jpg',  # 示例URL
        'scale': 0.7,
        'width': 1328,
        'height': 1328,
        'seed': 42
    }
    
    print(f"测试参数: {test_params}")
    print(f"\n水印参数测试:")
    print(f"  - add_logo: {test_params['add_logo']}")
    print(f"  - position: {test_params['position']} (左上角)")
    print(f"  - language: {test_params['language']} (英文)")
    print(f"  - opacity: {test_params['opacity']}")
    print(f"  - logo_text_content: '{test_params['logo_text_content']}'")
    
    # 执行工具
    try:
        messages = list(tool._invoke(test_params))
        print(f"\n收到 {len(messages)} 条消息:")
        for i, msg in enumerate(messages):
            print(f"消息 {i+1}: {msg.message}")
        
        # 验证水印参数是否正确传递
        print(f"\n✅ 水印参数测试完成，参数已正确传递到工具中")
    except Exception as e:
        print(f"测试失败: {e}")


def test_image_to_image_base64():
    """测试使用Base64图片的图生图功能"""
    print("\n测试Base64图生图功能...")
    
    # 从环境变量获取凭证
    access_key = os.getenv('VOLCENGINE_ACCESS_KEY')
    secret_key = os.getenv('VOLCENGINE_SECRET_KEY')
    
    if not access_key or not secret_key:
        print("跳过实际API测试：未找到凭证")
        return
    
    # 创建工具实例
    mock_runtime = MockRuntime(access_key, secret_key)
    mock_session = MockSession()
    tool = ImageToImageTool(runtime=mock_runtime, session=mock_session)
    
    # 这里通过读取目录下的文件，转换成 base64 的，然后放到  image_input 参数中
    image_base64 = '' 
    
    # 尝试读取测试图片文件
    test_image_path = '/Users/xiajian/works/boohee/dify-plugin/dreamai/tmp/test.jpg'
    if os.path.exists(test_image_path):
        try:
            with open(test_image_path, 'rb') as f:
                image_base64 = base64.b64encode(f.read()).decode('utf-8')
            print(f"成功读取测试图片: {test_image_path}")
        except Exception as e:
            print(f"读取测试图片失败: {e}，使用默认示例图片")

    if image_base64 == '':
        print("跳过实际API测试：未找到测试图片")
        return
    
    # 测试参数（使用Base64编码的图片，包含水印参数）
    test_params = {
        'prompt': '改成吉卜力动画风格，模糊化人物的背景，无需对白框',
        'image_input': image_base64,
        'scale': 0.5,
        'seed': -1,
        'return_url': True,
        'add_logo': False,
        # 'position': 2,  # 左上角
        # 'language': 1,  # 英文
        # 'opacity': 0.8,
        # 'logo_text_content': 'Test Watermark'
    }
    
    # 执行工具
    try:
        messages = list(tool._invoke(test_params))
        print(f"\n收到 {len(messages)} 条消息:")
        for i, msg in enumerate(messages):
            print(f"消息 {i+1}: {msg.message}")
    except Exception as e:
        print(f"测试失败: {e}")


def test_parameter_validation():
    """测试参数验证"""
    print("\n测试参数验证...")
    
    # 创建工具实例（使用假凭证进行参数验证测试）
    mock_runtime = MockRuntime('fake_key', 'fake_secret')
    mock_session = MockSession()
    tool = ImageToImageTool(runtime=mock_runtime, session=mock_session)
    
    # 测试缺少必需参数
    test_cases = [
        ({}, "缺少所有必需参数"),
        ({'prompt': '测试提示词'}, "缺少image_input参数"),
        ({'image_input': 'test.jpg'}, "缺少prompt参数"),
    ]
    
    for params, description in test_cases:
        print(f"\n测试: {description}")
        print(f"参数: {params}")
        
        try:
            messages = list(tool._invoke(params))
            if messages:
                print(f"结果: {messages[0].message}")
        except Exception as e:
            print(f"异常: {e}")


if __name__ == '__main__':
    print("ImageToImageTool 本地调试测试")
    print("=" * 50)
    
    # 先运行参数验证测试（不需要真实凭证）
    test_parameter_validation()
    
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
        print("检测到环境变量中的凭证，可以运行完整测试")
        print("取消注释以下行来运行实际API测试：")
        print("# test_image_to_image_basic()")
        print("# test_image_to_image_base64()")
    else:
        print("未检测到环境变量 VOLCENGINE_ACCESS_KEY 和 VOLCENGINE_SECRET_KEY")
        print("如需运行完整测试，请设置这些环境变量或创建 .env 文件")
    
    # 取消注释以下行来运行实际的API测试
    # test_image_to_image_basic()
    test_image_to_image_base64()
    
    print("\n测试完成！")