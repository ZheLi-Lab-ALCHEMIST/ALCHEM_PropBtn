# ALCHEM_PropBtn 模块依赖关系

## 📊 导入结构概览

### 统一导入策略
- **使用绝对导入**: 所有模块使用 `from ALCHEM_PropBtn.xxx import yyy` 格式
- **无回退逻辑**: 直接导入，失败即报错，便于调试
- **清晰的层次**: backend → mixins → nodes → __init__

## 🔄 模块依赖关系图

```
ALCHEM_PropBtn/
├── backend/
│   ├── logging_config.py      # 无依赖，提供日志功能
│   ├── websocket_server.py    # 依赖: logging_config
│   ├── memory.py              # 依赖: logging_config, websocket_server
│   ├── molecular_utils.py     # 依赖: logging_config, memory
│   └── api.py                 # 依赖: memory, molecular_utils, websocket_server
│
├── nodes/
│   ├── mixins/
│   │   └── molstar_display_mixin.py  # 依赖: backend.molecular_utils, backend.memory
│   │
│   ├── examples_with_mixin.py   # 依赖: mixins.molstar_display_mixin (推荐使用)
│   │
│   └── [已废弃的节点文件]       # ⚠️ DEPRECATED
│       ├── standard_molecular_node.py
│       ├── test_simple_node.py
│       ├── test_tab_aware_processing.py
│       └── simple_process_node.py
│
└── __init__.py                # 导入所有节点，注册到ComfyUI

```

## 📦 核心模块说明

### backend/logging_config.py
- **作用**: 统一的日志系统
- **依赖**: 无（基础模块）
- **导出**: `get_alchem_logger()`, `get_memory_logger()`

### backend/memory.py
- **作用**: Tab感知的内存管理
- **依赖**: 
  - `from .logging_config import get_memory_logger`
  - `from .websocket_server import notify_molecular_update, notify_molecular_edit, notify_molecular_delete`
- **导出**: `MOLECULAR_DATA_CACHE`, `CACHE_LOCK`, `store_molecular_data()`, `get_molecular_data()`

### backend/molecular_utils.py
- **作用**: 分子数据获取工具
- **依赖**:
  - `from .logging_config import get_alchem_logger`
  - `from .memory import get_cache_status, get_molecular_data`
- **导出**: `get_molecular_content()`

### nodes/mixins/molstar_display_mixin.py
- **作用**: 3D显示功能混入
- **依赖**:
  - `from ALCHEM_PropBtn.backend.molecular_utils import get_molecular_content`
  - `from ALCHEM_PropBtn.backend.memory import MOLECULAR_DATA_CACHE, CACHE_LOCK, store_molecular_data`
- **导出**: `MolstarDisplayMixin` 类

## 🚀 推荐的导入方式

### 创建新节点（使用Mixin）
```python
from ALCHEM_PropBtn.nodes.mixins.molstar_display_mixin import MolstarDisplayMixin

class YourNode(MolstarDisplayMixin):
    # 你的节点实现
    pass
```

### 使用后端功能
```python
# 日志
from ALCHEM_PropBtn.backend.logging_config import get_alchem_logger
logger = get_alchem_logger('YourModule')

# 内存管理
from ALCHEM_PropBtn.backend.memory import store_molecular_data, get_molecular_data

# 分子数据工具
from ALCHEM_PropBtn.backend.molecular_utils import get_molecular_content
```

## ⚠️ 废弃节点说明

以下节点已标记为 DEPRECATED，仅供参考：
- `standard_molecular_node.py` - 传统节点模板
- `test_simple_node.py` - 测试节点
- `test_tab_aware_processing.py` - Tab感知处理节点
- `simple_process_node.py` - 简化处理节点

**建议**: 新节点开发请使用 `MolstarDisplayMixin` 架构，参考 `examples_with_mixin.py`

## 📝 导入清理总结

### 已完成的改进
1. ✅ 移除所有 try/except 导入回退
2. ✅ 统一使用绝对导入路径
3. ✅ 移除 sys.path 修改
4. ✅ 标记废弃节点
5. ✅ 创建清晰的依赖关系图

### 导入错误处理
- 直接让导入错误暴露，便于调试
- 不创建空函数作为回退
- 保持代码简洁明了