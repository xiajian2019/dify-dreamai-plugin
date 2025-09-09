import json
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
            
            yield self.create_text_message("Starting motion imitation generation...")
            
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
                yield self.create_text_message(f"Motion imitation failed: {error_msg}")
                return
            
            # 获取生成的视频
            data = result.get('data', {})
            
            if return_url and 'video_url' in data:
                video_url = data['video_url']
                yield self.create_text_message(f"Motion imitation video generated successfully!\nVideo URL: {video_url}")
                # 注意：Dify可能不支持直接显示视频，这里只返回URL
            elif 'binary_data_base64' in data:
                binary_data = data['binary_data_base64']
                yield self.create_blob_message(blob=binary_data, meta={'mime_type': 'video/mp4'})
                yield self.create_text_message("Motion imitation video generated successfully!")
            else:
                yield self.create_text_message("No video data found in response")
                
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")