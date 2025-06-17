# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## User Communication Preferences
用中文回答我。
每次都用审视的目光，仔公看我输入的潜在问题，你要指出我的问题，并给出明显在我思考框架之外的建议。
不要过度设计，专注于实现功能。
除非非常必要，不要随便设计回退方案，因为这是维护的噩梦，bug的源泉。


## Project Overview
ALCHEM_PropBtn 是一个 ComfyUI 自定义节点扩展，专注于分子文件处理和3D可视化。项目采用方案B架构（节点主动数据获取模式），提供上传按钮和3D显示功能，并集成WebSocket实时同步功能。

**当前状态**: ✅ 项目架构稳定，核心功能完善，代码质量优化完成

## Architecture - 方案B架构 (Node-Pull Pattern)

### Core Design Pattern
- **节点定义**: 在节点的 INPUT_TYPES 中设置特殊属性来启用功能
- **前端检测**: JavaScript 模块检测属性并添加对应 Widget
- **数据存储**: 文件上传到后端内存缓存，以节点ID为key
- **节点执行**: 节点通过工具函数从后端内存获取数据

### Key Properties for Node Configuration
```python
"molecular_file": ("STRING", {
    "molecular_upload": True,       # 启用上传按钮 (📁 Upload)
    "molstar_3d_display": True,     # 启用3D显示按钮 (🧪 3D View)
    "molecular_folder": "molecules", # 文件存储目录
    "display_mode": "ball_and_stick", # 3D显示模式
    "background_color": "#1E1E1E",   # 3D背景色
    "tooltip": "支持上传和3D显示的分子文件"
})
```

## Directory Structure

### 核心文件结构 (方案B架构)

#### 节点定义
- `__init__.py` - 主入口，节点注册
- `nodes/standard_molecular_node.py` - 标准分子处理节点
- `nodes/test_simple_node.py` - 基础测试节点
- `nodes/test_tab_aware_processing.py` - Tab感知处理节点

#### 后端服务
- `backend/api.py` - REST API路由
- `backend/memory.py` - Tab感知内存管理
- `backend/molecular_utils.py` - 分子数据工具
- `backend/websocket_server.py` - 实时同步服务
- `backend/logging_config.py` - 统一日志系统

#### 前端模块
- `web/js/extensionMain.js` - 扩展协调器
- `web/js/uploadMolecules.js` - 分子上传模块
- `web/js/custom3DDisplay.js` - 3D显示和编辑
- `web/js/modules/` - 功能模块目录
  - `api-client.js` - API客户端
  - `data-processor.js` - 数据处理器
  - `molstar-core.js` - MolStar集成
  - `ui-integrated.js` - UI集成模块
  - `websocket-client.js` - WebSocket客户端
- `web/js/utils/logger.js` - 前端日志系统

## Development Commands

### ComfyUI 开发流程
```bash
# 重启 ComfyUI（修改Python节点后必须）
# 直接重启 ComfyUI 服务器以加载节点更改

# 查看加载状态
# 检查 ComfyUI 控制台中的 ALCHEM 日志输出
```

### 浏览器调试工具
```javascript
// 扩展状态检查
window.getCustomWidgetStatus()      // 查看扩展整体状态
window.customWidgetsExtension.status()  // 访问扩展API

// WebSocket和内存调试
debugWebSocket()        // WebSocket连接状态
debugNodeIds()          // 节点ID生成和内存状态  
debugMultiTabMemory()   // 多Tab内存隔离测试

// 日志系统控制
setGlobalLogLevel('debug')   // 设置日志级别
// 可选: 'debug', 'info', 'warn', 'error'
```

### 代码质量检查
```bash
# 检查文件行数（代码优化后）
wc -l nodes/test_tab_aware_processing.py  # 应该 < 400行

# 验证节点ID绑定
# 确保编辑按钮严格绑定到节点ID，不使用文件名查找
```

## API Endpoints
- `POST /alchem_propbtn/api/molecular` - 分子数据操作和编辑
- `POST /alchem_propbtn/api/upload_molecular` - 文件上传
- `GET /alchem_propbtn/api/status` - 系统状态监控
- `GET /alchem_propbtn/ws` - WebSocket实时同步连接

## Node Development Guide

