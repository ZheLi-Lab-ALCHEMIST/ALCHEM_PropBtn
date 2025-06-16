# ALCHEM_PropBtn 开发者指南

## 🚀 快速开始

### 开发环境设置

1. **基础要求**:
   - ComfyUI 已安装并运行
   - Python 3.8+ 
   - 现代浏览器（支持ES6+）

2. **开发工具**:
   - 浏览器开发者工具
   - Python IDE（推荐VS Code）
   - Git版本控制

### 项目结构理解

```
ALCHEM_PropBtn/
├── 📁 nodes/           # 节点定义（Python）
├── 📁 backend/         # 后端服务（Python）  
├── 📁 web/            # 前端资源（JavaScript）
├── 📁 docs/           # 文档
└── 📄 CLAUDE.md       # AI开发指导
```

## 🧬 工作流连接指南

### 节点输入输出规范

#### 1. Upload节点（StandardMolecularAnalysisNode）
```python
输入: molecular_file (STRING) - 分子文件名
输出: 
  - file_content (STRING) - 分子文件内容 🔑
  - analysis_result (STRING) - 分析结果
```

#### 2. Process节点（TabAwareProcessingNode）
```python
输入: 
  - input_molecular_content (STRING, multiline) - 分子文件内容 🔑
  - output_filename (STRING) - 输出文件名
  - processing_type - 处理类型
输出:
  - processed_content (STRING) - 处理后的分子内容 🔑
  - processed_filename (STRING) - 处理后的文件名
  - processing_report (STRING) - 处理报告
```

### 正确的连接方式

#### 基本工作流
```
StandardMolecularAnalysisNode
    ↓ file_content
TabAwareProcessingNode
    ↓ processed_content  
AnotherProcessingNode
```

#### 多步处理工作流
```
Upload节点 → Process节点1 → Process节点2 → Display节点
         ↓              ↓              ↓
      原始文件      删除氢原子      分子居中
```

## 🔧 开发工作流

### 1. 修改Python代码

```bash
# 修改节点代码
vim nodes/your_node.py

# 重启ComfyUI（必须！）
# 直接重启ComfyUI服务器
```

### 2. 修改JavaScript代码

```bash
# 修改前端代码
vim web/js/your_module.js

# 刷新浏览器页面即可
```

### 3. 调试和测试

```javascript
// 浏览器控制台调试工具
window.getCustomWidgetStatus()     // 查看扩展状态
debugWebSocket()                   // WebSocket状态
debugNodeIds()                     // 节点ID和内存状态
debugMultiTabMemory()              // 多Tab内存测试

// 设置日志级别
setGlobalLogLevel('debug')         // 显示详细日志
```

## 🏗️ 创建自定义节点

### 快速开始模板

#### 1. 复制标准模板
```bash
cp nodes/standard_molecular_node.py nodes/your_new_node.py
```

#### 2. 基础节点结构
```python
from ..backend.molecular_utils import get_molecular_content

class YourCustomNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "molecular_file": ("STRING", {
                    "molecular_upload": True,        # 🔑 启用上传按钮
                    "molstar_3d_display": True,      # 🔑 启用3D显示按钮
                    "molecular_folder": "molecules", # 存储文件夹
                    "tooltip": "你的节点说明"
                }),
                "custom_param": ("STRING", {"default": "value"})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("result", "report")
    FUNCTION = "process_data"
    CATEGORY = "🧪 ALCHEM/Your Category"
    
    def process_data(self, molecular_file, custom_param, **kwargs):
        """处理分子数据"""
        try:
            # 🔑 第1步：获取分子数据（必须）
            content, metadata = get_molecular_content(molecular_file)
            
            # 🔑 第2步：检查获取是否成功（必须）
            if not metadata.get('success'):
                return ("", f"错误：{metadata.get('error')}")
            
            # 🚀 第3步：你的业务逻辑
            result = self.your_processing_logic(content, metadata, custom_param)
            
            return (result, "处理完成")
            
        except Exception as e:
            return ("", f"处理异常：{str(e)}")
    
    def your_processing_logic(self, content, metadata, param):
        """实现你的具体功能"""
        # content: 完整的分子文件内容字符串
        # metadata: 包含格式、原子数等信息的字典
        
        # 利用预分析的信息
        file_format = metadata.get('format_name', 'Unknown')
        atom_count = metadata.get('atoms', 0)
        data_source = metadata.get('source', 'unknown')
        
        # 在这里添加你的处理逻辑
        processed_content = content  # 示例：直接返回原内容
        
        return processed_content

# 节点注册
NODE_CLASS_MAPPINGS = {
    "YourCustomNode": YourCustomNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "YourCustomNode": "🧪 Your Custom Node",
}
```

