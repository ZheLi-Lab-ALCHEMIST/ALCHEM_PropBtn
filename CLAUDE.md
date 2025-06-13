# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## User Communication Preferences
用中文回答我
每次都用审视的目光，仔公看我输入的潜在问题，你要指出我的问题，并给出明显在我思考框架之外的建议
如果你觉得我说的太离谱了，你就骂回，帮我瞬间清醒
不要过度设计，专注于实现功能。

## Project Overview
ALCHEM_PropBtn 是一个 ComfyUI 自定义节点扩展，专注于分子文件处理和3D可视化。项目采用方案B架构（节点主动数据获取模式），提供上传按钮和3D显示功能。

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

### Active Files (方案B架构)
- `__init__.py` - 主入口，注册节点和API路由
- `nodes/test_simple_node.py` - 测试和验证节点
- `nodes/standard_molecular_node.py` - 标准开发模板
- `backend/api.py` - 简化API模块（上传、查询、状态）
- `backend/memory.py` - 内存管理和数据缓存
- `backend/molecular_utils.py` - 分子数据处理工具
- `web/js/extensionMain.js` - 扩展协调器
- `web/js/uploadMolecules.js` - 分子上传模块
- `web/js/custom3DDisplay.js` - 3D显示模块

### Deprecated Files
- `nodes/nodes.py` - 废弃的旧节点（已被方案B替代）

## Development Commands

### ComfyUI Operations
```bash
# 重启 ComfyUI (开发时经常需要)
# 需要手动重启 ComfyUI 服务器以加载节点更改

# 查看节点加载状态
# 检查 ComfyUI 控制台输出中的 ALCHEM_PropBtn 日志
```

### Development Testing
```bash
# 在浏览器控制台中调试扩展
window.getCustomWidgetStatus()  # 查看扩展状态
window.customWidgetsExtension.status()  # 访问扩展API
window.customWidgetsExtension.utils.setLogLevel('debug')  # 调整日志级别
```

## API Endpoints
- `POST /alchem_propbtn/api/molecular` - 分子数据操作
- `POST /alchem_propbtn/api/upload_molecular` - 文件上传
- `GET /alchem_propbtn/api/status` - 系统状态

## Node Development Guide

### 创建新的分子处理节点
1. 参考 `nodes/standard_molecular_node.py` 作为模板
2. 在 INPUT_TYPES 中添加必要的属性：
   - `molecular_upload: True` for upload functionality
   - `molstar_3d_display: True` for 3D display
3. 使用 `molecular_utils.get_molecular_content()` 获取数据
4. 在 `__init__.py` 中注册新节点

### Widget开发模式
1. 在 `web/js/` 中创建新的功能模块
2. 在 `extensionMain.js` 中注册模块
3. 使用属性检测模式：检测节点属性 → 创建对应Widget

## Key Implementation Details

### 数据流程 (Upload → Display → Process)
1. **Upload**: 用户点击📁按钮 → uploadMolecules.js → API存储到内存
2. **Display**: 用户点击🧪按钮 → custom3DDisplay.js → 从内存获取数据 → MolStar渲染
3. **Process**: 节点执行时 → molecular_utils.get_molecular_content() → 从内存获取处理

### Memory Management
- 文件内容存储在 `backend/memory.py` 的内存缓存中
- 使用节点ID作为缓存key
- 支持自动清理和状态监控

## Important Notes
- **避免修改废弃文件**: `nodes/nodes.py` 已废弃，不要编辑
- **重启要求**: 修改Python节点后需要重启ComfyUI
- **前端调试**: 使用浏览器控制台查看扩展状态和日志
- **架构一致性**: 新功能应遵循方案B的属性驱动模式