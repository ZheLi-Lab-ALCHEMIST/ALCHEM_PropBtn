"""
🧪 简洁的分子上传和3D显示测试节点 - 正确的架构实现

这个节点展示了正确的数据流架构：
1. 节点只定义输入输出，不做内存管理
2. execution_hook自动拦截get_input_data，从后端内存获取数据  
3. 前端uploadMolecules.js处理上传到后端内存
4. 前端custom3DDisplay.js处理3D显示
5. 节点只处理业务逻辑

关键理解：节点不需要自己管理内存，架构已经处理好了！
"""

import os
import json
import hashlib
import time

class SimpleUploadAndDisplayTestNode:
    """
    🧪🎯 简洁测试节点 - molecular_upload + molstar_3d_display
    
    展示正确的架构使用方式：
    - molecular_upload: True (前端会添加上传按钮，数据存储到后端内存)
    - molstar_3d_display: True (前端会添加3D显示按钮，从后端内存获取数据)
    - execution_hook会自动拦截，将文件名替换为内存中的内容
    - 节点只需要处理接收到的内容即可，无需管理内存
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "molecular_file": ("STRING", {
                    "default": "molecule.pdb",
                    "molecular_upload": True,        # 🧪 启用分子上传功能
                    "molstar_3d_display": True,      # 🧪 启用3D显示功能  
                    "molecular_folder": "molecules", # 上传到molecules文件夹
                    "display_mode": "ball_and_stick",# 3D显示模式
                    "background_color": "#1E1E1E",   # 3D背景色
                    "tooltip": "分子文件名 - 可以上传新文件或查看已有文件的3D结构"
                }),
                "test_mode": (["simple", "detailed", "debug"], {
                    "default": "simple",
                    "tooltip": "测试模式：简单/详细/调试"
                })
            },
            "hidden": {
                "_alchem_node_id": ("STRING", {"default": ""})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("file_content", "test_result")
    OUTPUT_TOOLTIPS = ("分子文件内容", "测试结果报告")
    FUNCTION = "test_molecular_workflow"
    CATEGORY = "🧪 ALCHEM/Simple Test"
    
    def test_molecular_workflow(self, molecular_file, test_mode, _alchem_node_id="", **kwargs):
        """
        测试分子工作流 - 使用新的molecular_utils工具
        
        展示方案B的标准用法：节点主动获取分子数据
        """
        try:
            # 🎯 使用新的工具函数获取分子数据
            from ..backend.molecular_utils import get_molecular_content
            
            print(f"🔍 原始输入: {molecular_file}")
            
            # 智能获取分子内容和元数据
            content, metadata = get_molecular_content(
                input_value=molecular_file,
                node_id=_alchem_node_id,
                fallback_to_file=True
            )
            
            print(f"🎯 工具函数处理结果:")
            print(f"   成功: {metadata.get('success')}")
            print(f"   来源: {metadata.get('source')}")
            print(f"   内容长度: {len(content)} 字符")
            
            # 更新molecular_file为实际内容
            molecular_file = content
            
            # 获取节点ID用于调试  
            node_id = metadata.get('node_id', 'unknown')
            
            print(f"🧪 简洁测试节点执行 - 节点ID: {node_id}")
            print(f"   模式: {test_mode}")
            print(f"   molecular_file类型: {type(molecular_file)}")
            print(f"   molecular_file长度: {len(str(molecular_file))}")
            print(f"   所有kwargs: {list(kwargs.keys())}")
            
            # 🎯 现在使用新工具，分析处理结果
            if not metadata.get('success'):
                # 数据获取失败
                error_info = metadata.get('error', '未知错误')
                test_result = f"""❌ 分子数据获取失败
                
输入: {str(molecular_file)[:100]}...
错误: {error_info}
来源: {metadata.get('source', 'unknown')}

🔧 方案B工具函数调试信息:
- 节点ID: {node_id}
- 输入类型: {metadata.get('input_type')}
- 是否文件名: {metadata.get('is_filename')}
- 尝试的数据源: {metadata.get('source')}
- 内存错误: {metadata.get('memory_error', '无')}
- 文件错误: {metadata.get('file_error', '无')}

方案B架构状态: 工具函数工作正常，但数据源有问题"""
                
                return (str(molecular_file), test_result)
            
            else:
                # 🎉 数据获取成功！
                content = molecular_file  # 已经是正确的内容
                
                # 使用元数据中的分析结果
                file_format = metadata.get('format_name', 'Unknown')
                atoms_count = metadata.get('atoms', 'N/A')
                total_lines = metadata.get('total_lines', len(content.split('\n')))
                data_source = metadata.get('source', 'unknown')
                
                test_result = f"""✅ 方案B测试成功 - 工具函数完美工作！
                
🎯 新架构验证：
- molecular_utils工具 ✅ 正常工作
- 智能数据获取 ✅ 成功识别和转换
- 后端内存 ✅ 数据可用
- 节点处理 ✅ 正常执行

📊 文件分析（来自工具函数）：
- 格式: {file_format}
- 数据来源: {data_source}
- 总行数: {total_lines}
- 原子数: {atoms_count}
- 内容长度: {len(content)} 字符
- 测试模式: {test_mode}

🔧 方案B架构优势：
- ✅ 不依赖execution_hook，更稳定
- ✅ 智能判断输入类型（文件名/内容）
- ✅ 自动内存查找和文件系统回退
- ✅ 详细的元数据和错误信息
- ✅ 更好的调试和维护性

🚀 数据流验证: 上传→内存→工具函数→节点接收内容 ✅"""

                return (content[:500] + "..." if len(content) > 500 else content, test_result)
                
        except Exception as e:
            error_result = f"""❌ 测试异常: {str(e)}

这可能表明：
1. execution_hook安装有问题
2. 数据类型处理有问题  
3. 后端内存访问异常"""
            
            return (str(molecular_file), error_result)
    
    @classmethod
    def IS_CHANGED(cls, molecular_file, test_mode):
        # 基于内容和模式生成哈希
        content = f"{molecular_file}_{test_mode}_{time.time()}"
        return hashlib.md5(content.encode()).hexdigest()


# 节点注册
NODE_CLASS_MAPPINGS = {
    "SimpleUploadAndDisplayTestNode": SimpleUploadAndDisplayTestNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SimpleUploadAndDisplayTestNode": "🧪🎯 Simple Upload+3D Test", 
}