"""
🧪 使用MolstarDisplayMixin的示例节点 - 核心功能展示

═══════════════════════════════════════════════════════════════════════════════
                        两种节点类型的标准定义范式
═══════════════════════════════════════════════════════════════════════════════

## 📋 节点类型分类

### 🔸 输入节点 (Upload/Source Nodes)
**特征**: 接收文件名，提供内容输出，通常是工作流的起点
**输入**: `molecular_file` (文件名)
**输出**: `file_content` (分子内容)
**用途**: 上传分子文件，提供分子数据源
**示例**: SimpleMolecularAnalyzer

### 🔸 中间节点 (Processing/Transform Nodes) 
**特征**: 接收内容输入，进行处理，输出处理后的内容
**输入**: `input_molecular_content` (分子内容)
**输出**: `processed_content` (处理后内容) 
**用途**: 分子编辑、变换、分析等中间处理
**示例**: SimpleTabAwareProcessor

## 🎯 Mixin使用模式对比

### 传统方式 (400+ 行复杂代码)：
- 复杂的内存管理逻辑
- 重复的调试信息生成  
- 手动错误处理
- 手动3D显示配置

### 新方式 (30-50 行简洁代码)：
- 零配置启用3D显示
- 标准化的错误处理
- 自动调试信息生成
- 自动节点ID和CACHE管理

## 🚀 核心优势：
1. **代码减少90%** - 专注业务逻辑，基础设施自动处理
2. **配置统一** - 标准化的节点定义模式
3. **类型明确** - 清晰的输入节点vs中间节点区分
4. **维护简单** - Mixin升级，所有节点自动受益
5. **CACHE自动管理** - 自动节点ID获取和数据存储

## 🛠️ 快速开发指南

### 🔑 Mixin配置机制详解

#### **cls.get_molstar_input_config() 做了什么？**

传统方式需要手动配置很多属性：
```python
# ❌ 传统方式 - 繁琐且容易出错
"molecular_file": ("STRING", {
    "default": "molecule.pdb",
    "molecular_upload": True,        # 启用上传按钮
    "molstar_3d_display": True,      # 启用3D显示按钮
    "molecular_folder": "molecules", # 存储文件夹
    "display_mode": "ball_and_stick", # 3D显示模式
    "background_color": "#1E1E1E",   # 3D背景色
    "tooltip": "分子文件 - 支持上传和3D显示"
}),
"_alchem_node_id": ("STRING", {"default": ""})  # 隐藏的节点ID参数
```

**Mixin方式自动生成相同配置：**
```python
# ✅ Mixin方式 - 一行代码自动生成上述所有配置
**cls.get_molstar_input_config("molecular_file")

# ** 语法说明：Python字典解包，等同于：
config = cls.get_molstar_input_config("molecular_file")
# config = {
#     "molecular_file": ("STRING", {所有属性}),
#     "_alchem_node_id": ("STRING", {"default": ""})
# }
# **config 将字典内容展开到 "required" 中
```

### 创建输入节点 (文件名输入模式):
```python
class YourUploadNode(MolstarDisplayMixin):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                **cls.get_molstar_input_config("molecular_file"),  # 🔑 自动生成完整配置
                # 等价于上面传统方式的所有属性设置，但只需一行代码
                
                # 你的其他参数...
                "analysis_type": (["basic", "detailed"], {"default": "basic"})
            }
        }
    
    def your_function(self, molecular_file, analysis_type, **kwargs):
        content, metadata = self.get_molecular_data(molecular_file, kwargs)  # 🔑 一行获取
        # 你的业务逻辑...
        return (content, debug_info)
```

### 创建中间节点 (内容输入模式):
```python
class YourProcessNode(MolstarDisplayMixin):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                **cls.get_processing_input_config("input_content", "output_filename"),  # 🔑 自动生成双参数配置
                # 自动生成：
                # - input_content: ("STRING", {multiline: True, ...})  内容输入框
                # - output_filename: ("STRING", {molstar_3d_display: True, ...})  3D显示文件名
                # - _alchem_node_id: ("STRING", {"default": ""})  隐藏节点ID
                
                # 你的其他参数...
                "processing_type": (["remove_h", "center"], {"default": "remove_h"})
            }
        }
    
    def your_function(self, input_content, output_filename, processing_type, **kwargs):
        return self.process_direct_content(  # 🔑 一行处理完整流程
            content=input_content,
            output_filename=output_filename, 
            node_id=kwargs.get('_alchem_node_id', ''),
            processing_func=your_business_logic,
            processing_type=processing_type  # 传递给处理函数的参数
        )
```

#### **为什么使用这种方式？**
1. **减少重复代码** - 避免每个节点都写相同的属性配置
2. **确保一致性** - 所有节点的3D显示配置完全相同
3. **易于维护** - 修改Mixin一处，所有节点自动受益
4. **避免错误** - 不会忘记配置某个必需的属性
"""