#### 3. 在__init__.py中注册
```python
from .nodes.your_new_node import NODE_CLASS_MAPPINGS as YOUR_MAPPINGS
NODE_CLASS_MAPPINGS.update(YOUR_MAPPINGS)
```

### 注册节点

在 `__init__.py` 中添加：

```python
# 导入你的节点
try:
    from .nodes.your_custom_node import NODE_CLASS_MAPPINGS as YOUR_MAPPINGS
    NODE_CLASS_MAPPINGS.update(YOUR_MAPPINGS)
    logger.success("你的节点加载成功")
except ImportError as e:
    logger.warning(f"你的节点导入失败: {e}")
```

## 🎨 创建自定义Widget

### 前端Widget开发

1. **定义检测逻辑**:

```javascript
// web/js/extensionMain.js
export const processYourWidget = (nodeType, nodeData) => {
    const { input } = nodeData ?? {};
    const { required } = input ?? {};
    
    // 查找你的自定义属性
    const foundWidget = Object.entries(required).find(([_, inputSpec]) =>
        inputSpec[1]?.your_custom_attribute === true
    );

    if (foundWidget) {
        const [inputName, inputSpec] = foundWidget;
        return {
            inputName,
            inputSpec,
            your_widget: createYourCustomWidget(inputName, inputSpec)
        };
    }
    
    return null;
};
```

2. **创建Widget工厂**:

```javascript
// web/js/your_widget.js
export const createYourCustomWidget = () => {
    return (node, inputName, inputData) => {
        const inputOptions = inputData[1] ?? {};
        
        // 创建自定义按钮
        const widget = node.addWidget(
            'button',
            `${inputName}_custom`,
            '🎯 Your Action',
            () => {
                // 你的按钮逻辑
                handleYourAction(node, inputName);
            },
            { serialize: false }
        );
        
        return { widget };
    };
};

const handleYourAction = async (node, inputName) => {
    // 实现你的功能逻辑
    console.log('执行自定义操作');
};
```

## 🔌 API开发

### 后端API端点

```python
# backend/api.py
@app.route('/alchem_propbtn/api/your_feature', methods=['POST'])
async def handle_your_feature(request):
    """处理你的自定义API请求"""
    try:
        data = await request.json()
        
        # 验证请求
        if not data.get('node_id'):
            return web.json_response({'success': False, 'error': '缺少node_id'})
        
        # 处理逻辑
        result = await process_your_feature(data)
        
        # 返回结果
        return web.json_response({
            'success': True,
            'data': result,
            'message': '操作成功'
        })
        
    except Exception as e:
        logger.error(f"API错误: {e}")
        return web.json_response({'success': False, 'error': str(e)})
```

### 前端API调用

```javascript
// web/js/modules/api-client.js
export class APIClient {
    async callYourFeature(nodeId, params) {
        try {
            const response = await fetch('/alchem_propbtn/api/your_feature', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    node_id: nodeId,
                    ...params
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                return result.data;
            } else {
                throw new Error(result.error);
            }
            
        } catch (error) {
            console.error('API调用失败:', error);
            throw error;
        }
    }
}
```

## 🧪 测试和调试

### 单元测试

```python
# 创建测试节点进行验证
class YourTestNode:
    def test_basic_functionality(self):
        """测试基础功能"""
        # 测试代码
        pass
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试代码
        pass
```

### 调试技巧

