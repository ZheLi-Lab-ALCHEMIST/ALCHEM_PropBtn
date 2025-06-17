"""
🧪 MolstarDisplayMixin - 3D显示功能统一混入包装

═══════════════════════════════════════════════════════════════════════════════
                           3D显示功能快速集成方案
═══════════════════════════════════════════════════════════════════════════════

## 🎯 设计目标：让任何节点轻松获得3D显示能力

### 使用方式：
```python
from .mixins.molstar_display_mixin import MolstarDisplayMixin

class YourCustomNode(MolstarDisplayMixin):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                **cls.get_molstar_input_config("input_molecular_file"),
                "your_param": ("STRING", {"default": "value"})
            }
        }
    
    def your_function(self, input_molecular_file, your_param, **kwargs):
        # 🔑 一行代码获取分子数据
        content, metadata = self.get_molecular_data(input_molecular_file, kwargs)
        
        # 🔑 一行代码处理错误
        if not self.validate_molecular_data(metadata):
            return self.create_error_output(metadata)
        
        # 🚀 专注于你的业务逻辑
        result = your_processing_logic(content)
        
        # 🔑 一行代码生成调试信息
        debug_info = self.generate_debug_info(kwargs.get('_alchem_node_id'), metadata)
        
        return (result, debug_info)
```

### 核心优势：
1. **零配置** - 一行代码启用3D显示
2. **统一接口** - 所有节点使用相同的数据获取方式
3. **自动调试** - 标准化的调试信息生成
4. **错误处理** - 统一的错误处理模板
5. **高度复用** - 适用于任何类型的分子节点
"""

import json
import time
from typing import Tuple, Dict, Any, Optional


