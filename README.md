# dify-dreamai-plugin 

**Author:** xiajian
**Version:** 0.0.1
**Type:** tool


当前项目为 dify 的插件项目，用于调用火山引擎中的即梦AI的API。

## 项目简介

即梦AI是火山引擎提供的一个AI服务，用于生成图片以及视频。本插件为Dify平台提供了完整的即梦AI集成功能。

- **官方文档**: https://www.volcengine.com/docs/85621/1544716
- **Python SDK**: https://github.com/volcengine/volc-sdk-python
- **SDK代码位置**: 当前文件目录下的 `volc-sdk-python` 文件夹

## 插件功能

本插件提供了三个主要工具：

1. **cv_process** - 同步图片/视频生成
2. **cv_submit_task** - 异步任务提交
3. **cv_get_result** - 异步任务结果查询

## 安装和配置

### 1. 环境要求

- Python 3.12+
- Dify 插件开发环境

### 2. 依赖安装

```bash
pip install -r requirements.txt
```

### 3. 配置凭证

在使用插件前，需要配置火山引擎的API凭证：

- **VolcEngine Access Key**: 您的火山引擎访问密钥
- **VolcEngine Secret Key**: 您的火山引擎密钥

## 使用方法 

调用参考: 

同步接口(直接返回结果) Action=CVProcess
调用示例
示例在SDK中的路径：https://github.com/volcengine/volc-sdk-python/blob/main/volcengine/example/visual/cv_process.py# coding:utf-8
from __future__ import print_function

from volcengine.visual.VisualService import VisualService

if __name__ == '__main__':
    visual_service = VisualService()

    # call below method if you don't set ak and sk in $HOME/.volc/config
    visual_service.set_ak('your ak')
    visual_service.set_sk('your sk')
    
    # 请求Body(查看接口文档请求参数-请求示例，将请求参数内容复制到此)
    form = {
        "req_key": "xxx",
        # ...
    }

    resp = visual_service.cv_process(form)
    print(resp)

异步提交任务(返回taskId) Action=CVSubmitTask
调用示例
示例在SDK中的路径：https://github.com/volcengine/volc-sdk-python/blob/main/volcengine/example/visual/cv_submit_task.py# coding:utf-8
from __future__ import print_function

from volcengine import visual
from volcengine.visual.VisualService import VisualService

if __name__ == '__main__':
    visual_service = VisualService()

    # call below method if you don't set ak and sk in $HOME/.volc/config
    visual_service.set_ak('your ak')
    visual_service.set_sk('your sk')
    
    # 请求Body(查看接口文档请求参数-请求示例，将请求参数内容复制到此)
    form = {
        "req_key": "xxx",
        # ...
    }
    resp = visual_service.cv_submit_task( form)
    print(resp)

异步查询任务(返回结果) Action=CVGetResult
调用示例
示例在SDK中的路径：https://github.com/volcengine/volc-sdk-python/blob/main/volcengine/example/visual/cv_get_result.py# coding:utf-8
from __future__ import print_function

from volcengine import visual
from volcengine.visual.VisualService import VisualService

if __name__ == '__main__':
    visual_service = VisualService()

    # call below method if you don't set ak and sk in $HOME/.volc/config
    visual_service.set_ak('your ak')
    visual_service.set_sk('your sk')
    
    # 请求Body(查看接口文档请求参数-请求示例，将请求参数内容复制到此)
    form = {
        "req_key": "xxx",
        "task_id": "xxx"
    }
    resp = visual_service.cv_get_result(form)
    print(resp)

同步转异步提交任务(返回taskId)Action=CVSync2AsyncSubmitTask
调用示例
示例在SDK中的路径：https://github.com/volcengine/volc-sdk-python/blob/main/volcengine/example/visual/cv_sync2async_submit_task.py# coding:utf-8
from __future__ import print_function

from volcengine import visual
from volcengine.visual.VisualService import VisualService

if __name__ == '__main__':
    visual_service = VisualService()

    # call below method if you don't set ak and sk in $HOME/.volc/config
    visual_service.set_ak('your ak')
    visual_service.set_sk('your ak')
    
    # 请求Body(查看接口文档请求参数-请求示例，将请求参数内容复制到此)
    form = {
        "req_key": "xxx",
        # ...

    }
    resp = visual_service.cv_sync2async_submit_task(form)
    print(resp)

同步转异步查询任务(返回结果)Action=CVSync2AsyncGetResult
调用示例
示例在SDK中的路径：https://github.com/volcengine/volc-sdk-python/blob/main/volcengine/example/visual/cv_sync2async_get_result.py# coding:utf-8
from __future__ import print_function

from volcengine import visual
from volcengine.visual.VisualService import VisualService

if __name__ == '__main__':
    visual_service = VisualService()

    # call below method if you don't set ak and sk in $HOME/.volc/config
    visual_service.set_ak('your ak')
    visual_service.set_sk('your ak')
    
    # 请求Body(查看接口文档请求参数-请求示例，将请求参数内容复制到此)
    form = {
        "req_key": "xxx",
        "task_id": "xxx",
        "req_json": "{\"logo_info\":{\"add_logo\":true，\"position\":1, \"language\":1,\"opacity\"：0.5}}"
    }
    resp = visual_service.cv_sync2async_get_result(form)
    print(resp)







