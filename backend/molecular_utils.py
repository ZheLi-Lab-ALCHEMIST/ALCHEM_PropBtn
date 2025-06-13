"""
🧪 分子数据工具模块 (molecular_utils.py)

提供统一的分子数据获取和处理工具函数，供节点使用。
这是方案B的核心实现：节点主动获取数据，而不依赖execution_hook。

主要功能：
- 智能分子数据获取：自动判断输入是文件名还是内容
- 内存数据检索：从后端内存获取缓存的分子数据
- 文件系统回退：当内存没有数据时从文件系统读取
- 数据验证和格式检测：确保获取到的是有效的分子数据
"""

import os
import logging
import hashlib
import time
from typing import Optional, Dict, Any, Tuple

logger = logging.getLogger(__name__)

def get_molecular_content(input_value: str, node_id: Optional[str] = None, fallback_to_file: bool = True) -> Tuple[str, Dict[str, Any]]:
    """
    🎯 核心工具函数：智能获取分子数据内容
    
    Args:
        input_value: 输入值（可能是文件名或已经是内容）
        node_id: 当前节点ID（可选，用于调试）
        fallback_to_file: 是否回退到文件系统（默认True）
        
    Returns:
        Tuple[content, metadata]: (分子内容字符串, 元数据字典)
        
    工作原理：
    1. 智能判断输入是文件名还是内容
    2. 如果是文件名，从内存查找并获取内容
    3. 如果内存没有，根据fallback_to_file决定是否从文件系统读取
    4. 返回内容和详细的元数据信息
    """
    try:
        # 步骤1：智能判断输入类型
        content_type, is_filename = _detect_input_type(input_value)
        
        metadata = {
            "node_id": node_id or "unknown",
            "input_type": content_type,
            "is_filename": is_filename,
            "processing_time": time.time(),
            "source": "unknown",
            "success": False
        }
        
        logger.debug(f"🔍 分子数据获取 - 节点ID: {node_id}")
        logger.debug(f"   输入类型: {content_type}")
        logger.debug(f"   是否文件名: {is_filename}")
        
        # 步骤2：如果输入已经是内容，直接返回
        if not is_filename:
            logger.debug("✅ 输入已经是分子内容，直接返回")
            
            # 分析内容并更新元数据
            content_metadata = _analyze_molecular_content(input_value)
            metadata.update(content_metadata)
            metadata["source"] = "direct_input"
            metadata["success"] = True
            
            return input_value, metadata
        
        # 步骤3：输入是文件名，尝试从内存获取
        filename = str(input_value).strip()
        content = None
        
        try:
            from .molecular_memory import get_cache_status, get_molecular_data
            
            # 查找内存中的同名文件
            cache_status = get_cache_status()
            logger.debug(f"🧠 内存缓存状态: {cache_status.get('total_nodes', 0)} 个节点")
            
            for cached_node in cache_status.get('nodes', []):
                if cached_node.get('filename') == filename:
                    source_node_id = cached_node.get('node_id')
                    logger.debug(f"🔄 找到内存缓存: {filename} (节点 {source_node_id})")
                    
                    source_data = get_molecular_data(source_node_id)
                    if source_data and 'content' in source_data:
                        content = source_data['content']
                        
                        # 更新元数据
                        metadata.update({
                            "source": "memory_cache",
                            "source_node_id": source_node_id,
                            "cached_at": source_data.get('cached_at'),
                            "file_size": len(content),
                            "success": True
                        })
                        
                        # 添加缓存的分析结果
                        cache_metadata = {
                            "format": source_data.get('format'),
                            "format_name": source_data.get('format_name'),
                            "atoms": source_data.get('atoms'),
                            "file_stats": source_data.get('file_stats')
                        }
                        metadata.update(cache_metadata)
                        
                        logger.info(f"✅ 从内存获取分子数据成功: {filename}")
                        logger.debug(f"   来源节点: {source_node_id}")
                        logger.debug(f"   内容长度: {len(content)} 字符")
                        
                        return content, metadata
                        
            logger.debug(f"⚠️ 内存中未找到文件: {filename}")
            
        except Exception as memory_error:
            logger.warning(f"🚨 内存数据获取失败: {memory_error}")
            metadata["memory_error"] = str(memory_error)
        
        # 步骤4：如果内存没有数据，尝试从文件系统读取
        if fallback_to_file:
            logger.debug(f"📁 尝试从文件系统读取: {filename}")
            
            try:
                import folder_paths
                
                # 构建文件路径
                input_dir = folder_paths.get_input_directory()
                molecules_dir = os.path.join(input_dir, 'molecules')
                file_path = os.path.join(molecules_dir, filename)
                
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 分析文件内容
                    content_metadata = _analyze_molecular_content(content)
                    
                    # 更新元数据
                    file_stats = os.stat(file_path)
                    metadata.update({
                        "source": "file_system",
                        "file_path": file_path,
                        "file_size": file_stats.st_size,
                        "file_mtime": file_stats.st_mtime,
                        "success": True
                    })
                    metadata.update(content_metadata)
                    
                    logger.info(f"✅ 从文件系统读取成功: {filename}")
                    logger.debug(f"   文件路径: {file_path}")
                    logger.debug(f"   内容长度: {len(content)} 字符")
                    
                    return content, metadata
                else:
                    logger.warning(f"❌ 文件不存在: {file_path}")
                    metadata["file_error"] = f"文件不存在: {file_path}"
                    
            except Exception as file_error:
                logger.warning(f"🚨 文件系统读取失败: {file_error}")
                metadata["file_error"] = str(file_error)
        
        # 步骤5：所有方法都失败了
        error_msg = f"无法获取分子数据: {filename}"
        logger.error(f"❌ {error_msg}")
        
        metadata.update({
            "source": "none",
            "success": False,
            "error": error_msg
        })
        
        return input_value, metadata  # 返回原始输入
        
    except Exception as e:
        logger.exception(f"🚨 分子数据获取过程中发生异常: {e}")
        
        error_metadata = {
            "node_id": node_id or "unknown",
            "success": False,
            "error": str(e),
            "source": "exception"
        }
        
        return str(input_value), error_metadata


