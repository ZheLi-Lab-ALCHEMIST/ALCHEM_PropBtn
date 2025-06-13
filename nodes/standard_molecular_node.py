"""
🧪 标准化分子节点模板 (standard_molecular_node.py)

═══════════════════════════════════════════════════════════════════════════════
                            分子节点开发完整指南
═══════════════════════════════════════════════════════════════════════════════

## 🎯 核心架构：方案B - 节点主动获取数据

### 📋 INPUT_TYPES配置指南

```python
"molecular_file": ("STRING", {
    "molecular_upload": True,       # 🔑 启用上传按钮 (📁 Upload)
    "molstar_3d_display": True,     # 🔑 启用3D显示按钮 (🧪 3D View)
    "molecular_folder": "molecules", # 文件存储目录
    "display_mode": "ball_and_stick", # 3D显示模式
    "background_color": "#1E1E1E",   # 3D背景色
    "tooltip": "支持上传和3D显示的分子文件"
})
```

### 🔄 双按钮联动工作流

#### 1️⃣ 上传按钮 (📁 Upload) 工作流：
```
用户操作：点击📁按钮 → 选择分子文件 → 上传
前端处理：uploadMolecules.js → 调用 /api/upload_molecular
后端存储：molecular_memory.py → 存储到内存缓存
结果：文件内容存储在后端，key为节点ID
```

#### 2️⃣ 3D显示按钮 (🧪 3D View) 工作流：
```
用户操作：点击🧪按钮 → 打开3D显示窗口
前端处理：custom3DDisplay.js → 调用 /api/molecular
数据获取：从后端内存获取分子内容 → MolStar渲染
结果：显示交互式3D分子结构
```

#### 3️⃣ 节点执行时的数据获取：
```python
# 在节点函数中使用工具获取数据
from ..backend.molecular_utils import get_molecular_content

content, metadata = get_molecular_content(
    input_value=molecular_file,  # 用户输入（文件名或内容）
    fallback_to_file=True       # 允许文件系统回退
)

# content: 完整的分子文件内容
# metadata: 详细的元数据信息（来源、格式、统计等）
```

### 🔍 数据流详解

#### 方案A（已废弃）：execution_hook拦截
```
❌ 节点执行 → hook拦截get_input_data → 替换文件名为内容 → 节点接收
   问题：依赖ComfyUI内部API，不稳定
```

#### 方案B（推荐）：节点主动获取
```
✅ 节点执行 → 调用get_molecular_content() → 智能获取内容 → 节点处理
   优势：稳定、明确、可控、易调试
```

### 🛠️ get_molecular_content() 工具详解

#### 🔸 智能判断输入类型：
- **短字符串 + 有文件扩展名** → 识别为文件名，从内存/文件系统获取
- **长内容 + 多行结构** → 识别为已有内容，直接返回
- **包含分子格式关键词** → 识别为分子内容，直接返回

#### 🔸 多级数据源查找：
1. **内存缓存优先**：从molecular_memory中按文件名查找
2. **文件系统回退**：从input/molecules/目录读取文件
3. **详细错误信息**：无法获取时提供调试信息

#### 🔸 丰富的元数据返回：
```python
metadata = {
    "success": True/False,           # 是否成功获取
    "source": "memory_cache/file_system/direct_input",  # 数据来源
    "format": ".pdb/.mol/.sdf",      # 文件格式
    "format_name": "Protein Data Bank", # 格式全名
    "atoms": 124,                    # 原子数量
    "total_lines": 156,              # 总行数
    "file_size": 5432,              # 文件大小
    "node_id": "4",                 # 节点ID
    # ... 更多分析信息
}
```

### 💡 开发自定义节点的标准步骤

#### 第1步：INPUT_TYPES定义
```python
@classmethod
def INPUT_TYPES(cls):
    return {
        "required": {
            "molecular_file": ("STRING", {
                "molecular_upload": True,      # 必须：启用上传
                "molstar_3d_display": True,    # 必须：启用3D显示
                "molecular_folder": "molecules", # 推荐：指定文件夹
                "tooltip": "你的提示信息"
            }),
            # 其他参数...
        }
    }
```

#### 第2步：节点函数实现
```python
def your_function(self, molecular_file, other_params):
    # 🎯 必须：使用工具获取分子数据
    from ..backend.molecular_utils import get_molecular_content
    
    content, metadata = get_molecular_content(molecular_file)
    
    # 🔍 推荐：检查获取是否成功
    if not metadata.get('success'):
        return f"错误：{metadata.get('error')}"
    
    # 🚀 使用content进行你的业务逻辑
    result = your_processing_logic(content, metadata)
    
    return result
```

#### 第3步：错误处理最佳实践
```python
try:
    content, metadata = get_molecular_content(molecular_file)
    
    if not metadata.get('success'):
        # 获取失败的处理
        error_info = {
            "error": metadata.get('error'),
            "attempted_sources": [metadata.get('source')],
            "debug_info": metadata
        }
        return json.dumps(error_info, ensure_ascii=False)
    
    # 成功的处理...
    
except Exception as e:
    # 异常的处理
    return f"处理异常：{str(e)}"
```

### 🎨 前端按钮自定义

#### 上传按钮样式自定义：
```javascript
// molecular_folder: 控制上传到哪个文件夹
// tooltip: 控制按钮提示文字
// 前端会自动检测molecular_upload属性并添加按钮
```

#### 3D显示按钮样式自定义：
```javascript
// display_mode: "ball_and_stick" | "spacefill" | "cartoon"
// background_color: 3D查看器背景色
// 前端会自动检测molstar_3d_display属性并添加按钮
```

### ⚡ 性能优化建议

1. **缓存利用**：多次执行同一节点时，工具会自动利用内存缓存
2. **按需加载**：只有在需要时才调用get_molecular_content()
3. **元数据复用**：利用metadata中的分析结果，避免重复解析
4. **错误快速返回**：检查metadata.success，快速处理失败情况

### 🔧 调试技巧

1. **查看元数据**：打印metadata了解数据获取详情
2. **检查数据源**：metadata.source告诉你数据来自哪里
3. **内容验证**：检查content长度和格式是否符合预期
4. **日志监控**：工具函数会输出详细的日志信息

这个模板展示了所有关键概念的实际应用，可以作为开发新节点的参考。
"""