1. **Python调试**:
```python
from ..backend.logging_config import get_alchem_logger
logger = get_alchem_logger('YourModule')

logger.debug("调试信息")
logger.success("操作成功")
logger.error("错误信息")
```

2. **JavaScript调试**:
```javascript
// 使用统一日志系统
import { getALCHEMLogger } from './utils/logger.js';
const logger = getALCHEMLogger('YourModule');

logger.debug("调试信息");
logger.success("操作成功");
```

3. **网络调试**:
```javascript
// 监听WebSocket消息
webSocketClient.on('your_event', (message) => {
    console.log('收到消息:', message);
});
```

## 📊 性能优化

### 内存管理

```python
# 使用Tab感知的节点ID
def get_unique_node_id(self, node_id):
    tab_id = self.get_current_tab_id()
    return f"{tab_id}_node_{node_id}"

# 及时清理缓存
def cleanup_old_cache(self):
    current_time = time.time()
    for key, data in list(CACHE.items()):
        if current_time - data['timestamp'] > CACHE_TIMEOUT:
            del CACHE[key]
```

### 前端优化

```javascript
// 防抖处理
const debouncedHandler = debounce(yourHandler, 300);

// 按需加载
const loadMolstarWhenNeeded = async () => {
    if (!window.MolStar) {
        await loadMolstarLibrary();
    }
};

// 缓存重复请求
const requestCache = new Map();
const cachedAPICall = async (key, apiCall) => {
    if (requestCache.has(key)) {
        return requestCache.get(key);
    }
    
    const result = await apiCall();
    requestCache.set(key, result);
    return result;
};
```

## 🔒 安全注意事项

### 输入验证

```python
def validate_molecular_file(content):
    """验证分子文件内容"""
    if len(content) > MAX_FILE_SIZE:
        raise ValueError("文件过大")
    
    if not re.match(r'^[A-Za-z0-9\s\.\-\+\n]+$', content):
        raise ValueError("文件包含无效字符")
    
    return True
```

### 错误处理

```python
try:
    result = process_molecular_data(content)
except Exception as e:
    logger.error(f"处理失败: {e}")
    # 不要泄露敏感信息
    return {"error": "处理失败，请检查输入"}
```

## 📝 代码规范

### Python代码风格

```python
# 使用类型提示
def process_data(self, content: str, options: dict) -> tuple[str, str]:
    """
    处理分子数据
    
    Args:
        content: 分子文件内容
        options: 处理选项
        
    Returns:
        tuple: (处理结果, 状态信息)
    """
    pass

# 使用统一的日志系统
logger = get_alchem_logger(__name__)

# 函数保持简洁（<50行）
def simple_function():
    """保持函数简洁"""
    pass
```

### JavaScript代码风格

```javascript
// 使用ES6+语法
const processData = async (data) => {
    try {
        const result = await apiCall(data);
        return result;
    } catch (error) {
        logger.error('处理失败:', error);
        throw error;
    }
};

// 使用统一的错误处理
const handleError = (error, context) => {
    logger.error(`${context}: ${error.message}`);
    // 用户友好的错误提示
    alert(`操作失败: ${error.message}`);
};
```

## 🚀 部署和发布

### 版本管理

```bash
# 更新版本号
# 在package.json中更新version字段

# 创建发布tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### 文档更新

1. 更新README.md
2. 更新CLAUDE.md中的当前状态
3. 添加新功能的使用说明
4. 更新API文档

## 💡 常见问题解决

### 节点不显示
- 检查`__init__.py`中的节点注册
- 确认ComfyUI重启
- 查看控制台错误信息

### Widget不工作
- 检查属性名拼写
- 确认前端模块加载
- 使用浏览器控制台调试

### API调用失败
- 检查网络连接
- 验证请求格式
- 查看后端日志

### 内存数据丢失
- 确认使用正确的节点ID
- 检查Tab感知逻辑
- 验证缓存未被清理

## 📞 获取帮助

- 查看项目文档：`docs/` 目录
- 使用调试工具：浏览器控制台函数
- 检查日志输出：ComfyUI控制台
- 提交Issue：项目仓库