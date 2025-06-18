"""RDKit扩展节点模块"""

# 导入所有RDKit节点
try:
    from .editor_node import RDKitMolecularEditor
    
    # 节点注册
    NODE_CLASS_MAPPINGS = {
        "RDKitMolecularEditor": RDKitMolecularEditor,
    }
    
    NODE_DISPLAY_NAME_MAPPINGS = {
        "RDKitMolecularEditor": "🧪⚗️ RDKit Molecular Editor",
    }
    
except Exception as e:
    # 🔧 只显示核心错误信息，避免冗长的RDKit安装提示重复显示
    if "No module named 'rdkit'" in str(e):
        print(f"⚠️ RDKit节点导入失败: RDKit未安装")
    elif "No module named 'nodes.mixins'" in str(e):
        print(f"⚠️ RDKit节点导入失败: MolstarDisplayMixin导入错误")
    else:
        print(f"⚠️ RDKit节点导入失败: {e}")
    
    NODE_CLASS_MAPPINGS = {}
    NODE_DISPLAY_NAME_MAPPINGS = {}