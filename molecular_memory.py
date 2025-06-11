import os
import json
import time
import threading
import hashlib
import logging
from typing import Dict, Any, Optional, List
import folder_paths

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🎯 全局分子数据缓存（模仿rdkit_molstar的MOLECULE_CACHE）
MOLECULAR_DATA_CACHE: Dict[str, Dict[str, Any]] = {}

# 活跃节点管理（类似rdkit_molstar的ACTIVE_NODE）
ACTIVE_MOLECULAR_NODE = {
    "node_id": None,
    "instance_id": None,
    "molecular_data": None,
    "last_modified": None,
    "editor_id": "system"
}

# WebSocket客户端列表（用于实时更新通知）
WS_CLIENTS: List = []

# 线程锁，确保缓存操作的线程安全
CACHE_LOCK = threading.Lock()

class MolecularDataManager:
    """
    🧪 分子数据内存管理器
    
    负责管理分子数据的存储、检索和缓存，模仿rdkit_molstar的机制
    提供线程安全的操作和实时更新通知
    """
    
    @classmethod
    def store_molecular_data(cls, node_id: str, filename: str, folder: str = "molecules", 
                           instance_id: str = None) -> Optional[Dict[str, Any]]:
        """
        在节点执行时将分子数据存储到全局缓存
        
        Args:
            node_id: ComfyUI节点的唯一ID
            filename: 分子文件名
            folder: 存储文件夹（默认molecules）
            instance_id: 节点实例ID
            
        Returns:
            存储的分子数据对象，如果失败则返回None
        """
        try:
            with CACHE_LOCK:
                logger.info(f"🧪 开始存储分子数据 - 节点ID: {node_id}, 文件: {filename}")
                
                # 1. 构建文件路径
                input_dir = folder_paths.get_input_directory()
                file_path = os.path.join(input_dir, folder, filename)
                
                if not os.path.exists(file_path):
                    logger.error(f"🚨 分子文件不存在: {file_path}")
                    return None
                
                # 2. 读取和解析文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 3. 创建分子数据对象
                molecular_data = {
                    # 基本信息
                    "filename": filename,
                    "folder": folder,
                    "node_id": node_id,
                    "instance_id": instance_id,
                    
                    # 文件内容和格式
                    "content": content,
                    "format": cls._detect_format(filename),
                    "format_name": cls._get_format_name(filename),
                    
                    # 解析的结构信息
                    "atoms": cls._count_atoms(content),
                    "bonds": cls._count_bonds(content),
                    "coordinates": cls._extract_coordinates(content),
                    "metadata": cls._extract_metadata(content),
                    
                    # 文件统计信息
                    "file_stats": {
                        "size": os.path.getsize(file_path),
                        "modified": os.path.getmtime(file_path),
                        "lines": len(content.split('\n')),
                        "chars": len(content)
                    },
                    
                    # 缓存信息
                    "cached_at": time.time(),
                    "access_count": 0,
                    "last_accessed": time.time(),
                    
                    # 状态标记
                    "is_active": False,
                    "processing_complete": True
                }
                
                # 4. 🎯 存储到全局缓存（类似rdkit_molstar）
                global MOLECULAR_DATA_CACHE
                cache_key = str(node_id)
                MOLECULAR_DATA_CACHE[cache_key] = molecular_data
                
                logger.info(f"🚀 分子数据已缓存 - 节点ID: {node_id}")
                logger.info(f"   - 文件: {filename}")
                logger.info(f"   - 格式: {molecular_data['format_name']}")
                logger.info(f"   - 原子数: {molecular_data['atoms']}")
                logger.info(f"   - 文件大小: {molecular_data['file_stats']['size']} 字节")
                logger.info(f"   - 缓存键: {cache_key}")
                
                # 5. 通知监听器（如果有的话）
                cls._notify_cache_update(node_id, molecular_data, "stored")
                
                return molecular_data
                
        except Exception as e:
            logger.error(f"🚨 存储分子数据时出错: {e}")
            import traceback
            logger.error(f"错误详情: {traceback.format_exc()}")
            return None
    
    @classmethod
    def get_molecular_data(cls, node_id: str) -> Optional[Dict[str, Any]]:
        """
        从全局缓存获取分子数据
        
        Args:
            node_id: 节点ID
            
        Returns:
            分子数据对象，如果不存在则返回None
        """
        try:
            with CACHE_LOCK:
                global MOLECULAR_DATA_CACHE
                cache_key = str(node_id)
                
                if cache_key in MOLECULAR_DATA_CACHE:
                    molecular_data = MOLECULAR_DATA_CACHE[cache_key]
                    # 更新访问统计
                    molecular_data["access_count"] += 1
                    molecular_data["last_accessed"] = time.time()
                    
                    logger.info(f"🔍 从缓存获取分子数据 - 节点ID: {node_id}")
                    logger.info(f"   - 文件: {molecular_data['filename']}")
                    logger.info(f"   - 访问次数: {molecular_data['access_count']}")
                    
                    return molecular_data
                else:
                    logger.warning(f"⚠️ 未找到节点 {node_id} 的缓存数据")
                    return None
                    
        except Exception as e:
            logger.error(f"🚨 获取分子数据时出错: {e}")
            return None
    
    @classmethod
    def get_cache_status(cls) -> Dict[str, Any]:
        """
        获取缓存状态信息
        
        Returns:
            缓存状态统计信息
        """
        try:
            with CACHE_LOCK:
                global MOLECULAR_DATA_CACHE
                
                total_nodes = len(MOLECULAR_DATA_CACHE)
                total_size = 0
                node_info = []
                
                for node_id, data in MOLECULAR_DATA_CACHE.items():
                    data_size = len(str(data))
                    total_size += data_size
                    
                    node_info.append({
                        "node_id": node_id,
                        "filename": data.get("filename", "unknown"),
                        "format": data.get("format", "unknown"),
                        "atoms": data.get("atoms", 0),
                        "size": data_size,
                        "cached_at": data.get("cached_at", 0),
                        "access_count": data.get("access_count", 0),
                        "is_active": data.get("is_active", False)
                    })
                
                return {
                    "total_nodes": total_nodes,
                    "total_cache_size": total_size,
                    "nodes": node_info,
                    "timestamp": time.time()
                }
                
        except Exception as e:
            logger.error(f"🚨 获取缓存状态时出错: {e}")
            return {"error": str(e)}
    
    @classmethod
    def clear_cache(cls, node_id: str = None) -> bool:
        """
        清除缓存数据
        
        Args:
            node_id: 如果指定，只清除该节点的缓存；否则清除所有缓存
            
        Returns:
            是否成功
        """
        try:
            with CACHE_LOCK:
                global MOLECULAR_DATA_CACHE
                
                if node_id:
                    cache_key = str(node_id)
                    if cache_key in MOLECULAR_DATA_CACHE:
                        del MOLECULAR_DATA_CACHE[cache_key]
                        logger.info(f"🗑️ 已清除节点 {node_id} 的缓存数据")
                        cls._notify_cache_update(node_id, None, "cleared")
                    else:
                        logger.warning(f"⚠️ 节点 {node_id} 的缓存数据不存在")
                else:
                    MOLECULAR_DATA_CACHE.clear()
                    logger.info("🗑️ 已清除所有分子数据缓存")
                    cls._notify_cache_update("all", None, "cleared_all")
                
                return True
                
        except Exception as e:
            logger.error(f"🚨 清除缓存时出错: {e}")
            return False
    
    @classmethod
    def set_active_node(cls, node_id: str) -> bool:
        """
        设置活跃节点
        
        Args:
            node_id: 要设置为活跃的节点ID
            
        Returns:
            是否成功
        """
        try:
            with CACHE_LOCK:
                global MOLECULAR_DATA_CACHE, ACTIVE_MOLECULAR_NODE
                
                cache_key = str(node_id)
                if cache_key not in MOLECULAR_DATA_CACHE:
                    logger.warning(f"⚠️ 节点 {node_id} 的数据不在缓存中，无法设置为活跃")
                    return False
                
                # 清除之前的活跃状态
                if ACTIVE_MOLECULAR_NODE["node_id"]:
                    prev_key = str(ACTIVE_MOLECULAR_NODE["node_id"])
                    if prev_key in MOLECULAR_DATA_CACHE:
                        MOLECULAR_DATA_CACHE[prev_key]["is_active"] = False
                
                # 设置新的活跃节点
                MOLECULAR_DATA_CACHE[cache_key]["is_active"] = True
                ACTIVE_MOLECULAR_NODE.update({
                    "node_id": node_id,
                    "molecular_data": MOLECULAR_DATA_CACHE[cache_key],
                    "last_modified": time.time(),
                    "editor_id": "system"
                })
                
                logger.info(f"🎯 节点 {node_id} 已设置为活跃节点")
                cls._notify_cache_update(node_id, MOLECULAR_DATA_CACHE[cache_key], "activated")
                
                return True
                
        except Exception as e:
            logger.error(f"🚨 设置活跃节点时出错: {e}")
            return False
    
    @classmethod
    def get_active_node(cls) -> Optional[Dict[str, Any]]:
        """
        获取当前活跃节点信息
        
        Returns:
            活跃节点信息，如果没有则返回None
        """
        global ACTIVE_MOLECULAR_NODE
        
        if ACTIVE_MOLECULAR_NODE["node_id"]:
            return {**ACTIVE_MOLECULAR_NODE}  # 返回副本
        return None
    
    # 🔧 内部辅助方法
    
    @classmethod
    def _detect_format(cls, filename: str) -> str:
        """检测文件格式"""
        ext = os.path.splitext(filename)[1].lower()
        format_map = {
            '.pdb': 'PDB', '.mol': 'MOL', '.sdf': 'SDF', 
            '.xyz': 'XYZ', '.mol2': 'MOL2', '.cif': 'CIF',
            '.fasta': 'FASTA', '.fa': 'FASTA', '.gro': 'GRO'
        }
        return format_map.get(ext, 'Unknown')
    
    @classmethod
    def _get_format_name(cls, filename: str) -> str:
        """获取格式全名"""
        ext = os.path.splitext(filename)[1].lower()
        name_map = {
            '.pdb': 'Protein Data Bank',
            '.mol': 'MDL Molfile',
            '.sdf': 'Structure Data File',
            '.xyz': 'XYZ Coordinates',
            '.mol2': 'Tripos Mol2',
            '.cif': 'Crystallographic Information File',
            '.fasta': 'FASTA Sequence',
            '.fa': 'FASTA Sequence',
            '.gro': 'GROMACS'
        }
        return name_map.get(ext, f'Unknown ({ext})')
    
    @classmethod
    def _count_atoms(cls, content: str) -> int:
        """计算原子数量"""
        lines = content.split('\n')
        
        # PDB格式
        if any(line.startswith('HEADER') for line in lines[:5]):
            return len([line for line in lines if line.startswith('ATOM') or line.startswith('HETATM')])
        
        # XYZ格式
        elif content.strip().split('\n')[0].strip().isdigit():
            try:
                return int(content.strip().split('\n')[0])
            except:
                return 0
        
        # MOL/SDF格式
        elif len(lines) >= 4:
            try:
                counts_line = lines[3]
                atom_count = int(counts_line[:3].strip())
                return atom_count
            except:
                pass
        
        # 默认计算非空行数
        return len([line for line in lines if line.strip() and not line.startswith('#')])
    
    @classmethod
    def _count_bonds(cls, content: str) -> int:
        """计算键数量"""
        # PDB格式的CONECT记录
        conect_lines = [line for line in content.split('\n') if line.startswith('CONECT')]
        
        # MOL/SDF格式的键信息
        if not conect_lines:
            lines = content.split('\n')
            if len(lines) >= 4:
                try:
                    counts_line = lines[3]
                    bond_count = int(counts_line[3:6].strip())
                    return bond_count
                except:
                    pass
        
        return len(conect_lines)
    
    @classmethod
    def _extract_coordinates(cls, content: str) -> List[List[float]]:
        """提取原子坐标"""
        coordinates = []
        
        for line in content.split('\n'):
            if line.startswith('ATOM') or line.startswith('HETATM'):
                try:
                    x = float(line[30:38].strip())
                    y = float(line[38:46].strip()) 
                    z = float(line[46:54].strip())
                    coordinates.append([x, y, z])
                except:
                    continue
            elif line.strip() and not line.startswith('#') and len(line.split()) >= 4:
                # XYZ或其他格式
                try:
                    parts = line.split()
                    if len(parts) >= 4:
                        x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                        coordinates.append([x, y, z])
                except:
                    continue
        
        return coordinates
    
    @classmethod
    def _extract_metadata(cls, content: str) -> Dict[str, Any]:
        """提取元数据"""
        metadata = {}
        
        for line in content.split('\n')[:20]:  # 只检查前20行
            if line.startswith('HEADER'):
                metadata['header'] = line[10:].strip()
            elif line.startswith('TITLE'):
                metadata['title'] = line[10:].strip()
            elif line.startswith('COMPND'):
                metadata['compound'] = line[10:].strip()
            elif line.startswith('AUTHOR'):
                metadata['author'] = line[10:].strip()
            elif line.startswith('REMARK'):
                if 'remarks' not in metadata:
                    metadata['remarks'] = []
                metadata['remarks'].append(line[10:].strip())
            elif line.startswith('>'):  # FASTA或SDF注释
                metadata['comment'] = line[1:].strip()
        
        return metadata
    
    @classmethod
    def _notify_cache_update(cls, node_id: str, molecular_data: Optional[Dict[str, Any]], action: str):
        """通知缓存更新（为将来的WebSocket支持预留）"""
        try:
            # 这里可以添加WebSocket通知逻辑
            logger.debug(f"🔔 缓存更新通知 - 节点: {node_id}, 操作: {action}")
            
            # 预留：发送WebSocket消息给前端
            # if WS_CLIENTS:
            #     message = {
            #         "type": "molecular_cache_updated",
            #         "node_id": node_id,
            #         "action": action,
            #         "timestamp": time.time()
            #     }
            #     # 发送给所有连接的客户端
            
        except Exception as e:
            logger.error(f"🚨 发送缓存更新通知时出错: {e}")


# 🌟 全局管理器实例
molecular_memory = MolecularDataManager()

# 🔧 便捷函数（兼容现有代码）
def store_molecular_data(node_id: str, filename: str, folder: str = "molecules", instance_id: str = None):
    """便捷的存储函数"""
    return molecular_memory.store_molecular_data(node_id, filename, folder, instance_id)

def get_molecular_data(node_id: str):
    """便捷的获取函数"""
    return molecular_memory.get_molecular_data(node_id)

def get_cache_status():
    """便捷的状态获取函数"""
    return molecular_memory.get_cache_status()

def clear_cache(node_id: str = None):
    """便捷的清除函数"""
    return molecular_memory.clear_cache(node_id)

def set_active_node(node_id: str):
    """便捷的活跃节点设置函数"""
    return molecular_memory.set_active_node(node_id)

def get_active_node():
    """便捷的活跃节点获取函数"""
    return molecular_memory.get_active_node() 