class MolstarDisplayMixin:
    """
    🧪 Molstar 3D显示功能混入类
    
    为节点提供标准化的3D显示能力，包括：
    - 统一的输入配置生成
    - 标准化的数据获取接口
    - 自动化的调试信息生成
    - 统一的错误处理
    """
    
    # 🎨 默认3D显示配置
    DEFAULT_MOLSTAR_CONFIG = {
        "molstar_3d_display": True,
        "molecular_folder": "molecules",
        "display_mode": "ball_and_stick",
        "background_color": "#1E1E1E",
    }
    
    # 🎨 默认上传配置
    DEFAULT_UPLOAD_CONFIG = {
        "molecular_upload": True,
        "molecular_folder": "molecules",
    }
    
    @classmethod
    def get_molstar_input_config(
        cls, 
        param_name: str = "molecular_file",
        enable_upload: bool = True,
        enable_3d_display: bool = True,
        custom_config: Optional[Dict] = None
    ) -> Dict[str, Tuple]:
        """
        🔑 生成标准化的Molstar input配置 - 文件名输入模式
        """
        """
        🔑 生成标准化的Molstar input配置
        
        Args:
            param_name: 参数名称
            enable_upload: 是否启用上传功能
            enable_3d_display: 是否启用3D显示功能
            custom_config: 自定义配置覆盖
            
        Returns:
            标准化的INPUT_TYPES配置字典
        """
        config = {"default": "molecule.pdb"}
        
        # 启用上传功能
        if enable_upload:
            config.update(cls.DEFAULT_UPLOAD_CONFIG)
        
        # 启用3D显示功能
        if enable_3d_display:
            config.update(cls.DEFAULT_MOLSTAR_CONFIG)
        
        # 应用自定义配置
        if custom_config:
            config.update(custom_config)
        
        # 确保有提示信息
        if "tooltip" not in config:
            features = []
            if enable_upload:
                features.append("上传")
            if enable_3d_display:
                features.append("3D显示")
            config["tooltip"] = f"分子文件 - 支持{'/'.join(features)}"
        
        return {
            param_name: ("STRING", config),
            "_alchem_node_id": ("STRING", {"default": ""})  # 隐藏参数
        }
    
    @classmethod
    def get_processing_input_config(
        cls,
        content_param: str = "input_molecular_content", 
        output_param: str = "output_filename",
        enable_3d_display: bool = True,
        custom_config: Optional[Dict] = None
    ) -> Dict[str, Tuple]:
        """
        🔄 生成处理节点的input配置 - 内容输入模式
        
        专为中间处理节点设计：
        - 接收上游节点的内容输入
        - 输出文件名支持3D显示
        - 适用于 test_tab_aware_processing.py 这类节点
        
        Args:
            content_param: 内容输入参数名
            output_param: 输出文件名参数名
            enable_3d_display: 是否启用3D显示
            custom_config: 自定义配置
            
        Returns:
            处理节点的INPUT_TYPES配置
        """
        config = {
            # 内容输入 - 来自上游节点
            content_param: ("STRING", {
                "multiline": True,
                "default": "",
                "tooltip": "输入的分子文件内容（来自上游节点）"
            }),
            # 隐藏的节点ID参数
            "_alchem_node_id": ("STRING", {"default": ""})
        }
        
        # 输出文件名配置
        output_config = {"default": "processed_molecule.pdb"}
        
        if enable_3d_display:
            output_config.update(cls.DEFAULT_MOLSTAR_CONFIG)
            output_config["tooltip"] = "处理后的文件名 - 支持3D显示"
        
        # 应用自定义配置
        if custom_config and 'output_config' in custom_config:
            output_config.update(custom_config['output_config'])
        
        config[output_param] = ("STRING", output_config)
        
        return config
    
    def get_molecular_data(
        self, 
        input_value: str, 
        kwargs: Dict[str, Any],
        fallback_to_file: bool = True
    ) -> Tuple[str, Dict[str, Any]]:
        """
        🎯 统一的分子数据获取接口
        
        Args:
            input_value: 输入值（文件名或内容）
            kwargs: 节点执行参数（包含_alchem_node_id）
            fallback_to_file: 是否允许文件系统回退
            
        Returns:
            (content, metadata) 元组
        """
        try:
            # 尝试相对导入，失败则使用绝对导入
            try:
                from ...backend.molecular_utils import get_molecular_content
            except ImportError:
                import sys
                import os
                # 添加项目根目录到Python路径
                current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                if current_dir not in sys.path:
                    sys.path.insert(0, current_dir)
                from backend.molecular_utils import get_molecular_content
            
            node_id = kwargs.get('_alchem_node_id', '')
            
            # 🔍 调试日志
            print(f"[DEBUG] MolstarDisplayMixin.get_molecular_data:")
            print(f"  - 传入的node_id: '{node_id}'")
            print(f"  - node_id类型: {type(node_id)}")
            print(f"  - kwargs keys: {list(kwargs.keys())}")
            
            content, metadata = get_molecular_content(
                input_value=input_value,
                node_id=node_id,
                fallback_to_file=fallback_to_file
            )
            
            return content, metadata
            
        except Exception as e:
            # 创建错误元数据
            error_metadata = {
                'success': False,
                'error': f'数据获取异常: {str(e)}',
                'source': 'error',
                'node_id': kwargs.get('_alchem_node_id', 'unknown')
            }
            return str(input_value), error_metadata
    
    def process_direct_content(
        self,
        content: str,
        output_filename: str,
        node_id: str,
        processing_func: callable,
        **processing_params
    ) -> Tuple[str, str, str]:
        """
        🔄 处理直接内容输入的简化流程
        
        专为中间处理节点设计，简化test_tab_aware_processing.py的实现
        
        Args:
            content: 直接输入的分子内容
            output_filename: 输出文件名  
            node_id: 节点ID
            processing_func: 处理函数 (content, **params) -> processed_content
            **processing_params: 处理参数
            
        Returns:
            (processed_content, processing_report, debug_info)
        """
        try:
            # 🔑 修复：确保节点ID正确
            if not node_id:
                # 如果没有传入节点ID，尝试获取
                node_id = self._get_current_node_id()
            
            print(f"[DEBUG] MolstarDisplayMixin.process_direct_content:")
            print(f"  - 原始node_id: '{node_id}'")
            print(f"  - node_id类型: {type(node_id)}")
            print(f"  - output_filename: '{output_filename}'")
            print(f"  - processing_params: {processing_params}")
            
            # 验证输入内容
            if not content or len(content.strip()) < 10:
                error_report = "❌ 输入内容为空或过短"
                debug_info = self.generate_debug_info(node_id, {'success': False, 'error': '输入内容无效'})
                return ("", error_report, debug_info)
            
            # 执行处理
            processed_content = processing_func(content, **processing_params)
            
            if not processed_content:
                error_report = "❌ 处理失败，无输出内容"
                debug_info = self.generate_debug_info(node_id, {'success': False, 'error': '处理失败'})
                return (content, error_report, debug_info)
            
            # 存储处理结果供3D显示使用
            store_result = self.store_processed_data(processed_content, output_filename, node_id)
            
            # 生成处理报告
            input_atoms = len([l for l in content.split('\n') if l.startswith(('ATOM', 'HETATM'))])
            output_atoms = len([l for l in processed_content.split('\n') if l.startswith(('ATOM', 'HETATM'))])
            
            processing_report = f"""✅ 处理完成 (使用MolstarDisplayMixin)

🔧 处理信息:
- 输入原子数: {input_atoms}
- 输出原子数: {output_atoms}
- 输出文件: {output_filename}
- 存储状态: {'✓' if store_result.get('success') else '✗'}

🎯 架构优势:
- ✅ 直接内容处理模式
- ✅ 3D显示零配置启用  
- ✅ 简化的处理流程
- ✅ 标准化错误处理

🚀 3D显示就绪: {output_filename}"""
            
            # 生成调试信息
            metadata = {
                'success': True,
                'source': 'direct_input',
                'atoms': output_atoms,
                'format_name': 'PDB',  # 简化假设
                'total_lines': len(processed_content.split('\n'))
            }
            debug_info = self.generate_debug_info(node_id, metadata)
            
            return (processed_content, processing_report, debug_info)
            
        except Exception as e:
            error_report = f"❌ 处理异常: {str(e)}"
            debug_info = self.generate_debug_info(node_id, {'success': False, 'error': str(e)})
            return (content, error_report, debug_info)
    
    def validate_molecular_data(self, metadata: Dict[str, Any]) -> bool:
        """
        🔍 验证分子数据是否有效
        
        Args:
            metadata: get_molecular_data返回的元数据
            
        Returns:
            是否有效
        """
        return metadata.get('success', False)
    
    def create_error_output(
        self, 
        metadata: Dict[str, Any], 
        additional_outputs: Tuple = None
    ) -> Tuple:
        """
        ❌ 创建标准化的错误输出
        
        Args:
            metadata: 错误的元数据
            additional_outputs: 额外的输出项（用于匹配节点的RETURN_TYPES）
            
        Returns:
            标准化的错误输出元组
        """
        error_msg = metadata.get('error', '未知错误')
        node_id = metadata.get('node_id', 'unknown')
        
        error_result = f"""❌ 分子数据处理失败

错误信息: {error_msg}
节点ID: {node_id}
数据来源: {metadata.get('source', 'unknown')}

🔧 调试建议:
1. 检查文件是否已正确上传
2. 确认节点ID是否正确传递
3. 查看后端内存状态
4. 验证文件格式是否支持"""
        
        # 生成调试信息
        debug_info = self.generate_debug_info(node_id, metadata)
        
        # 构建输出元组
        base_output = ("", error_result, debug_info)
        
        if additional_outputs:
            return base_output + additional_outputs
        
        return base_output
    
    def generate_debug_info(
        self, 
        node_id: str, 
        metadata: Dict[str, Any],
        additional_info: Optional[Dict] = None
    ) -> str:
        """
        🔍 生成标准化的调试信息
        
        Args:
            node_id: 节点ID
            metadata: 数据元数据
            additional_info: 额外的调试信息
            
        Returns:
            格式化的调试信息字符串
        """
        try:
            # 尝试相对导入，失败则使用绝对导入
            try:
                from ...backend.memory import MOLECULAR_DATA_CACHE, CACHE_LOCK
            except ImportError:
                import sys
                import os
                current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                if current_dir not in sys.path:
                    sys.path.insert(0, current_dir)
                from backend.memory import MOLECULAR_DATA_CACHE, CACHE_LOCK
            
            debug_lines = [
                "🔍 === MolstarDisplayMixin调试信息 ===",
                f"节点ID: {node_id}",
                f"时间戳: {time.strftime('%H:%M:%S')}",
                ""
            ]
            
            # 数据获取状态
            debug_lines.extend([
                "🎯 === 数据获取状态 ===",
                f"获取成功: {'✓' if metadata.get('success') else '✗'}",
                f"数据来源: {metadata.get('source', 'N/A')}",
                f"输入类型: {metadata.get('input_type', 'N/A')}",
                f"内容长度: {len(metadata.get('content', ''))} 字符",
                ""
            ])
            
            # 错误信息
            if not metadata.get('success'):
                debug_lines.extend([
                    "❌ === 错误详情 ===",
                    f"错误信息: {metadata.get('error', 'N/A')}",
                    f"内存错误: {metadata.get('memory_error', '无')}",
                    f"文件错误: {metadata.get('file_error', '无')}",
                    ""
                ])
            
            # 格式信息
            if metadata.get('format_name'):
                debug_lines.extend([
                    "📄 === 格式信息 ===",
                    f"格式: {metadata.get('format_name')}",
                    f"原子数: {metadata.get('atoms', 'N/A')}",
                    f"总行数: {metadata.get('total_lines', 'N/A')}",
                    ""
                ])
            
            # 全局CACHE状态
            debug_lines.append("📊 === 全局CACHE状态 ===")
            with CACHE_LOCK:
                if not MOLECULAR_DATA_CACHE:
                    debug_lines.append("CACHE为空")
                else:
                    debug_lines.append(f"CACHE节点数: {len(MOLECULAR_DATA_CACHE)}")
                    for cache_node_id, cache_data in MOLECULAR_DATA_CACHE.items():
                        marker = "🎯" if cache_node_id == node_id else "🔸"
                        debug_lines.append(f"{marker} {cache_node_id}: {cache_data.get('filename', 'N/A')}")
            
            debug_lines.append("")
            
            # 3D显示状态
            debug_lines.extend([
                "🧪 === 3D显示状态 ===",
                "MolstarDisplayMixin: ✅ 已启用",
                f"节点数据可用: {'✓' if node_id in MOLECULAR_DATA_CACHE else '✗'}",
                f"3D按钮可点击: {'✓' if node_id in MOLECULAR_DATA_CACHE else '✗'}",
                ""
            ])
            
            # 额外信息
            if additional_info:
                debug_lines.extend([
                    "📋 === 额外调试信息 ===",
                    json.dumps(additional_info, ensure_ascii=False, indent=2),
                    ""
                ])
            
            debug_lines.append("🎆 === MolstarDisplayMixin调试完成 ===")
            
            return "\n".join(debug_lines)
            
        except Exception as e:
            return f"调试信息生成失败: {str(e)}"
    
    def process_molecular_content(
        self, 
        content: str, 
        metadata: Dict[str, Any],
        processing_func: callable
    ) -> Tuple[str, Dict[str, Any]]:
        """
        🔧 标准化的分子内容处理流程
        
        Args:
            content: 分子内容
            metadata: 数据元数据
            processing_func: 处理函数，接收(content, metadata)，返回processed_content
            
        Returns:
            (processed_content, updated_metadata)
        """
        try:
            processed_content = processing_func(content, metadata)
            
            # 更新元数据
            updated_metadata = metadata.copy()
            updated_metadata.update({
                'processed': True,
                'processing_time': time.time(),
                'original_length': len(content),
                'processed_length': len(processed_content)
            })
            
            return processed_content, updated_metadata
            
        except Exception as e:
            error_metadata = metadata.copy()
            error_metadata.update({
                'processing_error': str(e),
                'processed': False
            })
            return content, error_metadata
    
    def store_processed_data(
        self, 
        content: str, 
        filename: str,
        node_id: str,
        folder: str = "molecules"
    ) -> Dict[str, Any]:
        """
        💾 存储处理后的数据到后端内存
        
        Args:
            content: 处理后的内容
            filename: 文件名
            node_id: 节点ID
            folder: 存储文件夹
            
        Returns:
            存储结果元数据
        """
        print(f"[DEBUG] MolstarDisplayMixin.store_processed_data:")
        print(f"  - 存储的node_id: '{node_id}'")
        print(f"  - node_id类型: {type(node_id)}")
        print(f"  - filename: '{filename}'")
        print(f"  - content长度: {len(content)}")
        try:
            # 尝试相对导入，失败则使用绝对导入  
            try:
                from ...backend.memory import store_molecular_data
            except ImportError:
                import sys
                import os
                current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                if current_dir not in sys.path:
                    sys.path.insert(0, current_dir)
                from backend.memory import store_molecular_data
            
            result = store_molecular_data(
                node_id=node_id,
                filename=filename,
                folder=folder,
                content=content
            )
            
            return result or {}
            
        except Exception as e:
            return {
                'success': False,
                'error': f'存储失败: {str(e)}'
            }
    
    @classmethod
    def simple_force_execute_is_changed(cls, **kwargs):
        """
        🔥 简单强制执行IS_CHANGED - 解决缓存一致性问题
        
        方案1: 直接强制每次执行，确保数据一致性
        - 当CACHE数据被编辑后，节点会重新执行
        - 虽然性能不是最优，但简单可靠
        
        Args:
            **kwargs: 所有节点参数
            
        Returns:
            包含时间戳的字符串，确保每次都不同
        """
        import hashlib
        
        # 组合参数（排除_alchem_node_id）
        param_parts = []
        for key, value in sorted(kwargs.items()):
            if key != '_alchem_node_id':
                param_parts.append(f"{key}={value}")
        
        param_str = "_".join(param_parts)
        
        # 添加时间戳确保每次执行
        content = f"{param_str}_{time.time()}"
        
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_current_node_id(self) -> str:
        """
        🔑 获取当前节点ID - 复制自test_tab_aware_processing.py的逻辑
        
        Returns:
            节点ID字符串
        """
        try:
            import inspect
            
            # 尝试从调用栈获取节点ID
            for frame_info in inspect.stack():
                frame_locals = frame_info.frame.f_locals
                if 'unique_id' in frame_locals:
                    real_node_id = str(frame_locals['unique_id'])
                    
                    # 尝试获取tab感知的节点ID
                    tab_aware_node_id = self._get_tab_aware_node_id(real_node_id)
                    print(f"🎯 获取节点ID: {real_node_id} -> {tab_aware_node_id}")
                    return tab_aware_node_id
                    
            # 如果找不到，生成临时ID
            fallback_id = f"temp_node_{int(time.time()) % 100000}"
            print(f"⚠️ 未找到节点ID，使用回退方案: {fallback_id}")
            return fallback_id
            
        except Exception as e:
            print(f"❌ 获取节点ID失败: {e}")
            return f"error_node_{int(time.time()) % 100000}"
    
    def _get_tab_aware_node_id(self, real_node_id: str) -> str:
        """
        🔑 获取Tab感知的节点ID - 复制自test_tab_aware_processing.py的逻辑
        
        Args:
            real_node_id: 真实节点ID
            
        Returns:
            Tab感知的存储ID
        """
        try:
            # 尝试相对导入，失败则使用绝对导入
            try:
                from ...backend.memory import MOLECULAR_DATA_CACHE, CACHE_LOCK
            except ImportError:
                import sys
                import os
                current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                if current_dir not in sys.path:
                    sys.path.insert(0, current_dir)
                from backend.memory import MOLECULAR_DATA_CACHE, CACHE_LOCK
            
            # 查找已有的tab_id
            with CACHE_LOCK:
                for node_data in MOLECULAR_DATA_CACHE.values():
                    if node_data.get('tab_id'):
                        tab_id = node_data.get('tab_id')
                        return f"{tab_id}_node_{real_node_id}"
            
            # 默认fallback
            return f"workflow_default_node_{real_node_id}"
            
        except Exception as e:
            print(f"⚠️ 获取tab感知ID失败: {e}")
            return f"workflow_fallback_node_{real_node_id}"