import os
import json
import hashlib
import time

class StandardMolecularAnalysisNode:
    """
    🧪⚗️ 标准分子分析节点 - 完整示例
    
    ## 🎯 功能演示：
    1. **双按钮UI**：📁上传 + 🧪3D显示按钮自动生成
    2. **智能数据获取**：使用get_molecular_content()工具
    3. **多格式分析**：PDB/SDF/XYZ/FASTA等格式支持
    4. **多种输出**：JSON/CSV/Summary格式
    5. **完整错误处理**：详细的调试信息
    
    ## 🔄 用户交互流程：
    
    ### 上传流程：
    1. 用户点击📁按钮 → 选择分子文件 → 自动上传到后端内存
    2. 前端显示上传成功 → 文件名显示在下拉框中
    3. 用户可以继续选择其他文件或执行节点
    
    ### 3D显示流程：
    1. 用户点击🧪按钮 → 自动打开3D显示窗口
    2. 系统从后端内存获取分子数据 → MolStar渲染3D结构
    3. 用户可以交互操作：旋转、缩放、重置视角
    
    ### 节点执行流程：
    1. 用户点击执行 → 节点调用get_molecular_content()获取数据
    2. 工具智能判断输入类型 → 从内存/文件系统获取完整内容
    3. 节点进行分析处理 → 返回格式化结果
    
    ## 💡 开发者注意事项：
    - molecular_file参数会接收文件名，不要直接当内容使用
    - 必须使用get_molecular_content()获取实际内容
    - 检查metadata.success确认数据获取成功
    - 利用metadata中的格式信息，避免重复解析
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "molecular_file": ("STRING", {
                    "default": "molecule.pdb",
                    "molecular_upload": True,       # 🧪 启用分子上传
                    "molstar_3d_display": True,     # 🧪 启用3D显示
                    "molecular_folder": "molecules",
                    "display_mode": "ball_and_stick",
                    "background_color": "#1E1E1E",
                    "tooltip": "分子文件 - 支持上传和3D显示"
                }),
                "analysis_type": (["basic", "detailed", "structural", "chemical"], {
                    "default": "basic",
                    "tooltip": "分析类型"
                }),
                "output_format": (["json", "summary", "csv"], {
                    "default": "json",
                    "tooltip": "输出格式"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "FLOAT")
    RETURN_NAMES = ("analysis_result", "molecular_content", "confidence_score")
    OUTPUT_TOOLTIPS = ("分析结果", "分子内容", "置信度分数")
    FUNCTION = "analyze_molecule"
    CATEGORY = "🧪 ALCHEM/Standard"
    
    def analyze_molecule(self, molecular_file, analysis_type="basic", output_format="json"):
        """
        标准分子分析函数 - 展示方案B的最佳实践
        
        ## 📥 输入参数说明：
        - molecular_file: 分子文件名（不是内容！）需要通过工具获取实际内容
        - analysis_type: 分析类型 basic/detailed/structural/chemical
        - output_format: 输出格式 json/summary/csv
        
        ## 🔄 处理流程：
        1. 使用get_molecular_content()获取分子内容和元数据
        2. 检查数据获取是否成功，处理错误情况
        3. 根据analysis_type进行相应级别的分析
        4. 根据output_format格式化输出结果
        5. 计算置信度分数并返回
        
        ## 💡 关键点：
        - molecular_file只是文件名，真正的内容在get_molecular_content()返回的content中
        - metadata包含格式、原子数等预分析信息，可以直接使用
        - 始终检查metadata.success，确保数据获取成功
        - 利用工具的错误信息提供友好的错误反馈
        
        ## 🚀 返回值：
        - analysis_result: 格式化的分析结果
        - molecular_content: 分子文件内容（截断显示）
        - confidence_score: 分析置信度 (0.0-1.0)
        """
        try:
            # 🎯 步骤1：使用工具函数获取分子数据
            from ..backend.molecular_utils import get_molecular_content
            
            content, metadata = get_molecular_content(
                input_value=molecular_file,
                fallback_to_file=True
            )
            
            # 🎯 步骤2：检查数据获取是否成功
            if not metadata.get('success'):
                error_msg = f"分子数据获取失败: {metadata.get('error', '未知错误')}"
                return (
                    json.dumps({"error": error_msg}, ensure_ascii=False),
                    str(molecular_file),
                    0.0
                )
            
            # 🎯 步骤3：进行分子分析（使用获取到的内容）
            analysis_result = self._perform_analysis(content, metadata, analysis_type)
            
            # 🎯 步骤4：根据输出格式生成结果
            if output_format == "json":
                formatted_result = json.dumps(analysis_result, ensure_ascii=False, indent=2)
            elif output_format == "csv":
                formatted_result = self._to_csv(analysis_result)
            else:  # summary
                formatted_result = self._to_summary(analysis_result)
            
            # 计算置信度分数
            confidence = self._calculate_confidence(metadata, analysis_result)
            
            return (formatted_result, content[:1000] + "..." if len(content) > 1000 else content, confidence)
            
        except Exception as e:
            error_msg = f"分析过程中发生错误: {str(e)}"
            return (
                json.dumps({"error": error_msg}, ensure_ascii=False),
                str(molecular_file),
                0.0
            )
    
    def _perform_analysis(self, content: str, metadata: dict, analysis_type: str) -> dict:
        """
        执行具体的分子分析
        """
        analysis = {
            "basic_info": {
                "filename": metadata.get('source_node_id', 'unknown'),
                "format": metadata.get('format_name', 'Unknown'),
                "data_source": metadata.get('source', 'unknown'),
                "content_length": len(content),
                "total_lines": metadata.get('total_lines', 0),
                "analysis_type": analysis_type,
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
        # 基础分析
        if metadata.get('atoms'):
            analysis["structure"] = {
                "atom_count": metadata.get('atoms'),
                "has_coordinates": True
            }
        
        if metadata.get('sequences'):
            analysis["sequence"] = {
                "sequence_count": metadata.get('sequences'),
                "type": "protein_sequence"
            }
        
        # 详细分析
        if analysis_type in ["detailed", "structural", "chemical"]:
            analysis["detailed"] = self._detailed_analysis(content, metadata)
        
        # 结构分析
        if analysis_type == "structural":
            analysis["structural"] = self._structural_analysis(content)
        
        # 化学分析
        if analysis_type == "chemical":
            analysis["chemical"] = self._chemical_analysis(content)
        
        return analysis
    
    def _detailed_analysis(self, content: str, metadata: dict) -> dict:
        """详细分析"""
        lines = content.split('\n')
        
        detailed = {
            "line_distribution": {},
            "content_statistics": {
                "empty_lines": len([line for line in lines if not line.strip()]),
                "comment_lines": len([line for line in lines if line.strip().startswith('#')]),
                "data_lines": len([line for line in lines if line.strip() and not line.strip().startswith('#')])
            }
        }
        
        # 统计行类型分布（针对PDB格式）
        if metadata.get('format') == '.pdb':
            pdb_types = ['HEADER', 'ATOM', 'HETATM', 'CONECT', 'END']
            for pdb_type in pdb_types:
                count = len([line for line in lines if line.startswith(pdb_type)])
                if count > 0:
                    detailed["line_distribution"][pdb_type] = count
        
        return detailed
    
    def _structural_analysis(self, content: str) -> dict:
        """结构分析"""
        lines = content.split('\n')
        
        structural = {
            "coordinates": {"x_range": None, "y_range": None, "z_range": None},
            "bonds": {"count": 0, "types": []},
            "residues": {"count": 0, "types": set()}
        }
        
        # PDB格式的坐标分析
        atom_lines = [line for line in lines if line.startswith('ATOM')]
        if atom_lines:
            x_coords = []
            y_coords = []
            z_coords = []
            
            for line in atom_lines:
                try:
                    x = float(line[30:38].strip())
                    y = float(line[38:46].strip())
                    z = float(line[46:54].strip())
                    x_coords.append(x)
                    y_coords.append(y)
                    z_coords.append(z)
                    
                    # 残基类型
                    residue = line[17:20].strip()
                    structural["residues"]["types"].add(residue)
                except:
                    continue
            
            if x_coords:
                structural["coordinates"] = {
                    "x_range": [min(x_coords), max(x_coords)],
                    "y_range": [min(y_coords), max(y_coords)],
                    "z_range": [min(z_coords), max(z_coords)]
                }
                structural["residues"]["count"] = len(structural["residues"]["types"])
                structural["residues"]["types"] = list(structural["residues"]["types"])
        
        # 连接信息
        connect_lines = [line for line in lines if line.startswith('CONECT')]
        structural["bonds"]["count"] = len(connect_lines)
        
        return structural
    
    def _chemical_analysis(self, content: str) -> dict:
        """化学分析"""
        lines = content.split('\n')
        
        chemical = {
            "elements": {},
            "molecular_weight": 0.0,
            "charge": 0,
            "formula": "Unknown"
        }
        
        # 元素统计（从PDB ATOM记录）
        atom_lines = [line for line in lines if line.startswith('ATOM')]
        element_counts = {}
        
        for line in atom_lines:
            try:
                element = line[76:78].strip() or line[12:14].strip()[0]
                element_counts[element] = element_counts.get(element, 0) + 1
            except:
                continue
        
        chemical["elements"] = element_counts
        
        # 简化的分子式
        if element_counts:
            formula_parts = []
            for element in sorted(element_counts.keys()):
                count = element_counts[element]
                if count == 1:
                    formula_parts.append(element)
                else:
                    formula_parts.append(f"{element}{count}")
            chemical["formula"] = "".join(formula_parts)
        
        return chemical
    
    def _to_csv(self, analysis_result: dict) -> str:
        """转换为CSV格式"""
        csv_lines = ["property,value"]
        
        def flatten_dict(d, prefix=""):
            for key, value in d.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    csv_lines.extend(flatten_dict(value, full_key))
                elif isinstance(value, list):
                    csv_lines.append(f"{full_key},{';'.join(map(str, value))}")
                else:
                    csv_lines.append(f"{full_key},{value}")
        
        flatten_dict(analysis_result)
        return "\n".join(csv_lines)
    
    def _to_summary(self, analysis_result: dict) -> str:
        """转换为摘要格式"""
        basic = analysis_result.get("basic_info", {})
        
        summary = f"""🧪 分子分析摘要
