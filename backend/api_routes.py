"""
🧪 ALCHEM_PropBtn API路由定义

统一管理所有API端点的注册和路由处理。
将API路由逻辑从__init__.py中分离出来，保持代码结构清洁。
"""

import server
from aiohttp import web
import logging
import time

# 获取日志记录器
logger = logging.getLogger(__name__)

# 导入API处理器
try:
    from .molecular_api import molecular_api
    API_AVAILABLE = True
    logger.info("✅ API路由：Molecular API模块加载成功")
except ImportError as e:
    API_AVAILABLE = False
    logger.error(f"🚨 API路由：Molecular API模块加载失败 - {e}")


def register_api_routes():
    """
    注册所有ALCHEM_PropBtn的API路由
    
    这个函数应该在__init__.py中被调用，用于注册所有API端点。
    集中管理所有路由逻辑，保持__init__.py的简洁性。
    """
    
    # 分子数据查询API
    @server.PromptServer.instance.routes.post("/alchem_propbtn/api/molecular")
    async def handle_molecular_api_request(request: web.Request):
        """处理分子数据查询请求"""
        if not API_AVAILABLE:
            return web.json_response(
                {"success": False, "error": "Molecular API模块不可用"},
                status=500
            )
        
        try:
            json_data = await request.json()
            request_type = json_data.get("request_type")
            node_id = json_data.get("node_id")
            
            logger.info(f"🧪 接收到API请求: 类型='{request_type}', 节点ID='{node_id}'")
            
            # 调用API处理器
            response_data = molecular_api.handle_request(
                request_type=request_type,
                node_id=node_id,
                **{k: v for k, v in json_data.items() if k not in ['request_type', 'node_id']}
            )
            
            return web.json_response(response_data)
            
        except Exception as e:
            logger.exception(f"🚨处理 /alchem_propbtn/api/molecular 请求时出错: {e}")
            return web.json_response(
                {"success": False, "error": f"服务器内部错误: {str(e)}"},
                status=500
            )

    # 分子文件上传API
    @server.PromptServer.instance.routes.post("/alchem_propbtn/api/upload_molecular")
    async def handle_molecular_upload_request(request: web.Request):
        """处理分子文件上传请求"""
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
            custom_filename = None
            
            # 读取表单字段
            while True:
                field = await reader.next()
                if field is None:
                    break
                
                if field.name == 'file':
                    filename = field.filename
                    file_content = await field.read()
                    # 转换为字符串
                    if isinstance(file_content, (bytes, bytearray)):
                        try:
                            file_content = file_content.decode('utf-8')
                        except UnicodeDecodeError:
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
                elif field.name == 'custom_filename':
                    custom_filename = await field.text()
            
            # 验证必需字段
            if not file_content or not filename or not node_id:
                return web.json_response(
                    {"success": False, "error": "缺少必需字段: file, filename, node_id"},
                    status=400
                )
            
            # 使用自定义文件名
            actual_filename = custom_filename if custom_filename else filename
            
            logger.info(f"🧪 接收到分子文件上传: 节点ID={node_id}, 文件={actual_filename}, 大小={len(file_content)} 字符")
            if custom_filename:
                logger.info(f"🔧 使用自定义文件名同步: {filename} → {actual_filename}")
            
            # 存储到后端内存
            from .molecular_memory import store_molecular_data
            
            stored_data = store_molecular_data(
                node_id=node_id,
                filename=actual_filename,
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

    # 系统状态监控API
    @server.PromptServer.instance.routes.get("/alchem_propbtn/api/status")
    async def handle_status_request(request: web.Request):
        """获取系统状态"""
        try:
            status_info = {
                "api_available": API_AVAILABLE,
                "timestamp": time.time(),
                "version": "2.0.0-clean"  # 反映清洁架构版本
            }
            
            # 获取缓存状态
            if API_AVAILABLE:
                try:
                    from .molecular_api import api_get_cache_status
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
    
    logger.info("🚀 ALCHEM_PropBtn: API路由注册完成")
    logger.info("   - POST /alchem_propbtn/api/molecular (分子数据查询)")
    logger.info("   - POST /alchem_propbtn/api/upload_molecular (分子文件上传)")  
    logger.info("   - GET /alchem_propbtn/api/status (系统状态监控)")