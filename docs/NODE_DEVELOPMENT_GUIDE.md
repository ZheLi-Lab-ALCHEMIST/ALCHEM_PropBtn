# 🧪 ALCHEM分子节点开发快速指南

## 🚀 快速开始

### 1. 复制模板
```bash
cp nodes/standard_molecular_node.py nodes/your_new_node.py
```

### 2. 修改类名和显示名
```python
class YourNewNode:
    # 修改节点功能逻辑
    
NODE_CLASS_MAPPINGS = {
    "YourNewNode": YourNewNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "YourNewNode": "🧪 Your Node Display Name",
}
```

### 3. 在__init__.py中注册
```python
from .nodes.your_new_node import NODE_CLASS_MAPPINGS as YOUR_MAPPINGS
NODE_CLASS_MAPPINGS.update(YOUR_MAPPINGS)
```

## 📋 必需的INPUT_TYPES配置

```python
@classmethod
def INPUT_TYPES(cls):
    return {
        "required": {
            "molecular_file": ("STRING", {
                "molecular_upload": True,      # 🔑 必须：启用上传按钮
                "molstar_3d_display": True,    # 🔑 必须：启用3D显示按钮
                "molecular_folder": "molecules", # 推荐：指定存储文件夹
                "tooltip": "你的节点说明"
            }),
            # 其他参数...
        }
    }
```

## 🎯 标准节点函数模板

```python
def your_function(self, molecular_file, other_params):
    """你的节点功能说明"""
    try:
        # 🔑 第1步：获取分子数据（必须）
        from ..backend.molecular_utils import get_molecular_content
        
        content, metadata = get_molecular_content(molecular_file)
        
        # 🔑 第2步：检查获取是否成功（必须）
        if not metadata.get('success'):
            return f"错误：{metadata.get('error')}"
        
        # 🚀 第3步：你的业务逻辑
        result = your_processing_logic(content, metadata)
        
        return result
        
    except Exception as e:
        return f"处理异常：{str(e)}"

def your_processing_logic(self, content, metadata):
    """实现你的具体功能"""
    # content: 完整的分子文件内容字符串
    # metadata: 包含格式、原子数等信息的字典
    
    # 利用预分析的信息
    file_format = metadata.get('format_name', 'Unknown')
    atom_count = metadata.get('atoms', 0)
    data_source = metadata.get('source', 'unknown')
    
    # 实现你的分析逻辑...
    
    return "你的结果"
```

## 📊 元数据信息参考

```python
metadata = {
    # 基本状态
    "success": True,                    # 是否成功获取数据
    "source": "memory_cache",           # 数据来源：memory_cache/file_system/direct_input
    "error": "错误信息",                 # 失败时的错误信息
    
    # 文件信息
    "format": ".pdb",                   # 文件扩展名
    "format_name": "Protein Data Bank", # 格式全名
    "total_lines": 156,                 # 总行数
    "content_length": 5432,             # 内容长度
    "file_size": 5432,                  # 文件大小
    
    # 分子信息（如果可解析）
    "atoms": 124,                       # 原子数量
    "sequences": 3,                     # 序列数量（FASTA格式）
    
    # 来源信息
    "node_id": "4",                     # 源节点ID
    "source_node_id": "4",             # 同上
    "cached_at": "2024-01-01 12:00:00", # 缓存时间
    
    # 调试信息
    "input_type": "filename",           # 输入类型
    "is_filename": True,                # 是否为文件名
    "processing_time": 1609459200.0     # 处理时间戳
}
```

## 🎨 按钮自定义选项

### 上传按钮配置：
```python
"molecular_file": ("STRING", {
    "molecular_upload": True,           # 启用上传按钮
    "molecular_folder": "molecules",    # 存储文件夹
    "tooltip": "按钮提示文字"
})
```

### 3D显示按钮配置：
```python
"molecular_file": ("STRING", {
    "molstar_3d_display": True,         # 启用3D显示按钮
    "display_mode": "ball_and_stick",   # 显示模式：ball_and_stick/spacefill/cartoon
    "background_color": "#1E1E1E",      # 背景色
    "tooltip": "点击查看3D结构"
})
```

## 🔧 常见问题解决

### Q: 节点执行时显示文件名而不是内容？
A: 检查是否使用了`get_molecular_content()`函数获取内容。

### Q: 获取数据失败？
A: 检查`metadata.success`和`metadata.error`了解具体原因。

### Q: 按钮不显示？
A: 确认INPUT_TYPES中设置了`molecular_upload: True`和`molstar_3d_display: True`。

### Q: 3D显示空白？
A: 确认分子文件格式正确，检查浏览器控制台是否有错误。

## 📝 完整示例节点

参考`nodes/standard_molecular_node.py`查看完整的实现示例，包含：
- 完整的错误处理
- 多种分析类型
- 多种输出格式
- 详细的注释说明

## 🚀 性能优化技巧

1. **利用元数据**：使用`metadata`中的预分析结果，避免重复解析
2. **检查成功状态**：总是检查`metadata.success`，快速处理失败情况
3. **缓存友好**：相同文件多次处理时，工具会自动利用缓存
4. **按需获取**：只在真正需要时调用`get_molecular_content()`

开始开发你的分子处理节点吧！🎉