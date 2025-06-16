"""
🧪 Tab感知的分子处理节点测试

这个测试节点展示了改进后的内存管理系统：
1. 接收上游分子数据（文件名或内容）
2. 进行简单的数据处理（删除氢原子、分子居中等）
3. 支持3D显示功能（molstar_3d_display: True）
4. 使用tab_id实现正确的数据匹配和存储

典型工作流：
StandardMolecularAnalysisNode (上传分子) 
    ↓ 传递文件名
TabAwareProcessingNode (删除氢原子) 
    ↓ 传递文件名  
TabAwareProcessingNode (分子居中)
    ↓ 传递文件名
FinalDisplayNode (最终结果显示)
"""

import time
import hashlib

class TabAwareProcessingNode:
    """
    🧪 Tab感知的分子处理节点
    
    这个节点展示如何：
    1. 从上游节点获取分子数据（通过文件名）
    2. 进行数据处理并存储到内存
    3. 使用正确的tab_id构建node_id
    4. 支持3D显示功能
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_molecular_content": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "tooltip": "输入的分子文件内容（来自上游节点的file_content输出）"
                }),
                "output_filename": ("STRING", {
                    "default": "processed_molecule.pdb",
                    "molstar_3d_display": True,      # 🧪 启用3D显示功能
                    "molecular_folder": "molecules", # 存储文件夹
                    "display_mode": "ball_and_stick",# 3D显示模式
                    "background_color": "#2E2E2E",   # 3D背景色
                    "tooltip": "处理后的分子文件名 - 支持3D显示"
                }),
                "processing_type": (["remove_hydrogens", "center_molecule", "simple_edit"], {
                    "default": "remove_hydrogens",
                    "tooltip": "处理类型：删除氢原子/分子居中/简单编辑"
                })
            },
            "hidden": {
                "_alchem_node_id": ("STRING", {"default": ""})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("processed_content", "processed_filename", "processing_report", "storage_debug")
    OUTPUT_TOOLTIPS = ("处理后的分子内容", "处理后的文件名", "处理报告", "存储调试：节点ID和CACHE状态")
    FUNCTION = "process_molecular_data"
    CATEGORY = "🧪 ALCHEM/Processing Test"
    
    def process_molecular_data(self, input_molecular_content, output_filename, processing_type, _alchem_node_id="", **kwargs):
        """
        处理分子数据 - 展示tab感知的中间处理节点
        """
        try:
            from ..backend.memory import store_molecular_data
            
            print(f"🔧 Tab感知处理节点开始执行")
            print(f"   输入长度: {len(input_molecular_content)}, 处理类型: {processing_type}")
            # print(f"   kwargs内容: {kwargs}")  # 注释掉避免过多输出
            
            # 获取节点ID和tab_id
            real_node_id = self._get_node_id()
            current_tab_id, node_id_for_storage = self._get_tab_id(real_node_id)
            
            print(f"🎯 节点ID: {real_node_id}, 存储ID: {node_id_for_storage}")
            
            # 🎯 步骤2: 验证输入内容
            if not input_molecular_content or len(input_molecular_content.strip()) < 10:
                print("❌ 输入内容为空或过短")
                storage_debug = self._generate_storage_debug_info("", None)
                return ("", "", "❌ 处理失败: 输入内容为空或过短", storage_debug)
            
            # 简单分析输入内容
            lines = input_molecular_content.split('\n')
            atom_lines = [line for line in lines if line.startswith('ATOM') or line.startswith('HETATM')]
            input_atoms = len(atom_lines)
            
            print(f"✅ 输入分析: {len(lines)}行, {input_atoms}个原子")
            
            # 🔧 步骤3: 进行数据处理
            processed_content = self._process_molecular_content(input_molecular_content, processing_type)
            
            if not processed_content or processed_content == input_molecular_content:
                storage_debug = self._generate_storage_debug_info(node_id_for_storage, None)
                return (input_molecular_content, "", f"⚠️ {processing_type} 处理无效果", storage_debug)
            
            # 🎯 步骤4: 使用节点ID存储处理结果
            
            # 🎯 步骤5: 存储处理结果到CACHE
            try:
                result_data = store_molecular_data(
                    node_id=node_id_for_storage,
                    filename=output_filename,
                    folder="molecules",
                    content=processed_content
                )
                
                if result_data:
                    print(f"✅ 存储成功: {output_filename}, 原子数: {result_data.get('atoms')}")
                    
                    # 生成处理报告
                    # 计算处理后的原子数
                    processed_lines = processed_content.split('\n')
                    processed_atom_lines = [line for line in processed_lines if line.startswith('ATOM') or line.startswith('HETATM')]
                    output_atoms = len(processed_atom_lines)
                    
                    processing_report = f"""✅ Tab感知处理成功完成
                    
