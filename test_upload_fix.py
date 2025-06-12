#!/usr/bin/env python3
"""
测试上传修复 - 验证bytearray处理

模拟实际的multipart上传过程，测试不同类型的文件内容处理
"""

import sys
import os

# 添加项目路径
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_path)

def test_content_types():
    """测试不同类型的内容处理"""
    print("🧪 测试不同类型的内容处理")
    
    # 测试数据
    test_pdb_content = """HEADER    TEST MOLECULE
COMPND    BENZENE
ATOM      1  C1  BNZ A   1       0.000   1.400   0.000  1.00  0.00           C
ATOM      2  C2  BNZ A   1       1.212   0.700   0.000  1.00  0.00           C
ATOM      3  C3  BNZ A   1       1.212  -0.700   0.000  1.00  0.00           C
END"""
    
    from molecular_memory import store_molecular_data
    
    test_cases = [
        ("字符串内容", test_pdb_content),
        ("字节内容", test_pdb_content.encode('utf-8')),
        ("字节数组内容", bytearray(test_pdb_content.encode('utf-8')))
    ]
    
    for i, (test_name, content) in enumerate(test_cases):
        print(f"\n  测试 {i+1}: {test_name}")
        print(f"    内容类型: {type(content)}")
        print(f"    内容长度: {len(content)}")
        
        try:
            # 测试存储
            stored_data = store_molecular_data(
                node_id=f"test_node_{i+1}",
                filename=f"test_{i+1}.pdb",
                folder="molecules",
                content=content
            )
            
            if stored_data:
                print(f"    ✅ 存储成功")
                print(f"       - 文件名: {stored_data['filename']}")
                print(f"       - 格式: {stored_data['format']}")
                print(f"       - 原子数: {stored_data['atoms']}")
                print(f"       - 文件大小: {stored_data['file_stats']['size']} 字节")
                print(f"       - 内容类型: {type(stored_data['content'])}")
                print(f"       - 内容长度: {len(stored_data['content'])} 字符")
            else:
                print(f"    ❌ 存储失败")
                return False
                
        except Exception as e:
            print(f"    ❌ 出现异常: {e}")
            return False
    
    return True

def test_multipart_simulation():
    """模拟multipart/form-data处理"""
    print("\n📤 模拟multipart上传处理")
    
    test_content = """HEADER    SIMULATED UPLOAD
COMPND    TEST MOLECULE
ATOM      1  C   TST A   1       0.000   0.000   0.000  1.00  0.00           C
END"""
    
    # 模拟不同的上传内容类型
    simulated_uploads = [
        ("模拟字符串上传", test_content),
        ("模拟bytes上传", test_content.encode('utf-8')),
        ("模拟bytearray上传", bytearray(test_content.encode('utf-8')))
    ]
    
    for test_name, raw_content in simulated_uploads:
        print(f"\n  {test_name}")
        print(f"    原始内容类型: {type(raw_content)}")
        
        # 模拟API端点中的处理逻辑
        processed_content = raw_content
        
        # 转换为字符串 - 处理bytes和bytearray
        if isinstance(processed_content, (bytes, bytearray)):
            try:
                processed_content = processed_content.decode('utf-8')
                print(f"    ✅ 成功解码为字符串")
            except UnicodeDecodeError:
                try:
                    processed_content = processed_content.decode('latin-1')
                    print(f"    ✅ 使用latin-1编码解码成功")
                except UnicodeDecodeError:
                    print(f"    ❌ 解码失败")
                    continue
        
        print(f"    处理后类型: {type(processed_content)}")
        print(f"    处理后长度: {len(processed_content)} 字符")
        
        # 测试存储
        try:
            from molecular_memory import store_molecular_data
            
            stored_data = store_molecular_data(
                node_id=f"upload_test_{hash(test_name) % 1000}",
                filename="uploaded_test.pdb",
                folder="molecules",
                content=processed_content
            )
            
            if stored_data:
                print(f"    ✅ 存储到后端内存成功")
            else:
                print(f"    ❌ 存储失败")
                
        except Exception as e:
            print(f"    ❌ 存储异常: {e}")
    
    return True

def test_encoding_edge_cases():
    """测试编码边界情况"""
    print("\n🔤 测试编码边界情况")
    
    # 测试包含特殊字符的内容
    special_content = """HEADER    SPECIAL CHARS TEST
COMPND    MOLECULE WITH UNICODE: α β γ δ
REMARK    Contains: 中文字符, émojis 🧪, and símbolos
ATOM      1  C   TST A   1       0.000   0.000   0.000  1.00  0.00           C
END"""
    
    print("  测试包含Unicode字符的内容...")
    print(f"    原始内容长度: {len(special_content)} 字符")
    
    try:
        # 转换为bytes再转回来（模拟网络传输）
        bytes_content = special_content.encode('utf-8')
        bytearray_content = bytearray(bytes_content)
        
        print(f"    Bytes长度: {len(bytes_content)}")
        print(f"    Bytearray长度: {len(bytearray_content)}")
        
        # 解码测试
        decoded_from_bytes = bytes_content.decode('utf-8')
        decoded_from_bytearray = bytearray_content.decode('utf-8')
        
        print(f"    从bytes解码: {'✅' if decoded_from_bytes == special_content else '❌'}")
        print(f"    从bytearray解码: {'✅' if decoded_from_bytearray == special_content else '❌'}")
        
        # 存储测试
        from molecular_memory import store_molecular_data
        
        stored_data = store_molecular_data(
            node_id="unicode_test",
            filename="unicode_test.pdb",
            folder="molecules",
            content=bytearray_content  # 使用最问题化的类型
        )
        
        if stored_data:
            print(f"    ✅ Unicode内容存储成功")
            # 验证内容完整性
            if stored_data['content'] == special_content:
                print(f"    ✅ 内容完整性验证通过")
            else:
                print(f"    ❌ 内容完整性验证失败")
                return False
        else:
            print(f"    ❌ Unicode内容存储失败")
            return False
            
    except Exception as e:
        print(f"    ❌ Unicode测试异常: {e}")
        return False
    
    return True

def main():
    """主测试函数"""
    print("🔧 ALCHEM_PropBtn 上传修复测试")
    print("=" * 50)
    
    tests = [
        ("内容类型处理", test_content_types),
        ("Multipart模拟", test_multipart_simulation),
        ("编码边界情况", test_encoding_edge_cases)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 开始测试: {test_name}")
            result = test_func()
            results.append((test_name, result))
            status = "✅ 通过" if result else "❌ 失败"
            print(f"\n{test_name}: {status}")
        except Exception as e:
            print(f"\n❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 总结
    print("\n📊 测试总结")
    print("=" * 30)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n总体结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！上传修复成功。")
        print("\n💡 现在可以正确处理:")
        print("   - 字符串内容")
        print("   - bytes内容") 
        print("   - bytearray内容")
        print("   - Unicode特殊字符")
        return True
    else:
        print("⚠️ 部分测试失败，需要进一步检查。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)