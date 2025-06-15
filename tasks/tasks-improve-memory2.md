# 内存管理改进 - 最简解决方案

## 📋 项目背景

### 当前情况
ALCHEM_PropBtn 是一个 ComfyUI 自定义节点扩展，专注于分子文件处理和3D可视化。项目采用方案B架构（节点主动数据获取模式），提供分子文件上传按钮和3D显示功能。

### 现有功能
- **分子上传节点**: 如 `StandardMolecularAnalysisNode`，包含：
  - `molecular_upload: True` - 📁 上传按钮，文件存储到后端全局CACHE
  - `molstar_3d_display: True` - 🧪 3D显示按钮，从CACHE获取数据显示
- **全局CACHE系统**: 使用节点ID作为key存储分子数据
- **WebSocket实时同步**: 支持分子编辑和多tab数据同步

### 要解决的问题
我想添加一些**中间处理节点**，它们能够：
1. **接收上游分子数据**: 从前面的upload节点获取分子结构
2. **进行数据处理**: 如删除氢原子、分子居中、格式转换等
3. **支持3D显示**: 处理节点也要有 `molstar_3d_display: True`，能查看和编辑处理后的结果
4. **数据流传递**: 处理后的数据能继续传递给下游节点

### 典型工作流场景
```
StandardMolecularAnalysisNode (上传分子)
    ↓ 传递文件名
ProcessNode1 (删除氢原子) 
    ↓ 传递文件名  
ProcessNode2 (分子居中)
    ↓ 传递文件名
FinalDisplayNode (最终结果显示)
```

每个节点都应该能通过🧪按钮查看当前阶段的分子结构。

## 🎯 核心技术问题
- 中间处理节点无法通过molstar_3d按钮显示分子结构
- 后端不知道前端的tab_id信息
- node_id的hash后缀导致匹配困难

## 🚀 最简解决方案

### 第1步：去掉hash编码机制
**目标**: 让前后端node_id完全一致

**修改点**: 
- 前端上传时，node_id格式简化为: `workflow_fl40l5_node_23` (去掉`_2tn0e6`hash)
- 后端存储时，直接使用这个简化的node_id作为缓存key

### 第2步：CACHE添加tab_id字段
**文件**: `backend/memory.py`

```python
# 全局缓存结构增强
MOLECULAR_DATA_CACHE = {
    "workflow_fl40l5_node_23": {
        "filename": "molecule.pdb",
        "content": "...",
        "tab_id": "workflow_fl40l5",  # 新增：Tab标识
        # ... 其他字段保持不变
    }
}
```

**实现**:
```python
def store_molecular_data(node_id: str, filename: str, folder: str = "molecules", content: str = None):
    # 提取tab_id
    tab_id = None
    if "_node_" in node_id:
        tab_id = node_id.split("_node_")[0]  # "workflow_fl40l5"
    
    molecular_data = {
        "node_id": node_id,
        "filename": filename,
        "content": content,
        "tab_id": tab_id,  # 新增字段
        # ... 其他字段
    }
    
    MOLECULAR_DATA_CACHE[node_id] = molecular_data
```

### 第3步：upload节点同步tab_id
**目标**: 有upload功能的节点主动记录tab_id

**修改点**: 
```python
# 在有molecular_upload的节点function开始时
def molecular_analysis(self, molecular_file, **kwargs):
    node_id = kwargs.get('_alchem_node_id', '')
    
    # 第一件事：同步tab_id到CACHE
    if node_id and "_node_" in node_id:
        tab_id = node_id.split("_node_")[0]
        if node_id in MOLECULAR_DATA_CACHE:
            MOLECULAR_DATA_CACHE[node_id]["tab_id"] = tab_id
            print(f"✅ 同步tab_id: {tab_id} -> {node_id}")
    
    # 然后正常处理...
```

### 第4步：process节点同步机制
**目标**: 中间处理节点把结果存到CACHE，使用正确的完整node_id