from .mixins.molstar_display_mixin import MolstarDisplayMixin
import time


# ═════════════════════════════════════════════════════════════════════════════
# 示例1: 输入节点 - 分子分析器 (对比standard_molecular_node.py)
# ═════════════════════════════════════════════════════════════════════════════

class SimpleMolecularAnalyzer(MolstarDisplayMixin):
    """
    🧪📊 输入节点示例 - 分子分析器 (使用Mixin简化版)
    
    📋 节点类型: 输入源节点 (Upload/Source Node)
    📥 输入模式: 文件名输入 (molecular_file)
    📤 输出模式: 分子内容 + 分析结果
    🔗 工作流位置: 工作流起点，为下游节点提供分子数据
    
    对比原始standard_molecular_node.py：
    - 原版: 600+ 行复杂代码，手动配置
    - 新版: 80 行简洁代码，零配置3D显示
    - 功能相同: 上传+分析+3D显示，但代码更简洁
    
    💡 使用场景:
    - 工作流的起点，上传分子文件
    - 进行基础分析和格式识别
    - 提供分子内容给下游处理节点
    - 支持3D显示查看上传的分子结构
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                **cls.get_molstar_input_config("molecular_file"),
                "analysis_type": (["basic", "detailed"], {
                    "default": "basic",
                    "tooltip": "分析类型"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("analysis_result", "molecular_content", "debug_info")
    FUNCTION = "analyze_molecule"
    CATEGORY = "🧪 ALCHEM/Examples with Mixin"
    
    def analyze_molecule(self, molecular_file, analysis_type, **kwargs):
        """简化版分子分析"""
        # 🔑 一行代码获取分子数据
        content, metadata = self.get_molecular_data(molecular_file, kwargs)
        
        # 🔑 一行代码验证数据
        if not self.validate_molecular_data(metadata):
            return self.create_error_output(metadata)
        
        # 🚀 专注于业务逻辑：分析
        analysis_result = self._perform_analysis(content, metadata, analysis_type)
        
        # 🔑 一行代码生成调试信息
        debug_info = self.generate_debug_info(kwargs.get('_alchem_node_id'), metadata)
        
        return (analysis_result, content, debug_info)
    
    def _perform_analysis(self, content: str, metadata: dict, analysis_type: str) -> str:
        """业务逻辑：分子分析"""
        lines = content.split('\n')
        atom_lines = [line for line in lines if line.startswith('ATOM')]
        
        if analysis_type == "basic":
            return f"""🧪 基础分析结果:
- 格式: {metadata.get('format_name', 'Unknown')}
- 总行数: {len(lines)}
- 原子数: {len(atom_lines)}
- 数据来源: {metadata.get('source')}"""
        
        else:  # detailed
            elements = {}
            for line in atom_lines:
                if len(line) > 76:
                    element = line[76:78].strip() or line[12:14].strip()[0]
                    elements[element] = elements.get(element, 0) + 1
            
            return f"""🧪 详细分析结果:
