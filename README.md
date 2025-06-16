# ALCHEM_PropBtn - ComfyUI 分子处理扩展

🧪 一个专业的ComfyUI自定义节点扩展，专注于分子文件处理、3D可视化和实时编辑功能。

## ✨ 核心特性

- 🧬 **分子文件处理** - 支持PDB、MOL、MOL2、SDF等格式
- 🎯 **属性驱动架构** - 通过INPUT_TYPES属性自动启用功能
- 🚀 **实时同步** - WebSocket实时数据同步和编辑
- 🔧 **内存管理** - Tab感知的智能内存缓存系统
- 📡 **3D可视化** - 集成MolStar进行分子3D显示
- ⚡ **模块化设计** - 清晰的前后端分离架构

## 🎯 快速开始

### 安装

1. 克隆到ComfyUI自定义节点目录：
```bash
cd ComfyUI/custom_nodes/
git clone <repository-url> ALCHEM_PropBtn
```

2. 重启ComfyUI

3. 在节点列表中找到"🧪 ALCHEM"分类

### 基本使用

1. **添加标准分子节点**：
   - 拖入"🧪📁 Standard Molecular Analysis"节点
   - 点击"📁 Upload"按钮上传分子文件
   - 点击"🧪 3D View"按钮查看3D结构

2. **分子处理链**：
   - 上游节点 → Tab感知处理节点 → 下游节点
   - 支持删除氢原子、分子居中等操作
   - 每个节点独立存储，避免数据混乱

## 🏗️ 项目架构

### 方案B架构（节点主动数据获取）

```
┌─ 节点定义 ──┐    ┌─ 前端检测 ──┐    ┌─ 后端存储 ──┐
│ INPUT_TYPES │ ─► │ JS模块检测  │ ─► │ 内存缓存    │
│ 特殊属性    │    │ 添加Widget  │    │ 节点ID索引  │
└─────────────┘    └─────────────┘    └─────────────┘
                           │
┌─ 节点执行 ──┐    ┌─ 数据获取 ──┘
│ 工具函数    │ ◄──│ API调用
│ 内存读取    │    │ WebSocket同步
└─────────────┘    └─────────────
```

### 目录结构

```
ALCHEM_PropBtn/
├── __init__.py                 # 节点注册入口
├── backend/                    # 后端服务
│   ├── api.py                 # API路由处理
│   ├── memory.py              # 内存管理系统
│   ├── molecular_utils.py     # 分子数据工具
│   ├── websocket_server.py    # WebSocket服务
│   └── logging_config.py      # 统一日志系统
├── nodes/                      # 节点定义
│   ├── standard_molecular_node.py    # 标准分子节点
│   ├── test_simple_node.py          # 测试节点
│   └── test_tab_aware_processing.py # 处理节点
├── web/                        # 前端资源
│   ├── js/
│   │   ├── extensionMain.js   # 扩展协调器
│   │   ├── uploadMolecules.js # 上传模块
│   │   ├── custom3DDisplay.js # 3D显示模块
│   │   ├── modules/           # 功能模块
│   │   └── utils/             # 工具函数
│   ├── css/                   # 样式文件
│   └── lib/                   # 第三方库
└── docs/                       # 文档
```

## 🧪 核心节点

### 1. Standard Molecular Analysis Node
- **功能**: 基础分子文件分析和上传
- **属性**: `molecular_upload: True`, `molstar_3d_display: True`
- **用途**: 工作流起点，上传和初始化分子数据

### 2. Tab-Aware Processing Node  
- **功能**: 分子数据处理和编辑
- **处理类型**: 删除氢原子、分子居中、简单编辑
- **特点**: Tab感知，避免数据混乱

### 3. Simple Test Node
- **功能**: 基础功能测试和验证
- **用途**: 开发和调试

## 🔧 开发指南

### 创建自定义节点

```python
class YourMolecularNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "molecular_file": ("STRING", {
                    "molecular_upload": True,       # 启用上传功能
                    "molstar_3d_display": True,     # 启用3D显示
                    "molecular_folder": "molecules", # 存储目录
                    "display_mode": "ball_and_stick"
                })
            }
        }
    
    def process_data(self, molecular_file, **kwargs):
        # 使用工具函数获取数据
        from ..backend.molecular_utils import get_molecular_content
        content = get_molecular_content(molecular_file)
        
        # 处理逻辑...
        return (result,)
```

### 属性配置

| 属性 | 类型 | 功能 | 示例 |
|-----|------|------|------|
| `molecular_upload` | bool | 启用上传按钮 | `True` |
| `molstar_3d_display` | bool | 启用3D显示按钮 | `True` |
| `molecular_folder` | str | 文件存储目录 | `"molecules"` |
| `display_mode` | str | 3D显示模式 | `"ball_and_stick"` |
| `background_color` | str | 3D背景色 | `"#1E1E1E"` |

## 🔌 API接口

### REST API
- `POST /alchem_propbtn/api/upload_molecular` - 分子文件上传
- `POST /alchem_propbtn/api/molecular` - 分子数据操作
- `GET /alchem_propbtn/api/status` - 系统状态查询

### WebSocket
- `GET /alchem_propbtn/ws` - 实时数据同步连接
- 支持数据变更通知和自动更新

## 🎨 UI组件

### 自动生成的Widget
- **📁 Upload按钮** - 文件上传界面
- **🧪 3D View按钮** - MolStar 3D查看器
- **🔧 Edit按钮** - 实时分子编辑

### 3D查看器特性
- MolStar集成
- 多种显示模式
- 实时编辑同步
- 响应式设计

## 🚀 高级功能

### Tab感知内存管理
- 多Tab隔离存储
- 智能节点ID生成
- 自动缓存清理

### WebSocket实时同步
- 数据变更推送
- 自动UI更新
- 连接管理和重连

### 统一日志系统
```python
from backend.logging_config import get_alchem_logger
logger = get_alchem_logger('ModuleName')

logger.success("操作成功")
logger.molecular("分子相关操作")
logger.network("网络通信")
```

## 🐛 调试工具

浏览器控制台中可用的调试函数：

```javascript
// 扩展状态
window.getCustomWidgetStatus()

// WebSocket调试
debugWebSocket()
debugNodeIds()

// 多Tab内存调试
debugMultiTabMemory()

// 日志级别控制
setGlobalLogLevel('debug')
```

## 📝 许可证

[在此添加许可证信息]

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 支持

如有问题，请提交Issue或联系开发团队。