# 测试文件说明

## test_text_to_image.py

这是用于本地调试 `TextToImageTool` 类的测试文件。

### 功能特性

1. **参数验证测试** - 测试缺少凭证和必需参数的情况
2. **基础文生图测试** - 测试基本的文生图功能
3. **水印功能测试** - 测试带水印的文生图功能

### 使用方法

#### 1. 安装依赖
```bash
cd /Users/xiajian/works/boohee/dify-plugin/dreamai
pip install -r requirements.txt
```

#### 2. 配置凭证

**方法一：设置环境变量（推荐）**
```bash
export VOLCENGINE_ACCESS_KEY="your_access_key_here"
export VOLCENGINE_SECRET_KEY="your_secret_key_here"
```

**方法二：直接修改代码**
在测试文件中找到以下行并替换为实际凭证：
```python
access_key = os.getenv('VOLCENGINE_ACCESS_KEY', 'your_access_key_here')
secret_key = os.getenv('VOLCENGINE_SECRET_KEY', 'your_secret_key_here')
```

#### 3. 运行测试

**运行参数验证测试（不需要真实凭证）：**
```bash
python test/test_text_to_image.py
```

**运行完整测试（需要真实凭证）：**
取消注释测试文件末尾的以下行：
```python
# test_text_to_image_basic()
# test_text_to_image_with_watermark()
```

### 测试用例说明

#### test_parameter_validation()
- 测试缺少 VolcEngine 凭证的情况
- 测试缺少必需参数 `prompt` 的情况
- 不需要真实的 API 凭证

#### test_text_to_image_basic()
- 测试基础的文生图功能
- 使用即梦AI 3.1模型
- 生成1024x1024像素的图片
- 需要真实的 VolcEngine 凭证

#### test_text_to_image_with_watermark()
- 测试带水印的文生图功能
- 使用即梦AI 3.0模型
- 生成512x512像素的图片
- 添加自定义水印文字
- 需要真实的 VolcEngine 凭证

### 注意事项

1. **凭证安全**：请勿将真实凭证提交到版本控制系统
2. **API限制**：请注意 VolcEngine API 的调用频率限制
3. **网络连接**：确保网络连接正常，API调用可能需要较长时间
4. **错误处理**：测试文件包含详细的错误处理和日志输出

### 调试技巧

1. **查看详细错误**：测试文件会打印完整的异常堆栈信息
2. **分步调试**：可以在关键位置添加 `print()` 语句来跟踪执行流程
3. **参数调整**：可以修改测试参数来测试不同的场景
4. **单独测试**：可以单独运行某个测试函数进行针对性调试

### 示例输出

```
TextToImageTool 本地调试测试
==================================================

=== 参数验证测试 ===
测试1: 缺少凭证
结果: Error: VolcEngine credentials not found

测试2: 缺少prompt
结果: Error: prompt is required

==================================================
注意：以下测试需要真实的 VolcEngine 凭证
请设置环境变量或修改代码中的凭证配置
==================================================

测试完成！
```