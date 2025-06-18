"""
🧪 RDKit核心处理器

基于RDKit的专业分子处理功能，包括：
- 智能分子格式解析
- 3D结构优化
- 氢原子管理
- 分子标准化
- 构象生成
"""

from ..utils.dependency_check import ensure_rdkit

# 确保RDKit可用，不可用直接报错
rdkit_modules = ensure_rdkit()
Chem = rdkit_modules['Chem']
AllChem = rdkit_modules['AllChem']
Descriptors = rdkit_modules['Descriptors']


class RDKitProcessor:
    """RDKit分子处理器"""
    
    @staticmethod
    def parse_molecular_content(content: str):
        """
        智能解析分子内容为RDKit分子对象
        
        Args:
            content: 分子文件内容字符串
            
        Returns:
            tuple: (mol_object, detected_format)
        """
        content = content.strip()
        
        # 1. 检测PDB格式
        if "ATOM" in content.upper() or "HETATM" in content.upper():
            mol = Chem.MolFromPDBBlock(content)
            if mol is not None:
                return mol, "PDB"
        
        # 2. 检测SDF格式 (有$$$$结束符)
        if "$$$$" in content:
            mol = Chem.MolFromMolBlock(content)
            if mol is not None:
                return mol, "SDF"
        
        # 3. 检测SMILES格式 (通常是单行或几行)
        if len(content.split('\n')) <= 2 and not content.startswith(('@', '>', '#')):
            mol = Chem.MolFromSmiles(content)
            if mol is not None:
                return mol, "SMILES"
        
        # 4. 尝试作为MOL格式解析
        mol = Chem.MolFromMolBlock(content)
        if mol is not None:
            return mol, "MOL"
        
        # 5. 最后尝试作为PDB解析 (某些PDB文件可能没有明显的ATOM标识)
        mol = Chem.MolFromPDBBlock(content)
        if mol is not None:
            return mol, "PDB"
        
        return None, "UNKNOWN"
    
    @staticmethod
    def mol_to_content(mol, target_format: str, original_content: str = "") -> str:
        """
        将RDKit分子对象转换为指定格式的字符串
        
        Args:
            mol: RDKit分子对象
            target_format: 目标格式 (PDB/SDF/MOL/SMILES)
            original_content: 原始内容，用于格式推断
            
        Returns:
            转换后的分子内容字符串
        """
        if mol is None:
            return original_content or "# 分子对象无效"
        
        target_format = target_format.upper()
        
        try:
            if target_format == "PDB":
                return Chem.MolToPDBBlock(mol)
            elif target_format == "SDF":
                return Chem.MolToMolBlock(mol)
            elif target_format == "MOL":
                return Chem.MolToMolBlock(mol)
            elif target_format == "SMILES":
                return Chem.MolToSmiles(mol)
            else:
                # 默认返回PDB格式
                return Chem.MolToPDBBlock(mol)
                
        except Exception as e:
            return f"# 格式转换失败: {str(e)}\n{original_content}"
    
    @staticmethod
    def add_hydrogens(mol):
        """
        添加氢原子
        
        Args:
            mol: RDKit分子对象
            
        Returns:
            添加氢原子后的分子对象
        """
        if mol is None:
            return None
        
        try:
            return Chem.AddHs(mol)
        except Exception as e:
            print(f"❌ 添加氢原子失败: {e}")
            return mol
    
    @staticmethod  
    def remove_hydrogens(mol):
        """
        移除氢原子
        
        Args:
            mol: RDKit分子对象
            
        Returns:
            移除氢原子后的分子对象
        """
        if mol is None:
            return None
        
        try:
            return Chem.RemoveHs(mol)
        except Exception as e:
            print(f"❌ 移除氢原子失败: {e}")
            return mol
    
    @staticmethod
    def optimize_structure_3d(mol, max_iterations: int = 1000):
        """
        3D结构优化
        
        Args:
            mol: RDKit分子对象
            max_iterations: 最大优化迭代次数
            
        Returns:
            优化后的分子对象
        """
        if mol is None:
            return None
        
        try:
            # 创建分子副本
            mol_copy = Chem.Mol(mol)
            
            # 添加氢原子 (优化需要)
            mol_copy = Chem.AddHs(mol_copy)
            
            # 生成初始3D构象
            embed_result = AllChem.EmbedMolecule(mol_copy)
            if embed_result != 0:
                print("⚠️ 3D构象生成失败，使用随机构象")
                AllChem.EmbedMolecule(mol_copy, useRandomCoords=True)
            
            # UFF力场优化
            optimize_result = AllChem.UFFOptimizeMolecule(mol_copy, maxIters=max_iterations)
            
            if optimize_result == 0:
                print(f"✅ 3D结构优化成功 (迭代次数: {max_iterations})")
            else:
                print(f"⚠️ 3D结构优化未完全收敛 (迭代次数: {max_iterations})")
            
            return mol_copy
            
        except Exception as e:
            print(f"❌ 3D结构优化失败: {e}")
            return mol
    
    @staticmethod
    def standardize_molecule(mol):
        """
        分子标准化
        
        包括：
        - 清理分子结构
        - 标准化芳香性
        - 移除立体化学信息（可选）
        
        Args:
            mol: RDKit分子对象
            
        Returns:
            标准化后的分子对象
        """
        if mol is None:
            return None
        
        try:
            # 清理分子
            mol_copy = Chem.Mol(mol)
            
            # 标准化芳香性
            Chem.SanitizeMol(mol_copy)
            
            # 设置芳香性
            Chem.SetAromaticity(mol_copy)
            
            print("✅ 分子标准化完成")
            return mol_copy
            
        except Exception as e:
            print(f"❌ 分子标准化失败: {e}")
            return mol
    
    @staticmethod
    def generate_conformer(mol, num_conformers: int = 1, max_iterations: int = 1000):
        """
        生成分子构象
        
        Args:
            mol: RDKit分子对象
            num_conformers: 生成构象数量
            max_iterations: 优化迭代次数
            
        Returns:
            包含构象的分子对象
        """
        if mol is None:
            return None
        
        try:
            # 创建分子副本并添加氢原子
            mol_copy = Chem.Mol(mol)
            mol_copy = Chem.AddHs(mol_copy)
            
            # 生成多个构象
            conformer_ids = AllChem.EmbedMultipleConfs(
                mol_copy, 
                numConfs=num_conformers,
                pruneRmsThresh=0.5  # 剔除相似构象
            )
            
            if len(conformer_ids) == 0:
                print("⚠️ 构象生成失败，使用随机构象")
                AllChem.EmbedMolecule(mol_copy, useRandomCoords=True)
                return mol_copy
            
            # 优化所有构象
            for conf_id in conformer_ids:
                AllChem.UFFOptimizeMolecule(mol_copy, confId=conf_id, maxIters=max_iterations)
            
            print(f"✅ 生成 {len(conformer_ids)} 个优化构象")
            return mol_copy
            
        except Exception as e:
            print(f"❌ 构象生成失败: {e}")
            return mol
    
    @staticmethod
    def calculate_basic_properties(mol):
        """
        计算基本分子性质
        
        Args:
            mol: RDKit分子对象
            
        Returns:
            包含分子性质的字典
        """
        if mol is None:
            return {}
        
        try:
            properties = {
                "molecular_weight": Descriptors.MolWt(mol),
                "logp": Descriptors.MolLogP(mol),
                "hbd": Descriptors.NumHDonors(mol),  # 氢键供体
                "hba": Descriptors.NumHAcceptors(mol),  # 氢键受体
                "rotatable_bonds": Descriptors.NumRotatableBonds(mol),
                "aromatic_rings": Descriptors.NumAromaticRings(mol),
                "heavy_atoms": mol.GetNumHeavyAtoms(),
                "total_atoms": mol.GetNumAtoms(),
            }
            
            return properties
            
        except Exception as e:
            print(f"❌ 分子性质计算失败: {e}")
            return {}