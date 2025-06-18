"""
🧪 ALCHEM_PropBtn 简化内存管理模块

专注于核心功能：分子数据的存储和查询
删除了过度设计的分析功能和未使用的活跃节点机制
"""

import os
import time
import threading
from typing import Dict, Any, Optional
import folder_paths

# 使用统一的ALCHEM日志系统
from .logging_config import get_memory_logger

# 初始化统一Logger
logger = get_memory_logger()

# 尝试导入WebSocket通知功能
try:
    from .websocket_server import notify_molecular_update, notify_molecular_edit, notify_molecular_delete
    WEBSOCKET_NOTIFY_AVAILABLE = True
    logger.success("WebSocket通知功能加载成功")
except ImportError as e:
    WEBSOCKET_NOTIFY_AVAILABLE = False
    logger.warning(f"WebSocket通知功能不可用 - {e}")
    
    # 创建空的异步通知函数，避免代码报错
    async def notify_molecular_update(node_id, data):
        pass
    async def notify_molecular_edit(node_id, data):
        pass
    async def notify_molecular_delete(node_id):
        pass

# 全局分子数据缓存 - 简化版本
MOLECULAR_DATA_CACHE: Dict[str, Dict[str, Any]] = {}

# 🔑 将被移除：全局活跃tab_id（已被前端传参替代）
# ACTIVE_TAB_ID: Optional[str] = None  # 已废弃，使用前端传入的_alchem_node_id

# 线程锁，确保缓存操作的线程安全
CACHE_LOCK = threading.Lock()