═══════════════════════════════════════
📁 文件信息: {basic.get('format', 'Unknown')} 格式
📊 数据来源: {basic.get('data_source', 'unknown')}
📏 内容长度: {basic.get('content_length', 0)} 字符
📄 总行数: {basic.get('total_lines', 0)}
🔬 分析类型: {basic.get('analysis_type', 'basic')}
🕒 分析时间: {basic.get('timestamp', 'unknown')}
"""
        
        if "structure" in analysis_result:
            structure = analysis_result["structure"]
            summary += f"\n🧬 结构信息:\n• 原子数: {structure.get('atom_count', 'N/A')}"
        
        if "sequence" in analysis_result:
            sequence = analysis_result["sequence"]
            summary += f"\n🧲 序列信息:\n• 序列数: {sequence.get('sequence_count', 'N/A')}"
        
        return summary
    
    def _calculate_confidence(self, metadata: dict, analysis_result: dict) -> float:
        """计算分析置信度"""
        confidence = 0.5  # 基础分数
        
        # 数据来源加分
        if metadata.get('source') == 'memory_cache':
            confidence += 0.2
        elif metadata.get('source') == 'file_system':
            confidence += 0.1
        
        # 格式识别加分
        if metadata.get('format') in ['.pdb', '.sdf', '.mol']:
            confidence += 0.2
        
        # 结构数据加分
        if analysis_result.get("structure", {}).get("atom_count"):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    @classmethod
    def IS_CHANGED(cls, molecular_file, analysis_type, output_format):
        # 基于输入参数生成哈希
        content = f"{molecular_file}_{analysis_type}_{output_format}_{time.time()}"
        return hashlib.md5(content.encode()).hexdigest()


# 节点注册
NODE_CLASS_MAPPINGS = {
    "StandardMolecularAnalysisNode": StandardMolecularAnalysisNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "StandardMolecularAnalysisNode": "🧪⚗️ Standard Molecular Analysis",
}