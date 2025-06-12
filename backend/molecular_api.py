import json
import traceback
from typing import Dict, Any, Optional, List
import logging

# 设置日志
logger = logging.getLogger(__name__)

try:
    from .molecular_memory import (
        get_molecular_data, 
        get_cache_status, 
        get_active_node,
        set_active_node,
        clear_cache,
        MOLECULAR_DATA_CACHE,
        ACTIVE_MOLECULAR_NODE
    )
    MEMORY_AVAILABLE = True
    logger.info("🧪 分子API：内存管理器加载成功")
except ImportError as e:
    logger.error(f"🚨 分子API：内存管理器加载失败 - {e}")
    MEMORY_AVAILABLE = False

class MolecularAPI:
    """
    🧪 分子数据API
    
    提供RESTful接口，让前端JavaScript代码能够：
    1. 从后端内存获取分子数据
    2. 查询缓存状态
    3. 管理活跃节点
    4. 清除缓存数据
    
    这解决了之前分子数据只存在前端的问题！
    """
    
    @staticmethod
    def handle_request(request_type: str, node_id: str = None, **kwargs) -> Dict[str, Any]:
        """
        处理来自前端的API请求
        
        Args:
            request_type: 请求类型 ('get_data', 'get_status', 'set_active', 'clear_cache')
            node_id: 节点ID（如果需要）
            **kwargs: 其他参数
            
        Returns:
            响应数据字典
        """
        try:
            if not MEMORY_AVAILABLE:
                return {
                    "success": False,
                    "error": "分子内存管理器不可用",
                    "data": None
                }
            
            logger.info(f"🔥 处理分子API请求: {request_type}, 节点ID: {node_id}")
            
            if request_type == "get_molecular_data":
                return MolecularAPI._get_molecular_data(node_id)
            
            elif request_type == "get_cache_status":
                return MolecularAPI._get_cache_status()
            
            elif request_type == "get_active_node":
                return MolecularAPI._get_active_node()
            
            elif request_type == "set_active_node":
                return MolecularAPI._set_active_node(node_id)
            
            elif request_type == "clear_cache":
                return MolecularAPI._clear_cache(node_id)
            
            elif request_type == "search_nodes":
                return MolecularAPI._search_nodes(kwargs.get("query", ""))
            
            elif request_type == "get_all_nodes":
                return MolecularAPI._get_all_nodes()
            
            else:
                return {
                    "success": False,
                    "error": f"未知的请求类型: {request_type}",
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"🚨 处理分子API请求时出错: {e}")
            logger.error(f"错误详情: {traceback.format_exc()}")
            
            return {
                "success": False,
                "error": f"服务器内部错误: {str(e)}",
                "data": None
            }
    
    @staticmethod
    def _get_molecular_data(node_id: str) -> Dict[str, Any]:
        """获取指定节点的分子数据"""
        if not node_id:
            return {
                "success": False,
                "error": "节点ID不能为空",
                "data": None
            }
        
        molecular_data = get_molecular_data(node_id)
        
        if molecular_data:
            # 🌟 为前端优化数据格式
            optimized_data = {
                # 基本信息
                "filename": molecular_data.get("filename"),
                "format": molecular_data.get("format"),
                "format_name": molecular_data.get("format_name"),
                "node_id": molecular_data.get("node_id"),
                
                # 结构信息
                "atoms": molecular_data.get("atoms", 0),
                "bonds": molecular_data.get("bonds", 0),
                "coordinates": molecular_data.get("coordinates", []),
                
                # 文件内容（用于3D显示）
                "content": molecular_data.get("content", ""),
                
                # 元数据
                "metadata": molecular_data.get("metadata", {}),
                
                # 统计信息
                "file_stats": molecular_data.get("file_stats", {}),
                "cached_at": molecular_data.get("cached_at"),
                "access_count": molecular_data.get("access_count", 0),
                "last_accessed": molecular_data.get("last_accessed"),
                
                # 状态信息
                "is_active": molecular_data.get("is_active", False),
                "processing_complete": molecular_data.get("processing_complete", True)
            }
            
            logger.info(f"🔍 成功获取分子数据 - 节点: {node_id}")
            logger.info(f"   文件: {optimized_data['filename']}")
            logger.info(f"   格式: {optimized_data['format_name']}")
            logger.info(f"   原子数: {optimized_data['atoms']}")
            
            return {
                "success": True,
                "error": None,
                "data": optimized_data
            }
        else:
            logger.warning(f"⚠️ 未找到节点 {node_id} 的分子数据")
            return {
                "success": False,
                "error": f"未找到节点 {node_id} 的分子数据",
                "data": None
            }
    
    @staticmethod
    def _get_cache_status() -> Dict[str, Any]:
        """获取缓存状态"""
        try:
            status = get_cache_status()
            
            logger.info(f"📊 缓存状态查询成功")
            logger.info(f"   节点数: {status.get('total_nodes', 0)}")
            logger.info(f"   缓存大小: {status.get('total_cache_size', 0)} 字符")
            
            return {
                "success": True,
                "error": None,
                "data": status
            }
        except Exception as e:
            logger.error(f"🚨 获取缓存状态失败: {e}")
            return {
                "success": False,
                "error": f"获取缓存状态失败: {str(e)}",
                "data": None
            }
    
    @staticmethod
    def _get_active_node() -> Dict[str, Any]:
        """获取当前活跃节点"""
        try:
            active_node = get_active_node()
            
            if active_node:
                logger.info(f"🎯 当前活跃节点: {active_node.get('node_id')}")
                return {
                    "success": True,
                    "error": None,
                    "data": active_node
                }
            else:
                logger.info("🎯 当前没有活跃节点")
                return {
                    "success": True,
                    "error": None,
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"🚨 获取活跃节点失败: {e}")
            return {
                "success": False,
                "error": f"获取活跃节点失败: {str(e)}",
                "data": None
            }
    
    @staticmethod
    def _set_active_node(node_id: str) -> Dict[str, Any]:
        """设置活跃节点"""
        if not node_id:
            return {
                "success": False,
                "error": "节点ID不能为空",
                "data": None
            }
        
        try:
            success = set_active_node(node_id)
            
            if success:
                logger.info(f"🎯 成功设置活跃节点: {node_id}")
                return {
                    "success": True,
                    "error": None,
                    "data": {"active_node_id": node_id}
                }
            else:
                logger.warning(f"⚠️ 设置活跃节点失败: {node_id}")
                return {
                    "success": False,
                    "error": f"设置活跃节点失败，节点 {node_id} 可能不存在",
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"🚨 设置活跃节点时出错: {e}")
            return {
                "success": False,
                "error": f"设置活跃节点时出错: {str(e)}",
                "data": None
            }
    
    @staticmethod
    def _clear_cache(node_id: str = None) -> Dict[str, Any]:
        """清除缓存"""
        try:
            success = clear_cache(node_id)
            
            if success:
                if node_id:
                    logger.info(f"🗑️ 成功清除节点 {node_id} 的缓存")
                    message = f"成功清除节点 {node_id} 的缓存"
                else:
                    logger.info("🗑️ 成功清除所有缓存")
                    message = "成功清除所有缓存"
                
                return {
                    "success": True,
                    "error": None,
                    "data": {"message": message}
                }
            else:
                logger.warning(f"⚠️ 清除缓存失败")
                return {
                    "success": False,
                    "error": "清除缓存失败",
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"🚨 清除缓存时出错: {e}")
            return {
                "success": False,
                "error": f"清除缓存时出错: {str(e)}",
                "data": None
            }
    
    @staticmethod
    def _search_nodes(query: str) -> Dict[str, Any]:
        """搜索节点"""
        try:
            global MOLECULAR_DATA_CACHE
            
            if not query:
                # 如果没有查询条件，返回所有节点
                return MolecularAPI._get_all_nodes()
            
            query_lower = query.lower()
            matching_nodes = []
            
            for node_id, data in MOLECULAR_DATA_CACHE.items():
                # 搜索匹配条件：文件名、格式、节点ID
                filename = data.get("filename", "").lower()
                format_name = data.get("format_name", "").lower()
                node_id_lower = str(node_id).lower()
                
                if (query_lower in filename or 
                    query_lower in format_name or 
                    query_lower in node_id_lower):
                    
                    matching_nodes.append({
                        "node_id": node_id,
                        "filename": data.get("filename"),
                        "format": data.get("format"),
                        "format_name": data.get("format_name"),
                        "atoms": data.get("atoms", 0),
                        "cached_at": data.get("cached_at"),
                        "is_active": data.get("is_active", False)
                    })
            
            logger.info(f"🔍 搜索 '{query}' 找到 {len(matching_nodes)} 个匹配节点")
            
            return {
                "success": True,
                "error": None,
                "data": {
                    "query": query,
                    "total_matches": len(matching_nodes),
                    "nodes": matching_nodes
                }
            }
            
        except Exception as e:
            logger.error(f"🚨 搜索节点时出错: {e}")
            return {
                "success": False,
                "error": f"搜索节点时出错: {str(e)}",
                "data": None
            }
    
    @staticmethod
    def _get_all_nodes() -> Dict[str, Any]:
        """获取所有节点列表"""
        try:
            global MOLECULAR_DATA_CACHE
            
            all_nodes = []
            
            for node_id, data in MOLECULAR_DATA_CACHE.items():
                all_nodes.append({
                    "node_id": node_id,
                    "filename": data.get("filename"),
                    "format": data.get("format"),
                    "format_name": data.get("format_name"),
                    "atoms": data.get("atoms", 0),
                    "bonds": data.get("bonds", 0),
                    "file_size": data.get("file_stats", {}).get("size", 0),
                    "cached_at": data.get("cached_at"),
                    "access_count": data.get("access_count", 0),
                    "last_accessed": data.get("last_accessed"),
                    "is_active": data.get("is_active", False),
                    "processing_complete": data.get("processing_complete", True)
                })
            
            # 按最后访问时间排序
            all_nodes.sort(key=lambda x: x.get("last_accessed", 0), reverse=True)
            
            logger.info(f"📋 获取所有节点列表，共 {len(all_nodes)} 个节点")
            
            return {
                "success": True,
                "error": None,
                "data": {
                    "total_nodes": len(all_nodes),
                    "nodes": all_nodes
                }
            }
            
        except Exception as e:
            logger.error(f"🚨 获取节点列表时出错: {e}")
            return {
                "success": False,
                "error": f"获取节点列表时出错: {str(e)}",
                "data": None
            }


# 🌟 全局API实例
molecular_api = MolecularAPI()

# 🔧 便捷函数（供其他模块调用）
def api_get_molecular_data(node_id: str):
    """便捷的API调用函数 - 获取分子数据"""
    return molecular_api.handle_request("get_molecular_data", node_id=node_id)

def api_get_cache_status():
    """便捷的API调用函数 - 获取缓存状态"""
    return molecular_api.handle_request("get_cache_status")

def api_get_active_node():
    """便捷的API调用函数 - 获取活跃节点"""
    return molecular_api.handle_request("get_active_node")

def api_set_active_node(node_id: str):
    """便捷的API调用函数 - 设置活跃节点"""
    return molecular_api.handle_request("set_active_node", node_id=node_id)

def api_clear_cache(node_id: str = None):
    """便捷的API调用函数 - 清除缓存"""
    return molecular_api.handle_request("clear_cache", node_id=node_id)

def api_search_nodes(query: str = ""):
    """便捷的API调用函数 - 搜索节点"""
    return molecular_api.handle_request("search_nodes", query=query)

def api_get_all_nodes():
    """便捷的API调用函数 - 获取所有节点"""
    return molecular_api.handle_request("get_all_nodes") 