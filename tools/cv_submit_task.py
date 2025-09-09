import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from volcengine.visual.VisualService import VisualService


class CVSubmitTaskTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            # 获取凭证
            access_key = self.runtime.credentials.get('volcengine_access_key')
            secret_key = self.runtime.credentials.get('volcengine_secret_key')
            
            if not access_key or not secret_key:
                yield self.create_text_message("Error: VolcEngine credentials not found")
                return
            
            # 获取参数
            req_key = tool_parameters.get('req_key')
            request_body = tool_parameters.get('request_body')
            
            if not req_key or not request_body:
                yield self.create_text_message("Error: req_key and request_body are required")
                return
            
            # 解析请求体
            try:
                form_data = json.loads(request_body)
                form_data['req_key'] = req_key
            except json.JSONDecodeError:
                yield self.create_text_message("Error: Invalid JSON format in request_body")
                return
            
            # 创建VisualService实例
            visual_service = VisualService()
            visual_service.set_ak(access_key)
            visual_service.set_sk(secret_key)
            
            yield self.create_text_message("Submitting async task...")
            
            # 调用cv_submit_task API
            response = visual_service.cv_submit_task(form_data)
            
            # 返回结果
            yield self.create_json_message({
                "status": "success",
                "message": "Task submitted successfully",
                "result": response
            })
            
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")