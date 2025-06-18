"""
🧪⚗️ RDKit分子编辑器节点

基于MolstarDisplayMixin架构的专业分子编辑节点，提供：
- 氢原子智能添加/移除
- 3D结构优化和能量最小化  
- 分子标准化和清理
- 低能构象生成
- 完美集成3D显示功能
"""

# 🔧 修复：避免与ComfyUI的nodes模块冲突，使用直接文件导入
import sys
import os
import importlib.util

# 计算项目根目录
current_file = os.path.abspath(__file__)
rdkit_extension_dir = os.path.dirname(os.path.dirname(current_file))
project_root = os.path.dirname(rdkit_extension_dir) 

# 🔑 解决方案：直接从文件路径导入，但设置正确的模块上下文
mixin_file_path = os.path.join(project_root, 'nodes', 'mixins', 'molstar_display_mixin.py')

# 确保项目根目录和nodes目录都在sys.path中，供MolstarDisplayMixin内部导入使用
if project_root not in sys.path:
    sys.path.insert(0, project_root)

nodes_dir = os.path.join(project_root, 'nodes')
if nodes_dir not in sys.path:
    sys.path.insert(0, nodes_dir)

# 使用importlib导入，但设置正确的模块名避免冲突
spec = importlib.util.spec_from_file_location("alchem_molstar_display_mixin", mixin_file_path)
mixin_module = importlib.util.module_from_spec(spec)

# 🔑 关键：设置模块的搜索路径，让它能找到backend
mixin_module.__file__ = mixin_file_path
mixin_module.__path__ = [os.path.dirname(mixin_file_path)]

spec.loader.exec_module(mixin_module)
MolstarDisplayMixin = mixin_module.MolstarDisplayMixin

print(f"✅ MolstarDisplayMixin导入成功 (避免ComfyUI nodes冲突)")

# 🔧 先检查RDKit依赖，再导入RDKit相关模块
from ..utils.dependency_check import ensure_rdkit

# 确保RDKit可用，不可用就直接报错
ensure_rdkit()

# RDKit可用后，安全导入RDKit处理器
from ..backend.rdkit_processor import RDKitProcessor


