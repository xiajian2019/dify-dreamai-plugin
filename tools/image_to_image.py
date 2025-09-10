import json
import base64
import time
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
            
            # 第一步：提交任务
            yield self.create_text_message("正在提交图生图任务...")
            submit_response = visual_service.cv_sync2async_submit_task({
                "req_key": 'jimeng_img2img_v30_L',
                "request_body": json.dumps(form_data)
            })
            
            # 检查响应是否有错误
            if 'code' in submit_response and submit_response.get('code') != 10000:
                error_msg = submit_response.get('message', 'Unknown error')
                yield self.create_text_message(f"提交任务失败: {error_msg}")
                return
            
            task_id = submit_response.get('data', {}).get('task_id')
            if not task_id:
                yield self.create_text_message("提交任务失败: 未获取到task_id")
                return
            
            yield self.create_text_message(f"任务已提交，task_id: {task_id}，开始轮询结果...")
            
            # 第二步：轮询任务结果
            max_attempts = 60  # 最多轮询5分钟
            attempt = 0
            
            while attempt < max_attempts:
                time.sleep(5)  # 等待5秒
                attempt += 1
                
                # 查询任务结果
                result_response = visual_service.cv_sync2async_get_result({"task_id": task_id})
                
                # 检查响应是否有错误
                if 'code' in result_response and result_response.get('code') != 10000:
                    yield self.create_text_message(f"查询任务失败: {result_response.get('message', 'Unknown error')}")
                    return
                
                data = result_response.get('data', {})
                status = data.get('status')
                
                if status == 'in_queue':
                    yield self.create_text_message(f"任务排队中... (第{attempt}次查询)")
                    continue
                elif status == 'generating':
                    yield self.create_text_message(f"任务生成中... (第{attempt}次查询)")
                    continue
                elif status == 'done':
                    # 任务完成，处理结果
                    if return_url and data.get('image_urls'):
                        image_urls = data['image_urls']
                        for i, image_url in enumerate(image_urls):
                            yield self.create_image_message(image_url=image_url)
                        yield self.create_text_message(f"图片生成成功！共生成{len(image_urls)}张图片")
                    elif data.get('binary_data_base64'):
                        binary_data_list = data['binary_data_base64']
                        for i, binary_data in enumerate(binary_data_list):
                            yield self.create_blob_message(blob=binary_data, meta={'mime_type': 'image/png'})
                        yield self.create_text_message(f"图片生成成功！共生成{len(binary_data_list)}张图片")
                    else:
                        yield self.create_text_message("任务完成，但未找到图片数据")
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