**实现策略**:
```python
def process_molecular_data(self, input_molecular_file, output_filename, **kwargs):
    node_id = kwargs.get('_alchem_node_id', '')  # 后端给的是纯数字 "23"
    
    # 关键：从CACHE中找到当前tab_id
    current_tab_id = None
    for cache_key, data in MOLECULAR_DATA_CACHE.items():
        if data.get("filename") == input_molecular_file:
            current_tab_id = data.get("tab_id")
            break
    
    # 重构完整node_id
    if current_tab_id and node_id:
        full_node_id = f"{current_tab_id}_node_{node_id}"
    else:
        full_node_id = f"node_{node_id}"  # 回退方案
    
    # 处理数据...
    processed_content = process(input_content)
    
    # 存储到CACHE
    store_molecular_data(
        node_id=full_node_id,
        filename=output_filename,
        content=processed_content
    )
    
    print(f"✅ 处理结果已存储: {full_node_id} -> {output_filename}")
```

## 📋 具体实施步骤

### Step 1: 修改前端hash机制
**文件**: `web/js/uploadMolecules.js` 或相关前端文件
```javascript
// 原来: workflow_fl40l5_node_23_2tn0e6
// 改为: workflow_fl40l5_node_23

function generateNodeId(tabId, nodeId) {
    return `${tabId}_node_${nodeId}`;  // 去掉hash
}
```

### Step 2: 修改memory.py
```python
def store_molecular_data(cls, node_id: str, filename: str, folder: str = "molecules", content: str = None):
    # 提取tab_id
    tab_id = None
    if "_node_" in node_id:
        tab_id = node_id.split("_node_")[0]
    
    molecular_data = {
        "node_id": node_id,
        "filename": filename,
        "folder": folder,
        "content": content,
        "tab_id": tab_id,  # 🔑 新增
        "cached_at": time.time(),
        # ... 其他字段保持不变
    }
    
    MOLECULAR_DATA_CACHE[node_id] = molecular_data
```

### Step 3: 修改get_molecular_content()
```python
def get_molecular_content(input_value: str, node_id: Optional[str] = None):
    # 如果输入是文件名，尝试从CACHE获取
    if is_filename(input_value):
        filename = input_value
        
        # 方法1：精确匹配（如果有完整node_id）
        if node_id and node_id in MOLECULAR_DATA_CACHE:
            data = MOLECULAR_DATA_CACHE[node_id]
            if data.get("filename") == filename:
                return data["content"], metadata
        
        # 方法2：文件名匹配 + tab_id推断
        if node_id and node_id.isdigit():
            # 后端传来的是纯数字，需要找到对应的tab_id
            for cache_key, data in MOLECULAR_DATA_CACHE.items():
                if data.get("filename") == filename:
                    # 找到了，用这个tab_id重构完整node_id
                    tab_id = data.get("tab_id")
                    if tab_id:
                        full_node_id = f"{tab_id}_node_{node_id}"
                        if full_node_id in MOLECULAR_DATA_CACHE:
                            return MOLECULAR_DATA_CACHE[full_node_id]["content"], metadata
        
        # 方法3：简单文件名匹配（回退）
        for data in MOLECULAR_DATA_CACHE.values():
            if data.get("filename") == filename:
                return data["content"], metadata
    
    return input_value, metadata  # 已经是内容
```

### Step 4: 修改标准节点
```python
# StandardMolecularAnalysisNode
def molecular_analysis(self, molecular_file, **kwargs):
    node_id = kwargs.get('_alchem_node_id', '')
    
    # 🔑 关键：同步tab_id
    if node_id and "_node_" in node_id and node_id in MOLECULAR_DATA_CACHE:
        tab_id = node_id.split("_node_")[0]
        MOLECULAR_DATA_CACHE[node_id]["tab_id"] = tab_id
    
    # 正常处理...
    content, metadata = get_molecular_content(molecular_file, node_id)
    return process(content)
```

## ⚠️ 注意事项

### 关键原则
1. **保持简单**: 只加tab_id字段，不搞复杂的注册表
2. **向后兼容**: 不破坏现有的节点和工作流
3. **渐进实施**: 一步一步实施，每步都要能工作

### 验证清单
- [ ] 去掉hash后，前后端node_id一致
- [ ] CACHE中有tab_id字段
- [ ] upload节点能正确同步tab_id
- [ ] process节点能重构正确的完整node_id
- [ ] molstar_3d按钮能在process节点中正常工作

### 最小可行方案
如果上述方案还是复杂，可以进一步简化：
1. 前端直接传递tab_id作为隐藏参数
2. 所有节点都在function开始时同步tab_id
3. 完全基于文件名匹配，忽略node_id

## 🎯 成功标准
- 中间处理节点的molstar_3d按钮能正常显示分子结构
- 不同tab的数据不互相干扰
- 现有功能保持正常