def _detect_input_type(input_value: str) -> Tuple[str, bool]:
    """
    检测输入类型：判断是文件名还是文件内容
    
    Returns:
        Tuple[type_description, is_filename]
    """
    content = str(input_value).strip()
    
    # 判断标准
    if len(content) < 50:  # 很短，可能是文件名
        if '.' in content and not '\n' in content:
            return "filename", True
        else:
            return "short_content", False
    
    # 检查是否包含分子文件特征
    molecular_indicators = [
        'HEADER', 'ATOM', 'HETATM', 'CONECT',  # PDB格式
        '$$$$',  # SDF格式
        '>',  # FASTA格式
        'data_'  # CIF格式
    ]
    
    for indicator in molecular_indicators:
        if indicator in content:
            return "molecular_content", False
    
    # 检查是否有多行结构
    if '\n' in content and len(content.split('\n')) > 3:
        return "multiline_content", False
    
    # 默认认为是文件名
    return "possible_filename", True


def _analyze_molecular_content(content: str) -> Dict[str, Any]:
    """
    分析分子内容，提取格式和统计信息
    """
    try:
        lines = content.split('\n')
        
        analysis = {
            "total_lines": len(lines),
            "content_length": len(content),
            "format": "unknown",
            "format_name": "Unknown"
        }
        
        # PDB格式检测
        if any(line.startswith(('HEADER', 'ATOM', 'HETATM')) for line in lines):
            analysis["format"] = ".pdb"
            analysis["format_name"] = "Protein Data Bank"
            
            # 统计原子数
            atom_lines = [line for line in lines if line.startswith('ATOM')]
            analysis["atoms"] = len(atom_lines)
            
        # SDF格式检测
        elif '$$$$' in content:
            analysis["format"] = ".sdf"
            analysis["format_name"] = "Structure Data Format"
            
            # 尝试解析原子数（SDF格式第4行的前3位）
            if len(lines) >= 4:
                try:
                    atom_count = int(lines[3][:3].strip())
                    analysis["atoms"] = atom_count
                except:
                    pass
                    
        # XYZ格式检测
        elif len(lines) > 0 and lines[0].strip().isdigit():
            analysis["format"] = ".xyz"
            analysis["format_name"] = "XYZ Coordinates"
            
            try:
                analysis["atoms"] = int(lines[0].strip())
            except:
                pass
                
        # FASTA格式检测
        elif content.startswith('>'):
            analysis["format"] = ".fasta"
            analysis["format_name"] = "FASTA Sequence"
            
            sequences = content.count('>')
            analysis["sequences"] = sequences
            
        return analysis
        
    except Exception as e:
        logger.warning(f"分析分子内容时出错: {e}")
        return {
            "total_lines": len(content.split('\n')) if content else 0,
            "content_length": len(content),
            "format": "unknown",
            "format_name": "Unknown",
            "analysis_error": str(e)
        }


def create_molecular_node_function(original_function):
    """
    🎯 装饰器：为节点函数添加自动分子数据获取功能
    
    使用方法：
    @create_molecular_node_function
    def process_molecule(self, molecular_file, other_params):
        # molecular_file 已经自动转换为内容
        return process_content(molecular_file)
    """
    def wrapper(self, *args, **kwargs):
        # 查找molecular相关的参数
        molecular_params = []
        
        # 获取函数的参数名
        import inspect
        sig = inspect.signature(original_function)
        param_names = list(sig.parameters.keys())[1:]  # 跳过self
        
        # 检查哪些参数可能是分子数据
        for i, param_name in enumerate(param_names):
            if 'molecular' in param_name.lower() or 'molecule' in param_name.lower():
                if i < len(args):
                    molecular_params.append((i, param_name, args[i]))
        
        # 转换分子参数
        new_args = list(args)
        for i, param_name, value in molecular_params:
            content, metadata = get_molecular_content(value)
            new_args[i] = content
            
            # 添加元数据到kwargs
            kwargs[f'_{param_name}_metadata'] = metadata
        
        # 调用原始函数
        return original_function(self, *new_args, **kwargs)
    
    return wrapper


# 向后兼容的函数别名
resolve_molecular_input = get_molecular_content  # 别名