"""
ComfyUI执行钩子 - 拦截数据流，从后端内存获取分子数据

这个模块实现了plan2.md中描述的关键机制：
- 拦截ComfyUI的get_input_data函数
- 检测分子输入字段
- 从后端内存直接获取分子内容，而不是读取文件
"""

import os
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# 导入分子内存管理器
try:
    from .molecular_memory import get_molecular_data, MOLECULAR_DATA_CACHE
    MEMORY_AVAILABLE = True
    logger.info("🧪 执行钩子：分子内存管理器加载成功")
except ImportError as e:
    logger.error(f"🚨 执行钩子：分子内存管理器加载失败 - {e}")
    MEMORY_AVAILABLE = False

class MolecularExecutionHook:
    """
    分子数据执行钩子
    
    负责在ComfyUI节点执行时拦截输入数据获取，
    将分子文件路径替换为后端内存中的实际内容
    """
    
    def __init__(self):
        self.original_get_input_data = None
        self.hooked = False
        
    def install_hook(self):
        """安装执行钩子"""
        if not MEMORY_AVAILABLE:
            logger.warning("⚠️ 分子内存管理器不可用，跳过执行钩子安装")
            return False
            
        try:
            # 尝试导入ComfyUI的执行模块
            import execution
            
            # 🔍 调试：检查execution模块的内容
            logger.info(f"🔍 execution模块属性: {dir(execution)}")
            
            # 保存原始函数
            if hasattr(execution, 'get_input_data'):
                self.original_get_input_data = execution.get_input_data
                
                # 替换为我们的钩子函数
                execution.get_input_data = self.hooked_get_input_data
                self.hooked = True
                
                logger.info("🔗 成功安装分子数据执行钩子")
                logger.info(f"🔍 原始函数类型: {type(self.original_get_input_data)}")
                return True
            else:
                logger.warning("⚠️ 无法找到ComfyUI的get_input_data函数")
                logger.warning(f"🔍 可用属性: {[attr for attr in dir(execution) if not attr.startswith('_')]}")
                return False
                
        except Exception as e:
            logger.error(f"🚨 安装执行钩子时出错: {e}")
            return False
    
    def uninstall_hook(self):
        """卸载执行钩子"""
        if self.hooked and self.original_get_input_data:
            try:
                import execution
                execution.get_input_data = self.original_get_input_data
                self.hooked = False
                logger.info("🔗 成功卸载分子数据执行钩子")
            except Exception as e:
                logger.error(f"🚨 卸载执行钩子时出错: {e}")
    
    def hooked_get_input_data(self, inputs, class_def, unique_id, outputs=None, prompt=None, extra_pnginfo=None):
        """
        钩子函数：拦截输入数据获取
        
        检查是否有分子输入字段，如果有则从后端内存获取内容
        """
        logger.debug(f"🔗 执行钩子被调用 - 节点ID: {unique_id}, 类: {getattr(class_def, '__name__', 'unknown')}")
        
        try:
            # 🎯 检查是否是分子相关的节点
            node_class_name = class_def.__name__ if hasattr(class_def, '__name__') else str(class_def)
            
            # 调用原始函数获取基础数据
            if self.original_get_input_data:
                input_data = self.original_get_input_data(inputs, class_def, unique_id, outputs, prompt, extra_pnginfo)
            else:
                # 如果没有原始函数，回退到基础实现
                input_data = self._fallback_get_input_data(inputs, class_def, unique_id)
            
            # 🧪 检查并处理分子输入
            modified_data = self._process_molecular_inputs(input_data, unique_id, node_class_name, class_def)
            
            return modified_data
            
        except Exception as e:
            logger.error(f"🚨 钩子函数执行出错: {e}")
            # 出错时回退到原始函数
            if self.original_get_input_data:
                return self.original_get_input_data(inputs, class_def, unique_id, outputs, prompt, extra_pnginfo)
            else:
                return self._fallback_get_input_data(inputs, class_def, unique_id)
    
    def _process_molecular_inputs(self, input_data: Dict[str, Any], unique_id: str, node_class_name: str, class_def=None) -> Dict[str, Any]:
        """
        处理分子输入数据
        
        检查input_data中是否有分子文件路径，如果有则从后端内存获取内容替换
        """
        if not isinstance(input_data, dict):
            return input_data
        
        modified_data = input_data.copy()
        modifications_made = False
        
        # 🔧 总是添加节点ID信息，方便调试
        modified_data['_alchem_node_id'] = unique_id
        
        # 🔍 遍历所有输入字段
        for field_name, field_value in input_data.items():
            if self._is_molecular_field(field_name, field_value, node_class_name, class_def):
                # 🚀 尝试从后端内存获取分子数据
                molecular_content = self._get_molecular_content_from_memory(unique_id, field_name, field_value)
                
                if molecular_content is not None:
                    modified_data[field_name] = molecular_content
                    # 🔧 同时传递节点ID信息给节点函数
                    modified_data['_alchem_node_id'] = unique_id
                    modifications_made = True
                    logger.info(f"🧪 节点 {unique_id} 的字段 '{field_name}' 已从后端内存获取分子数据")
                    logger.debug(f"   原始值: {field_value}")
                    logger.debug(f"   内容长度: {len(molecular_content)} 字符")
                else:
                    # 🔧 如果直接查找失败，尝试按文件名查找并复制数据
                    logger.warning(f"🔍 节点 {unique_id} 直接查找失败，尝试按文件名查找: {field_value}")
                    
                    try:
                        from .molecular_memory import get_cache_status, get_molecular_data, store_molecular_data
                        cache_status = get_cache_status()
                        
                        # 查找同名文件
                        for cached_node in cache_status.get('nodes', []):
                            if cached_node.get('filename') == field_value:
                                source_node_id = cached_node.get('node_id')
                                logger.info(f"🔄 找到同名文件缓存，源节点: {source_node_id}")
                                
                                # 获取源数据
                                source_data = get_molecular_data(source_node_id)
                                if source_data and 'content' in source_data:
                                    # 复制到当前节点
                                    store_molecular_data(
                                        node_id=unique_id,
                                        filename=field_value,
                                        folder=source_data.get('folder', 'molecules'),
                                        content=source_data['content']
                                    )
                                    
                                    # 使用复制的内容
                                    modified_data[field_name] = source_data['content']
                                    # 🔧 同时传递节点ID信息给节点函数
                                    modified_data['_alchem_node_id'] = unique_id
                                    modifications_made = True
                                    logger.info(f"✅ 数据复制成功: {source_node_id} → {unique_id}")
                                    logger.debug(f"   内容长度: {len(source_data['content'])} 字符")
                                break
                    except Exception as copy_error:
                        logger.error(f"🚨 数据复制失败: {copy_error}")
        
        if modifications_made:
            logger.info(f"🎯 节点 {unique_id} ({node_class_name}) 已应用分子数据内存优化")
        
        return modified_data
    
    def _is_molecular_field(self, field_name: str, field_value: Any, node_class_name: str, class_def=None) -> bool:
        """
        判断是否是分子输入字段
        
        🔧 改进检测逻辑：检查字段的INPUT_TYPES属性，而不是硬编码类名
        """
        # 🎯 方法1：检查字段的INPUT_TYPES属性（最准确）
        if class_def and hasattr(class_def, 'INPUT_TYPES'):
            try:
                input_types = class_def.INPUT_TYPES()
                required = input_types.get('required', {})
                optional = input_types.get('optional', {})
                
                # 检查字段是否有分子相关属性
                for field_dict in [required, optional]:
                    if field_name in field_dict:
                        field_config = field_dict[field_name]
                        if isinstance(field_config, (list, tuple)) and len(field_config) >= 2:
                            field_attrs = field_config[1] if isinstance(field_config[1], dict) else {}
                            
                            # 检查是否有分子相关属性
                            molecular_attrs = [
                                'molecular_upload', 'molstar_3d_display', 
                                'custom_text_upload', 'molecular_file'
                            ]
                            
                            for attr in molecular_attrs:
                                if field_attrs.get(attr) is True:
                                    logger.debug(f"🎯 字段 '{field_name}' 具有分子属性: {attr}")
                                    return True
            except Exception as e:
                logger.debug(f"检查字段属性时出错: {e}")
        
        # 🎯 方法2：检查字段名称（备用）
        molecular_field_names = [
            'molecular_file', 'molecule_file', 'mol_file', 'pdb_file',
            'structure_file', 'molecular_data', 'molecule_data'
        ]
        
        if any(name in field_name.lower() for name in molecular_field_names):
            logger.debug(f"🎯 字段名 '{field_name}' 匹配分子字段模式")
            return True
        
        # 🎯 方法3：检查节点类名（兼容性）
        molecular_node_classes = [
            'MolecularUploadDemoNode', 'DualAttributeTestNode', 
            'Demo3DDisplayNode', 'DualButtonDemoNode',
            'SimpleUploadAndDisplayTestNode',
            'StandardMolecularAnalysisNode'  # 🔧 添加新的标准节点
        ]
        
        if node_class_name in molecular_node_classes:
            logger.debug(f"🎯 节点类 '{node_class_name}' 在分子节点白名单中")
            return True
        
        # 🎯 方法4：检查值的特征（文件扩展名）
        if isinstance(field_value, str) and field_value:
            molecular_extensions = ['.pdb', '.mol', '.sdf', '.xyz', '.mol2', '.cif', '.gro', '.fasta', '.fa']
            if any(field_value.lower().endswith(ext) for ext in molecular_extensions):
                logger.debug(f"🎯 字段值 '{field_value}' 具有分子文件扩展名")
                return True
        
        return False
    
    def _get_molecular_content_from_memory(self, node_id: str, field_name: str, original_value: Any) -> Optional[str]:
        """
        从后端内存获取分子内容
        
        Args:
            node_id: 节点ID
            field_name: 字段名称
            original_value: 原始值（通常是文件名或路径）
            
        Returns:
            分子文件内容字符串，如果未找到则返回None
        """
        try:
            # 🔍 尝试从后端内存获取数据
            molecular_data = get_molecular_data(node_id)
            
            if molecular_data and 'content' in molecular_data:
                logger.debug(f"🚀 从后端内存获取分子数据 - 节点: {node_id}")
                logger.debug(f"   文件名: {molecular_data.get('filename', 'unknown')}")
                logger.debug(f"   格式: {molecular_data.get('format', 'unknown')}")
                logger.debug(f"   原子数: {molecular_data.get('atoms', 'unknown')}")
                
                return molecular_data['content']
            else:
                logger.debug(f"⚠️ 节点 {node_id} 在后端内存中未找到分子数据")
                return None
                
        except Exception as e:
            logger.error(f"🚨 从后端内存获取分子数据时出错: {e}")
            return None
    
    def _fallback_get_input_data(self, inputs, class_def, unique_id):
        """
        回退的get_input_data实现
        
        当原始函数不可用时使用的基础实现
        """
        input_data = {}
        
        # 基础的输入数据处理
        if hasattr(class_def, 'INPUT_TYPES'):
            input_types = class_def.INPUT_TYPES()
            required = input_types.get('required', {})
            
            for field_name in required:
                if field_name in inputs:
                    input_data[field_name] = inputs[field_name]
        
        return input_data


# 全局钩子实例
molecular_execution_hook = MolecularExecutionHook()

def install_molecular_execution_hook():
    """安装分子数据执行钩子"""
    return molecular_execution_hook.install_hook()

def uninstall_molecular_execution_hook():
    """卸载分子数据执行钩子"""
    molecular_execution_hook.uninstall_hook()

# 获取钩子状态
def get_hook_status():
    """获取钩子安装状态"""
    return {
        "installed": molecular_execution_hook.hooked,
        "memory_available": MEMORY_AVAILABLE,
        "cached_nodes": len(MOLECULAR_DATA_CACHE) if MEMORY_AVAILABLE else 0
    }