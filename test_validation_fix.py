#!/usr/bin/env python3
"""
测试ComfyUI验证修复

验证节点输入验证逻辑是否正确处理后端内存中的文件
"""

import sys
import os

# 添加项目路径
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_path)

def test_input_types():
    """测试INPUT_TYPES方法"""
    print("🧪 测试1：INPUT_TYPES方法")
    
    try:
        from nodes import MolecularUploadDemoNode
        
        # 调用INPUT_TYPES
        input_types = MolecularUploadDemoNode.INPUT_TYPES()
        
        print("  ✓ INPUT_TYPES调用成功")
        print(f"  📋 输入类型: {input_types}")
        
        # 检查molecular_file字段
        molecular_file_config = input_types['required']['molecular_file']
        print(f"  🧪 molecular_file配置: {molecular_file_config}")
        
        # 验证现在是STRING类型
        if molecular_file_config[0] == "STRING":
            print("  ✅ molecular_file已修改为STRING类型（支持任意输入）")
            return True
        else:
            print(f"  ❌ molecular_file仍然是列表类型: {molecular_file_config[0]}")
            return False
            
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        return False

def test_validate_inputs():
    """测试VALIDATE_INPUTS方法"""
    print("\n🔍 测试2：VALIDATE_INPUTS方法")
    
    try:
        from nodes import MolecularUploadDemoNode
        
        # 先模拟在后端内存中存储一个文件
        print("  ✓ 模拟在后端内存中存储文件...")
        from molecular_memory import store_molecular_data
        
        test_content = """HEADER    TEST VALIDATION
COMPND    VALIDATION TEST
ATOM      1  C1  TST A   1       0.000   0.000   0.000  1.00  0.00           C
END"""
        
        stored_data = store_molecular_data(
            node_id="validation_test_node",
            filename="validation_test.pdb",
            content=test_content
        )
        
        if stored_data:
            print(f"  ✅ 测试文件已存储: {stored_data['filename']}")
        else:
            print("  ❌ 测试文件存储失败")
            return False
        
        # 测试验证函数
        print("  ✓ 测试VALIDATE_INPUTS...")
        
        # 测试1：验证存在于后端内存中的文件
        result1 = MolecularUploadDemoNode.VALIDATE_INPUTS("validation_test.pdb")
        print(f"  📋 验证后端内存文件结果: {result1}")
        
        if result1 is True:
            print("  ✅ 后端内存文件验证通过")
        else:
            print(f"  ❌ 后端内存文件验证失败: {result1}")
            return False
        
        # 测试2：验证不存在的文件
        result2 = MolecularUploadDemoNode.VALIDATE_INPUTS("nonexistent_file.pdb")
        print(f"  📋 验证不存在文件结果: {result2}")
        
        if isinstance(result2, str) and "未找到" in result2:
            print("  ✅ 不存在文件正确报错")
        else:
            print(f"  ❌ 不存在文件验证逻辑有问题: {result2}")
            return False
        
        # 测试3：验证默认占位符
        result3 = MolecularUploadDemoNode.VALIDATE_INPUTS("no_molecular_files_found.pdb")
        print(f"  📋 验证默认占位符结果: {result3}")
        
        if result3 is True:
            print("  ✅ 默认占位符验证通过")
        else:
            print(f"  ❌ 默认占位符验证失败: {result3}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_workflow_simulation():
    """模拟完整的工作流程"""
    print("\n🔄 测试3：工作流程模拟")
    
    try:
        from nodes import MolecularUploadDemoNode
        
        # 创建节点实例
        node = MolecularUploadDemoNode()
        
        # 模拟节点执行参数
        molecular_file = "validation_test.pdb"  # 这个文件在测试2中已经存储到后端内存
        processing_mode = "analysis"
        output_format = "json"
        enable_validation = True
        detail_level = 0.5
        
        print(f"  ✓ 模拟节点执行...")
        print(f"    - 分子文件: {molecular_file}")
        print(f"    - 处理模式: {processing_mode}")
        
        # 模拟执行（包含unique_id）
        kwargs = {"unique_id": "validation_test_node"}
        
        result = node.process_molecular_file(
            molecular_file=molecular_file,
            processing_mode=processing_mode,
            output_format=output_format,
            enable_validation=enable_validation,
            detail_level=detail_level,
            **kwargs
        )
        
        print(f"  ✅ 节点执行成功")
        print(f"    - 返回类型: {type(result)}")
        print(f"    - 返回长度: {len(result) if isinstance(result, tuple) else 'N/A'}")
        
        if isinstance(result, tuple) and len(result) >= 4:
            molecular_data, analysis_report, validation_result, confidence_score = result
            print(f"    - 分子数据长度: {len(molecular_data)} 字符")
            print(f"    - 分析报告长度: {len(analysis_report)} 字符")
            print(f"    - 置信度分数: {confidence_score}")
            return True
        else:
            print(f"  ❌ 返回结果格式不正确: {result}")
            return False
        
    except Exception as e:
        print(f"  ❌ 工作流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🔧 ComfyUI验证修复测试")
    print("=" * 50)
    
    tests = [
        ("INPUT_TYPES配置", test_input_types),
        ("VALIDATE_INPUTS逻辑", test_validate_inputs),
        ("工作流程模拟", test_workflow_simulation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} 测试出现异常: {e}")
            results.append((test_name, False))
    
    # 测试总结
    print("\n📊 测试总结")
    print("=" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！ComfyUI验证修复成功。")
        print("\n💡 修复要点:")
        print("   - molecular_file现在是STRING类型，支持任意输入")
        print("   - VALIDATE_INPUTS会检查后端内存中的文件")
        print("   - 节点可以正确处理上传到后端内存的文件")
        return True
    else:
        print("⚠️ 部分测试失败，需要进一步检查。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)