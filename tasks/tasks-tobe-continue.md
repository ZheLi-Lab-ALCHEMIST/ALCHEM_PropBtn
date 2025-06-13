# ALCHEM_PropBtn 项目开发现状

> **当前状态**: 🎯 核心功能完成，架构稳定，准备WebSocket开发
> 
> **更新时间**: 2025年6月13日

## 🚀 项目简介

**ALCHEM_PropBtn** 是一个ComfyUI分子编辑与可视化扩展，实现了分子文件上传、3D显示和数据管理功能。当前版本采用稳定的方案B架构，下一步将开发WebSocket实时同步功能。

## ✅ 当前完成的功能

### 🧪 核心功能（100%完成）
- **分子文件上传** - 支持PDB、MOL、SDF、XYZ等8种格式，智能重命名处理
- **3D分子显示** - 基于MolStar的专业级3D查看器，纯净界面
- **后端内存管理** - 毫秒级数据访问，双重存储（内存+文件系统）
- **智能数据获取** - 方案B架构，节点主动获取数据，稳定可靠
- **日志系统** - 可配置的日志等级控制，debug模式显示详细信息

### 🏗️ 技术架构

#### 后端架构（Python）
```
backend/
├── molecular_memory.py    # 分子数据内存管理（核心）
├── molecular_api.py       # RESTful API处理器
└── molecular_utils.py     # 方案B数据获取工具
```

#### 前端架构（JavaScript模块化）
```
web/js/
├── extensionMain.js       # 主协调器，日志系统
├── uploadMolecules.js     # 分子文件上传处理
├── custom3DDisplay.js     # 3D显示协调器
└── modules/               # 模块化组件
    ├── molstar-core.js    # MolStar 3D渲染
    ├── data-processor.js  # 数据处理
    ├── ui-integrated.js   # UI组件管理
    └── api-client.js      # API通信
```

#### 节点架构（方案B）
```
nodes/
├── test_simple_node.py         # 测试验证节点
├── standard_molecular_node.py  # 标准开发模板
└── nodes.py                    # 废弃（已清空）
```

### 🔗 核心API端点
1. **POST** `/alchem_propbtn/api/molecular` - 分子数据查询
2. **POST** `/alchem_propbtn/api/upload_molecular` - 分子文件上传
3. **GET** `/alchem_propbtn/api/status` - 系统状态监控

### 🎯 数据流架构（方案B）
```
文件上传 → 格式验证 → 后端内存存储
    ↓
节点执行 → molecular_utils.get_molecular_content() → 智能数据获取
    ↓
3D显示 → API查询内存 → MolStar渲染
```

## 🛠️ 开发环境设置

### 快速开始
1. **日志调试** - 在浏览器控制台设置：
   ```javascript
   customWidgetsExtension.utils.setLogLevel('debug')  // 显示详细日志
   ```

2. **测试节点** - 在ComfyUI中添加"🧪🎯 Simple Upload+3D Test"节点

3. **API测试** - 检查系统状态：
   ```bash
   curl http://localhost:8188/alchem_propbtn/api/status
   ```

### 新节点开发流程
1. 复制 `standard_molecular_node.py` 作为模板
2. 修改类名和功能描述
3. 使用 `molecular_utils.get_molecular_content()` 获取数据
4. 在 `__init__.py` 中注册新节点

## 🚀 下一步开发计划：WebSocket实时同步

### 🎯 WebSocket开发目标
实现50ms高频实时同步，支持多用户协作编辑分子结构。

### 📋 WebSocket开发任务列表

#### Phase 1: WebSocket基础架构（估计1-2天）
- [ ] **后端WebSocket服务器**
  - [ ] 创建 `backend/websocket_server.py`
  - [ ] 实现连接管理、房间机制
  - [ ] 集成现有的molecular_memory系统

- [ ] **前端WebSocket客户端**
  - [ ] 创建 `web/js/modules/websocket-client.js`
  - [ ] 实现连接、重连、心跳机制
  - [ ] 与现有数据流集成

