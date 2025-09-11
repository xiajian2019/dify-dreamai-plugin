import json
import time
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from volcengine.visual.VisualService import VisualService


class TextToVideoTool(Tool):
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
            
            # 获取视频质量参数，默认使用720P
            req_key = tool_parameters.get('req_key', 'jimeng_t2v_v30')
            
            # 构建请求数据
            form_data = {
                'req_key': req_key,
                'prompt': prompt
            }
            
            # 添加可选参数
            seed = tool_parameters.get('seed', -1)
            if seed != -1:
                form_data['seed'] = int(seed)
            
            frames = tool_parameters.get('frames', 121)
            form_data['frames'] = int(frames)
            
            aspect_ratio = tool_parameters.get('aspect_ratio', '16:9')
            form_data['aspect_ratio'] = str(aspect_ratio)
            
            # 初始化VisualService
            visual_service = VisualService()
            visual_service.set_ak(access_key)
            visual_service.set_sk(secret_key)
            
            # 第一步：提交任务
            yield self.create_text_message("正在提交文生视频任务...")
            # 打印提交请求参数
            print(f"提交请求参数: {form_data}")
            submit_resp = visual_service.cv_sync2async_submit_task(form_data)
            
            # 检查响应是否有错误
            if 'code' in submit_resp and submit_resp.get('code') != 10000:
                error_msg = submit_resp.get('message', 'Unknown error')
                yield self.create_text_message(f"提交任务失败: {error_msg}")
                return
            
            # 解析提交响应
            submit_result = submit_resp
            
            if submit_result.get('code') != 10000:
                error_msg = submit_result.get('message', 'Unknown error')
                yield self.create_text_message(f"提交任务失败: {error_msg}")
                return
            
            task_id = submit_result.get('data', {}).get('task_id')
            if not task_id:
                yield self.create_text_message("提交任务失败: 未获取到task_id")
                return
            
            yield self.create_text_message(f"任务已提交，task_id: {task_id}，开始轮询结果，最多轮询10分钟")
            
            # 第二步：轮询任务结果
            max_attempts = 120  # 视频生成时间较长，最多轮询10分钟
            attempt = 0
            
            while attempt < max_attempts:
                time.sleep(5)  # 等待5秒
                attempt += 1
                
                # 查询任务结果
                query_params = {"task_id": task_id, "req_key": req_key}
                result_resp = visual_service.cv_sync2async_get_result(query_params)
                
                # 检查响应是否有错误
                if 'code' in result_resp and result_resp.get('code') != 10000:
                    error_msg = result_resp.get('message', 'Unknown error')
                    yield self.create_text_message(f"查询任务失败: {error_msg}")
                    return
                
                data = result_resp.get('data', {})
                status = data.get('status')
                
                if status == 'in_queue':
                    yield self.create_text_message(f"第{attempt}次轮询，任务排队中\n")
                    continue
                elif status == 'generating':
                    yield self.create_text_message(f"第{attempt}次轮询，任务生成中\n")
                    continue
                elif status == 'done':
                     # 任务完成，处理结果
                     if data.get('video_url'):
                         video_url = data['video_url']
                         yield self.create_text_message(f"视频生成成功！地址: {video_url}")

                         # 返回结果
                         data_resp = {
                            "task_id": task_id,
                            "req_key": req_key,
                            "video_url": video_url,
                         }
                         yield self.create_json_message(data_resp)
                     else:
                         yield self.create_text_message("任务完成，但未找到视频数据")
                     return
                elif status in ['not_found', 'expired']:
                    yield self.create_text_message(f"任务状态异常: {status}，停止查询")
                    return
                else:
                    yield self.create_text_message(f"未知任务状态: {status}")
                    continue

            yield self.create_text_message("任务轮询超时，请稍后手动查询结果")
            yield self.create_json_message({ "task_id": task_id, "req_key": req_key })
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")