from .nodes.nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# 导入测试节点
try:
    from .nodes.test_node import NODE_CLASS_MAPPINGS as TEST_NODE_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as TEST_NODE_DISPLAY_MAPPINGS
    # 合并节点映射
    NODE_CLASS_MAPPINGS.update(TEST_NODE_MAPPINGS)
    NODE_DISPLAY_NAME_MAPPINGS.update(TEST_NODE_DISPLAY_MAPPINGS)
except ImportError as e:
    print(f"⚠️ 测试节点导入失败: {e}")

# ====================================================================================================
# 导入并注册Web API
#
# 这部分代码负责将我们的自定义API路由注册到ComfyUI的Web服务器中
# 使得前端JavaScript代码可以通过fetch()调用后端Python函数
# ====================================================================================================
import server
from aiohttp import web
import logging
import time

# 获取日志记录器
logger = logging.getLogger(__name__)

try:
    # 尝试从我们的API模块导入处理函数
    from .backend.molecular_api import molecular_api
    API_AVAILABLE = True
    logger.info("✅ ALCHEM_PropBtn: Molecular API模块加载成功")
except ImportError:
    API_AVAILABLE = False
    logger.error("🚨 ALCHEM_PropBtn: Molecular API模块加载失败")

# 安装执行钩子
try:
    from .backend.execution_hook import install_molecular_execution_hook
    hook_installed = install_molecular_execution_hook()
    if hook_installed:
        logger.info("🔗 ALCHEM_PropBtn: 分子数据执行钩子安装成功")
    else:
        logger.warning("⚠️ ALCHEM_PropBtn: 分子数据执行钩子安装失败")
except ImportError as e:
    logger.error(f"🚨 ALCHEM_PropBtn: 执行钩子模块加载失败 - {e}")

# 分子数据查询API
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

# 分子文件上传API - 直接存储到后端内存
@server.PromptServer.instance.routes.post("/alchem_propbtn/api/upload_molecular")
async def handle_molecular_upload_request(request: web.Request):
    """
    处理分子文件上传请求，直接存储到后端内存
    
    接收multipart/form-data格式的文件上传请求：
    - file: 分子文件
    - node_id: 目标节点ID
    - folder: 存储文件夹（可选，默认molecules）
    """
    if not API_AVAILABLE:
        return web.json_response(
            {"success": False, "error": "Molecular API模块不可用"},
            status=500
        )
    
    try:
        # 解析multipart表单数据
        reader = await request.multipart()
        
        file_content = None
        filename = None
        node_id = None
        folder = "molecules"
        custom_filename = None  # 🔧 新增：自定义文件名支持
        
        # 读取表单字段
        while True:
            field = await reader.next()
            if field is None:
                break
            
            if field.name == 'file':
                filename = field.filename
                file_content = await field.read()
                # 转换为字符串 - 处理bytes和bytearray
                if isinstance(file_content, (bytes, bytearray)):
                    try:
                        file_content = file_content.decode('utf-8')
                    except UnicodeDecodeError:
                        # 如果UTF-8解码失败，尝试其他编码
                        try:
                            file_content = file_content.decode('latin-1')
                        except UnicodeDecodeError:
                            logger.error(f"🚨 无法解码文件内容: {filename}")
                            return web.json_response(
                                {"success": False, "error": f"无法解码文件 {filename}，请检查文件编码"},
                                status=400
                            )
            elif field.name == 'node_id':
                node_id = await field.text()
            elif field.name == 'folder':
                folder = await field.text()
            elif field.name == 'custom_filename':  # 🔧 新增：处理自定义文件名
                custom_filename = await field.text()
        
        # 验证必需字段
        if not file_content or not filename or not node_id:
            return web.json_response(
                {"success": False, "error": "缺少必需字段: file, filename, node_id"},
                status=400
            )
        
        # 🔧 使用自定义文件名（如果提供）来同步重命名
        actual_filename = custom_filename if custom_filename else filename
        
        logger.info(f"🧪 接收到分子文件上传: 节点ID={node_id}, 文件={actual_filename}, 大小={len(file_content)} 字符")
        if custom_filename:
            logger.info(f"🔧 使用自定义文件名同步: {filename} → {actual_filename}")
        
        # 直接存储到后端内存
        from .backend.molecular_memory import store_molecular_data
        
        stored_data = store_molecular_data(
            node_id=node_id,
            filename=actual_filename,  # 使用实际文件名
            folder=folder,
            content=file_content
        )
        
        if stored_data:
            logger.info(f"✅ 分子文件已存储到后端内存: {filename} -> 节点 {node_id}")
            return web.json_response({
                "success": True,
                "data": {
                    "filename": filename,
                    "node_id": node_id,
                    "format": stored_data.get("format"),
                    "atoms": stored_data.get("atoms", 0),
                    "file_size": stored_data.get("file_stats", {}).get("size", 0),
                    "cached_at": stored_data.get("cached_at")
                },
                "message": f"分子文件 {filename} 已成功存储到后端内存"
            })
        else:
            logger.error(f"🚨 存储分子文件到后端内存失败: {filename}")
            return web.json_response(
                {"success": False, "error": "存储分子文件到后端内存失败"},
                status=500
            )
        
    except Exception as e:
        logger.exception(f"🚨 处理分子文件上传时出错: {e}")
        return web.json_response(
            {"success": False, "error": f"服务器内部错误: {str(e)}"},
            status=500
        )

# 获取系统状态API - 用于调试和监控
@server.PromptServer.instance.routes.get("/alchem_propbtn/api/status")
async def handle_status_request(request: web.Request):
    """
    获取ALCHEM_PropBtn系统状态
    
    返回：
    - API可用性
    - 执行钩子状态
    - 后端内存缓存状态
    """
    try:
        status_info = {
            "api_available": API_AVAILABLE,
            "timestamp": time.time(),
            "version": "1.0.0"
        }
        
        # 获取执行钩子状态
        try:
            from .backend.execution_hook import get_hook_status
            hook_status = get_hook_status()
            status_info["execution_hook"] = hook_status
        except ImportError:
            status_info["execution_hook"] = {"error": "执行钩子模块不可用"}
        
        # 获取缓存状态
        if API_AVAILABLE:
            try:
                from .backend.molecular_api import api_get_cache_status
                cache_response = api_get_cache_status()
                if cache_response["success"]:
                    status_info["cache"] = cache_response["data"]
                else:
                    status_info["cache"] = {"error": cache_response["error"]}
            except Exception as e:
                status_info["cache"] = {"error": f"获取缓存状态失败: {str(e)}"}
        else:
            status_info["cache"] = {"error": "API不可用"}
        
        return web.json_response({
            "success": True,
            "data": status_info
        })
        
    except Exception as e:
        logger.exception(f"🚨 获取系统状态时出错: {e}")
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