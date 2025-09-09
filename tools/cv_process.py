import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from volcengine.visual.VisualService import VisualService


class CVProcessTool(Tool):
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
            
            # 构建请求数据
            form_data = {
                'req_key': 'jimeng_high_aes_general_v21_L',  # 固定值：即梦AI-文生图2.1
                'prompt': prompt
            }
            
            # 添加可选参数
            seed = tool_parameters.get('seed', -1)
            if seed != -1:
                form_data['seed'] = int(seed)
            
            width = tool_parameters.get('width', 512)
            height = tool_parameters.get('height', 512)
            form_data['width'] = int(width)
            form_data['height'] = int(height)
            
            use_pre_llm = tool_parameters.get('use_pre_llm', True)
            form_data['use_pre_llm'] = bool(use_pre_llm)
            
            use_sr = tool_parameters.get('use_sr', True)
            form_data['use_sr'] = bool(use_sr)
            
            return_url = tool_parameters.get('return_url', True)
            form_data['return_url'] = bool(return_url)
            
            # 处理水印参数
            add_logo = tool_parameters.get('add_logo', False)
            if add_logo:
                logo_info = {
                    'add_logo': True,
                    'position': int(tool_parameters.get('logo_position', 0)),
                    'language': int(tool_parameters.get('logo_language', 0)),
                    'opacity': float(tool_parameters.get('logo_opacity', 1.0))
                }
                logo_text_content = tool_parameters.get('logo_text_content')
                if logo_text_content:
                    logo_info['logo_text_content'] = logo_text_content
                form_data['logo_info'] = logo_info
            
            # 处理AIGC元数据参数
            add_aigc_meta = tool_parameters.get('add_aigc_meta', False)
            
            if add_aigc_meta:
                aigc_meta = {}
                content_producer = tool_parameters.get('content_producer')
                if content_producer:
                    aigc_meta['content_producer'] = content_producer
                producer_id = tool_parameters.get('producer_id')
                if producer_id:
                    aigc_meta['producer_id'] = producer_id
                content_propagator = tool_parameters.get('content_propagator')
                if content_propagator:
                    aigc_meta['content_propagator'] = content_propagator
                propagate_id = tool_parameters.get('propagate_id')
                if propagate_id:
                    aigc_meta['propagate_id'] = propagate_id
                
                if aigc_meta:
                    form_data['aigc_meta'] = json.dumps(aigc_meta)
            
            # 创建VisualService实例
            visual_service = VisualService()
            visual_service.set_ak(access_key)
            visual_service.set_sk(secret_key)
            
            yield self.create_text_message(f"Generating image with prompt: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")
            
            # 调用cv_process API
            response = visual_service.cv_process(form_data)
            
            # 解析响应结果
            result_data = {
                "status": "success",
                "message": "Image generation completed",
                "prompt": prompt,
                "parameters": {
                    "width": width,
                    "height": height,
                    "seed": seed,
                    "use_pre_llm": use_pre_llm,
                    "use_sr": use_sr,
                    "return_url": return_url
                },
                "raw_response": response
            }
            
            # 提取关键字段
            if isinstance(response, dict):
                if 'code' in response and response['code'] == 10000:
                    result_data['success'] = True
                    if 'data' in response:
                        data = response['data']
                        # 提取base64图片数据
                        if 'binary_data_base64' in data:
                            result_data['image_base64'] = data['binary_data_base64']
                            yield self.create_text_message("✅ Image generated successfully with base64 data")
                        
                        # 提取图片URL
                        if 'image_urls' in data and data['image_urls']:
                            result_data['image_urls'] = data['image_urls']
                            yield self.create_text_message(f"🔗 Generated {len(data['image_urls'])} image URL(s)")
                        
                        # 提取其他有用信息
                        if 'task_id' in data:
                            result_data['task_id'] = data['task_id']
                        if 'req_id' in data:
                            result_data['req_id'] = data['req_id']
                else:
                    result_data['success'] = False
                    result_data['error_code'] = response.get('code', 'unknown')
                    result_data['error_message'] = response.get('message', 'Unknown error')
                    yield self.create_text_message(f"❌ Generation failed: {result_data['error_message']}")
            
            # 返回结果
            yield self.create_json_message(result_data)
            
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")