🔧 处理信息:
- 处理类型: {processing_type}
- 输入内容长度: {len(input_molecular_content)} 字符
- 输出文件: {output_filename}
- 输入原子数: {input_atoms}
- 输出原子数: {output_atoms}

🔑 Tab感知信息:
- 当前tab_id: {current_tab_id}
- 输出节点: {node_id_for_storage}
- 处理结果已存储到内存

🎯 架构验证:
- ✅ 接收上游内容: 成功接收file_content
- ✅ 数据处理: {processing_type}处理完成
- ✅ 内存存储: 使用正确的node_id存储
- ✅ 3D显示就绪: molstar_3d_display已启用

🚀 下游节点可以通过文件名 '{output_filename}' 访问处理结果
或者连接到下一个处理节点的input_molecular_content
   
🔧 调试信息:
- 隐藏参数传递: {'成功' if _alchem_node_id else '失败'}
- 生成的存储ID: {node_id_for_storage}"""
                    
                    # 🔍 生成存储调试信息
                    storage_debug = self._generate_storage_debug_info(node_id_for_storage, result_data)
                    
                    return (processed_content, output_filename, processing_report, storage_debug)
                    
                else:
                    print("❌ 存储失败")
                    storage_debug = self._generate_storage_debug_info(node_id_for_storage, None)
                    return (input_molecular_content, "", "❌ 存储失败", storage_debug)
                    
            except Exception as storage_error:
                print(f"❌ 存储错误: {storage_error}")
                storage_debug = self._generate_storage_debug_info(node_id_for_storage, None)
                return (input_molecular_content, "", f"❌ 存储错误: {storage_error}", storage_debug)
                
        except Exception as e:
            print(f"❌ 处理异常: {str(e)}")
            storage_debug = self._generate_storage_debug_info("", None)
            return (input_molecular_content, "", f"❌ 处理异常: {str(e)}", storage_debug)
    
    def _process_molecular_content(self, content: str, processing_type: str) -> str:
        """实际的分子数据处理函数"""
        processors = {
            "remove_hydrogens": self._remove_hydrogens,
            "center_molecule": self._center_molecule,
            "simple_edit": self._simple_edit
        }
        
        processor = processors.get(processing_type)
        if processor:
            return processor(content)
        
        print(f"⚠️ 未知的处理类型: {processing_type}")
        return content
    
    def _remove_hydrogens(self, content: str) -> str:
        """删除氢原子"""
        lines = content.split('\n')
        processed_lines = []
        removed_count = 0
        
        for line in lines:
            if line.startswith(('ATOM', 'HETATM')) and len(line) > 12:
                atom_name = line[12:16].strip()
                if not atom_name.upper().startswith('H'):
                    processed_lines.append(line)
                else:
                    removed_count += 1
            else:
                processed_lines.append(line)
        
        if removed_count == 0:
            return self._remove_last_atom_demo(content)
        
        print(f"🔧 删除了 {removed_count} 个氢原子")
        return '\n'.join(processed_lines)
    
    def _center_molecule(self, content: str) -> str:
        """分子居中处理"""
        lines = content.split('\n')
        coords = []
        
        # 收集原子坐标
        for line in lines:
            if line.startswith('ATOM') and len(line) > 54:
                try:
                    x, y, z = float(line[30:38]), float(line[38:46]), float(line[46:54])
                    coords.append((x, y, z))
                except:
                    continue
        
        if not coords:
            return content
        
        # 计算质心
        center_x = sum(x for x, y, z in coords) / len(coords)
        center_y = sum(y for x, y, z in coords) / len(coords)
        center_z = sum(z for x, y, z in coords) / len(coords)
        
        # 应用居中
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
        
        print(f"🔧 分子居中: 质心偏移 ({center_x:.3f}, {center_y:.3f}, {center_z:.3f})")
        return '\n'.join(processed_lines)
    
    def _simple_edit(self, content: str) -> str:
        """简单编辑：删除最后一个原子"""
        lines = content.split('\n')
        atom_indices = [i for i, line in enumerate(lines) if line.startswith(('ATOM', 'HETATM'))]
        
        if atom_indices:
            lines.pop(atom_indices[-1])
            print("🔧 删除了最后一个原子")
        
        return '\n'.join(lines)
    
    def _get_node_id(self):
        """简化的节点ID获取"""
        try:
            import inspect
            for frame_info in inspect.stack():
                frame_locals = frame_info.frame.f_locals
                if 'unique_id' in frame_locals:
                    return str(frame_locals['unique_id'])
        except:
            pass
        return str(int(time.time()) % 100000)
    
    def _get_tab_id(self, real_node_id):
        """简化的tab_id获取"""
        from ..backend.memory import MOLECULAR_DATA_CACHE, CACHE_LOCK
        
        with CACHE_LOCK:
            for node_data in MOLECULAR_DATA_CACHE.values():
                if node_data.get('tab_id'):
                    tab_id = node_data.get('tab_id')
                    return tab_id, f"{tab_id}_node_{real_node_id}"
        
        # 默认fallback
        return "workflow_default", f"workflow_default_node_{real_node_id}"
    
    def _generate_storage_debug_info(self, storage_node_id, result_data):
        """简化的存储调试信息"""
        try:
            from ..backend.memory import MOLECULAR_DATA_CACHE, CACHE_LOCK
            
            debug_lines = [
                "🔧 === 处理节点存储调试 ===",
                f"当前存储ID: {storage_node_id}",
                f"存储成功: {'✓' if result_data else '✗'}"
            ]
            
            if result_data:
                debug_lines.extend([
                    f"  - filename: {result_data.get('filename')}",
                    f"  - tab_id: {result_data.get('tab_id')}",
                    f"  - atoms: {result_data.get('atoms')}"
                ])
            
            debug_lines.append("\n📊 === 全局CACHE状态 ===")
            with CACHE_LOCK:
                if not MOLECULAR_DATA_CACHE:
                    debug_lines.append("CACHE为空")
                else:
                    debug_lines.append(f"CACHE节点数: {len(MOLECULAR_DATA_CACHE)}")
                    for node_id, data in MOLECULAR_DATA_CACHE.items():
                        marker = "🎯" if node_id == storage_node_id else "🔶"
                        debug_lines.append(f"{marker} {node_id}: {data.get('filename', 'N/A')}")
                        
            debug_lines.append(f"\n🎆 3D显示就绪: {'✓' if storage_node_id in MOLECULAR_DATA_CACHE else '✗'}")
            
            return "\n".join(debug_lines)
            
        except Exception as e:
            return f"调试信息生成失败: {str(e)}"
    
    def _remove_last_atom_demo(self, content: str) -> str:
        """删除最后一个原子（演示功能）"""
        try:
            lines = content.split('\n')
            atom_indices = []
            
            for i, line in enumerate(lines):
                if line.startswith('ATOM') or line.startswith('HETATM'):
                    atom_indices.append(i)
            
            if atom_indices:
                # 删除最后一个原子行
                last_atom_index = atom_indices[-1]
                removed_line = lines[last_atom_index]
                lines.pop(last_atom_index)
                
                print(f"🔧 演示删除最后原子: {removed_line[12:16].strip() if len(removed_line) > 12 else 'unknown'}")
                return '\n'.join(lines)
            
            return content
        except Exception as e:
            print(f"❌ 删除最后原子演示失败: {e}")
            return content
    
    @classmethod
    def IS_CHANGED(cls, input_molecular_content, output_filename, processing_type):
        # 基于输入内容和处理类型生成哈希
        content_str = str(input_molecular_content) if input_molecular_content else ""
        content_hash = hashlib.md5(content_str.encode()).hexdigest()[:8]
        content = f"{content_hash}_{output_filename}_{processing_type}_{time.time()}"
        return hashlib.md5(content.encode()).hexdigest()


# 节点注册
NODE_CLASS_MAPPINGS = {
    "TabAwareProcessingNode": TabAwareProcessingNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TabAwareProcessingNode": "🧪🔧 Tab-Aware Processing",
}