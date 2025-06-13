"""
🧪 ALCHEM_PropBtn 简化内存管理模块

专注于核心功能：分子数据的存储和查询
删除了过度设计的分析功能和未使用的活跃节点机制
"""

import os
import time
import threading
import logging
from typing import Dict, Any, Optional
import folder_paths

# 设置日志
logger = logging.getLogger(__name__)

# 全局分子数据缓存 - 简化版本
MOLECULAR_DATA_CACHE: Dict[str, Dict[str, Any]] = {}

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
                    logger.error("🚨 存储失败：节点ID和文件名不能为空")
                    return None
                
                if not content:
                    logger.error("🚨 存储失败：文件内容不能为空")
                    return None
                
                logger.info(f"🧪 存储分子数据: 节点{node_id}, 文件{filename}")
                
                # 检测基本格式信息
                file_format = cls._detect_format(filename)
                
                # 创建存储数据结构
                molecular_data = {
                    "node_id": node_id,
                    "filename": filename,
                    "folder": folder,
                    "content": content,
                    "format": file_format,
                    "format_name": cls._get_format_name(file_format),
                    
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
                
                # 尝试保存到文件系统（用于持久化）
                try:
                    cls._save_to_filesystem(filename, folder, content)
                except Exception as e:
                    logger.warning(f"⚠️ 文件系统保存失败: {e}")
                
                logger.info(f"✅ 分子数据存储成功: {filename} -> 节点 {node_id}")
                return molecular_data
                
            except Exception as e:
                logger.exception(f"🚨 存储分子数据时出错: {e}")
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
                if node_id in MOLECULAR_DATA_CACHE:
                    data = MOLECULAR_DATA_CACHE[node_id]
                    
                    # 更新访问统计
                    data["last_accessed"] = time.time()
                    data["access_count"] = data.get("access_count", 0) + 1
                    
                    logger.debug(f"🔍 获取分子数据: 节点{node_id}, 文件{data.get('filename')}")
                    return data
                else:
                    logger.debug(f"⚠️ 节点 {node_id} 的数据不存在")
                    return None
                    
            except Exception as e:
                logger.exception(f"🚨 获取分子数据时出错: {e}")
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
                
                # 构建节点列表（简化版本）
                nodes = []
                for node_id, data in MOLECULAR_DATA_CACHE.items():
                    nodes.append({
                        "node_id": node_id,
                        "filename": data.get("filename"),
                        "format": data.get("format"),
                        "atoms": data.get("atoms", 0),
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
                logger.exception(f"🚨 获取缓存状态时出错: {e}")
                return {"error": str(e)}
    
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
                        logger.info(f"🗑️ 清除节点 {node_id} 的缓存")
                        return True
                    else:
                        logger.warning(f"⚠️ 节点 {node_id} 不存在")
                        return False
                else:
                    MOLECULAR_DATA_CACHE.clear()
                    logger.info("🗑️ 清除所有缓存")
                    return True
                    
            except Exception as e:
                logger.exception(f"🚨 清除缓存时出错: {e}")
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
    def _save_to_filesystem(filename: str, folder: str, content: str):
        """保存到文件系统（简化版本）"""
        try:
            # 获取ComfyUI的input目录
            input_dir = folder_paths.get_input_directory()
            target_dir = os.path.join(input_dir, folder)
            
            # 确保目录存在
            os.makedirs(target_dir, exist_ok=True)
            
            # 写入文件
            file_path = os.path.join(target_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            logger.debug(f"💾 文件已保存: {file_path}")
            
        except Exception as e:
            logger.warning(f"⚠️ 文件系统保存失败: {e}")
            raise


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