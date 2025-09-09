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
            
            # 创建VisualService实例
            visual_service = VisualService()
            visual_service.set_ak(access_key)
            visual_service.set_sk(secret_key)
            
            yield self.create_text_message(f"Generating image with prompt: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")
            
            # 调用cv_process API
            response = visual_service.cv_process(form_data)
            
            # 返回结果
            yield self.create_json_message({
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
                "result": response
            })
            
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")