#### Phase 2: 实时数据同步（估计2天）
- [ ] **同步协议设计**
  - [ ] 定义消息格式（JSON）
  - [ ] 实现增量同步机制
  - [ ] 处理并发冲突

- [ ] **数据同步实现**
  - [ ] 分子数据变更检测
  - [ ] 广播更新到所有客户端
  - [ ] 本地缓存同步

#### Phase 3: 协作功能（估计1天）
- [ ] **多用户管理**
  - [ ] 用户识别和状态管理
  - [ ] 权限控制机制
  - [ ] 实时用户列表显示

- [ ] **冲突解决**
  - [ ] 操作时间戳
  - [ ] 冲突检测算法
  - [ ] 自动合并策略

### 🏗️ WebSocket技术栈
- **后端**: Python + `websockets` 库 + `asyncio`
- **前端**: JavaScript WebSocket API + 自动重连
- **协议**: JSON消息格式，基于事件驱动
- **同步**: 增量同步 + 心跳检测

### 📁 WebSocket新增文件结构
```
backend/
├── websocket_server.py       # WebSocket服务器
├── realtime/                 # 实时同步模块
│   ├── __init__.py
│   ├── connection_manager.py # 连接管理
│   ├── sync_protocol.py      # 同步协议
│   └── conflict_resolver.py  # 冲突解决

web/js/modules/
├── websocket-client.js       # WebSocket客户端
├── realtime-sync.js         # 实时同步逻辑
└── collaboration.js         # 协作功能
```

### 🔧 WebSocket集成要点
1. **保持现有架构不变** - WebSocket作为新增层，不影响现有功能
2. **渐进式开发** - 先实现基础同步，再添加高级功能
3. **向后兼容** - 确保非WebSocket环境下功能正常
4. **性能优化** - 实现50ms高频同步目标

## 📚 重要参考文档

### 当前项目文档
- `plan2.md` - 完整系统架构设计
- `docs/NODE_DEVELOPMENT_GUIDE.md` - 节点开发指南
- `docs/CLEAN_ARCHITECTURE.md` - 清洁架构文档

### 代码示例
- `nodes/standard_molecular_node.py` - 标准节点开发模板
- `nodes/test_simple_node.py` - 测试节点实现示例
- `backend/molecular_utils.py` - 数据获取工具函数

## 🎯 给新AI助手的建议

1. **理解现有架构** - 重点关注方案B的数据获取模式，这是核心
2. **保持代码简洁** - 避免过度设计，保持与现有代码风格一致
3. **模块化开发** - 新功能应该作为独立模块，不破坏现有结构
4. **测试驱动** - 使用test_simple_node.py验证功能
5. **渐进式实现** - 先实现核心功能，再添加高级特性

## 🚨 注意事项

### 避免的陷阱
- ❌ 不要修改现有的核心模块（molecular_memory.py等）
- ❌ 不要重构已经稳定的前端模块化架构
- ❌ 不要使用方案A的execution_hook模式（已废弃）

### 推荐的开发方式
- ✅ 使用molecular_utils.py的工具函数
- ✅ 遵循现有的模块化架构
- ✅ 优先考虑性能和稳定性
- ✅ 保持日志信息的一致性

---

**当前状态**: 🎯 核心功能完成，架构稳定，MolStar完美运行，准备WebSocket开发

**技术优势**: 方案B稳定数据流、模块化设计、智能日志控制、完整开发文档

**下一个里程碑**: WebSocket实时同步功能开发 → 多用户协作编辑 → 完整分子编辑系统

**bug**:有多个tab时，在tab_A upload完，切换到tab_B，在tab_B upload，切换回A，A中node的molstar_3d按钮找不到内存了。
在tab_A upload完，切换到tab_B，在tab_B 不去 upload，切换回A，A中node的molstar_3d按钮显示还是正确的。
就是说，切换tab再上传分子，会导致之前tab中上传的分子的内存消失。