# 🚀 便利函数：快速创建支持3D显示的节点类
def create_molstar_node_class(
    class_name: str,
    processing_function: callable,
    input_params: Dict[str, Tuple] = None,
    return_types: Tuple[str, ...] = ("STRING", "STRING"),
    return_names: Tuple[str, ...] = ("result", "debug_info"),
    category: str = "🧪 ALCHEM/Custom"
) -> type:
    """
    🏭 工厂函数：快速创建支持3D显示的节点类
    
    Args:
        class_name: 节点类名
        processing_function: 处理函数 (content, metadata) -> result
        input_params: 额外的输入参数
        return_types: 返回类型
        return_names: 返回名称
        category: 节点分类
        
    Returns:
        动态创建的节点类
    """
    
    class GeneratedMolstarNode(MolstarDisplayMixin):
        @classmethod
        def INPUT_TYPES(cls):
            config = {
                "required": {
                    **cls.get_molstar_input_config("molecular_file"),
                }
            }
            
            if input_params:
                config["required"].update(input_params)
            
            return config
        
        RETURN_TYPES = return_types
        RETURN_NAMES = return_names
        FUNCTION = "execute"
        CATEGORY = category
        
        def execute(self, molecular_file, **kwargs):
            # 获取分子数据
            content, metadata = self.get_molecular_data(molecular_file, kwargs)
            
            # 验证数据
            if not self.validate_molecular_data(metadata):
                return self.create_error_output(metadata)
            
            # 执行处理
            try:
                result = processing_function(content, metadata)
                debug_info = self.generate_debug_info(
                    kwargs.get('_alchem_node_id'), 
                    metadata
                )
                return (result, debug_info)
                
            except Exception as e:
                error_metadata = metadata.copy()
                error_metadata['error'] = f'处理异常: {str(e)}'
                return self.create_error_output(error_metadata)
        
        @classmethod
        def IS_CHANGED(cls, molecular_file, _alchem_node_id="", **kwargs):
            """🔥 简单强制执行IS_CHANGED - 确保缓存一致性"""
            return cls.simple_force_execute_is_changed(
                molecular_file=molecular_file,
                _alchem_node_id=_alchem_node_id,
                **kwargs
            )
    
    # 设置类名
    GeneratedMolstarNode.__name__ = class_name
    GeneratedMolstarNode.__qualname__ = class_name
    
    return GeneratedMolstarNode