1. RDKit Molecular Editor节点，如果两个节点输出文件名一样，会导致其中一个CACHE的丢失

2. rdkit molecular editor 的edit_report输出，储状态那里有个叉号，是为什么呢：
✅ 处理完成 (使用MolstarDisplayMixin)       

  🔧 处理信息:
  - 输入原子数: 131
  - 输出原子数: 250
  - 输出文件: rdkit_edited.pdb
  - 存储状态: ✗

  🎯 架构优势:
  - ✅ 直接内容处理模式
  - ✅ 3D显示零配置启用
  - ✅ 简化的处理流程
  - ✅ 标准化错误处理

3.  rdkit molecular editor 这类中间处理节点，_alchem_node_id不会自动更新
  
4. _alchem_node_id有很多回退逻辑，都没啥用。目前的所有方案中，只有一种方案是对的，从前端获取，作为参数传入。