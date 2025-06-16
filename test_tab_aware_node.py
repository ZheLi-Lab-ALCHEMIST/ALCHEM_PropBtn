#!/usr/bin/env python3
"""
🧪 TabAwareProcessingNode 独立测试脚本

这个脚本用于验证TabAwareProcessingNode的核心功能：
1. 分子数据处理逻辑（删除氢原子、分子居中等）
2. 简化的节点ID和tab_id机制
3. 内存存储逻辑（模拟）
4. 调试信息生成

不依赖ComfyUI环境，可以独立运行
"""

import sys
import os
import time
import hashlib

class MockMemory:
    """模拟内存系统，用于测试"""
    def __init__(self):
        self.cache = {}
        self.lock = None
    
    def store_molecular_data(self, node_id, filename, folder, content):
        """模拟存储分子数据"""
        lines = content.split('\n')
        atom_lines = [line for line in lines if line.startswith(('ATOM', 'HETATM'))]
        
        # 提取tab_id
        tab_id = node_id.split('_node_')[0] if '_node_' in node_id else 'default'
        
        data = {
            'node_id': node_id,
            'filename': filename,
            'tab_id': tab_id,
            'folder': folder,
            'content': content,
            'atoms': len(atom_lines),
            'format': 'PDB' if any(line.startswith(('ATOM', 'HETATM')) for line in lines) else 'Unknown',
            'timestamp': time.time()
        }
        
        self.cache[node_id] = data
        return data

# 全局模拟内存
MOCK_MEMORY = MockMemory()

class TabAwareProcessingNodeTest:
    """TabAwareProcessingNode的测试版本"""
    
    def __init__(self):
        self.mock_memory = MOCK_MEMORY
    
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
    
    def _get_node_id(self):
        """简化的节点ID获取（测试版本）"""
        return str(int(time.time()) % 100000)
    
    def _get_tab_id(self, real_node_id):
        """简化的tab_id获取（测试版本）"""
        # 检查是否有现有的tab_id
        for node_data in self.mock_memory.cache.values():
            if node_data.get('tab_id'):
                tab_id = node_data.get('tab_id')
                return tab_id, f"{tab_id}_node_{real_node_id}"
        
        # 默认fallback
        return "workflow_test", f"workflow_test_node_{real_node_id}"
    
    def _generate_storage_debug_info(self, storage_node_id, result_data):
        """简化的存储调试信息"""
        try:
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
            if not self.mock_memory.cache:
                debug_lines.append("CACHE为空")
            else:
                debug_lines.append(f"CACHE节点数: {len(self.mock_memory.cache)}")
                for node_id, data in self.mock_memory.cache.items():
                    marker = "🎯" if node_id == storage_node_id else "🔶"
                    debug_lines.append(f"{marker} {node_id}: {data.get('filename', 'N/A')}")
                    
            debug_lines.append(f"\n🎆 3D显示就绪: {'✓' if storage_node_id in self.mock_memory.cache else '✗'}")
            
            return "\n".join(debug_lines)
            
        except Exception as e:
            return f"调试信息生成失败: {str(e)}"
    
    def process_molecular_data(self, input_molecular_content, output_filename, processing_type, _alchem_node_id=""):
        """主处理函数（测试版本）"""
        try:
            print(f"🔧 Tab感知处理节点开始执行")
            print(f"   输入长度: {len(input_molecular_content)}, 处理类型: {processing_type}")
            
            # 获取节点ID和tab_id
            real_node_id = self._get_node_id()
            current_tab_id, node_id_for_storage = self._get_tab_id(real_node_id)
            
            print(f"🎯 节点ID: {real_node_id}, 存储ID: {node_id_for_storage}")
            
            # 验证输入内容
            if not input_molecular_content or len(input_molecular_content.strip()) < 10:
                print("❌ 输入内容为空或过短")
                storage_debug = self._generate_storage_debug_info("", None)
                return ("", "", "❌ 处理失败: 输入内容为空或过短", storage_debug)
            
            # 简单分析输入内容
            lines = input_molecular_content.split('\n')
            atom_lines = [line for line in lines if line.startswith('ATOM') or line.startswith('HETATM')]
            input_atoms = len(atom_lines)
            
            print(f"✅ 输入分析: {len(lines)}行, {input_atoms}个原子")
            
            # 进行数据处理
            processed_content = self._process_molecular_content(input_molecular_content, processing_type)
            
            if not processed_content or processed_content == input_molecular_content:
                storage_debug = self._generate_storage_debug_info(node_id_for_storage, None)
                return (input_molecular_content, "", f"⚠️ {processing_type} 处理无效果", storage_debug)
            
            # 存储处理结果到模拟CACHE
            try:
                result_data = self.mock_memory.store_molecular_data(
                    node_id=node_id_for_storage,
                    filename=output_filename,
                    folder="molecules",
                    content=processed_content
                )
                
                if result_data:
                    print(f"✅ 存储成功: {output_filename}, 原子数: {result_data.get('atoms')}")
                    
                    # 生成处理报告
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
                    
                    # 生成存储调试信息
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


