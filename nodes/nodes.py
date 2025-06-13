"""
🗑️ 废弃文件：nodes.py

这个文件中的所有节点已经被新的方案B架构替代：

废弃的旧节点：
- CustomUploadTextNode
- CustomUploadConfigNode  
- Demo3DDisplayNode
- DualButtonDemoNode
- DualAttributeTestNode
- MolecularUploadDemoNode

新的推荐节点：
- test_simple_node.py: SimpleUploadAndDisplayTestNode (测试用)
- standard_molecular_node.py: StandardMolecularAnalysisNode (标准模板)

废弃原因：
1. 旧节点使用了过时的execution_hook机制
2. 代码复杂，内存管理逻辑混乱
3. 方案B提供了更简洁、稳定的实现方式

如需参考旧代码，可查看git历史记录。
"""

# 空的节点映射，防止导入错误
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}