#!/usr/bin/env python3
"""
🧪 Tab感知内存管理调试脚本

用于测试新的tab_id机制和内存管理改进
"""

import sys
import os

# 添加项目路径到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_tab_aware_memory():
    """测试tab感知的内存管理"""
    print("🧪 Tab感知内存管理测试开始")
    print("=" * 60)
    
    try:
        # 导入必要模块
        from backend.memory import store_molecular_data, get_molecular_data, get_cache_status, clear_cache
        from backend.molecular_utils import get_molecular_content
        
        # 清理缓存
        clear_cache()
        print("🧹 清理缓存完成")
        
        # 模拟PDB数据
        sample_pdb = """HEADER    TEST MOLECULE
COMPND    TEST
ATOM      1  C1  TEST A   1       0.000   1.000   0.000  1.00  0.00           C
ATOM      2  C2  TEST A   1       1.000   0.000   0.000  1.00  0.00           C
ATOM      3  H1  TEST A   1       0.500   1.500   0.000  1.00  0.00           H
ATOM      4  H2  TEST A   1       1.500  -0.500   0.000  1.00  0.00           H
END"""
        
        print("\n🎯 步骤1: 测试简化的node_id格式")
        print("-" * 40)
        
        # 测试不同的节点ID格式
        test_cases = [
            ("workflow_abc12_node_23", "test_molecule1.pdb"),
            ("workflow_def34_node_45", "test_molecule2.pdb"),
            ("workflow_abc12_node_67", "processed_molecule1.pdb"),  # 同tab不同节点
        ]
        
        for node_id, filename in test_cases:
            print(f"\n📁 存储数据: {node_id} -> {filename}")
            
            result = store_molecular_data(
                node_id=node_id,
                filename=filename,
                folder="molecules",
                content=sample_pdb
            )
            
            if result:
                print(f"✅ 存储成功:")
                print(f"   节点ID: {result['node_id']}")
                print(f"   文件名: {result['filename']}")
                print(f"   tab_id: {result['tab_id']}")
                print(f"   原子数: {result['atoms']}")
            else:
                print(f"❌ 存储失败")
        
        print("\n🎯 步骤2: 查看缓存状态")
        print("-" * 40)
        
        cache_status = get_cache_status()
        print(f"📊 缓存统计:")
        print(f"   总节点数: {cache_status['total_nodes']}")
        print(f"   总缓存大小: {cache_status['total_cache_size']} 字符")
        
        print(f"\n📋 节点列表:")
        for node in cache_status['nodes']:
            print(f"   {node['node_id']} | {node['filename']} | tab: {node['tab_id']}")
        
        print("\n🎯 步骤3: 测试tab感知的数据获取")
        print("-" * 40)
        
        # 测试不同场景的数据获取
        test_queries = [
            ("test_molecule1.pdb", "workflow_abc12_node_99"),  # 同tab不同节点，应该找到
            ("test_molecule2.pdb", "workflow_def34_node_88"),  # 不同tab，应该找到对应的
            ("processed_molecule1.pdb", "workflow_abc12_node_77"),  # 同tab处理结果
            ("nonexistent.pdb", "workflow_abc12_node_66"),  # 不存在的文件
        ]
        
        for filename, query_node_id in test_queries:
            print(f"\n🔍 查询: {filename} (节点: {query_node_id})")
            
            content, metadata = get_molecular_content(
                input_value=filename,
                node_id=query_node_id,
                fallback_to_file=False  # 只测试内存
            )
            
            if metadata['success']:
                print(f"✅ 查询成功:")
                print(f"   来源: {metadata['source']}")
                print(f"   源节点: {metadata.get('source_node_id', 'N/A')}")
                print(f"   tab_id: {metadata.get('tab_id', 'N/A')}")
                print(f"   内容长度: {len(content)} 字符")
            else:
                print(f"❌ 查询失败: {metadata.get('error', '未知错误')}")
        
        print("\n🎯 步骤4: 测试中间处理节点场景")
        print("-" * 40)
        
        # 模拟中间处理节点的工作流
        print("📝 模拟工作流: upload -> process1 -> process2")
        
        # 步骤4.1: 模拟从process1节点获取数据并处理
        process1_node_id = "workflow_abc12_node_100"
        
        print(f"\n🔧 Process1节点 ({process1_node_id}) 获取数据:")
        content, metadata = get_molecular_content(
            input_value="test_molecule1.pdb",
            node_id=process1_node_id,
            fallback_to_file=False
        )
        
        if metadata['success']:
            print(f"✅ Process1获取成功")
            
            # 模拟处理：删除氢原子
            lines = content.split('\n')
            processed_lines = [line for line in lines if not (line.startswith('ATOM') and 'H' in line)]
            processed_content = '\n'.join(processed_lines)
            
            # 存储处理结果
            result = store_molecular_data(
                node_id=process1_node_id,
                filename="no_hydrogens.pdb",
                folder="molecules", 
                content=processed_content
            )
            
            if result:
                print(f"✅ Process1处理结果已存储:")
                print(f"   输出文件: {result['filename']}")
                print(f"   原子数: {result['atoms']} (删除氢原子)")
                
                # 步骤4.2: 模拟process2节点获取process1的结果
                process2_node_id = "workflow_abc12_node_101"
                
                print(f"\n🔧 Process2节点 ({process2_node_id}) 获取Process1结果:")
                content2, metadata2 = get_molecular_content(
                    input_value="no_hydrogens.pdb",
                    node_id=process2_node_id,
                    fallback_to_file=False
                )
                
                if metadata2['success']:
                    print(f"✅ Process2获取成功:")
                    print(f"   tab匹配: {metadata2.get('tab_id') == result.get('tab_id')}")
                    print(f"   原子数: {metadata2.get('atoms')}")
                else:
                    print(f"❌ Process2获取失败")
            else:
                print(f"❌ Process1处理结果存储失败")
        else:
            print(f"❌ Process1获取失败")
        
        print("\n🎯 步骤5: 最终缓存状态")
        print("-" * 40)
        
        final_cache = get_cache_status()
        print(f"📊 最终统计:")
        print(f"   总节点数: {final_cache['total_nodes']}")
        
        # 按tab_id分组显示
        from collections import defaultdict
        by_tab = defaultdict(list)
        
        for node in final_cache['nodes']:
            tab_id = node['tab_id'] or 'unknown'
            by_tab[tab_id].append(node)
        
        for tab_id, nodes in by_tab.items():
            print(f"\n📂 Tab: {tab_id}")
            for node in nodes:
                print(f"   └─ {node['node_id']} | {node['filename']} | {node['atoms']} atoms")
        
        print("\n✅ Tab感知内存管理测试完成!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


def test_frontend_hash_mechanism():
    """测试前端hash机制简化"""
    print("\n🔧 前端Hash机制测试")
    print("=" * 40)
    
    # 模拟前端生成node_id的新逻辑
    def generate_simple_node_id(tab_id, node_id):
        """模拟简化的前端node_id生成"""
        return f"{tab_id}_node_{node_id}"
    
    # 测试用例
    test_cases = [
        ("workflow_abc12", 23),
        ("workflow_def34", 45),
        ("workflow_gh567", 89),
    ]
    
    print("🆔 新的简化ID生成:")
    for tab_id, node_id in test_cases:
        simple_id = generate_simple_node_id(tab_id, node_id)
        print(f"   {tab_id} + {node_id} = {simple_id}")
    
    print("\n✅ 前端Hash机制简化测试完成")


if __name__ == "__main__":
    print("🚀 开始ALCHEM_PropBtn Tab感知调试")
    test_tab_aware_memory()
    test_frontend_hash_mechanism()
    print("\n🎉 所有测试完成!")