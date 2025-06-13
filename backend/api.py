"""
🧪 ALCHEM_PropBtn 简化API模块

专注于核心功能：上传按钮 + 查看按钮
删除了所有未使用的冗余API，保持代码简洁。
"""

import server
from aiohttp import web
import logging
import time
from typing import Dict, Any

# 获取日志记录器
logger = logging.getLogger(__name__)

# 导入内存管理
try:
    from .molecular_memory import (
        get_molecular_data, 
        store_molecular_data,
        get_cache_status, 
        clear_cache
    )
    MEMORY_AVAILABLE = True
    logger.info("✅ API模块：内存管理器加载成功")
except ImportError as e:
    MEMORY_AVAILABLE = False
    logger.error(f"🚨 API模块：内存管理器加载失败 - {e}")


def register_api_routes():
    """
    注册ALCHEM_PropBtn的核心API路由
    
    只保留实际使用的3个端点：
    1. 分子文件上传 (upload_molecular)
    2. 分子数据查询 (molecular) 
    3. 系统状态监控 (status)
    """
    
    @server.PromptServer.instance.routes.post("/alchem_propbtn/api/molecular")
    async def handle_molecular_request(request: web.Request):
        """处理分子数据相关请求"""
        if not MEMORY_AVAILABLE:
            return web.json_response(
                {"success": False, "error": "内存管理器不可用"},
                status=500
            )
        
        try:
            json_data = await request.json()
            request_type = json_data.get("request_type")
            node_id = json_data.get("node_id")
            
            logger.info(f"🧪 API请求: {request_type}, 节点: {node_id}")
            
            # 只处理实际使用的API
            if request_type == "get_molecular_data":
                response = await _handle_get_molecular_data(node_id)
            elif request_type == "get_cache_status":
                response = await _handle_get_cache_status()
            elif request_type == "clear_cache":
                response = await _handle_clear_cache(node_id)  # 保留用于调试
            else:
                response = {
                    "success": False,
                    "error": f"未知的请求类型: {request_type}"
                }
            
            return web.json_response(response)
            
        except Exception as e:
            logger.exception(f"🚨 处理分子API请求时出错: {e}")
            return web.json_response(
                {"success": False, "error": f"服务器内部错误: {str(e)}"},
                status=500
            )

    @server.PromptServer.instance.routes.post("/alchem_propbtn/api/upload_molecular")
    async def handle_upload_request(request: web.Request):
        """处理分子文件上传请求"""
        if not MEMORY_AVAILABLE:
            return web.json_response(
                {"success": False, "error": "内存管理器不可用"},
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
                                logger.error(f"🚨 无法解码文件: {filename}")
                                return web.json_response(
                                    {"success": False, "error": f"无法解码文件 {filename}"},
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
            
            logger.info(f"🧪 上传分子文件: 节点={node_id}, 文件={actual_filename}")
            if custom_filename:
                logger.info(f"🔧 使用自定义文件名: {filename} → {actual_filename}")
            
            # 存储到内存
            stored_data = store_molecular_data(
                node_id=node_id,
                filename=actual_filename,
                folder=folder,
                content=file_content
            )
            
            if stored_data:
                logger.info(f"✅ 文件已存储: {filename} -> 节点 {node_id}")
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
                    "message": f"分子文件 {filename} 上传成功"
                })
            else:
                logger.error(f"🚨 存储分子文件失败: {filename}")
                return web.json_response(
                    {"success": False, "error": "存储分子文件失败"},
                    status=500
                )
            
        except Exception as e:
            logger.exception(f"🚨 处理文件上传时出错: {e}")
            return web.json_response(
                {"success": False, "error": f"服务器内部错误: {str(e)}"},
                status=500
            )

    @server.PromptServer.instance.routes.get("/alchem_propbtn/api/status")
    async def handle_status_request(request: web.Request):
        """获取系统状态"""
        try:
            status_info = {
                "api_available": MEMORY_AVAILABLE,
                "timestamp": time.time(),
                "version": "2.0.0-simplified"  # 反映简化架构版本
            }
            
            # 获取缓存状态
            if MEMORY_AVAILABLE:
                try:
                    cache_response = await _handle_get_cache_status()
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
    
    logger.info("🚀 ALCHEM_PropBtn 简化API路由注册完成")
    logger.info("   - POST /alchem_propbtn/api/molecular (分子数据操作)")
    logger.info("   - POST /alchem_propbtn/api/upload_molecular (文件上传)")  
    logger.info("   - GET /alchem_propbtn/api/status (系统状态)")


# ====================================================================================================
# 核心处理函数 - 只保留实际使用的
# ====================================================================================================

async def _handle_get_molecular_data(node_id: str) -> Dict[str, Any]:
    """获取指定节点的分子数据"""
    if not node_id:
        return {"success": False, "error": "节点ID不能为空"}
    
    try:
        molecular_data = get_molecular_data(node_id)
        
        if molecular_data:
            # 为前端优化数据格式
            optimized_data = {
                "filename": molecular_data.get("filename"),
                "format": molecular_data.get("format"),
                "format_name": molecular_data.get("format_name"),
                "node_id": molecular_data.get("node_id"),
                "atoms": molecular_data.get("atoms", 0),
                "bonds": molecular_data.get("bonds", 0),
                "coordinates": molecular_data.get("coordinates", []),
                "content": molecular_data.get("content", ""),
                "metadata": molecular_data.get("metadata", {}),
                "file_stats": molecular_data.get("file_stats", {}),
                "cached_at": molecular_data.get("cached_at"),
                "access_count": molecular_data.get("access_count", 0),
                "last_accessed": molecular_data.get("last_accessed"),
                "is_active": molecular_data.get("is_active", False),
                "processing_complete": molecular_data.get("processing_complete", True)
            }
            
            logger.info(f"🔍 获取分子数据成功: 节点{node_id}, 文件{optimized_data['filename']}")
            return {"success": True, "data": optimized_data}
        else:
            logger.warning(f"⚠️ 未找到节点 {node_id} 的数据")
            return {"success": False, "error": f"未找到节点 {node_id} 的分子数据"}
            
    except Exception as e:
        logger.error(f"🚨 获取分子数据失败: {e}")
        return {"success": False, "error": f"获取分子数据失败: {str(e)}"}


async def _handle_get_cache_status() -> Dict[str, Any]:
    """获取缓存状态"""
    try:
        status = get_cache_status()
        logger.info(f"📊 缓存状态: {status.get('total_nodes', 0)}个节点")
        return {"success": True, "data": status}
    except Exception as e:
        logger.error(f"🚨 获取缓存状态失败: {e}")
        return {"success": False, "error": f"获取缓存状态失败: {str(e)}"}


async def _handle_clear_cache(node_id: str = None) -> Dict[str, Any]:
    """清除缓存（调试用）"""
    try:
        success = clear_cache(node_id)
        if success:
            message = f"成功清除节点 {node_id} 的缓存" if node_id else "成功清除所有缓存"
            logger.info(f"🗑️ {message}")
            return {"success": True, "data": {"message": message}}
        else:
            logger.warning("⚠️ 清除缓存失败")
            return {"success": False, "error": "清除缓存失败"}
    except Exception as e:
        logger.error(f"🚨 清除缓存出错: {e}")
        return {"success": False, "error": f"清除缓存出错: {str(e)}"}


# ====================================================================================================
# 便捷调试函数 - 仅保留必要的
# ====================================================================================================

def clear_cache_api(node_id: str = None):
    """便捷函数 - 清除缓存（调试用）"""
    import asyncio
    return asyncio.run(_handle_clear_cache(node_id))