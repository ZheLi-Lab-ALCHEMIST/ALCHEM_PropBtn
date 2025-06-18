"""
🧪 RDKit依赖检查模块

简单直接的依赖管理：
- 需要RDKit就直接要求安装
- 不搞复杂的降级逻辑  
- 错误信息清晰，安装指导明确
"""

def check_rdkit_status():
    """
    检查RDKit安装状态
    
    Returns:
        tuple: (is_available: bool, error_message: str)
    """
    try:
        # 尝试导入RDKit核心模块
        from rdkit import Chem
        from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors
        
        # 简单测试RDKit是否正常工作
        test_mol = Chem.MolFromSmiles('CCO')
        if test_mol is None:
            return False, "RDKit导入成功但功能异常"
        
        return True, "RDKit可用"
        
    except ImportError as e:
        error_msg = f"""❌ RDKit未安装或版本不兼容！

🔧 推荐安装方法：
conda install -c conda-forge rdkit

🔧 备选安装方法：
pip install rdkit

📋 RDKit是专业的化学信息学库，ALCHEM RDKit扩展需要它来提供：
• 分子结构优化和能量最小化
• 氢原子的智能添加和移除
• 多种分子格式的精确转换 (PDB/SDF/MOL/SMILES)
• 分子描述符和物理化学性质计算
• 分子构象生成和标准化

💡 安装完成后请重启ComfyUI以加载RDKit扩展节点。

🔍 详细错误信息: {str(e)}"""
        
        return False, error_msg

def ensure_rdkit():
    """
    确保RDKit可用，不可用就直接报错
    
    这是给RDKit节点开头调用的函数，如果RDKit不可用会直接抛出异常。
    遵循"需要就要求安装"的原则，不搞复杂的降级逻辑。
    
    Raises:
        ImportError: 当RDKit不可用时
    """
    is_available, error_message = check_rdkit_status()
    
    if not is_available:
        raise ImportError(error_message)
    
    # RDKit可用，返回导入的模块供使用
    from rdkit import Chem
    from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors
    
    return {
        'Chem': Chem,
        'AllChem': AllChem, 
        'Descriptors': Descriptors,
        'rdMolDescriptors': rdMolDescriptors
    }