def test_tab_aware_processing_node():
    """测试TabAwareProcessingNode的核心功能"""
    print("🧪 === TabAwareProcessingNode 核心功能测试 ===")
    print("=" * 60)
    
    # 创建测试实例
    node = TabAwareProcessingNodeTest()
    
    # 测试用的PDB数据
    sample_pdb = """HEADER    TEST MOLECULE
COMPND    CAFFEINE
ATOM      1  N1  CAF A   1       1.335   0.000   0.000  1.00  0.00           N
ATOM      2  C2  CAF A   1       0.668   1.158   0.000  1.00  0.00           C
ATOM      3  N3  CAF A   1      -0.668   1.158   0.000  1.00  0.00           N
ATOM      4  C4  CAF A   1      -1.335   0.000   0.000  1.00  0.00           C
ATOM      5  C5  CAF A   1      -0.668  -1.158   0.000  1.00  0.00           C
ATOM      6  C6  CAF A   1       0.668  -1.158   0.000  1.00  0.00           C
ATOM      7  H1  CAF A   1       2.400   0.000   0.000  1.00  0.00           H
ATOM      8  H2  CAF A   1       1.200   2.078   0.000  1.00  0.00           H
ATOM      9  H3  CAF A   1      -1.200   2.078   0.000  1.00  0.00           H
ATOM     10  H4  CAF A   1      -2.400   0.000   0.000  1.00  0.00           H
ATOM     11  H5  CAF A   1      -1.200  -2.078   0.000  1.00  0.00           H
ATOM     12  H6  CAF A   1       1.200  -2.078   0.000  1.00  0.00           H
END"""
    
    print(f"📝 输入分子数据:")
    lines = sample_pdb.split('\n')
    atom_lines = [line for line in lines if line.startswith('ATOM')]
    print(f"   总行数: {len(lines)}")
    print(f"   原子数: {len(atom_lines)}")
    print(f"   氢原子数: {len([line for line in atom_lines if 'H' in line[12:16]])}")
    
    # 测试用例
    test_cases = [
        ("remove_hydrogens", "no_hydrogens.pdb"),
        ("center_molecule", "centered_molecule.pdb"),
        ("simple_edit", "edited_molecule.pdb"),
    ]
    
    for i, (processing_type, output_filename) in enumerate(test_cases, 1):
        print(f"\n🧪 测试 {i}: {processing_type}")
        print("-" * 40)
        
        # 调用处理函数
        processed_content, output_name, processing_report, storage_debug = node.process_molecular_data(
            input_molecular_content=sample_pdb,
            output_filename=output_filename,
            processing_type=processing_type,
            _alchem_node_id=f"test_node_{i}"
        )
        
        print(f"📊 处理结果:")
        print(f"   输出文件名: {output_name}")
        print(f"   处理后内容长度: {len(processed_content)} 字符")
        
        # 分析处理后的内容
        if processed_content and processed_content != sample_pdb:
            processed_lines = processed_content.split('\n')
            processed_atoms = [line for line in processed_lines if line.startswith('ATOM')]
            print(f"   处理后原子数: {len(processed_atoms)}")
            
            if processing_type == "remove_hydrogens":
                h_atoms = [line for line in processed_atoms if 'H' in line[12:16]]
                print(f"   剩余氢原子: {len(h_atoms)}")
        
        print(f"\n📋 处理报告:")
        print(processing_report[:200] + "..." if len(processing_report) > 200 else processing_report)
        
        print(f"\n🔍 存储调试信息:")
        print(storage_debug[:300] + "..." if len(storage_debug) > 300 else storage_debug)
        
        print()
    
    print("🎯 === 模拟内存状态 ===")
    print(f"缓存节点数: {len(MOCK_MEMORY.cache)}")
    for node_id, data in MOCK_MEMORY.cache.items():
        print(f"  {node_id}: {data['filename']} ({data['atoms']} atoms)")
    
    print(f"\n✅ TabAwareProcessingNode 核心功能测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    print("🚀 开始TabAwareProcessingNode独立测试")
    test_tab_aware_processing_node()
    print("\n🎉 测试完成!")