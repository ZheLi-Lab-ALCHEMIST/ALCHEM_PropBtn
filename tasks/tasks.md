# ALCHEM_PropBtn 项目开发任务规划

## 📊 当前项目完成度分析

基于对项目代码的深度分析，当前完成度如下：

### ✅ 已完成模块（约75%整体进度）

#### 1. 后端Python架构（85%完成）
- ✅ **nodes.py** - 完整的节点定义系统
  - ✅ CustomUploadTextNode, CustomUploadConfigNode
  - ✅ Demo3DDisplayNode
  - ✅ DualButtonDemoNode, DualAttributeTestNode
  - ✅ MolecularUploadDemoNode（完整的分子上传演示）
  - ✅ 双Property支持验证
  
- ✅ **molecular_memory.py** - 分子数据内存管理系统
  - ✅ 全局缓存机制 MOLECULAR_DATA_CACHE
  - ✅ 线程安全操作
  - ✅ 文件格式检测和解析
  - ✅ 原子、键、坐标提取
  - ✅ 活跃节点管理
  - ✅ 缓存生命周期管理

- ✅ **molecular_api.py** - RESTful API接口
  - ✅ 分子数据查询接口
  - ✅ 缓存状态管理
  - ✅ 节点管理接口
  - ✅ 搜索和过滤功能

- ✅ **__init__.py** - ComfyUI集成
  - ✅ Web API路由注册
  - ✅ /alchem_propbtn/api/molecular 端点

#### 2. 前端JavaScript架构（80%完成）
- ✅ **extensionMain.js** - 主协调器
  - ✅ 模块化扩展架构
  - ✅ 统一日志系统
  - ✅ 扩展状态监控
  - ✅ 调试接口

- ✅ **uploadCore.js** - 文件上传核心
  - ✅ 拖拽上传支持
  - ✅ 进度条显示
  - ✅ 文件验证
  - ✅ ComfyUI集成

- ✅ **uploadMolecules.js** - 分子文件上传
  - ✅ 多格式支持（PDB, MOL, SDF, XYZ, MOL2, CIF, GRO, FASTA）
  - ✅ 格式验证和分析
  - ✅ 前端内存存储
  - ✅ 拖拽支持

- ✅ **custom3DDisplay.js** - 3D显示基础
  - ✅ 后端API集成
  - ✅ 内存数据读取
  - ✅ 演示3D查看器
  - ✅ 文件内容分析

### ❌ 缺失的关键模块（约25%待完成）

#### 1. 🧬 MolStar 3D编辑集成（0%完成）
- ❌ MolStar库集成
- ❌ 真正的3D分子编辑器
- ❌ 实时编辑功能
- ❌ 原子级操作（添加、删除、修改）
- ❌ 编辑历史追踪

#### 2. 🔄 WebSocket实时同步（0%完成）
- ❌ WebSocket服务器端实现
- ❌ 50ms高频同步机制
- ❌ 编辑操作防抖处理
- ❌ 断线重连机制

#### 3. 🚀 高级API端点（30%完成）
- ❌ WebSocket升级端点
- ❌ 分子数据导出端点
- ❌ 批量操作端点

---

## 🎯 实施规划与优先级

### 阶段1：核心功能完善（高优先级）

#### 任务1.1：WebSocket实时同步系统
**预估时间**: 3-4天  
**优先级**: 🔴 极高

**子任务**：
1. **后端WebSocket服务器**
   ```python
   # 文件：websocket_server.py
   - WebSocket连接管理
   - 消息路由系统
   - 分子数据同步协议
   - 50ms防抖优化
   ```

2. **前端WebSocket客户端**
   ```javascript
   // 文件：web/js/websocketClient.js
   - 连接管理和重连
   - 消息序列化/反序列化
   - 编辑事件监听
   - 同步状态管理
   ```

3. **集成到molecular_api.py**
   ```python
   - WebSocket路由注册
   - 消息处理器
   - 数据同步逻辑
   ```

#### 任务1.2：MolStar 3D编辑器集成
**预估时间**: 5-6天  
**优先级**: 🔴 极高

**子任务**：
1. **MolStar库集成**
   ```javascript
   // 文件：web/js/molstarEditor.js
   - MolStar库加载
   - 3D查看器初始化
   - 基础渲染功能
   ```

2. **编辑功能实现**
   ```javascript
   // 继续完善 molstarEditor.js
   - 原子操作工具栏
   - 键操作功能
   - 编辑事件捕获
   - 实时更新机制
   ```

3. **与WebSocket集成**
   ```javascript
   // 数据同步
   - 编辑操作广播
   - 远程变更应用
   - 冲突解决机制
   ```

#### 任务1.3：Property系统优化
**预估时间**: 1-2天  
**优先级**: 🟡 中等

**子任务**：
1. **双Property支持验证**
   ```javascript
   // 更新 extensionMain.js
   - 完善Property检测逻辑
   - 处理Property冲突
   - 优化Widget布局
   ```

2. **新Property类型支持**
   ```python
   # 更新 nodes.py
   - molstar_editable Property
   - 编辑器配置选项
   - 权限和安全设置
   ```

### 阶段2：功能增强（中优先级）

#### 任务2.1：高级API端点
**预估时间**: 2-3天  
**优先级**: 🟡 中等

