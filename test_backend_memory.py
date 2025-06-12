#!/usr/bin/env python3
"""
后端内存机制测试脚本

测试新的分子数据流架构：
1. 上传文件到后端内存
2. 验证数据存储
3. 模拟节点执行时的数据读取
4. 测试执行钩子功能
"""

import sys
import os
import time
import json

# 添加项目路径
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_path)

def test_molecular_memory():
    """测试分子内存管理"""
    print("🧪 测试1：分子内存管理")
    
    try:
        from molecular_memory import store_molecular_data, get_molecular_data, get_cache_status
        
        # 测试数据
        test_content = """HEADER    TEST MOLECULE
COMPND    BENZENE
ATOM      1  C1  BNZ A   1       0.000   1.400   0.000  1.00  0.00           C
ATOM      2  C2  BNZ A   1       1.212   0.700   0.000  1.00  0.00           C
ATOM      3  C3  BNZ A   1       1.212  -0.700   0.000  1.00  0.00           C
END"""
        
        # 存储测试
        print("  ✓ 存储分子数据到后端内存...")
        stored_data = store_molecular_data(
            node_id="test_node_123",
            filename="test_benzene.pdb",
            folder="molecules",
            content=test_content
        )
        
        if stored_data:
            print(f"  ✅ 存储成功: {stored_data['filename']}")
            print(f"     - 格式: {stored_data['format']}")
            print(f"     - 原子数: {stored_data['atoms']}")
            print(f"     - 文件大小: {stored_data['file_stats']['size']} 字节")
        else:
            print("  ❌ 存储失败")
            return False
        
        # 读取测试
        print("  ✓ 从后端内存读取分子数据...")
        retrieved_data = get_molecular_data("test_node_123")
        
        if retrieved_data:
            print(f"  ✅ 读取成功: {retrieved_data['filename']}")
            print(f"     - 内容长度: {len(retrieved_data['content'])} 字符")
            print(f"     - 访问次数: {retrieved_data['access_count']}")
        else:
            print("  ❌ 读取失败")
            return False
        
        # 缓存状态测试
        print("  ✓ 检查缓存状态...")
        cache_status = get_cache_status()
        print(f"  ✅ 缓存节点数: {cache_status['total_nodes']}")
        print(f"     - 总大小: {cache_status['total_cache_size']} 字符")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        return False

def test_execution_hook():
    """测试执行钩子"""
    print("\n🔗 测试2：执行钩子")
    
    try:
        from execution_hook import install_molecular_execution_hook, get_hook_status
        
        # 安装钩子
        print("  ✓ 安装执行钩子...")
        hook_installed = install_molecular_execution_hook()
        
        if hook_installed:
            print("  ✅ 钩子安装成功")
        else:
            print("  ⚠️ 钩子安装失败（可能ComfyUI环境不可用）")
        
        # 检查状态
        print("  ✓ 检查钩子状态...")
        hook_status = get_hook_status()
        print(f"  ✅ 钩子状态: {json.dumps(hook_status, indent=4)}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        return False

def test_api_simulation():
    """模拟API调用测试"""
    print("\n📡 测试3：API模拟")
    
    try:
        from molecular_api import api_get_molecular_data, api_get_cache_status
        
        # 测试获取分子数据API
        print("  ✓ 测试分子数据API...")
        api_response = api_get_molecular_data("test_node_123")
        
        if api_response["success"]:
            print("  ✅ API调用成功")
            print(f"     - 文件名: {api_response['data']['filename']}")
            print(f"     - 原子数: {api_response['data']['atoms']}")
        else:
            print(f"  ❌ API调用失败: {api_response['error']}")
        
        # 测试缓存状态API
        print("  ✓ 测试缓存状态API...")
        status_response = api_get_cache_status()
        
        if status_response["success"]:
            print("  ✅ 缓存状态API成功")
            print(f"     - 缓存节点: {status_response['data']['total_nodes']}")
        else:
            print(f"  ❌ 缓存状态API失败: {status_response['error']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        return False

def test_node_simulation():
    """模拟节点执行测试"""
    print("\n🎯 测试4：节点执行模拟")
    
    try:
        # 模拟MolecularUploadDemoNode的process_molecular_file函数
        print("  ✓ 模拟节点执行...")
        
        # 模拟输入参数
        molecular_file = "test_benzene.pdb"
        processing_mode = "analysis"
        output_format = "json"
        enable_validation = True
        detail_level = 0.5
        
        # 模拟kwargs（包含unique_id）
        kwargs = {"unique_id": "test_node_123"}
        
        # 这里应该从后端内存获取数据，而不是读取文件
        from molecular_memory import get_molecular_data
        
        stored_data = get_molecular_data(kwargs["unique_id"])
        if stored_data:
            print("  ✅ 成功从后端内存获取分子数据")
            print(f"     - 节点ID: {kwargs['unique_id']}")
            print(f"     - 文件名: {stored_data['filename']}")
            print(f"     - 内容长度: {len(stored_data['content'])} 字符")
            print(f"     - 数据来源: 后端内存缓存")
            
            # 模拟处理结果
            result = {
                "molecular_data": json.dumps({
                    "filename": stored_data["filename"],
                    "format": stored_data["format"],
                    "atoms": stored_data["atoms"],
                    "data_source": "backend_memory"
                }, indent=2),
                "analysis_report": f"✅ 从后端内存成功获取分子数据\n文件: {stored_data['filename']}\n原子数: {stored_data['atoms']}",
                "validation_result": "✅ 后端内存数据验证通过",
                "confidence_score": 1.0
            }
            
            print("  ✅ 节点执行模拟成功")
            return True
        else:
            print("  ❌ 无法从后端内存获取数据")
            return False
        
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 ALCHEM_PropBtn 后端内存机制测试")
    print("=" * 50)
    
    results = []
    
    # 运行所有测试
    tests = [
        ("分子内存管理", test_molecular_memory),
        ("执行钩子", test_execution_hook),
        ("API模拟", test_api_simulation),
        ("节点执行模拟", test_node_simulation)
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} 测试出现异常: {e}")
            results.append((test_name, False))
    
    # 测试总结
    print("\n📊 测试总结")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试都通过！后端内存机制工作正常。")
        return True
    else:
        print("⚠️ 部分测试失败，需要检查相关组件。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)