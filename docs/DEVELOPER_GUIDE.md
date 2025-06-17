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

### 🧪 推荐使用Mixin架构（新方式）

#### 1. 使用Mixin模板（推荐）
```bash
# 参考现代化的Mixin示例
cp nodes/examples_with_mixin.py nodes/your_new_node.py
```

#### 2. 传统方式（不推荐，代码复杂）
```bash
cp nodes/standard_molecular_node.py nodes/your_new_node.py
```

### 🧪 Mixin架构节点开发

#### 📋 两种节点类型选择

##### 🔸 类型1: 输入节点（文件名输入模式）
**用途**: 工作流起点，上传分子文件，进行分析
**示例**: `SimpleMolecularAnalyzer`

```python
from .mixins.molstar_display_mixin import MolstarDisplayMixin

class YourAnalyzerNode(MolstarDisplayMixin):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                **cls.get_molstar_input_config("molecular_file"),  # 🔑 一行启用📁上传+🧪3D
                # 你的业务参数
                "analysis_type": (["basic", "detailed", "advanced"], {"default": "basic"}),
                "custom_option": ("STRING", {"default": "value"})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("analysis_result", "molecular_content", "debug_info")
    FUNCTION = "analyze_molecule"
    CATEGORY = "🧪 ALCHEM/Your Category"
    
    def analyze_molecule(self, molecular_file, analysis_type, custom_option, **kwargs):
        # 🔑 一行获取数据
        content, metadata = self.get_molecular_data(molecular_file, kwargs)
        
        # 🔑 一行验证数据
        if not self.validate_molecular_data(metadata):
            return self.create_error_output(metadata)
        
        # 🚀 专注业务逻辑
        analysis_result = self._perform_analysis(content, metadata, analysis_type, custom_option)
        debug_info = self.generate_debug_info(kwargs.get('_alchem_node_id'), metadata)
        
        return (analysis_result, content, debug_info)
    
    def _perform_analysis(self, content, metadata, analysis_type, custom_option):
        """你的分析逻辑"""
        # content: 完整分子文件内容
        # metadata: 包含格式、原子数等信息
        
        lines = content.split('\n')
        atom_lines = [line for line in lines if line.startswith(('ATOM', 'HETATM'))]
        
        if analysis_type == "basic":
            return f"分子格式: {metadata.get('format_name')}, 原子数: {len(atom_lines)}"
        elif analysis_type == "detailed":
            # 添加详细分析逻辑
            return f"详细分析结果..."
        else:
            # 高级分析
            return f"高级分析结果..."
    
    @classmethod
    def IS_CHANGED(cls, molecular_file, analysis_type, custom_option, _alchem_node_id=""):
        return cls.simple_force_execute_is_changed(
            molecular_file=molecular_file,
            analysis_type=analysis_type,
            custom_option=custom_option,
            _alchem_node_id=_alchem_node_id
        )
```

##### 🔸 类型2: 中间节点（内容输入模式）
**用途**: 处理上游数据，进行分子变换、编辑等
**示例**: `SimpleTabAwareProcessor`

