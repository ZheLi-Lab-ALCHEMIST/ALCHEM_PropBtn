#!/usr/bin/env python3
"""
测试节点语法的临时脚本
"""

import ast
import sys
import os

def check_syntax(file_path):
    """检查Python文件语法"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # 尝试解析AST
        ast.parse(source, filename=file_path)
        print(f"✅ {file_path} 语法正确")
        return True
        
    except SyntaxError as e:
        print(f"❌ {file_path} 语法错误:")
        print(f"   行 {e.lineno}: {e.text.strip() if e.text else ''}")
        print(f"   错误: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ {file_path} 检查失败: {e}")
        return False

if __name__ == "__main__":
    # 检查所有节点文件
    files_to_check = [
        "nodes/test_simple_node.py",
        "nodes/test_tab_aware_processing.py", 
        "nodes/standard_molecular_node.py"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            check_syntax(file_path)
        else:
            print(f"⚠️ 文件不存在: {file_path}")