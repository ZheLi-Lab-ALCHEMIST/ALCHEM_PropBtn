"""
🧪⚗️ ALCHEM RDKit扩展

基于ALCHEM_PropBtn的MolstarDisplayMixin架构，提供专业的RDKit分子编辑功能。

核心特性:
- 完全基于现有的MolstarDisplayMixin架构
- 专业的分子编辑和结构优化
- 智能格式转换和分子分析
- 与现有3D显示系统无缝集成

依赖要求:
- RDKit >= 2023.3.1

安装方法:
conda install -c conda-forge rdkit
# 或
pip install rdkit
"""

# 导入所有RDKit节点
from .nodes import *

__version__ = "1.0.0"
__author__ = "ALCHEM Project"