class MolecularDataManager:
    """
    🧪 简化的分子数据内存管理器
    
    专注于核心功能：
    1. 存储分子数据到内存缓存
    2. 从缓存获取分子数据  
    3. 缓存状态查询
    4. 缓存清理（调试用）
    """
    
    @classmethod
    def store_molecular_data(cls, node_id: str, filename: str, folder: str = "molecules", 
                           content: str = None) -> Optional[Dict[str, Any]]:
        """
        存储分子数据到内存缓存
        
        Args:
            node_id: ComfyUI节点的唯一ID
            filename: 分子文件名
            folder: 存储文件夹（默认molecules）
            content: 分子文件内容
            
        Returns:
            存储的数据字典，失败返回None
        """
        with CACHE_LOCK:
            try:
                # 验证必需参数
                if not node_id or not filename:
                    logger.error("存储失败：节点ID和文件名不能为空")
                    return None
                
                if not content:
                    logger.error("存储失败：文件内容不能为空")
                    return None
                
                # 🔍 调试日志：追踪节点ID格式
                logger.molecular(f"[DEBUG] 存储分子数据开始:")
                logger.molecular(f"  - 原始node_id: '{node_id}'")
                logger.molecular(f"  - node_id类型: {type(node_id)}")
                logger.molecular(f"  - node_id长度: {len(node_id)}")
                logger.molecular(f"  - 文件名: {filename}")
                
                # 检测基本格式信息
                file_format = cls._detect_format(filename)
                
                # 🔑 提取tab_id（关键新增）
                tab_id = None
                if "_node_" in node_id:
                    tab_id = node_id.split("_node_")[0]  # 例如: "workflow_fl40l5"
                    logger.molecular(f"[DEBUG] 解析node_id:")
                    logger.molecular(f"  - 提取的tab_id: '{tab_id}'")
                    logger.molecular(f"  - 分割后的节点部分: '{node_id.split('_node_')[1] if len(node_id.split('_node_')) > 1 else 'None'}")
                else:
                    logger.warning(f"[DEBUG] node_id格式异常，未包含'_node_': '{node_id}'")
                
                # 创建存储数据结构
                molecular_data = {
                    "node_id": node_id,
                    "filename": filename,
                    "folder": folder,
                    "content": content,
                    "format": file_format,
                    "format_name": cls._get_format_name(file_format),
                    "tab_id": tab_id,  # 🔑 新增：Tab标识
                    
                    # 基本统计信息
                    "file_stats": {
                        "size": len(content),
                        "lines": content.count('\n') + 1
                    },
                    
                    # 简单的原子计数（不做复杂分析）
                    "atoms": cls._simple_atom_count(content, file_format),
                    
                    # 缓存管理信息
                    "cached_at": time.time(),
                    "last_accessed": time.time(),
                    "access_count": 0
                }
                
                # 保存到全局缓存
                MOLECULAR_DATA_CACHE[node_id] = molecular_data
                
                # 🔍 调试日志：验证存储
                logger.molecular(f"[DEBUG] 数据已存储到缓存:")
                logger.molecular(f"  - 缓存key: '{node_id}'")
                logger.molecular(f"  - 当前缓存中的所有keys: {list(MOLECULAR_DATA_CACHE.keys())}")
                logger.molecular(f"  - 缓存大小: {len(MOLECULAR_DATA_CACHE)}")
                
                # 🔑 修复：保存到文件系统时传递节点ID，避免重名文件覆盖
                try:
                    cls._save_to_filesystem(filename, folder, content, node_id)
                except Exception as e:
                    logger.warning(f"文件系统保存失败: {e}")
                
                logger.success(f"[DEBUG] 分子数据存储成功: {filename} -> 节点 {node_id}")
                
                # 🚀 发送WebSocket通知（改进的安全调用）
                if WEBSOCKET_NOTIFY_AVAILABLE:
                    try:
                        # 使用线程池执行异步通知
                        import asyncio
                        import concurrent.futures
                        import threading
                        
                        def run_async_notify():
                            """在新线程中运行异步通知"""
                            # 创建新的事件循环
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                # 运行异步函数
                                loop.run_until_complete(notify_molecular_update(node_id, molecular_data))
                                logger.network(f"[DEBUG] WebSocket更新通知发送成功")
                            finally:
                                loop.close()
                        
                        # 在新线程中执行
                        thread = threading.Thread(target=run_async_notify, daemon=True)
                        thread.start()
                        
                        logger.network(f"[DEBUG] WebSocket更新通知详情:")
                        logger.network(f"  - 节点ID: '{node_id}'")
                        logger.network(f"  - 通知类型: 'update'")
                        logger.network(f"  - 文件名: {molecular_data.get('filename')}")
                        
                    except Exception as e:
                        logger.error(f"WebSocket通知失败: {e}")
                        import traceback
                        traceback.print_exc()
                
                return molecular_data
                
            except Exception as e:
                logger.error(f"存储分子数据时出错: {e}")
                return None
    
    @classmethod
    def get_molecular_data(cls, node_id: str) -> Optional[Dict[str, Any]]:
        """
        从缓存获取分子数据
        
        Args:
            node_id: 节点ID
            
        Returns:
            分子数据字典，不存在返回None
        """
        with CACHE_LOCK:
            try:
                # 🔍 调试日志：追踪数据获取
                logger.debug(f"[DEBUG] 获取分子数据:")
                logger.debug(f"  - 请求的node_id: '{node_id}'")
                logger.debug(f"  - 缓存中的keys: {list(MOLECULAR_DATA_CACHE.keys())}")
                
                if node_id in MOLECULAR_DATA_CACHE:
                    data = MOLECULAR_DATA_CACHE[node_id]
                    
                    # 更新访问统计
                    data["last_accessed"] = time.time()
                    data["access_count"] = data.get("access_count", 0) + 1
                    
                    logger.debug(f"[DEBUG] 找到数据:")
                    logger.debug(f"  - 文件名: {data.get('filename')}")
                    logger.debug(f"  - tab_id: {data.get('tab_id')}")
                    logger.debug(f"  - 访问次数: {data.get('access_count')}")
                    return data
                else:
                    logger.warning(f"[DEBUG] 节点 '{node_id}' 的数据不存在!")
                    logger.warning(f"  - 可用的keys: {list(MOLECULAR_DATA_CACHE.keys())}")
                    return None
                    
            except Exception as e:
                logger.error(f"获取分子数据时出错: {e}")
                return None
    
    @classmethod
    def get_cache_status(cls) -> Dict[str, Any]:
        """
        获取缓存状态统计
        
        Returns:
            缓存状态字典
        """
        with CACHE_LOCK:
            try:
                total_nodes = len(MOLECULAR_DATA_CACHE)
                total_cache_size = sum(len(data.get("content", "")) for data in MOLECULAR_DATA_CACHE.values())
                
                # 构建节点列表（增加tab_id信息）
                nodes = []
                for node_id, data in MOLECULAR_DATA_CACHE.items():
                    nodes.append({
                        "node_id": node_id,
                        "filename": data.get("filename"),
                        "format": data.get("format"),
                        "atoms": data.get("atoms", 0),
                        "tab_id": data.get("tab_id"),  # 🔑 新增：Tab标识
                        "cached_at": data.get("cached_at"),
                        "access_count": data.get("access_count", 0)
                    })
                
                # 按访问时间排序
                nodes.sort(key=lambda x: x.get("access_count", 0), reverse=True)
                
                return {
                    "total_nodes": total_nodes,
                    "total_cache_size": total_cache_size,
                    "nodes": nodes,
                    "status": "active" if total_nodes > 0 else "empty"
                }
                
            except Exception as e:
                logger.error(f"获取缓存状态时出错: {e}")
                return {"error": str(e)}
    
    @classmethod
    def edit_molecular_data(cls, node_id: str, edit_type: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        编辑分子数据（简单版本，用于概念验证）
        
        Args:
            node_id: 节点ID
            edit_type: 编辑类型（'remove_last_atom'）
            **kwargs: 编辑参数
            
        Returns:
            编辑后的数据字典，失败返回None
        """
        with CACHE_LOCK:
            try:
                # 🔧 调试：显示缓存中的所有节点ID
                logger.debug(f"[DEBUG] 编辑分子数据:")
                logger.debug(f"  - 目标node_id: '{node_id}'")
                logger.debug(f"  - 编辑类型: {edit_type}")
                logger.debug(f"  - 缓存中的节点ID列表: {list(MOLECULAR_DATA_CACHE.keys())}")
                
                if node_id not in MOLECULAR_DATA_CACHE:
                    logger.warning(f"节点 {node_id} 的数据不存在，无法编辑")
                    logger.warning(f"可用的节点ID: {list(MOLECULAR_DATA_CACHE.keys())}")
                    return None
                
                molecular_data = MOLECULAR_DATA_CACHE[node_id]
                original_content = molecular_data.get("content", "")
                
                if edit_type == "remove_last_atom":
                    # 🧪 简单编辑：删除PDB中最后一个原子
                    logger.molecular(f"开始编辑: {edit_type}, 原始内容长度: {len(original_content)}")
                    edited_content = cls._remove_last_atom_from_pdb(original_content)
                    logger.molecular(f"编辑完成: 新内容长度: {len(edited_content)}")
                    
                    if edited_content != original_content:
                        # 更新数据
                        molecular_data["content"] = edited_content
                        molecular_data["atoms"] = cls._simple_atom_count(edited_content, molecular_data.get("format", ""))
                        molecular_data["last_edited"] = time.time()
                        molecular_data["edit_history"] = molecular_data.get("edit_history", [])
                        molecular_data["edit_history"].append({
                            "type": edit_type,
                            "timestamp": time.time(),
                            "description": "删除最后一个原子"
                        })
                        
                        logger.success(f"编辑成功: 节点 {node_id} 删除最后一个原子")
                        
                        # 🚀 发送WebSocket编辑通知（改进的安全调用）
                        if WEBSOCKET_NOTIFY_AVAILABLE:
                            try:
                                edit_info = {
                                    "edit_type": edit_type,
                                    "description": "删除最后一个原子",
                                    "atoms_count": molecular_data["atoms"],
                                    "timestamp": time.time()
                                }
                                
                                # 使用线程池执行异步通知
                                import asyncio
                                import threading
                                
                                def run_async_notify():
                                    """在新线程中运行异步通知"""
                                    # 创建新的事件循环
                                    loop = asyncio.new_event_loop()
                                    asyncio.set_event_loop(loop)
                                    try:
                                        # 运行异步函数
                                        loop.run_until_complete(notify_molecular_edit(node_id, edit_info))
                                        logger.network(f"[DEBUG] WebSocket编辑通知发送成功")
                                    finally:
                                        loop.close()
                                
                                # 在新线程中执行
                                thread = threading.Thread(target=run_async_notify, daemon=True)
                                thread.start()
                                
                                logger.network(f"[DEBUG] WebSocket编辑通知详情:")
                                logger.network(f"  - 节点ID: '{node_id}'")
                                logger.network(f"  - 通知类型: 'edit'")
                                logger.network(f"  - 编辑类型: {edit_type}")
                                
                            except Exception as e:
                                logger.error(f"WebSocket编辑通知失败: {e}")
                                import traceback
                                traceback.print_exc()
                        
                        return molecular_data
                    else:
                        logger.warning(f"编辑无效果: 节点 {node_id}")
                        return None
                        
                else:
                    logger.warning(f"不支持的编辑类型: {edit_type}")
                    return None
                    
            except Exception as e:
                logger.error(f"编辑分子数据时出错: {e}")
                return None
    
    @classmethod
    def clear_cache(cls, node_id: str = None) -> bool:
        """
        清除缓存数据（调试用）
        
        Args:
            node_id: 指定节点ID，None则清除所有
            
        Returns:
            是否成功
        """
        with CACHE_LOCK:
            try:
                if node_id:
                    if node_id in MOLECULAR_DATA_CACHE:
                        del MOLECULAR_DATA_CACHE[node_id]
                        logger.storage(f"清除节点 {node_id} 的缓存")
                        return True
                    else:
                        logger.warning(f"节点 {node_id} 不存在")
                        return False
                else:
                    MOLECULAR_DATA_CACHE.clear()
                    logger.storage("清除所有缓存")
                    return True
                    
            except Exception as e:
                logger.error(f"清除缓存时出错: {e}")
                return False
    
    # ====================================================================================================
    # 简化的辅助函数 - 只保留必需的
    # ====================================================================================================
    
    @staticmethod
    def _detect_format(filename: str) -> str:
        """简单的格式检测"""
        ext = filename.lower().split('.')[-1] if '.' in filename else ""
        return ext if ext in ['pdb', 'mol', 'sdf', 'xyz', 'mol2', 'cif', 'gro'] else "unknown"
    
    @staticmethod
    def _get_format_name(file_format: str) -> str:
        """获取格式全名"""
        format_names = {
            "pdb": "Protein Data Bank",
            "mol": "MDL Molfile", 
            "sdf": "Structure Data File",
            "xyz": "XYZ Format",
            "mol2": "Tripos MOL2",
            "cif": "Crystallographic Information File",
            "gro": "GROMACS Format"
        }
        return format_names.get(file_format, "Unknown Format")
    
    @staticmethod
    def _simple_atom_count(content: str, file_format: str) -> int:
        """简单的原子计数（不做复杂分析）"""
        try:
            if file_format == "pdb":
                return content.count("ATOM") + content.count("HETATM")
            elif file_format in ["mol", "sdf"]:
                lines = content.split('\n')
                if len(lines) > 3:
                    counts_line = lines[3].split()
                    return int(counts_line[0]) if counts_line else 0
            elif file_format == "xyz":
                lines = content.split('\n')
                return int(lines[0]) if lines and lines[0].isdigit() else 0
            else:
                # 其他格式的简单估算
                return len([line for line in content.split('\n') if line.strip() and not line.startswith('#')])
        except:
            return 0
    
    @staticmethod
    def _save_to_filesystem(filename: str, folder: str, content: str, node_id: str = None):
        """
        保存到文件系统（修复版本） - 添加节点ID避免重名文件冲突
        
        Args:
            filename: 原始文件名
            folder: 存储文件夹
            content: 文件内容
            node_id: 节点ID，用于生成唯一文件名
        """
        try:
            # 获取ComfyUI的input目录
            input_dir = folder_paths.get_input_directory()
            target_dir = os.path.join(input_dir, folder)
            
            # 确保目录存在
            os.makedirs(target_dir, exist_ok=True)
            
            # 🔑 修复：为重名文件添加节点ID后缀，避免覆盖
            if node_id:
                # 分离文件名和扩展名
                name_parts = filename.rsplit('.', 1)
                if len(name_parts) == 2:
                    name, ext = name_parts
                    # 提取节点数字部分作为后缀
                    node_suffix = node_id.split('_node_')[-1] if '_node_' in node_id else node_id[-3:]
                    unique_filename = f"{name}_node{node_suffix}.{ext}"
                else:
                    # 没有扩展名的情况
                    node_suffix = node_id.split('_node_')[-1] if '_node_' in node_id else node_id[-3:]
                    unique_filename = f"{filename}_node{node_suffix}"
                
                logger.storage(f"[DEBUG] 文件重名保护:")
                logger.storage(f"  - 原始文件名: {filename}")
                logger.storage(f"  - 节点ID: {node_id}")
                logger.storage(f"  - 唯一文件名: {unique_filename}")
            else:
                unique_filename = filename
            
            # 写入文件（使用唯一文件名）
            file_path = os.path.join(target_dir, unique_filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            logger.storage(f"文件已保存: {file_path}")
            
        except Exception as e:
            logger.warning(f"文件系统保存失败: {e}")
            raise
    
    @staticmethod
    def _remove_last_atom_from_pdb(content: str) -> str:
        """
        从PDB内容中删除最后一个原子（简单编辑功能）
        
        Args:
            content: PDB文件内容
            
        Returns:
            编辑后的PDB内容
        """
        try:
            lines = content.split('\n')
            logger.molecular(f"解析PDB: 总行数 {len(lines)}")
            
            # 找到所有原子行的索引
            atom_line_indices = []
            for i, line in enumerate(lines):
                if line.startswith('ATOM') or line.startswith('HETATM'):
                    atom_line_indices.append(i)
            
            logger.molecular(f"找到 {len(atom_line_indices)} 个原子行")
            
            if not atom_line_indices:
                logger.warning(f"没有找到ATOM或HETATM行，无法删除原子")
                return content
            
            # 删除最后一个原子行
            last_atom_index = atom_line_indices[-1]
            removed_line = lines[last_atom_index]
            logger.molecular(f"删除第 {last_atom_index+1} 行原子: {removed_line[:50]}...")
            
            # 创建新的行列表，跳过最后一个原子行
            result_lines = []
            for i, line in enumerate(lines):
                if i != last_atom_index:
                    result_lines.append(line)
            
            result_content = '\n'.join(result_lines)
            logger.molecular(f"编辑完成: {len(lines)} → {len(result_lines)} 行")
            
            return result_content
            
        except Exception as e:
            logger.error(f"删除原子失败: {e}")
            return content  # 返回原始内容
    


# ====================================================================================================
# 便捷全局函数 - 简化版本
# ====================================================================================================

def store_molecular_data(node_id: str, filename: str, folder: str = "molecules", content: str = None):
    """便捷函数 - 存储分子数据"""
    return MolecularDataManager.store_molecular_data(node_id, filename, folder, content)

def get_molecular_data(node_id: str):
    """便捷函数 - 获取分子数据"""
    return MolecularDataManager.get_molecular_data(node_id)

def get_cache_status():
    """便捷函数 - 获取缓存状态"""
    return MolecularDataManager.get_cache_status()

def clear_cache(node_id: str = None):
    """便捷函数 - 清除缓存"""
    return MolecularDataManager.clear_cache(node_id)

def edit_molecular_data(node_id: str, edit_type: str, **kwargs):
    """便捷函数 - 编辑分子数据"""
    return MolecularDataManager.edit_molecular_data(node_id, edit_type, **kwargs)


# ====================================================================================================
# 🔑 Active Tab ID 管理功能
# ====================================================================================================

def update_active_tab_id(tab_id: str):
    """
    [已废弃] 更新活跃的tab_id
    
    现在使用前端传入的_alchem_node_id，不再需要全局状态
    """
    logger.debug(f"🔧 update_active_tab_id已废弃，传入的tab_id: {tab_id} 将被忽略")
    pass

def get_active_tab_id() -> Optional[str]:
    """
    [已废弃] 获取当前活跃的tab_id
    
    现在使用前端传入的_alchem_node_id，不再需要全局状态
    """
    logger.debug(f"🔧 get_active_tab_id已废弃，返回None")
    return None

def extract_tab_id_from_node_id(node_id: str) -> Optional[str]:
    """
    从节点ID中提取tab_id
    
    Args:
        node_id: 格式如 "workflow_nv6wm_node_6"
        
    Returns:
        提取的tab_id，如 "workflow_nv6wm"
    """
    if '_node_' in node_id:
        return node_id.split('_node_')[0]
    return None