```python
class YourProcessingNode(MolstarDisplayMixin):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                **cls.get_processing_input_config(
                    content_param="input_molecular_content",  # 内容输入框
                    output_param="output_filename",           # 🧪3D显示文件名
                    custom_config={
                        'output_config': {
                            "default": "your_processed_molecule.pdb",
                            "tooltip": "处理后的分子文件名"
                        }
                    }
                ),
                # 你的业务参数
                "processing_mode": (["transform", "filter", "edit"], {"default": "transform"}),
                "intensity": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 2.0})
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("processed_content", "processing_report", "debug_info")
    FUNCTION = "process_molecular_data"
    CATEGORY = "🧪 ALCHEM/Your Category"
    
    def process_molecular_data(self, input_molecular_content, output_filename, processing_mode, intensity, **kwargs):
        # 🔑 一行完成整个处理流程！
        return self.process_direct_content(
            content=input_molecular_content,
            output_filename=output_filename,
            node_id=kwargs.get('_alchem_node_id', ''),
            processing_func=self._process_molecular_content,
            processing_mode=processing_mode,
            intensity=intensity
        )
    
    def _process_molecular_content(self, content: str, processing_mode: str, intensity: float) -> str:
        """你的处理逻辑"""
        if processing_mode == "transform":
            return self._transform_molecule(content, intensity)
        elif processing_mode == "filter":
            return self._filter_molecule(content, intensity)
        elif processing_mode == "edit":
            return self._edit_molecule(content, intensity)
        return content
    
    def _transform_molecule(self, content: str, intensity: float) -> str:
        """分子变换逻辑"""
        # 实现你的变换算法
        return content
    
    @classmethod
    def IS_CHANGED(cls, input_molecular_content, output_filename, processing_mode, intensity, _alchem_node_id=""):
        return cls.simple_force_execute_is_changed(
            input_molecular_content=input_molecular_content,
            output_filename=output_filename,
            processing_mode=processing_mode,
            intensity=intensity,
            _alchem_node_id=_alchem_node_id
        )
```

#### 📋 传统方式节点结构（不推荐）
```python
# ❌ 传统方式：需要手动配置大量属性，容易出错
from ..backend.molecular_utils import get_molecular_content

class YourCustomNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "molecular_file": ("STRING", {
                    "molecular_upload": True,        
                    "molstar_3d_display": True,      
                    "molecular_folder": "molecules", 
                    "display_mode": "ball_and_stick",
                    "background_color": "#1E1E1E",
                    "tooltip": "手动配置所有属性"
                }),
                "_alchem_node_id": ("STRING", {"default": ""}),  # 手动添加
                "custom_param": ("STRING", {"default": "value"})
            }
        }
    
    # ... 需要手动实现所有错误处理、调试信息等逻辑
```

#### 3. 节点注册和导出

**在节点文件末尾添加：**
```python
# 节点注册
NODE_CLASS_MAPPINGS = {
    "YourAnalyzerNode": YourAnalyzerNode,
    "YourProcessingNode": YourProcessingNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "YourAnalyzerNode": "🧪📊 Your Analyzer (输入节点)",
    "YourProcessingNode": "🧪⚡ Your Processor (处理节点)",
}
```

**在 `__init__.py` 中注册：**
```python
# 导入你的节点
try:
    from .nodes.your_new_node import NODE_CLASS_MAPPINGS as YOUR_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as YOUR_DISPLAY_MAPPINGS
    NODE_CLASS_MAPPINGS.update(YOUR_MAPPINGS)
    NODE_DISPLAY_NAME_MAPPINGS.update(YOUR_DISPLAY_MAPPINGS)
    logger.success("你的节点加载成功")
except ImportError as e:
    logger.warning(f"你的节点导入失败: {e}")
```

### 🧪 Mixin优势总结

#### ✅ 使用Mixin的好处：
1. **代码减少90%** - 从400+行减少到30-50行
2. **零配置3D显示** - 一行代码启用完整功能
3. **自动错误处理** - 标准化的异常处理模板
4. **严格数据隔离** - 避免重名文件数据混乱
5. **Tab感知内存** - 多Tab环境下的智能数据管理
6. **自动调试信息** - 统一的调试信息生成
7. **强制缓存一致性** - 自动解决IS_CHANGED问题

#### ❌ 传统方式的问题：
1. **重复代码多** - 每个节点都要写相同的基础逻辑
2. **容易出错** - 手动配置属性容易遗漏
3. **维护困难** - 修改基础功能需要改所有节点
4. **数据混乱** - 重名文件会导致节点间数据错乱
5. **调试困难** - 缺乏统一的调试信息

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
# 创建发布tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# 查看版本历史
git tag -l
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