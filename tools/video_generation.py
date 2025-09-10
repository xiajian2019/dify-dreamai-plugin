import json
import time
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from volcengine.visual.VisualService import VisualService


class VideoGenerationTool(Tool):
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
            
            # 获取视频质量，默认使用Pro
            video_quality = tool_parameters.get('video_quality', 'pro')
            
            # 根据视频质量设置req_key
            if video_quality == 'pro':
                req_key = 'jimeng_video_v30_pro_L'  # 即梦AI-视频生成3.0 Pro
            elif video_quality == '720p':
                req_key = 'jimeng_video_v30_720p_L'  # 即梦AI-视频生成3.0 720P
            elif video_quality == '1080p':
                req_key = 'jimeng_video_v30_1080p_L'  # 即梦AI-视频生成3.0 1080P
            else:
                req_key = 'jimeng_video_v30_pro_L'  # 默认使用Pro
            
            # 构建请求数据
            form_data = {
                'req_key': req_key,
                'prompt': prompt
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
            
            # 运动强度
            motion_strength = tool_parameters.get('motion_strength', 'medium')
            form_data['motion_strength'] = motion_strength
            
            # 摄像机运动
            camera_motion = tool_parameters.get('camera_motion', 'none')
            form_data['camera_motion'] = camera_motion
            
            # 参考图像（可选）
            reference_image = tool_parameters.get('reference_image')
            if reference_image:
                form_data['reference_image'] = reference_image
                
                # 参考强度
                reference_strength = tool_parameters.get('reference_strength', 0.5)
                form_data['reference_strength'] = float(reference_strength)
            
            use_pre_llm = tool_parameters.get('use_pre_llm', True)
            form_data['use_pre_llm'] = bool(use_pre_llm)
            
            return_url = tool_parameters.get('return_url', True)
            form_data['return_url'] = bool(return_url)
            
            # 初始化VisualService
            visual_service = VisualService()
            visual_service.set_ak(access_key)
            visual_service.set_sk(secret_key)
            
            # 第一步：提交任务
            yield self.create_text_message(f"正在提交{video_quality}视频生成任务...")
            
            # 调用异步提交API
            submit_resp = visual_service.cv_submit_task(form_data)
            
            if submit_resp['ResponseMetadata']['Error']:
                error_msg = submit_resp['ResponseMetadata']['Error']
                yield self.create_text_message(f"API Error: {error_msg}")
                return
            
            # 解析提交响应
            submit_result = submit_resp['Result']
            
            if submit_result.get('code') != 10000:
                error_msg = submit_result.get('message', 'Unknown error')
                yield self.create_text_message(f"Task submission failed: {error_msg}")
                return
            
            # 获取任务ID
            task_data = submit_result.get('data', {})
            task_id = task_data.get('task_id')
            
            if not task_id:
                yield self.create_text_message("Task submission failed: No task_id received")
                return
            
            yield self.create_text_message(f"任务已提交，task_id: {task_id}，开始轮询结果...")
            
            # 第二步：轮询任务结果
            max_attempts = 120  # 视频生成时间较长，最多轮询10分钟
            attempt = 0
            
            while attempt < max_attempts:
                time.sleep(5)  # 等待5秒
                attempt += 1
                
                # 查询任务结果
                query_data = {'task_id': task_id}
                result_resp = visual_service.cv_get_result(query_data)
                
                if result_resp['ResponseMetadata']['Error']:
                    error_msg = result_resp['ResponseMetadata']['Error']
                    yield self.create_text_message(f"Query task failed: {error_msg}")
                    return
                
                result = result_resp['Result']
                
                if result.get('code') != 10000:
                    error_msg = result.get('message', 'Unknown error')
                    yield self.create_text_message(f"Query task failed: {error_msg}")
                    return
                
                data = result.get('data', {})
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
                        yield self.create_text_message(f"Video generated successfully using {video_quality} quality!\nVideo URL: {video_url}")
                    elif 'binary_data_base64' in data:
                        binary_data = data['binary_data_base64']
                        yield self.create_blob_message(blob=binary_data, meta={'mime_type': 'video/mp4'})
                        yield self.create_text_message(f"Video generated successfully using {video_quality} quality!")
                    else:
                        yield self.create_text_message("任务完成，但未找到视频数据")
                    return
                elif status in ['failed', 'expired']:
                    yield self.create_text_message(f"任务状态异常: {status}，停止查询")
                    return
                else:
                    yield self.create_text_message(f"未知任务状态: {status}")
                    continue
            
            yield self.create_text_message("任务轮询超时，请稍后手动查询结果")
                
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")