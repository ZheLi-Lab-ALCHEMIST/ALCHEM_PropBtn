# 🧪 ALCHEM_PropBtn 清洁架构文档

> **代码清理完成** - 移除了所有历史遗留的"屎山"代码，保持架构简洁性
> 更新时间：2025年6月13日

## 🎯 核心架构：方案B - 节点主动数据获取

### 📁 精简后的目录结构

```
ALCHEM_PropBtn/
├── backend/                    # 后端核心模块
│   ├── molecular_memory.py     # ✅ 内存管理系统
│   ├── molecular_api.py        # ✅ RESTful API处理器
│   └── molecular_utils.py      # ✅ 方案B核心工具 (NEW)
├── nodes/                      # 节点定义
│   ├── test_simple_node.py     # ✅ 测试验证节点
│   ├── standard_molecular_node.py # ✅ 标准开发模板
│   └── nodes.py               # 🗑️ 废弃文件（已清空）
├── web/js/                     # 前端JavaScript模块
│   ├── extensionMain.js        # ✅ 主协调器
│   ├── uploadMolecules.js      # ✅ 分子上传处理
│   ├── custom3DDisplay.js      # ✅ 3D显示主协调器
│   └── modules/               # ✅ 模块化JS组件
├── docs/                       # 文档
│   ├── NODE_DEVELOPMENT_GUIDE.md # ✅ 开发快速指南
│   └── CLEAN_ARCHITECTURE.md    # ✅ 本文档
└── __init__.py                # ✅ 插件入口（已简化）
```

### 🗑️ 已删除的废弃代码

#### 完全删除的文件：
- `backend/execution_hook.py` - 方案A的hook机制，已废弃
- `nodes/test_node.py` - 早期测试节点，已被test_simple_node.py替代
- `tests/` 整个目录 - 过时的测试脚本

#### 清空的废弃文件：
- `nodes/nodes.py` - 所有旧节点已清空，保留文件避免导入错误

#### 简化的模块：
- `__init__.py` - 移除了execution_hook导入，只保留核心API注册

## 🎯 清洁架构的核心原则

### 1. 单一职责原则
- **molecular_memory.py**: 专注内存管理
- **molecular_api.py**: 专注API处理
- **molecular_utils.py**: 专注数据获取工具
- **前端模块**: 各自专注特定功能

### 2. 依赖倒置原则
- 节点不直接访问内存，通过molecular_utils工具
- 前端不直接操作后端，通过REST API
- 模块间通过明确的接口通信

### 3. 开闭原则
- 新节点通过复制模板开发，无需修改核心代码
- 工具函数支持扩展，不需要修改现有逻辑

## 🚀 数据流架构（方案B）

### 📤 上传流程：
```
用户点击📁 → uploadMolecules.js → /api/upload_molecular → molecular_memory.py
```

### 🧪 3D显示流程：
```
用户点击🧪 → custom3DDisplay.js → /api/molecular → molecular_memory.py → MolStar
```

### ⚙️ 节点执行流程：
```
节点执行 → molecular_utils.get_molecular_content() → molecular_memory.py → 返回内容
```

## 📋 有效的节点列表

### 🧪 测试节点
- **SimpleUploadAndDisplayTestNode** (`test_simple_node.py`)
  - 用途：验证架构功能
  - 特点：展示方案B的使用方法

### 🏗️ 标准模板节点
- **StandardMolecularAnalysisNode** (`standard_molecular_node.py`)
  - 用途：开发参考模板
  - 特点：完整的功能示例和文档

## 🛠️ 开发新节点的标准流程

### 1. 复制模板
```bash
cp nodes/standard_molecular_node.py nodes/your_new_node.py
```

### 2. 修改节点类
```python
class YourNewNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "molecular_file": ("STRING", {
                    "molecular_upload": True,      # 必须
                    "molstar_3d_display": True,    # 必须
                    "tooltip": "你的说明"
                })
            }
        }
    
    def your_function(self, molecular_file):
        # 使用工具获取数据
        from ..backend.molecular_utils import get_molecular_content
        content, metadata = get_molecular_content(molecular_file)
        
        # 你的业务逻辑
        return your_result
```

### 3. 注册节点
在`__init__.py`中添加导入即可自动注册。

## 🔧 核心API端点

### 分子数据查询
- **POST** `/alchem_propbtn/api/molecular`
- 用途：前端获取分子数据，支持3D显示

### 分子文件上传  
- **POST** `/alchem_propbtn/api/upload_molecular`
- 用途：上传分子文件到后端内存

### 系统状态监控
- **GET** `/alchem_propbtn/api/status`
- 用途：调试和监控系统状态

## 📊 性能优化特性

### 1. 内存缓存系统
- 高速访问：毫秒级数据检索
- 智能缓存：LRU策略，自动清理
- 多节点支持：独立的数据隔离

### 2. 智能数据获取
- 自动类型判断：文件名 vs 文件内容
- 多数据源：内存缓存 → 文件系统回退
- 错误处理：详细的调试信息

### 3. 模块化前端
- 按需加载：减少初始加载时间
- 独立模块：降低耦合度
- 组件复用：提高开发效率

## 🔍 调试和监控

### 日志级别
- **INFO**: 正常操作日志
- **DEBUG**: 详细调试信息
- **WARNING**: 非致命错误
- **ERROR**: 严重错误

### 监控端点
- `/alchem_propbtn/api/status` - 系统状态
- molecular_utils工具返回详细metadata

### 常见问题排查
1. **节点找不到数据** → 检查metadata.success和error信息
2. **按钮不显示** → 确认molecular_upload和molstar_3d_display属性
3. **3D显示异常** → 检查浏览器控制台和网络请求

## 🎉 清理成果

### 代码行数减少
- **删除**: ~3000行废弃代码
- **简化**: ~500行重构代码
- **保留**: ~2000行核心功能代码

### 维护性提升
- **模块职责清晰** - 每个文件专注特定功能
- **依赖关系简单** - 减少模块间耦合
- **文档完整** - 详细的开发指南

### 稳定性增强
- **不依赖ComfyUI内部API** - 避免版本兼容问题
- **明确的错误处理** - 问题更容易定位
- **标准化的开发流程** - 减少开发错误

---

**架构清理完成** ✅  
现在ALCHEM_PropBtn拥有一个简洁、稳定、易维护的代码架构！