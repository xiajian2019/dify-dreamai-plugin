import json
import time
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from volcengine.visual.VisualService import VisualService


class TextToImageTool(Tool):
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
            
            # 获取模型版本，默认使用3.1
            model_version = tool_parameters.get('model_version', '3.1')
            
            # 根据模型版本设置req_key
            if model_version == '3.0':
                req_key = 'jimeng_t2i_v30'  # 即梦文生图3.0
            elif model_version == 'doubao_3.0':
                # 豆包3.0模型使用固定的req_key
                req_key = 'high_aes_general_v30l_zt2i'
            elif model_version == '4.0':
                req_key = 'jimeng_t2i_v40'  # 即梦文生图4.0
            else:
                req_key = 'jimeng_t2i_v31'  # 即梦文生图3.1
            
            # 构建请求数据
            form_data = {
                'req_key': req_key,
                'prompt': prompt
            }
            
            # 添加可选参数
            seed = tool_parameters.get('seed', -1)
            if seed != -1:
                form_data['seed'] = int(seed)
            
            # 处理图片链接参数（4.0版本支持）
            image_urls_str = tool_parameters.get('image_urls')
            if image_urls_str and model_version == '4.0':
                # 将换行分割的字符串转换为数组
                image_urls = [url.strip() for url in image_urls_str.split('\n') if url.strip()]
                if image_urls:
                    form_data['image_urls'] = image_urls
            
            # 处理尺寸参数
            if model_version == '4.0':
                # 4.0版本支持size参数
                size = tool_parameters.get('size')
                if size:
                    form_data['size'] = int(size)
                
                # 4.0版本的宽高参数需要同时传入或都不传
                width = tool_parameters.get('width')
                height = tool_parameters.get('height')
                if width is not None and height is not None:
                    form_data['width'] = int(width)
                    form_data['height'] = int(height)
                elif width is not None or height is not None:
                    yield self.create_text_message("Error: For 4.0 model, width and height must be specified together or not at all")
                    return
            else:
                # 其他版本使用传统的宽高参数
                width = tool_parameters.get('width', 1024)
                height = tool_parameters.get('height', 1024)
                form_data['width'] = int(width)
                form_data['height'] = int(height)
            
            use_pre_llm = tool_parameters.get('use_pre_llm', True)
            form_data['use_pre_llm'] = bool(use_pre_llm)
            
            use_sr = tool_parameters.get('use_sr', True)
            form_data['use_sr'] = bool(use_sr)
            
            return_url = tool_parameters.get('return_url', True)
            form_data['return_url'] = bool(return_url)
            
            # scale参数处理（支持豆包3.0和4.0）
            if model_version in ['doubao_3.0', '4.0'] and 'scale' in tool_parameters:
                scale_value = float(tool_parameters['scale'])
                # 根据模型版本验证范围
                if model_version == 'doubao_3.0':
                    if scale_value < 1.0 or scale_value > 10.0:
                        yield self.create_text_message("Error: Scale value for Doubao 3.0 must be between 1.0 and 10.0")
                        return
                elif model_version == '4.0':
                    if scale_value < 0.0 or scale_value > 1.0:
                        yield self.create_text_message("Error: Scale value for DreamAI 4.0 must be between 0.0 and 1.0")
                        return
                form_data['scale'] = scale_value
            elif model_version == 'doubao_3.0':
                form_data['scale'] = 2.5  # 默认值
            elif model_version == '4.0':
                form_data['scale'] = 0.5  # 默认值
            
            # 4.0版本特有参数
            if model_version == '4.0':
                # 强制生成单图参数
                force_single = tool_parameters.get('force_single', False)
                form_data['force_single'] = bool(force_single)
                
                # 宽高比范围参数
                min_ratio = tool_parameters.get('min_ratio')
                if min_ratio is not None:
                    form_data['min_ratio'] = float(min_ratio)
                
                max_ratio = tool_parameters.get('max_ratio')
                if max_ratio is not None:
                    form_data['max_ratio'] = float(max_ratio)
            
            # 处理水印参数
            add_logo = tool_parameters.get('add_logo', False)
            position = tool_parameters.get('position', 0)
            language = tool_parameters.get('language', 0)
            opacity = tool_parameters.get('opacity', 1.0)
            logo_text_content = tool_parameters.get('logo_text_content', '')
            
            # 构建req_json参数（用于查询任务时传递）
            req_json_data = {
                "return_url": return_url
            }
            
            if add_logo:
                req_json_data["logo_info"] = {
                    "add_logo": add_logo,
                    "position": int(position),
                    "language": int(language),
                    "opacity": float(opacity)
                }
                if logo_text_content:
                    req_json_data["logo_info"]["logo_text_content"] = logo_text_content
            
            req_json = json.dumps(req_json_data)
            
            # 初始化VisualService
            visual_service = VisualService()
            visual_service.set_ak(access_key)
            visual_service.set_sk(secret_key)
            
            # 第一步：提交任务
            yield self.create_text_message("正在提交文生图任务...")
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
            
            yield self.create_text_message(f"任务已提交，task_id: {task_id}，开始轮询结果...")
            
            # 第二步：轮询任务结果
            max_attempts = 60  # 最多轮询5分钟
            attempt = 0
            
            while attempt < max_attempts:
                time.sleep(5)  # 等待5秒
                attempt += 1
                
                # 查询任务结果
                query_params = {"task_id": task_id, "req_key": req_key}
                if req_json:
                    query_params["req_json"] = req_json
                result_resp = visual_service.cv_sync2async_get_result(query_params)
                
                # 检查响应是否有错误
                if 'code' in result_resp and result_resp.get('code') != 10000:
                    error_msg = result_resp.get('message', 'Unknown error')
                    yield self.create_text_message(f"查询任务失败: {error_msg}")
                    return
                
                data = result_resp.get('data', {})
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
                        yield self.create_text_message(f"图片生成成功！共生成{len(image_urls)}张图片")
                        data_resp = {
                            "task_id": task_id,
                            "req_key": req_key,
                            "image_urls": image_urls,
                        }
                        yield self.create_json_message(data_resp)
                     elif data.get('binary_data_base64'):
                        binary_data_list = data['binary_data_base64']
                        yield self.create_text_message(f"图片生成成功！共生成{len(binary_data_list)}张图片")

                        data_resp = {
                            "task_id": task_id,
                            "req_key": req_key,
                            "binary_data_base64": binary_data_list,
                        }
                        yield self.create_json_message(data_resp)
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