class RDKitMolecularEditor(MolstarDisplayMixin):
    """
    🧪⚗️ RDKit分子编辑器 - 专业化学编辑节点
    
    📋 节点类型: 中间处理节点 (基于SimpleTabAwareProcessor模式)
    📥 输入模式: 内容输入 (input_molecular_content)
    📤 输出模式: 编辑后内容 + 详细报告
    🔗 工作流位置: 上游分子节点 → RDKit编辑 → 下游节点/3D显示
    
    🧪 核心功能:
    - ✅ 氢原子智能添加/移除 (基于RDKit算法)
    - ✅ 3D结构优化和能量最小化 (UFF力场)
    - ✅ 分子标准化和结构清理
    - ✅ 低能构象生成和筛选
    - ✅ 完美集成现有3D显示系统
    - ✅ Tab感知内存管理和节点ID绑定
    
    🚀 Mixin集成优势:
    - 零配置3D显示 - 编辑结果立即可视化
    - 标准化错误处理 - 专业的错误信息
    - 自动调试信息 - 详细的处理报告
    - 强制IS_CHANGED - 确保缓存一致性
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                **cls.get_processing_input_config(
                    content_param="input_molecular_content",
                    output_param="output_filename",
                    custom_config={
                        'output_config': {
                            "default": "rdkit_edited.pdb",
                            "tooltip": "RDKit专业编辑后的分子 - 支持3D显示和实时同步"
                        }
                    }
                ),
                
                # RDKit编辑操作选项
                "edit_operation": ([
                    "add_hydrogens",        # 添加氢原子 (智能算法)
                    "remove_hydrogens",     # 移除氢原子
                    "optimize_structure",   # 3D结构优化 (UFF力场)
                    "standardize_mol",      # 分子标准化和清理
                    "generate_conformer"    # 生成低能构象
                ], {
                    "default": "add_hydrogens",
                    "tooltip": "选择RDKit分子编辑操作"
                }),
                
                # 优化参数
                "max_iterations": ("INT", {
                    "default": 1000,
                    "min": 100,
                    "max": 5000,
                    "step": 100,
                    "tooltip": "3D结构优化最大迭代次数 (仅优化和构象生成时使用)"
                }),
                
                # 构象生成参数
                "num_conformers": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 10,
                    "tooltip": "生成构象数量 (仅构象生成时使用)"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("edited_content", "edit_report", "debug_info")
    FUNCTION = "edit_molecule_with_rdkit"
    CATEGORY = "🧪 ALCHEM/RDKit"
    
    def edit_molecule_with_rdkit(self, input_molecular_content, output_filename, 
                               edit_operation, max_iterations, num_conformers, **kwargs):
        """🧪 RDKit专业分子编辑主函数"""
        
        # 🔑 修复：确保节点ID正确传递，如果_alchem_node_id为空，让Mixin自动获取
        node_id = kwargs.get('_alchem_node_id', '')
        if not node_id:
            print("⚠️ _alchem_node_id为空，将由Mixin自动获取节点ID")
        
        # 🔑 一行代码完成RDKit编辑流程！
        # 利用MolstarDisplayMixin的process_direct_content方法
        return self.process_direct_content(
            content=input_molecular_content,
            output_filename=output_filename,
            node_id=node_id,  # 传递给Mixin，如果为空会自动获取
            processing_func=self._rdkit_edit_molecule,
            # 传递给处理函数的参数
            edit_operation=edit_operation,
            max_iterations=max_iterations,
            num_conformers=num_conformers
        )
    
    def _rdkit_edit_molecule(self, content: str, edit_operation: str, 
                           max_iterations: int, num_conformers: int) -> str:
        """
        RDKit分子编辑核心逻辑
        
        Args:
            content: 输入的分子内容
            edit_operation: 编辑操作类型
            max_iterations: 最大迭代次数
            num_conformers: 构象数量
            
        Returns:
            编辑后的分子内容字符串
        """
        try:
            # 1. 解析输入分子
            mol, detected_format = RDKitProcessor.parse_molecular_content(content)
            
            if mol is None:
                raise ValueError(f"RDKit无法解析分子结构 (检测格式: {detected_format})")
            
            print(f"🧪 RDKit解析成功: {detected_format}格式, {mol.GetNumAtoms()}个原子")
            
            # 2. 执行编辑操作
            original_atoms = mol.GetNumAtoms()
            
            if edit_operation == "add_hydrogens":
                edited_mol = RDKitProcessor.add_hydrogens(mol)
                operation_desc = "添加氢原子"
                
            elif edit_operation == "remove_hydrogens":
                edited_mol = RDKitProcessor.remove_hydrogens(mol)
                operation_desc = "移除氢原子"
                
            elif edit_operation == "optimize_structure":
                edited_mol = RDKitProcessor.optimize_structure_3d(mol, max_iterations)
                operation_desc = f"3D结构优化 ({max_iterations}次迭代)"
                
            elif edit_operation == "standardize_mol":
                edited_mol = RDKitProcessor.standardize_molecule(mol)
                operation_desc = "分子标准化"
                
            elif edit_operation == "generate_conformer":
                edited_mol = RDKitProcessor.generate_conformer(mol, num_conformers, max_iterations)
                operation_desc = f"构象生成 ({num_conformers}个构象)"
                
            else:
                edited_mol = mol
                operation_desc = "无操作"
            
            if edited_mol is None:
                raise ValueError(f"RDKit编辑操作失败: {edit_operation}")
            
            # 3. 转换回字符串格式
            edited_content = RDKitProcessor.mol_to_content(edited_mol, detected_format, content)
            
            # 4. 生成编辑报告
            edited_atoms = edited_mol.GetNumAtoms()
            atom_change = edited_atoms - original_atoms
            
            print(f"✅ RDKit编辑完成: {operation_desc}")
            print(f"   原子数变化: {original_atoms} → {edited_atoms} ({atom_change:+d})")
            
            return edited_content
            
        except Exception as e:
            error_msg = f"RDKit编辑失败: {str(e)}"
            print(f"❌ {error_msg}")
            
            # 返回原始内容并添加错误信息
            return f"# {error_msg}\n# 原始内容:\n{content}"
    
    @classmethod
    def IS_CHANGED(cls, input_molecular_content, output_filename, edit_operation, 
                   max_iterations, num_conformers, _alchem_node_id=""):
        """🔥 强制执行IS_CHANGED - 确保RDKit编辑后数据一致性"""
        return cls.simple_force_execute_is_changed(
            input_molecular_content=input_molecular_content,
            output_filename=output_filename,
            edit_operation=edit_operation,
            max_iterations=max_iterations,
            num_conformers=num_conformers,
            _alchem_node_id=_alchem_node_id
        )