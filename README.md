# dify-dreamai-plugin 

**Author:** xiajian
**Version:** 0.0.1
**Type:** tool


当前项目为 dify 的插件项目，用于调用火山引擎中的即梦AI的API。

## 项目简介

即梦AI是火山引擎提供的一个AI服务，用于生成图片以及视频。本插件为Dify平台提供了完整的即梦AI集成功能。

- **官方文档**: https://www.volcengine.com/docs/85621/1544716
- **Python SDK**: https://github.com/volcengine/volc-sdk-python

## 插件功能

完善这里的功能描述: 

- **同步文生图**: 即梦2.0的API， 支持根据文本描述生成图片
- **文生图**: 支持根据文本描述生成图片, 已完成
- **图生图**: 支持根据图片生成图片, 已完成
- **视频生成**: 支持根据文本描述生成视频, 已完成
- **图片控制视频生成**: 支持根据图片生成视频, 未验证 


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

开通密钥后还需要，在火山引擎中开启即梦AI的服务。

## 本地安装配置 


```sh
dify signature generate -f your_key_pair
dify signature sign your_plugin_project.difypkg -p your_key_pair.private.pem

```

需要修改  docker-compose.yml 的文件， 找到  plugin_daemon 在 FORCE_VERIFYING_SIGNATURE 之后增加 一些配置

```
THIRD_PARTY_SIGNATURE_VERIFICATION_ENABLED: true
THIRD_PARTY_SIGNATURE_VERIFICATION_PUBLIC_KEYS: /app/storage/public_keys/your_key_pair.public.pem
```

进入 docker ps | grep  plugin 进入容器： 

进入容器 plugin 的容器后

```sh
mkdir -p storage/public_keys/
cd storage/public_keys/
echo 'your_key_pair.public.pem的内容' > your_key_pair.public.pem
# 重启容器：
docker compose up plugin_daemon -d 
```

这样就能安装本地插件了，以后都可以这样安装插件。 


