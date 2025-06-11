from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# ====================================================================================================
# 导入并注册Web API
#
# 这部分代码负责将我们的自定义API路由注册到ComfyUI的Web服务器中
# 使得前端JavaScript代码可以通过fetch()调用后端Python函数
# ====================================================================================================
import server
from aiohttp import web
import logging

# 获取日志记录器
logger = logging.getLogger(__name__)

try:
    # 尝试从我们的API模块导入处理函数
    from .molecular_api import molecular_api
    API_AVAILABLE = True
    logger.info("✅ ALCHEM_PropBtn: Molecular API模块加载成功")
except ImportError:
    API_AVAILABLE = False
    logger.error("🚨 ALCHEM_PropBtn: Molecular API模块加载失败")

# 这是一个装饰器，ComfyUI用它来发现和注册自定义API路由
@server.PromptServer.instance.routes.post("/alchem_propbtn/api/molecular")
async def handle_molecular_api_request(request: web.Request):
    """
    处理所有到 /alchem_propbtn/api/molecular 的POST请求
    
    这个函数是前端和后端之间的桥梁。
    它接收来自前端的JSON请求，调用我们的API处理器，然后返回JSON响应。
    """
    if not API_AVAILABLE:
        return web.json_response(
            {"success": False, "error": "Molecular API模块不可用"},
            status=500
        )
    
    try:
        # 从请求中获取JSON数据
        json_data = await request.json()
        request_type = json_data.get("request_type")
        node_id = json_data.get("node_id")
        
        logger.info(f"🧪 接收到API请求: 类型='{request_type}', 节点ID='{node_id}'")
        
        # 调用我们的API处理器来处理请求
        # 注意：不能同时传递位置参数和关键字参数，避免参数冲突
        response_data = molecular_api.handle_request(
            request_type=request_type,
            node_id=node_id,
            # 只传递除了request_type和node_id之外的其他参数
            **{k: v for k, v in json_data.items() if k not in ['request_type', 'node_id']}
        )
        
        # 将处理结果作为JSON返回给前端
        return web.json_response(response_data)
        
    except Exception as e:
        logger.exception(f"🚨处理 /alchem_propbtn/api/molecular 请求时出错: {e}")
        return web.json_response(
            {"success": False, "error": f"服务器内部错误: {str(e)}"},
            status=500
        )

# ====================================================================================================
# ComfyUI插件的标准导出
# ====================================================================================================
WEB_DIRECTORY = "./web"

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY"
] 