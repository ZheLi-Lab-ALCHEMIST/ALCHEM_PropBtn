"""
🧪 简化分子处理节点

这是一个简化版本的处理节点，专注于功能验证：
1. 接收分子内容进行处理
2. 简单的ID生成策略
3. 基本的3D显示支持
"""

import time
import hashlib

class SimpleMolecularProcessNode:
    """
    🧪 简化分子处理节点
    
    专注于基本功能：
    - 接收上游分子内容
    - 进行简单处理（删除最后原子）
    - 支持3D显示
    - 简化的ID管理
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_content": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "输入的分子文件内容"
                }),
                "output_name": ("STRING", {
                    "default": "simple_processed.pdb",
                    "molstar_3d_display": True,      # 🧪 启用3D显示功能
                    "molecular_folder": "molecules", # 存储文件夹
                    "display_mode": "ball_and_stick",# 3D显示模式
                    "background_color": "#333333",   # 3D背景色
                    "tooltip": "输出文件名 - 支持3D显示"
                }),
                "process_action": (["remove_last_atom", "add_demo_atom", "keep_original"], {
                    "default": "remove_last_atom",
                    "tooltip": "处理动作"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("processed_content", "output_filename", "process_log")
    OUTPUT_TOOLTIPS = ("处理后的分子内容", "输出文件名", "处理日志")
    FUNCTION = "simple_process"
    CATEGORY = "🧪 ALCHEM/Simple"
    
    def simple_process(self, input_content, output_name, process_action):
        """
        简化的分子处理函数
        """
        try:
            print(f"🔧 简化处理节点执行:")
            print(f"   输入长度: {len(input_content)} 字符")
            print(f"   处理动作: {process_action}")
            print(f"   输出名称: {output_name}")
            
            # 验证输入
            if not input_content or len(input_content.strip()) < 5:
                error_msg = "输入内容为空或太短"
                return ("", output_name, f"❌ 错误: {error_msg}")
            
            # 分析输入
            lines = input_content.split('\n')
            atom_lines = [line for line in lines if line.startswith('ATOM') or line.startswith('HETATM')]
            input_atoms = len(atom_lines)
            
            print(f"   输入分析: {len(lines)} 行, {input_atoms} 个原子")
            
            # 执行处理
            if process_action == "remove_last_atom":
                processed_content = self._remove_last_atom(input_content)
            elif process_action == "add_demo_atom":
                processed_content = self._add_demo_atom(input_content)
            else:  # keep_original
                processed_content = input_content
            
            # 分析输出
            processed_lines = processed_content.split('\n')
            processed_atom_lines = [line for line in processed_lines if line.startswith('ATOM') or line.startswith('HETATM')]
            output_atoms = len(processed_atom_lines)
            
            print(f"   输出分析: {len(processed_lines)} 行, {output_atoms} 个原子")
            
            # 存储到内存以支持3D显示
            try:
                from ..backend.memory import store_molecular_data
                
                # 生成简单的存储ID
                storage_id = f"simple_process_{int(time.time()) % 1000000}"
                
                result_data = store_molecular_data(
                    node_id=storage_id,
                    filename=output_name,
                    folder="molecules",
                    content=processed_content
                )
                
                if result_data:
                    print(f"✅ 数据已存储: {storage_id}")
                    storage_success = True
                else:
                    print(f"⚠️ 数据存储失败")
                    storage_success = False
                    
            except Exception as storage_error:
                print(f"❌ 存储异常: {storage_error}")
                storage_success = False
            
            # 生成处理日志
            process_log = f"""🧪 简化处理完成

📊 处理统计:
- 动作: {process_action}
- 输入原子: {input_atoms}
- 输出原子: {output_atoms}
- 原子变化: {output_atoms - input_atoms:+d}

💾 存储状态:
- 文件名: {output_name}
- 内存存储: {'✅ 成功' if storage_success else '❌ 失败'}
- 3D显示: {'✅ 可用' if storage_success else '❌ 不可用'}

🎯 使用说明:
- processed_content 可连接到下游节点
- output_filename 支持🧪 3D查看
- 简化的ID管理确保基本功能正常"""
            
            return (processed_content, output_name, process_log)
            
        except Exception as e:
            error_msg = f"处理异常: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            return (input_content, output_name, f"❌ {error_msg}")
    
    def _remove_last_atom(self, content: str) -> str:
        """删除最后一个原子"""
        try:
            lines = content.split('\n')
            atom_indices = []
            
            # 找到所有原子行的索引
            for i, line in enumerate(lines):
                if line.startswith('ATOM') or line.startswith('HETATM'):
                    atom_indices.append(i)
            
            if atom_indices:
                # 删除最后一个原子行
                last_index = atom_indices[-1]
                removed_line = lines[last_index]
                lines.pop(last_index)
                
                print(f"🔧 删除原子: {removed_line[12:16].strip() if len(removed_line) > 12 else 'unknown'}")
                return '\n'.join(lines)
            else:
                print("⚠️ 没有找到原子行")
                return content
                
        except Exception as e:
            print(f"❌ 删除原子失败: {e}")
            return content
    
    def _add_demo_atom(self, content: str) -> str:
        """添加一个演示原子"""
        try:
            lines = content.split('\n')
            
            # 找到插入位置（最后一个原子行之后）
            insert_pos = len(lines)
            for i in reversed(range(len(lines))):
                if lines[i].startswith('ATOM') or lines[i].startswith('HETATM'):
                    insert_pos = i + 1
                    break
            
            # 创建新原子行（简单的碳原子）
            demo_atom = "ATOM   9999  C   DEMO A 999       0.000   0.000   0.000  1.00  0.00           C  "
            
            lines.insert(insert_pos, demo_atom)
            print(f"🔧 添加演示原子: C")
            
            return '\n'.join(lines)
            
        except Exception as e:
            print(f"❌ 添加演示原子失败: {e}")
            return content
    
    @classmethod
    def IS_CHANGED(cls, input_content, output_name, process_action):
        # 基于输入内容生成哈希
        content_str = str(input_content) if input_content else ""
        hash_input = f"{content_str[:100]}_{output_name}_{process_action}_{time.time()}"
        return hashlib.md5(hash_input.encode()).hexdigest()


# 节点注册
NODE_CLASS_MAPPINGS = {
    "SimpleMolecularProcessNode": SimpleMolecularProcessNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SimpleMolecularProcessNode": "🧪⚗️ Simple Process",
}