**子任务**：
1. **导出功能**
   ```python
   # 文件：export_api.py
   - 多格式导出 (PDB, MOL, SDF)
   - 批量导出
   - 压缩打包
   ```

2. **批量操作**
   ```python
   # 扩展 molecular_api.py
   - 批量上传
   - 批量处理
   - 进度跟踪
   ```

#### 任务2.2：用户体验优化
**预估时间**: 2天  
**优先级**: 🟡 中等

**子任务**：
1. **UI/UX改进**
   ```javascript
   // 更新样式文件
   - 响应式设计
   - 主题支持
   - 无障碍功能
   ```

2. **错误处理优化**
   ```javascript
   // 所有模块
   - 友好错误提示
   - 恢复机制
   - 日志记录
   ```

### 阶段3：高级特性（低优先级）

#### 任务3.1：性能优化
**预估时间**: 2-3天  
**优先级**: 🟢 低

**子任务**：
1. **大文件支持**
   ```python
   - 流式处理
   - 内存优化
   - 分片上传
   ```

2. **缓存优化**
   ```python
   - LRU算法优化
   - 压缩存储
   - 预加载机制
   ```

#### 任务3.2：扩展功能
**预估时间**: 3-4天  
**优先级**: 🟢 低

**子任务**：
1. **分析工具集成**
   ```python
   - 分子属性计算
   - 结构验证
   - 统计分析
   ```

2. **外部工具链接**
   ```python
   - 第三方分析工具
   - 数据库集成
   - 云服务支持
   ```

---

## 📋 具体代码实施计划

### Week 1: WebSocket + 基础MolStar集成

#### Day 1-2: WebSocket服务器实现
```python
# 新文件：websocket_server.py
class MolecularWebSocketHandler:
    def __init__(self):
        self.clients = set()
        self.rooms = {}  # node_id -> clients
    
    async def handle_connection(self, websocket, path):
        # 连接管理逻辑
        pass
    
    async def handle_message(self, websocket, message):
        # 消息处理逻辑
        pass
    
    async def broadcast_molecular_update(self, node_id, molecular_data):
        # 广播分子数据更新
        pass
```

#### Day 3-4: MolStar基础集成
```javascript
// 新文件：web/js/molstarCore.js
class MolStarManager {
    constructor(container) {
        this.container = container;
        this.viewer = null;
        this.structureData = null;
    }
    
    async initViewer() {
        // MolStar查看器初始化
    }
    
    async loadStructure(molecularData) {
        // 加载分子结构
    }
    
    async updateStructure(changes) {
        // 更新结构变化
    }
}
```

#### Day 5: 集成测试和调试

### Week 2: 编辑功能 + UI优化

#### Day 1-3: 编辑功能实现
```javascript
// 扩展 molstarCore.js
class MolStarEditor extends MolStarManager {
    constructor(container, websocketClient) {
        super(container);
        this.wsClient = websocketClient;
        this.editHistory = [];
    }
    
    enableEditing() {
        // 启用编辑模式
    }
    
    addAtom(position, element) {
        // 添加原子
    }
    
    deleteAtom(atomId) {
        // 删除原子
    }
    
    addBond(atom1, atom2, bondType) {
        // 添加化学键
    }
}
```

#### Day 4-5: UI集成和测试

### Week 3: 测试、优化和文档

#### Day 1-3: 功能测试
- 端到端测试
- 性能测试
- 兼容性测试

#### Day 4-5: 文档和部署
- 用户文档
- 开发者文档
- 部署指南

---

## 🔧 开发环境设置

### 必需依赖
```bash
# Python依赖
pip install websockets aiohttp

# JavaScript依赖（CDN或npm）
# MolStar库：https://molstar.org/
```

### 开发工具
- VS Code + Python扩展
- Browser DevTools
- WebSocket测试工具

---

## ✅ 成功标准

### 功能完整性
- [ ] WebSocket实时同步工作正常
- [ ] MolStar 3D编辑功能完整
- [ ] 双Property支持验证通过
- [ ] 所有演示节点正常工作

### 性能指标
- [ ] WebSocket同步延迟 < 50ms
- [ ] 大分子文件(>1MB)加载 < 3秒
- [ ] 内存使用稳定，无泄漏

### 用户体验
- [ ] 直观的UI设计
- [ ] 友好的错误提示
- [ ] 完整的功能文档

---

## 🚀 下一步行动

### 立即开始（今天）
1. **创建WebSocket服务器文件**
   ```bash
   touch websocket_server.py
   ```

2. **设置MolStar开发环境**
   ```bash
   mkdir web/lib
   # 下载MolStar库
   ```

3. **创建测试案例**
   ```bash
   mkdir tests
   touch tests/test_websocket.py
   touch tests/test_molstar.py
   ```

### 本周目标
- [ ] WebSocket基础通信建立
- [ ] MolStar基础查看器运行
- [ ] 第一个实时编辑演示

### 月度里程碑
- [ ] 完整的3D分子编辑系统
- [ ] 50ms实时同步机制
- [ ] 用户友好的界面
- [ ] 完整的测试覆盖

---

*最后更新：2024年12月6日*  
*状态：准备开始实施*  
*预期完成：2024年12月底*