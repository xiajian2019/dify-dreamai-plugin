from dotenv import load_dotenv
from dify_plugin import Plugin, DifyPluginEnv

# 加载 .env 文件
load_dotenv()

plugin = Plugin(DifyPluginEnv(MAX_REQUEST_TIMEOUT=120))

if __name__ == '__main__':
    plugin.run()
