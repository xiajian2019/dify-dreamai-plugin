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


## 运行 & 打包

参考官方文档： 

https://docs.dify.ai/plugin-dev-zh/9231-extension-plugin



```sh 
# 运行
python -m main

# 打包
dify plugin package ./xxx
```


## 优化逻辑

根据 API 文档 优化 现存的工具: 

 https://www.volcengine.com/docs/85621/1537648
即梦AI-文生图2.1 


req_key
是
string
服务标识，取固定值: jimeng_high_aes_general_v21_L

仅支持 cv_process, 

其他接口 不支持 cv_process。

即梦AI-文生图2.1 其他参数： 

prompt
是
string
用于生成图像的提示词 ，中英文均可输入
prompt书写规范参考上文描述

seed
可选
int
随机种子，作为确定扩散初始状态的基础，默认-1（随机）。若随机种子为相同正整数且其他参数均一致，则生成图片极大概率效果一致
默认值：-1

width
可选
int
生成图像的宽
默认值：512
取值范围：[256, 768]
宽、高与512差距过大，则出图效果不佳、延迟过长概率显著增加。
超分前建议比例及对应宽高：width*height
1:1：512*512
4:3：512*384
3:4：384*512
3:2：512*341
2:3：341*512
16:9：512*288
9:16：288*512
height
可选
int
生成图像的高
默认值：512
取值范围：[256, 768]
use_pre_llm
可选
bool
开启文本扩写，会针对输入prompt进行扩写优化，如果输入prompt较短建议开启，如果输入prompt较长建议关闭
默认值：true
prompt过短，如长度小于4时，推荐扩写默认打开，保证出图效果更优；
prompt较长，如出图4张，可考虑1次关闭扩写，3次打开扩写，保证出图效果多样性
use_sr
可选
bool
True：文生图+AIGC超分
False：文生图
默认值：true
内置的超分功能，开启后可将上述宽高均乘以2返回，此参数打开后延迟会有增加
如上述宽高均为512和512，此参数关闭出图 512*512 ，此参数打开出图1024 * 1024
return_url
可选
bool
输出是否返回图片链接 （链接有效期为24小时）

logo_info
可选
LogoInfo
水印信息

aigc_meta
可选
AIGCMeta
隐式标识
隐式标识验证方式：
查看【png】或【mp4】格式，人工智能生成合成内容表示服务平台（后续预计增加jpg）
https://www.gcmark.com/web/index.html#/mark/check/image
查看【jpg】格式，使用app11 segment查看aigc元数据内容
如 https://cyber.meme.tips/jpdump/#












req_key
string
必选
算法名称，取固定值为jimeng_t2i_v30


req_key
string
必选
算法名称，取固定值为jimeng_t2i_v31


req_key
string
必选
服务标识
取固定值: jimeng_i2i_v30

## 遇到问题 

由于修改插件已有的逻辑，导致注册失败。 
换个空间就能注册成功了，推测是缓存的问题，这个事情几乎搞好一个上午。
增加尝试逻辑，确认问题在 测试应用中引入了 这个工具, 而工具中之前的action 已经被干掉了。

反复折腾好久，居然是因为这个问题。 还是考虑的不够全面。

An error occurred while parsing the data: b'handshake failed, invalid key'

这个错误原因是，debug 的调试key 是有效期的。出现这个就说明 key 过期了, 更换这个key 即可。






## 完善文生图 


## 完善图生图 













