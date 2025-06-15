# 🧪 分子处理工作流连接指南

## 📋 节点输入输出匹配

### 1. Upload节点（StandardMolecularAnalysisNode 或 SimpleUploadAndDisplayTestNode）
```
输入: molecular_file (STRING) - 分子文件名
输出: 
  - file_content (STRING) - 分子文件内容 🔑
  - analysis_result/test_result (STRING) - 分析/测试结果
```

### 2. Process节点（TabAwareProcessingNode）
```
输入: 
  - input_molecular_content (STRING, multiline) - 分子文件内容 🔑
  - output_filename (STRING) - 输出文件名
  - processing_type - 处理类型
输出:
  - processed_content (STRING) - 处理后的分子内容 🔑
  - processed_filename (STRING) - 处理后的文件名
  - processing_report (STRING) - 处理报告
```

## 🔗 正确的连接方式

### 基本工作流
```
SimpleUploadAndDisplayTestNode
    ↓ file_content
TabAwareProcessingNode (删除氢原子)
    ↓ processed_content  
TabAwareProcessingNode (分子居中)
    ↓ processed_content
最终显示节点
```

### 连接步骤
1. **Upload → Process**: 
   - 连接 `upload节点.file_content` → `process节点.input_molecular_content`

2. **Process → Process**: 
   - 连接 `process1节点.processed_content` → `process2节点.input_molecular_content`

3. **查看3D结构**:
   - 每个Process节点的 `output_filename` 参数都有🧪 3D View按钮
   - 点击可查看当前处理阶段的分子结构

## 🎯 完整示例工作流

### 场景：分子优化处理链
```
1. SimpleUploadAndDisplayTestNode
   📁 上传: caffeine.pdb
   🧪 3D查看: 原始分子结构
   → 输出: file_content (完整PDB内容)

2. TabAwareProcessingNode (remove_hydrogens)
   🔧 输入: caffeine.pdb内容
   🔧 处理: 删除所有氢原子
   🧪 3D查看: 无氢原子结构
   → 输出: processed_content (去氢PDB内容)

3. TabAwareProcessingNode (center_molecule)  
   🔧 输入: 去氢PDB内容
   🔧 处理: 分子居中
   🧪 3D查看: 居中后结构
   → 输出: processed_content (居中PDB内容)

4. 最终分析节点
   🔧 输入: 居中PDB内容
   📊 分析: 结构特征分析
```

## 🔑 Tab感知机制工作原理

### 1. ID生成
- Upload节点: `workflow_abc12_node_23`
- Process节点1: `workflow_abc12_node_24` 
- Process节点2: `workflow_abc12_node_25`

### 2. 数据存储
每个Process节点都会：
- 提取tab_id: `workflow_abc12`
- 构建完整node_id: `workflow_abc12_node_24`
- 存储处理结果到内存，使用完整node_id作为key

### 3. 3D显示
点击🧪按钮时：
- 前端使用完整node_id查找内存数据
- tab_id确保只显示当前工作流的数据
- 不同tab之间完全隔离

## 💡 最佳实践

### 1. 节点命名
```python
"output_filename": ("STRING", {
    "default": "step1_no_hydrogens.pdb",  # 描述性命名
    "molstar_3d_display": True,
    # ...
})
```

### 2. 处理类型选择
- `remove_hydrogens`: 删除氢原子，减少显示复杂度
- `center_molecule`: 分子居中，便于查看
- `simple_edit`: 删除最后一个原子（演示用）

### 3. 错误处理
- 每个节点都会验证输入内容
- 处理失败时返回原始内容
- 详细的错误信息便于调试

## 🧪 测试验证

### 验证清单
- [ ] Upload节点可以正常上传分子文件
- [ ] Upload节点的🧪按钮显示原始结构
- [ ] Process节点正确接收file_content
- [ ] Process节点成功处理数据
- [ ] Process节点的🧪按钮显示处理后结构
- [ ] 多个Process节点可以串联
- [ ] 不同tab之间数据隔离

### 调试技巧
1. **查看节点输出**: 检查processing_report了解处理详情
2. **比较原子数**: 确认处理是否生效
3. **使用3D显示**: 直观验证处理结果
4. **检查控制台**: 查看详细的日志信息

## 🚀 扩展可能

### 自定义处理节点
```python
# 基于TabAwareProcessingNode创建新的处理类型
class CustomMolecularProcessNode(TabAwareProcessingNode):
    def _process_molecular_content(self, content, processing_type):
        if processing_type == "your_custom_process":
            # 实现你的自定义处理逻辑
            return modified_content
        return super()._process_molecular_content(content, processing_type)
```

### 新的连接模式
- 分支处理：一个upload节点连接多个不同的process节点
- 合并处理：多个process节点的结果汇总到一个分析节点
- 对比分析：并行处理链用于效果对比

这个架构确保了分子处理工作流的灵活性和可扩展性，同时维持了数据的正确性和tab隔离。