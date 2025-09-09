import json
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
            
            yield self.create_text_message(f"Starting {video_quality} video generation...")
            
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
                yield self.create_text_message(f"Video generation failed: {error_msg}")
                return
            
            # 获取生成的视频
            data = result.get('data', {})
            
            if return_url and 'video_url' in data:
                video_url = data['video_url']
                yield self.create_text_message(f"Video generated successfully using {video_quality} quality!\nVideo URL: {video_url}")
                # 注意：Dify可能不支持直接显示视频，这里只返回URL
            elif 'binary_data_base64' in data:
                binary_data = data['binary_data_base64']
                yield self.create_blob_message(blob=binary_data, meta={'mime_type': 'video/mp4'})
                yield self.create_text_message(f"Video generated successfully using {video_quality} quality!")
            else:
                yield self.create_text_message("No video data found in response")
                
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")