- 格式: {metadata.get('format_name', 'Unknown')}
- 总行数: {len(lines)}
- 原子数: {len(atom_lines)}
- 元素分布: {elements}
- 数据来源: {metadata.get('source')}"""
    
    @classmethod
    def IS_CHANGED(cls, molecular_file, analysis_type, _alchem_node_id=""):
        """🔥 简单强制执行IS_CHANGED - 解决缓存一致性问题"""
        return cls.simple_force_execute_is_changed(
            molecular_file=molecular_file,
            analysis_type=analysis_type,
            _alchem_node_id=_alchem_node_id
        )


# ═════════════════════════════════════════════════════════════════════════════
# 示例2: 中间节点 - Tab感知处理器 (完整功能展示)
# ═════════════════════════════════════════════════════════════════════════════

class SimpleTabAwareProcessor(MolstarDisplayMixin):
    """
    🧪⚡ 中间节点示例 - Tab感知处理器 (完整功能展示)
    
    📋 节点类型: 中间处理节点 (Processing Node) - 完整实现
    📥 输入模式: 内容输入 (input_molecular_content)  
    📤 输出模式: 处理后内容 (processed_content)
    🔗 工作流位置: 上游节点 → 本节点 → 下游节点
    
    对比原始test_tab_aware_processing.py：
    - 原版: 400+ 行复杂代码，手动内存管理，复杂的Tab感知逻辑
    - 新版: 100 行简洁代码，Mixin自动处理所有基础设施
    - 功能完全相同: 删除氢原子/分子居中/简单编辑 + 自动CACHE存储 + 3D显示
    
    🔑 关键特性展示:
    - ✅ 自动节点ID获取和Tab感知
    - ✅ 自动CACHE存储，3D按钮立即可用
    - ✅ 完整的分子处理功能
    - ✅ 标准化错误处理和调试信息
    - ✅ 强制执行IS_CHANGED解决缓存一致性
    
    💡 这是完整功能的最佳示例，展示了如何用Mixin实现复杂的处理节点
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                **cls.get_processing_input_config(
                    content_param="input_molecular_content",
                    output_param="output_filename",
                    custom_config={
                        'output_config': {
                            "default": "processed_molecule.pdb",
                            "tooltip": "处理后的分子文件名 - 支持3D显示"
                        }
                    }
                ),
                "processing_type": (["remove_hydrogens", "center_molecule", "simple_edit"], {
                    "default": "remove_hydrogens",
                    "tooltip": "处理类型"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("processed_content", "processing_report", "debug_info")
    FUNCTION = "process_molecular_data"
    CATEGORY = "🧪 ALCHEM/Examples with Mixin"
    
    def process_molecular_data(self, input_molecular_content, output_filename, processing_type, **kwargs):
        """🔄 使用Mixin的简化处理流程"""
        
        # 🔑 修复：确保节点ID正确传递，如果_alchem_node_id为空，让Mixin自动获取
        node_id = kwargs.get('_alchem_node_id', '')
        if not node_id:
            print("⚠️ _alchem_node_id为空，将由Mixin自动获取节点ID")
        
        # 🔑 一行代码完成整个处理流程！
        return self.process_direct_content(
            content=input_molecular_content,
            output_filename=output_filename,
            node_id=node_id,  # 传递给Mixin，如果为空会自动获取
            processing_func=self._process_molecular_content,
            processing_type=processing_type
        )
    
    def _process_molecular_content(self, content: str, processing_type: str) -> str:
        """业务逻辑：实际的分子处理（与原版相同）"""
        if processing_type == "remove_hydrogens":
            return self._remove_hydrogens(content)
        elif processing_type == "center_molecule":
            return self._center_molecule(content)
        elif processing_type == "simple_edit":
            return self._simple_edit(content)
        return content
    
    def _remove_hydrogens(self, content: str) -> str:
        """删除氢原子（简化版）"""
        lines = content.split('\n')
        processed_lines = []
        for line in lines:
            if line.startswith(('ATOM', 'HETATM')) and len(line) > 12:
                atom_name = line[12:16].strip()
                if not atom_name.upper().startswith('H'):
                    processed_lines.append(line)
            else:
                processed_lines.append(line)
        return '\n'.join(processed_lines)
    
    def _center_molecule(self, content: str) -> str:
        """分子居中（简化版）"""
        lines = content.split('\n')
        coords = []
        
        for line in lines:
            if line.startswith('ATOM') and len(line) > 54:
                try:
                    x, y, z = float(line[30:38]), float(line[38:46]), float(line[46:54])
                    coords.append((x, y, z))
                except:
                    continue
        
        if not coords:
            return content
        
        center_x = sum(x for x, y, z in coords) / len(coords)
        center_y = sum(y for x, y, z in coords) / len(coords) 
        center_z = sum(z for x, y, z in coords) / len(coords)
        
        processed_lines = []
        for line in lines:
            if line.startswith('ATOM') and len(line) > 54:
                try:
                    x = float(line[30:38]) - center_x
                    y = float(line[38:46]) - center_y
                    z = float(line[46:54]) - center_z
                    new_line = line[:30] + f"{x:8.3f}{y:8.3f}{z:8.3f}" + line[54:]
                    processed_lines.append(new_line)
                except:
                    processed_lines.append(line)
            else:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def _simple_edit(self, content: str) -> str:
        """简单编辑：删除最后一个原子"""
        lines = content.split('\n')
        atom_indices = [i for i, line in enumerate(lines) if line.startswith(('ATOM', 'HETATM'))]
        if atom_indices:
            lines.pop(atom_indices[-1])
        return '\n'.join(lines)
    
    @classmethod
    def IS_CHANGED(cls, input_molecular_content, output_filename, processing_type, _alchem_node_id=""):
        """🔥 简单强制执行IS_CHANGED - 解决缓存一致性问题"""
        return cls.simple_force_execute_is_changed(
            input_molecular_content=input_molecular_content,
            output_filename=output_filename,
            processing_type=processing_type,
            _alchem_node_id=_alchem_node_id
        )


# ═════════════════════════════════════════════════════════════════════════════
# 📋 节点类型总结 - 完整开发指南
# ═════════════════════════════════════════════════════════════════════════════

"""
🎯 两种节点开发模式总结:

1️⃣ 输入节点 (SimpleMolecularAnalyzer)
   - 用途: 工作流起点，上传分子文件
   - 输入: molecular_file (文件名)
   - 配置: cls.get_molstar_input_config()
   - 数据获取: self.get_molecular_data()

2️⃣ 中间节点-完整版 (SimpleTabAwareProcessor)
   - 用途: 复杂处理，完整功能展示
   - 输入: input_molecular_content (内容)
   - 特点: 展示Mixin的全部能力
   - 示例: 完美替代test_tab_aware_processing.py

💡 选择指南:
- 🔸 上传节点 → 使用模式1
- 🔸 复杂处理 → 使用模式2

🚀 所有模式都自动获得:
✅ 3D显示功能 (molstar_3d_display)
✅ CACHE自动存储
✅ 缓存一致性 (强制IS_CHANGED) 
✅ 标准化错误处理
✅ 调试信息生成
✅ Tab感知节点ID管理
"""

# ═════════════════════════════════════════════════════════════════════════════
# 节点注册
# ═════════════════════════════════════════════════════════════════════════════

NODE_CLASS_MAPPINGS = {
    "SimpleMolecularAnalyzer": SimpleMolecularAnalyzer,
    "SimpleTabAwareProcessor": SimpleTabAwareProcessor,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SimpleMolecularAnalyzer": "🧪📊 Simple Analyzer (输入节点)", 
    "SimpleTabAwareProcessor": "🧪⚡ Tab-Aware Processor (中间节点-完整版)",
}