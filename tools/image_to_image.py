import json
import base64
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from volcengine.visual.VisualService import VisualService


class ImageToImageTool(Tool):
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
            
            reference_image = tool_parameters.get('reference_image')
            if not reference_image:
                yield self.create_text_message("Error: reference_image is required")
                return
            
            # 构建请求数据
            form_data = {
                'req_key': 'jimeng_img2img_v30_L',  # 即梦图生图3.0智能参考
                'prompt': prompt,
                'reference_image': reference_image
            }
            
            # 添加可选参数
            seed = tool_parameters.get('seed', -1)
            if seed != -1:
                form_data['seed'] = int(seed)
            
            width = tool_parameters.get('width', 1024)
            height = tool_parameters.get('height', 1024)
            form_data['width'] = int(width)
            form_data['height'] = int(height)
            
            # 参考强度
            reference_strength = tool_parameters.get('reference_strength', 0.5)
            form_data['reference_strength'] = float(reference_strength)
            
            # 智能参考模式
            reference_mode = tool_parameters.get('reference_mode', 'auto')
            form_data['reference_mode'] = reference_mode
            
            # 风格参考权重
            style_weight = tool_parameters.get('style_weight', 0.5)
            form_data['style_weight'] = float(style_weight)
            
            # 结构参考权重
            structure_weight = tool_parameters.get('structure_weight', 0.5)
            form_data['structure_weight'] = float(structure_weight)
            
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
            
            yield self.create_text_message("Starting image-to-image generation...")
            
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
                yield self.create_text_message(f"Image-to-image generation completed successfully!\nImage URL: {image_url}")
            elif 'binary_data_base64' in data:
                binary_data = data['binary_data_base64']
                yield self.create_blob_message(blob=binary_data, meta={'mime_type': 'image/png'})
                yield self.create_text_message("Image-to-image generation completed successfully!")
            else:
                yield self.create_text_message("No image data found in response")
                
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")