### 创建新的分子处理节点
1. **参考模板**: 使用 `nodes/standard_molecular_node.py` 作为标准模板
2. **属性配置**: 在 INPUT_TYPES 中添加所需属性：
   ```python
   "molecular_file": ("STRING", {
       "molecular_upload": True,        # 启用上传功能
       "molstar_3d_display": True,      # 启用3D显示
       "molecular_folder": "molecules", # 存储目录
       "tooltip": "支持上传和3D显示的分子文件"
   })
   ```
3. **数据获取**: 使用 `molecular_utils.get_molecular_content()` 获取数据
4. **节点注册**: 在 `__init__.py` 中注册新节点

### Widget开发模式（方案B架构）
1. **属性驱动**: 节点通过INPUT_TYPES属性声明需要的功能
2. **自动检测**: 前端JavaScript自动检测属性并添加对应Widget  
3. **模块化**: 每个功能模块独立，易于维护和扩展

## Key Implementation Details

### 数据流程 (Upload → Display → Edit → Sync)
1. **Upload**: 📁按钮 → uploadMolecules.js → API → Tab感知内存存储
2. **Display**: 🧪按钮 → custom3DDisplay.js → 节点ID获取数据 → MolStar渲染
3. **Edit**: 🔧按钮 → **严格节点ID绑定** → API编辑 → WebSocket推送更新
4. **Sync**: WebSocket客户端接收 → 自动刷新MolStar显示
5. **Process**: 节点执行 → molecular_utils.get_molecular_content() → 内存获取

### Tab感知内存管理 (核心优化)
- **存储key**: `workflow_{tab_hash}_node_{node_id}` 格式
- **多Tab隔离**: 不同Tab的相同节点ID独立存储
- **智能清理**: 自动清理过期缓存
- **状态监控**: 实时缓存状态查询

### 关键修复 - 节点ID严格绑定
- **问题**: 编辑按钮曾经按文件名查找数据，导致同名文件混乱
- **解决**: 强制所有操作严格绑定到节点ID，杜绝文件名查找
- **效果**: 每个节点的3D显示和编辑功能完全独立

### WebSocket实时同步
- **服务器**: 基于aiohttp的异步WebSocket  
- **功能**: 连接管理、心跳检测、自动重连
- **同步**: 内存变更 → 推送 → 前端自动更新
- **编辑**: 支持删除原子等实时分子编辑

## Logging System (统一日志系统)

### Python后端使用
```python
# 导入统一Logger
from backend.logging_config import get_alchem_logger

# 创建模块Logger
logger = get_alchem_logger('ModuleName')

# 使用标准方法
logger.debug("调试信息")
logger.success("操作成功")
logger.molecular("分子相关操作")
logger.network("网络通信")
logger.storage("存储操作")
logger.connection("连接状态")
logger.warning("警告信息")
logger.error("错误信息")
```

### JavaScript前端使用
```javascript
// 导入统一Logger
import { getALCHEMLogger } from './utils/logger.js';

// 创建模块Logger
const logger = getALCHEMLogger('ModuleName');

// 使用标准方法
logger.debug("调试信息");
logger.success("操作成功");
logger.molecular("分子相关操作");
logger.websocket("WebSocket通信");
logger.ui("界面操作");
```

### 统一表情符号标准
- 🔧 DEBUG - 调试信息
- ℹ️ INFO - 一般信息
- ✅ SUCCESS - 成功操作
- ⚠️ WARNING - 警告
- ❌ ERROR - 错误
- 🧪 MOLECULAR - 分子相关
- 📡 NETWORK - 网络通信
- 💾 STORAGE - 数据存储
- 🔗 CONNECTION - 连接状态
- ⚡ WEBSOCKET - WebSocket通信

## Important Notes

### 开发原则
- **架构一致性**: 新功能必须遵循方案B的属性驱动模式
- **节点ID绑定**: 所有UI操作严格绑定到节点ID，禁止文件名查找
- **代码质量**: 保持函数简洁（<50行），避免过度设计

### 开发流程
- **Python修改**: 需要重启ComfyUI服务器
- **JavaScript修改**: 刷新浏览器即可
- **调试工具**: 使用浏览器控制台内置的debug函数

### 技术规范
- **日志系统**: 必须使用统一的ALCHEM日志系统
- **WebSocket**: 使用提供的调试函数测试实时同步
- **内存管理**: 基于Tab感知的节点ID存储，确保数据隔离