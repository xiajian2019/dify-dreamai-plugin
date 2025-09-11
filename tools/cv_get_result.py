import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from volcengine.visual.VisualService import VisualService


class CVGetResultTool(Tool):
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
            task_id = tool_parameters.get('task_id')
            req_json = tool_parameters.get('req_json')
            
            if not req_key or not task_id:
                yield self.create_text_message("Error: req_key and task_id are required")
                return
            
            # 构建请求数据
            form_data = {
                'req_key': req_key,
                'task_id': task_id
            }
            
            # 处理req_json参数
            if req_json:
                try:
                    req_json_data = json.loads(req_json)
                    form_data['req_json'] = req_json
                except json.JSONDecodeError:
                    yield self.create_text_message("Error: Invalid JSON format in req_json parameter")
                    return
            
            # 创建VisualService实例
            visual_service = VisualService()
            visual_service.set_ak(access_key)
            visual_service.set_sk(secret_key)
            
            yield self.create_text_message("Retrieving task result...")
            
            # 调用cv_get_result API
            response = visual_service.cv_sync2async_get_result(form_data)
            
            # 返回结果
            yield self.create_json_message({
                "status": "success",
                "task_id": task_id,
                "result": response
            })
            
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")