import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from volcengine.visual.VisualService import VisualService


class TextToImageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            # 获取凭证
            access_key = self.runtime.credentials.get('volcengine_access_key')
            secret_key = self.runtime.credentials.get('volcengine_secret_key')
            
            if not access_key or not secret_key:
                yield self.create_text_message("Error: VolcEngine credentials not found")
                return
            
            # 获取必需参数
            prompt = tool_parameters.get('prompt')
            if not prompt:
                yield self.create_text_message("Error: prompt is required")
                return
            
            # 获取模型版本，默认使用3.1
            model_version = tool_parameters.get('model_version', '3.1')
            
            # 根据模型版本设置req_key
            if model_version == '3.0':
                req_key = 'jimeng_high_aes_general_v30_L'  # 即梦文生图3.0
            else:
                req_key = 'jimeng_high_aes_general_v31_L'  # 即梦文生图3.1
            
            # 构建请求数据
            form_data = {
                'req_key': req_key,
                'prompt': prompt
            }
            
            # 添加可选参数
            seed = tool_parameters.get('seed', -1)
            if seed != -1:
                form_data['seed'] = int(seed)
            
            width = tool_parameters.get('width', 1024)
            height = tool_parameters.get('height', 1024)
            form_data['width'] = int(width)
            form_data['height'] = int(height)
            
            # 3.1版本支持更多参数
            if model_version == '3.1':
                style = tool_parameters.get('style')
                if style:
                    form_data['style'] = style
                
                quality = tool_parameters.get('quality', 'standard')
                form_data['quality'] = quality
                
                aspect_ratio = tool_parameters.get('aspect_ratio')
                if aspect_ratio:
                    form_data['aspect_ratio'] = aspect_ratio
            
            use_pre_llm = tool_parameters.get('use_pre_llm', True)
            form_data['use_pre_llm'] = bool(use_pre_llm)
            
            use_sr = tool_parameters.get('use_sr', True)
            form_data['use_sr'] = bool(use_sr)
            
            return_url = tool_parameters.get('return_url', True)
            form_data['return_url'] = bool(return_url)
            
            # 初始化VisualService
            visual_service = VisualService()
            visual_service.set_ak(access_key)
            visual_service.set_sk(secret_key)
            
            yield self.create_text_message(f"Starting {model_version} text-to-image generation...")
            
            # 调用API
            resp = visual_service.cv_process(form_data)
            
            if resp['ResponseMetadata']['Error']:
                error_msg = resp['ResponseMetadata']['Error']
                yield self.create_text_message(f"API Error: {error_msg}")
                return
            
            # 解析响应
            result = resp['Result']
            
            if result.get('code') != 10000:
                error_msg = result.get('message', 'Unknown error')
                yield self.create_text_message(f"Generation failed: {error_msg}")
                return
            
            # 获取生成的图片
            data = result.get('data', {})
            
            if return_url and 'image_url' in data:
                image_url = data['image_url']
                yield self.create_image_message(image_url=image_url)
                yield self.create_text_message(f"Image generated successfully using {model_version}!\nImage URL: {image_url}")
            elif 'binary_data_base64' in data:
                binary_data = data['binary_data_base64']
                yield self.create_blob_message(blob=binary_data, meta={'mime_type': 'image/png'})
                yield self.create_text_message(f"Image generated successfully using {model_version}!")
            else:
                yield self.create_text_message("No image data found in response")
                
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")