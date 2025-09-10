import json
import time
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from volcengine.visual.VisualService import VisualService


class MotionImitationTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            # 获取凭证
            access_key = self.runtime.credentials.get('volcengine_access_key')
            secret_key = self.runtime.credentials.get('volcengine_secret_key')
            
            if not access_key or not secret_key:
                yield self.create_text_message("Error: VolcEngine credentials not found")
                return
            
            # 获取必需参数
            source_image = tool_parameters.get('source_image')
            if not source_image:
                yield self.create_text_message("Error: source_image is required")
                return
            
            motion_video = tool_parameters.get('motion_video')
            if not motion_video:
                yield self.create_text_message("Error: motion_video is required")
                return
            
            # 构建请求数据
            form_data = {
                'req_key': 'jimeng_motion_imitation_L',  # 动作模仿
                'source_image': source_image,
                'motion_video': motion_video
            }
            
            # 添加可选参数
            seed = tool_parameters.get('seed', -1)
            if seed != -1:
                form_data['seed'] = int(seed)
            
            # 视频时长（秒）
            duration = tool_parameters.get('duration', 4)
            form_data['duration'] = int(duration)
            
            # 帧率
            fps = tool_parameters.get('fps', 24)
            form_data['fps'] = int(fps)
            
            # 宽高比
            aspect_ratio = tool_parameters.get('aspect_ratio', '16:9')
            form_data['aspect_ratio'] = aspect_ratio
            
            # 动作强度
            motion_strength = tool_parameters.get('motion_strength', 0.8)
            form_data['motion_strength'] = float(motion_strength)
            
            # 面部保真度
            face_fidelity = tool_parameters.get('face_fidelity', 0.8)
            form_data['face_fidelity'] = float(face_fidelity)
            
            # 身体保真度
            body_fidelity = tool_parameters.get('body_fidelity', 0.8)
            form_data['body_fidelity'] = float(body_fidelity)
            
            # 背景保持
            preserve_background = tool_parameters.get('preserve_background', True)
            form_data['preserve_background'] = bool(preserve_background)
            
            # 平滑度
            smoothness = tool_parameters.get('smoothness', 0.5)
            form_data['smoothness'] = float(smoothness)
            
            return_url = tool_parameters.get('return_url', True)
            form_data['return_url'] = bool(return_url)
            
            # 初始化VisualService
            visual_service = VisualService()
            visual_service.set_ak(access_key)
            visual_service.set_sk(secret_key)
            
            # 第一步：提交任务
            yield self.create_text_message("正在提交动作模仿任务...")
            submit_data = {
                'req_key': 'cv_submit_task',
                'task_type': 'jimeng_motion_imitation_L',
                'request_body': json.dumps(form_data)
            }
            
            submit_resp = visual_service.cv_process(submit_data)
            
            if submit_resp['ResponseMetadata']['Error']:
                error_msg = submit_resp['ResponseMetadata']['Error']
                yield self.create_text_message(f"提交任务失败: {error_msg}")
                return
            
            submit_result = submit_resp['Result']
            if submit_result.get('code') != 10000:
                error_msg = submit_result.get('message', 'Unknown error')
                yield self.create_text_message(f"提交任务失败: {error_msg}")
                return
            
            task_id = submit_result.get('data', {}).get('task_id')
            if not task_id:
                yield self.create_text_message("提交任务失败: 未获取到task_id")
                return
            
            yield self.create_text_message(f"任务已提交，task_id: {task_id}，开始轮询结果...")
            
            # 第二步：轮询任务结果
            max_attempts = 120  # 视频生成时间较长，最多轮询10分钟
            attempt = 0
            
            while attempt < max_attempts:
                time.sleep(5)  # 等待5秒
                attempt += 1
                
                # 查询任务结果
                query_data = {
                    'req_key': 'cv_get_result',
                    'task_id': task_id
                }
                
                result_resp = visual_service.cv_process(query_data)
                
                if result_resp['ResponseMetadata']['Error']:
                    yield self.create_text_message(f"查询任务失败: {result_resp['ResponseMetadata']['Error']}")
                    return
                
                result_data = result_resp['Result']
                if result_data.get('code') != 10000:
                    yield self.create_text_message(f"查询任务失败: {result_data.get('message', 'Unknown error')}")
                    return
                
                data = result_data.get('data', {})
                status = data.get('status')
                
                if status == 'in_queue':
                    yield self.create_text_message(f"任务排队中... (第{attempt}次查询)")
                    continue
                elif status == 'generating':
                    yield self.create_text_message(f"任务生成中... (第{attempt}次查询)")
                    continue
                elif status == 'done':
                    # 任务完成，处理结果
                    if return_url and 'video_url' in data:
                        video_url = data['video_url']
                        yield self.create_text_message(f"动作模仿视频生成成功!\nVideo URL: {video_url}")
                    elif 'binary_data_base64' in data:
                        binary_data = data['binary_data_base64']
                        yield self.create_blob_message(blob=binary_data, meta={'mime_type': 'video/mp4'})
                        yield self.create_text_message("动作模仿视频生成成功!")
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
                
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")