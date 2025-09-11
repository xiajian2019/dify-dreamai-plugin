#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示脚本：展示 TextToVideoTool 的视频质量选择功能

本脚本演示如何使用不同的 req_key 参数来生成不同质量的视频：
- jimeng_t2v_v30: 720P 标准质量
- jimeng_t2v_v30_1080p: 1080P 高清质量

使用方法：
1. 确保已安装所需依赖：pip install -r requirements.txt
2. 设置环境变量 VOLCENGINE_ACCESS_KEY 和 VOLCENGINE_SECRET_KEY
3. 运行演示：python demo_text_to_video_quality.py
"""

import os
import sys
from unittest.mock import Mock

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.text_to_video import TextToVideoTool


class MockRuntime:
    """模拟 runtime 对象"""
    def __init__(self, access_key: str, secret_key: str):
        self.credentials = {
            'volcengine_access_key': access_key,
            'volcengine_secret_key': secret_key
        }


class MockSession:
    """模拟 session 对象"""
    def __init__(self):
        pass


def demo_720p_video():
    """演示720P视频生成"""
    print("=== 720P 标准质量视频生成演示 ===")
    
    # 检查环境变量
    access_key = os.getenv('VOLCENGINE_ACCESS_KEY')
    secret_key = os.getenv('VOLCENGINE_SECRET_KEY')
    
    if not access_key or not secret_key:
        print("请设置环境变量 VOLCENGINE_ACCESS_KEY 和 VOLCENGINE_SECRET_KEY")
        return
    
    # 创建工具实例
    mock_runtime = MockRuntime(access_key, secret_key)
    mock_session = MockSession()
    tool = TextToVideoTool(runtime=mock_runtime, session=mock_session)
    
    # 测试参数
    test_params = {
        'prompt': '一只可爱的小猫在阳光下的花园里玩耍，画面温馨美好',
        'seed': 42,
        'frames': 121,  # 5秒
        'aspect_ratio': '16:9',
        'req_key': 'jimeng_t2v_v30'  # 720P 标准质量
    }
    
    print(f"测试参数: {test_params}")
    print("开始生成720P视频...")
    
    try:
        messages = list(tool._invoke(test_params))
        print(f"\n收到 {len(messages)} 条消息:")
        for i, message in enumerate(messages, 1):
            print(f"消息 {i}: {message.message if hasattr(message, 'message') else 'N/A'}")
    except Exception as e:
        print(f"生成失败: {str(e)}")


def demo_1080p_video():
    """演示1080P视频生成"""
    print("\n=== 1080P 高清质量视频生成演示 ===")
    
    # 检查环境变量
    access_key = os.getenv('VOLCENGINE_ACCESS_KEY')
    secret_key = os.getenv('VOLCENGINE_SECRET_KEY')
    
    if not access_key or not secret_key:
        print("请设置环境变量 VOLCENGINE_ACCESS_KEY 和 VOLCENGINE_SECRET_KEY")
        return
    
    # 创建工具实例
    mock_runtime = MockRuntime(access_key, secret_key)
    mock_session = MockSession()
    tool = TextToVideoTool(runtime=mock_runtime, session=mock_session)
    
    # 测试参数
    test_params = {
        'prompt': 'A majestic eagle soaring through mountain peaks at sunset, cinematic view',
        'seed': 12345,
        'frames': 241,  # 10秒
        'aspect_ratio': '16:9',
        'req_key': 'jimeng_t2v_v30_1080p'  # 1080P 高清质量
    }
    
    print(f"测试参数: {test_params}")
    print("开始生成1080P视频...")
    
    try:
        messages = list(tool._invoke(test_params))
        print(f"\n收到 {len(messages)} 条消息:")
        for i, message in enumerate(messages, 1):
            print(f"消息 {i}: {message.message if hasattr(message, 'message') else 'N/A'}")
    except Exception as e:
        print(f"生成失败: {str(e)}")


def demo_quality_comparison():
    """演示质量对比"""
    print("\n=== 视频质量对比演示 ===")
    
    # 检查环境变量
    access_key = os.getenv('VOLCENGINE_ACCESS_KEY')
    secret_key = os.getenv('VOLCENGINE_SECRET_KEY')
    
    if not access_key or not secret_key:
        print("请设置环境变量 VOLCENGINE_ACCESS_KEY 和 VOLCENGINE_SECRET_KEY")
        return
    
    # 创建工具实例
    mock_runtime = MockRuntime(access_key, secret_key)
    mock_session = MockSession()
    tool = TextToVideoTool(runtime=mock_runtime, session=mock_session)
    
    # 相同提示词，不同质量
    base_params = {
        'prompt': '城市夜景，霓虹灯闪烁，车流穿梭，现代都市风光',
        'seed': 999,  # 使用相同种子确保内容一致性
        'frames': 121,  # 5秒
        'aspect_ratio': '16:9'
    }
    
    qualities = [
        ('720P 标准质量', 'jimeng_t2v_v30'),
        ('1080P 高清质量', 'jimeng_t2v_v30_1080p')
    ]
    
    for quality_name, req_key in qualities:
        print(f"\n--- {quality_name} ---")
        test_params = base_params.copy()
        test_params['req_key'] = req_key
        
        print(f"测试参数: {test_params}")
        print(f"开始生成{quality_name}视频...")
        
        try:
            messages = list(tool._invoke(test_params))
            print(f"收到 {len(messages)} 条消息:")
            for i, message in enumerate(messages, 1):
                print(f"消息 {i}: {message.message if hasattr(message, 'message') else 'N/A'}")
        except Exception as e:
            print(f"生成失败: {str(e)}")


if __name__ == '__main__':
    print("TextToVideoTool 视频质量选择功能演示")
    print("=" * 60)
    
    # 检查环境变量
    access_key = os.getenv('VOLCENGINE_ACCESS_KEY')
    secret_key = os.getenv('VOLCENGINE_SECRET_KEY')
    
    if not access_key or not secret_key:
        print("错误：未检测到环境变量 VOLCENGINE_ACCESS_KEY 和 VOLCENGINE_SECRET_KEY")
        print("请设置这些环境变量后再运行演示")
        print("\n示例：")
        print("export VOLCENGINE_ACCESS_KEY='your_access_key'")
        print("export VOLCENGINE_SECRET_KEY='your_secret_key'")
        sys.exit(1)
    
    print(f"检测到凭证，开始演示...")
    print(f"Access Key: {access_key[:10]}...")
    
    # 运行演示
    demo_720p_video()
    demo_1080p_video()
    demo_quality_comparison()
    
    print("\n=" * 60)
    print("演示完成！")
    print("\n参数说明：")
    print("- req_key: 'jimeng_t2v_v30' = 720P 标准质量")
    print("- req_key: 'jimeng_t2v_v30_1080p' = 1080P 高清质量")
    print("- 1080P 质量更高但生成时间可能更长")
    print("- 建议根据实际需求选择合适的质量等级")