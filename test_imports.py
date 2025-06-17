#!/usr/bin/env python3
"""
测试所有模块的导入是否正常工作
"""

import sys
import os

# 添加项目根目录到Python路径（仅用于测试）
project_root = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(project_root)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_imports():
    """测试所有关键模块的导入"""
    
    print("🧪 开始测试ALCHEM_PropBtn模块导入...")
    print("=" * 60)
    
    # 测试后端模块
    print("\n📦 测试后端模块导入:")
    
    try:
        from ALCHEM_PropBtn.backend.logging_config import get_alchem_logger
        print("✅ backend.logging_config 导入成功")
    except Exception as e:
        print(f"❌ backend.logging_config 导入失败: {e}")
    
    try:
        from ALCHEM_PropBtn.backend.memory import MOLECULAR_DATA_CACHE, store_molecular_data
        print("✅ backend.memory 导入成功")
    except Exception as e:
        print(f"❌ backend.memory 导入失败: {e}")
    
    try:
        from ALCHEM_PropBtn.backend.molecular_utils import get_molecular_content
        print("✅ backend.molecular_utils 导入成功")
    except Exception as e:
        print(f"❌ backend.molecular_utils 导入失败: {e}")
    
    try:
        from ALCHEM_PropBtn.backend.websocket_server import notify_molecular_update
        print("✅ backend.websocket_server 导入成功")
    except Exception as e:
        print(f"❌ backend.websocket_server 导入失败: {e}")
    
    # 测试Mixin模块
    print("\n📦 测试Mixin模块导入:")
    
    try:
        from ALCHEM_PropBtn.nodes.mixins.molstar_display_mixin import MolstarDisplayMixin
        print("✅ nodes.mixins.molstar_display_mixin 导入成功")
    except Exception as e:
        print(f"❌ nodes.mixins.molstar_display_mixin 导入失败: {e}")
    
    # 测试节点模块（虽然已废弃，但确保它们仍能导入）
    print("\n📦 测试节点模块导入（已废弃但应能导入）:")
    
    try:
        from ALCHEM_PropBtn.nodes.examples_with_mixin import SimpleMolecularAnalyzer
        print("✅ nodes.examples_with_mixin 导入成功")
    except Exception as e:
        print(f"❌ nodes.examples_with_mixin 导入失败: {e}")
    
    # 测试主入口
    print("\n📦 测试主入口导入:")
    
    try:
        from ALCHEM_PropBtn import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
        print("✅ 主入口 __init__.py 导入成功")
        print(f"   - 已注册节点数: {len(NODE_CLASS_MAPPINGS)}")
    except Exception as e:
        print(f"❌ 主入口导入失败: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 导入测试完成!")

if __name__ == "__main__":
    test_imports()