# ComfyUI Custom Widgets Extension

一个模块化的ComfyUI扩展，通过自定义属性为节点添加各种功能Widget，如上传按钮、3D显示等。

## 功能特点

✨ **自定义上传属性** - 演示如何添加自己的上传功能  
🧪 **3D分子显示** - 通过属性自动添加3D显示按钮  
🎨 **美观的UI** - 渐变色按钮和交互式模态框  
📁 **文件分类** - 自动将不同类型的文件存储到不同子文件夹  
🎯 **拖拽支持** - 支持直接拖拽文件到节点上传  
⚡ **实时进度** - 显示上传进度条  
🔄 **自动刷新** - 上传后自动刷新文件列表  
🏗️ **模块化架构** - 协调器 + 功能模块，代码组织清晰  

## 包含的节点

### 1. Custom Upload Text File
- 支持上传文本文件 (.txt, .json, .md)
- 自定义属性: `custom_text_upload: True`
- 文件存储到: `input/texts/` 文件夹
- 可选择文件编码格式
- 返回文件内容文本

### 2. Custom Upload Config File  
- 支持上传配置文件 (.json, .yaml, .yml, .toml)
- 自定义属性: `custom_config_upload: True`
- 文件存储到: `input/configs/` 文件夹
- 支持JSON解析
- 返回原始内容和解析信息

### 3. 🧪 Demo 3D Display Node ⭐ 新增！
- 演示3D显示功能的节点
- 自定义属性: `molstar_3d_display: True`
- 自动添加"🧪 显示3D结构"按钮
- 模拟分子结构数据（苯、水、咖啡因、阿司匹林）
- 美观的3D查看器模态框界面

## 安装方法

1. 将整个 `comfyui-customupload` 文件夹复制到 `ComfyUI/custom_nodes/` 目录下
2. 重启ComfyUI
3. 在节点列表中找到 `custom_upload` 分类下的节点

## 使用方法

### 基本使用
1. 添加任一节点到工作流
2. 对于上传节点：点击"📁 上传文件"按钮选择文件
3. 对于3D显示节点：点击"🧪 显示3D结构"按钮查看分子

### 拖拽上传
1. 直接将文件拖拽到上传节点上
2. 如果文件类型匹配，会自动触发上传

### 3D显示功能 ⭐ 新增！
1. 在`Demo 3D Display Node`中选择分子类型
2. 点击"🧪 显示3D结构"按钮
3. 在弹出的模态框中查看：
   - 📊 分子信息（分子式、分子量等）
   - 🎛️ 控制面板（显示模式切换）
   - 📋 PDB数据预览
   - 💡 功能说明

### 调试支持 🆕
在浏览器控制台中，可以使用以下命令查看扩展状态和控制日志：
```javascript
// 查看扩展状态
window.getCustomWidgetStatus()

// 访问扩展API
window.customWidgetsExtension.status()

// 调整日志级别 (debug, info, warn, error)
window.customWidgetsExtension.utils.setLogLevel('debug')

// 切换调试模式
window.customWidgetsExtension.utils.toggleDebug()
```

### 文件组织
- 文本文件会保存到: `ComfyUI/input/texts/`
- 配置文件会保存到: `ComfyUI/input/configs/`

## 开发者说明

### 扩展配置详解

扩展的核心配置位于 `extensionMain.js` 中：

```javascript
const EXTENSION_CONFIG = {
    // 扩展标识和基本信息
    name: "ComfyUI.CustomWidgets",           // ComfyUI官方扩展注册名称
    displayName: "Custom Widgets Extension", // 用户友好的显示名称  
    version: "1.0.0",
    description: "A modular extension that adds custom widgets...",
    author: "Custom Extension Team",
    
    // 功能模块注册表
    modules: {
        upload: {
            name: "📁 Upload Core",
            description: "File upload functionality with drag & drop support",
            version: "1.0.0"
        },
        display3D: {
            name: "🧪 3D Display", 
            description: "3D molecular structure display integration",
            version: "1.0.0"
        },
        myFeature: {  // 新增模块配置
            name: "🚀 My Feature",
            description: "Custom feature functionality",
            version: "1.0.0"
        }
    },
    
    // 扩展设置
    settings: {
        debugMode: true,              // 调试模式
        logLevel: 'info',            // 日志级别
        autoRefresh: true,           // 自动刷新ComfyUI组件
        enableMetrics: true          // 启用性能监控
    }
};
```

#### Config的作用：

1. **扩展标识管理** - `name` 用于ComfyUI官方注册，`displayName` 用于用户显示
2. **模块注册表** - 统一管理所有功能模块的信息和版本
3. **设置管理** - 控制日志级别、调试模式等运行时行为
4. **状态监控** - 为调试和性能分析提供统一的状态管理
5. **版本控制** - 每个模块独立版本管理，便于维护

### 自定义属性的实现原理

#### 1. 上传属性实现
```python
"text_file": (sorted(text_files), {
    "custom_text_upload": True,  # 🎯 自定义上传属性
    "custom_folder": "texts",
    "tooltip": "选择或上传一个文本文件"
})
```

#### 2. 3D显示属性实现 ⭐ 新增！
```python
"molecule_data": (["benzene", "caffeine", "aspirin", "water"], {
    "molstar_3d_display": True,  # 🎯 3D显示属性
    "display_mode": "ball_and_stick",
    "background_color": "#1E1E1E",
    "tooltip": "选择要显示的分子，点击3D按钮查看结构"
})
```

### 前端检测机制

```javascript
// 检测上传属性 (uploadCore.js)
const isCustomUploadInput = (inputSpec) => {
    return !!(inputOptions['custom_text_upload'] || inputOptions['custom_config_upload']);
};

// 检测3D显示属性 (custom3DDisplay.js) ⭐ 新增！
const isMolstar3DDisplayInput = (inputSpec) => {
    return !!(inputOptions['molstar_3d_display']);
};
```

### Widget创建

```javascript
// 上传Widget (uploadCore.js)
required.upload = createCustomUploadInput(inputName, inputSpec);

// 3D显示Widget (custom3DDisplay.js) ⭐ 新增！
required.molstar_3d = createMolstar3DDisplayInput(inputName, inputSpec);
```

## 🛠️ 开发指南：如何添加新功能按钮

### 步骤1: 创建功能模块文件

在 `web/js/` 目录下创建新的功能模块文件，例如 `myNewFeature.js`：

```javascript
// web/js/myNewFeature.js
import { app } from "../../../scripts/app.js";

// 1. 定义功能样式
export const myFeatureStyles = `
.my-custom-button {
    background: linear-gradient(45deg, #ff9800 0%, #f57c00 100%);
    border: none;
    border-radius: 6px;
    color: white;
    padding: 8px 16px;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    margin: 2px;
}
.my-custom-button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(255,152,0,0.3);
}
`;

// 2. 检测自定义属性
export const isMyFeatureInput = (inputSpec) => {
    const [inputName, inputOptions] = inputSpec;
    if (!inputOptions) return false;
    return !!(inputOptions['my_custom_feature']);
};

// 3. 创建输入定义
export const createMyFeatureInput = (inputName, inputSpec) => [
    'MYCUSTOMFEATURE',
    {
        ...inputSpec[1],
        originalInputName: inputName,
        featureType: 'my_feature'
    }
];

// 4. 功能核心逻辑
const executeMyFeature = async (node, inputName) => {
    try {
        console.log(`🚀 执行自定义功能 for node ${node.id}, input: ${inputName}`);
        
        // 获取节点数据
        const inputWidget = node.widgets.find(w => w.name === inputName);
        const inputValue = inputWidget ? inputWidget.value : 'default';
        
        // 执行你的功能逻辑
        alert(`✨ 功能执行成功！节点: ${node.id}, 输入值: ${inputValue}`);
        
        // 你可以在这里添加任何功能：
        // - 调用API
        // - 打开模态框
        // - 处理数据
        // - 与其他服务集成
        
    } catch (error) {
        console.error('🚀 功能执行失败:', error);
        alert(`功能执行失败: ${error.message}`);
    }
};

// 5. 创建Widget
export const createMyFeatureWidget = () => {
    return (node, inputName, inputData) => {
        const inputOptions = inputData[1] ?? {};
        const { originalInputName } = inputOptions;
        
        const featureWidget = node.addWidget(
            'button',
            `${inputName}_action`,
            '🚀 执行我的功能',
            () => {
                executeMyFeature(node, originalInputName);
            },
            { 
                serialize: false
            }
        );

        console.log(`🚀 Added my feature widget for ${originalInputName} on node ${node.type}`);
        return { widget: featureWidget };
    };
};

// 6. 初始化功能
export const initMyFeature = () => {
    const styleElement = document.createElement('style');
    styleElement.textContent = myFeatureStyles;
    document.head.appendChild(styleElement);
    console.log("🚀 My Feature module initialized");
};

// 7. 处理节点创建
export const handleMyFeatureNodeCreated = (node) => {
    if (node.type === 'MyCustomNode') {
        console.log(`🚀 Enhanced ${node.type} with my custom feature`);
    }
};

// 8. 处理节点定义
export const processMyFeatureNodes = (nodeType, nodeData) => {
    const { input } = nodeData ?? {};
    const { required } = input ?? {};
    if (!required) return null;

    const foundFeature = Object.entries(required).find(([_, inputSpec]) =>
        isMyFeatureInput(inputSpec)
    );

    if (foundFeature) {
        const [inputName, inputSpec] = foundFeature;
        console.log(`🚀 Added my feature for ${nodeData.name}: ${inputName}`);
        return {
            inputName,
            inputSpec,
            my_feature: createMyFeatureInput(inputName, inputSpec)
        };
    }
    
    return null;
};
```

### 步骤2: 在后端节点中添加属性

在 `nodes.py` 中添加新节点：

```python
class MyCustomNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_data": (["option1", "option2", "option3"], {
                    "my_custom_feature": True,  # 🎯 关键：自定义功能属性
                    "tooltip": "选择数据，然后点击功能按钮"
                }),
                "some_text": ("STRING", {"default": "Hello World"})
            }
        }
    
    RETURN_TYPES = ("STRING",)
    FUNCTION = "process"
    CATEGORY = "custom_upload"
    
    def process(self, input_data, some_text):
        return (f"Processed: {input_data} - {some_text}",)

# 注册节点
NODE_CLASS_MAPPINGS["MyCustomNode"] = MyCustomNode
NODE_DISPLAY_NAME_MAPPINGS["MyCustomNode"] = "🚀 My Custom Feature Node"
```

### 步骤3: 注册到扩展协调器

在 `extensionMain.js` 中添加新功能模块：

```javascript
// 在文件顶部添加导入
import { 
    initMyFeature,
    createMyFeatureWidget,
    processMyFeatureNodes,
    handleMyFeatureNodeCreated
} from "./myNewFeature.js";

// 在扩展配置中添加模块
const EXTENSION_CONFIG = {
    // ... 现有配置
    modules: {
        upload: {
            name: "📁 Upload Core",
            description: "File upload functionality with drag & drop support",
            version: "1.0.0"
        },
        display3D: {
            name: "🧪 3D Display", 
            description: "3D molecular structure display integration",
            version: "1.0.0"
        },
        myFeature: {  // 新增模块配置
            name: "🚀 My Feature",
            description: "Custom feature functionality",
            version: "1.0.0"
        }
    }
};

// 在initializeModules函数中添加初始化
const initializeModules = () => {
    try {
        // ... 现有代码
        
        // 初始化新功能模块
        initMyFeature();
        logger.info("My feature module initialized", 'myFeature');
        
        // ... 其余代码
    } catch (error) {
        // ... 错误处理
    }
};

// 在getCustomWidgets函数中注册Widget
const getCustomWidgets = () => {
    try {
        const widgets = {
            CUSTOMUPLOAD: createCustomUploadWidget(),
            MOLSTAR3DDISPLAY: createMolstar3DDisplayWidget(),
            MYCUSTOMFEATURE: createMyFeatureWidget()  // 新增
        };
        // ... 其余代码
    } catch (error) {
        // ... 错误处理
    }
};

// 在beforeRegisterNodeDef函数中处理节点
const beforeRegisterNodeDef = (nodeType, nodeData) => {
    try {
        // ... 现有处理逻辑
        
        // 处理新功能节点
        const myFeatureResult = processMyFeatureNodes(nodeType, nodeData);
        if (myFeatureResult) {
            required.my_feature = myFeatureResult.my_feature;
            logger.debug(`Processed my feature node: ${nodeData.name}`, 'myFeature');
            processed = true;
        }
        
        // ... 其余代码
    } catch (error) {
        // ... 错误处理
    }
};

// 在nodeCreated函数中处理节点创建
const nodeCreated = (node) => {
    try {
        // ... 现有处理逻辑
        
        // 处理新功能节点
        handleMyFeatureNodeCreated(node);
        
        // ... 其余代码
    } catch (error) {
        // ... 错误处理
    }
};
```

### 步骤4: 测试功能

1. 重启ComfyUI
2. 添加 `MyCustomNode` 到工作流
3. 应该会看到"🚀 执行我的功能"按钮
4. 点击按钮测试功能

### 🔧 高级功能开发技巧

#### 1. 与现有系统集成
```javascript
// 检查并使用现有功能
const tryUseExistingFeature = async (node) => {
    if (window.existingFeature && node.hasExistingMethod) {
        await node.hasExistingMethod();
        return true;
    }
    return false;
};
```

#### 2. 添加复杂UI
```javascript
// 创建模态框
const createFeatureModal = (title, content) => {
    const modal = document.createElement('div');
    modal.className = 'custom-feature-modal';
    // ... 模态框代码
    document.body.appendChild(modal);
    return modal;
};
```

#### 3. 异步数据处理
```javascript
// 处理异步操作
const processAsyncFeature = async (node, data) => {
    try {
        const response = await fetch('/api/my-feature', {
            method: 'POST',
            body: JSON.stringify(data),
            headers: { 'Content-Type': 'application/json' }
        });
        return await response.json();
    } catch (error) {
        console.error('Async feature failed:', error);
        throw error;
    }
};
```

#### 4. 状态管理
```javascript
// 功能状态管理
const featureState = {
    isProcessing: false,
    lastResult: null,
    cache: new Map()
};

const updateFeatureState = (key, value) => {
    featureState[key] = value;
    // 触发UI更新
};
```

### 🚀 功能扩展建议

1. **文件处理功能** - 添加 `custom_file_processor: True` 属性
2. **数据可视化** - 添加 `custom_chart_display: True` 属性  
3. **API集成** - 添加 `custom_api_call: True` 属性
4. **数据库操作** - 添加 `custom_db_query: True` 属性
5. **AI模型调用** - 添加 `custom_ai_inference: True` 属性

### 🐛 调试技巧

1. 使用浏览器开发者工具查看控制台日志
2. 利用 `window.customWidgetsExtension.logger` 进行统一日志记录
3. 检查 `window.getCustomWidgetStatus()` 获取扩展状态
4. 在功能函数中添加 `try-catch` 进行错误处理
5. 使用 `window.customWidgetsExtension.utils.setLogLevel('debug')` 调整日志级别

### 🎯 最佳实践

1. **模块化开发** - 每个功能独立一个文件
2. **统一命名** - 使用一致的命名规范
3. **错误处理** - 完善的异常捕获和用户提示
4. **性能优化** - 避免频繁DOM操作，使用事件委托
5. **文档编写** - 为每个功能编写清晰的注释和文档

## 文件结构 🏗️ 三层架构！

```
comfyui-customupload/
├── __init__.py                      # 初始化文件
├── nodes.py                         # 节点定义
├── README.md                       # 说明文档
├── package.json                    # 包信息
├── web/
│   └── js/
│       ├── extensionMain.js        # 🎛️ 扩展协调器 (主入口)
│       ├── uploadCore.js           # 📁 上传核心模块
│       ├── custom3DDisplay.js      # 🧪 3D显示模块
│       └── myNewFeature.js         # 🚀 新功能模块示例
└── example_files/
    ├── sample.txt                  # 示例文本文件
    └── sample_config.json          # 示例配置文件
```

### 🏗️ 三层模块化架构

#### 🎛️ `extensionMain.js` - 扩展协调器 (第1层)
- **职责**: ComfyUI扩展注册和模块协调
- 处理扩展生命周期管理
- 统一日志和错误处理
- 模块间通信协调
- 状态监控和调试支持
- **不包含**: 具体业务逻辑

#### 📁 `uploadCore.js` - 上传核心模块 (第2层)
- **职责**: 上传功能的核心实现
- 文件上传到服务器
- 拖拽支持
- 进度条显示
- 文件类型检测
- 上传Widget创建

#### 🧪 `custom3DDisplay.js` - 3D显示模块 (第2层)
- **职责**: 3D显示功能的核心实现
- MolStar集成逻辑
- 分子数据处理
- 模态框界面
- 3D显示Widget创建

### 🔄 模块间协作流程

```
ComfyUI
   ↓
🎛️ extensionMain.js (协调器)
   ├→ 📁 uploadCore.js (上传功能)
   ├→ 🧪 custom3DDisplay.js (3D显示功能)
   └→ 🚀 myNewFeature.js (新功能模块)
```

### 📊 架构优势

1. **清晰分层** - 协调层 + 功能层，职责明确
2. **独立开发** - 各模块可独立开发和测试
3. **易于维护** - 问题定位精确，修改影响范围小
4. **高可扩展** - 新功能模块可轻松集成
5. **统一管理** - 协调器提供统一的接口和状态管理

## 技术特点

- 🔗 **完全兼容ComfyUI原生机制** - 使用标准的扩展API
- 🎨 **模块化UI组件** - 美观的按钮和模态框样式
- 📦 **可扩展设计** - 易于添加新的自定义属性类型
- 🛡️ **错误处理** - 完善的错误提示和处理
- 🔄 **自动检测** - 基于属性自动添加功能
- 🧪 **演示友好** - 包含完整的示例和说明
- 🏗️ **三层架构** - 协调器 + 功能模块，代码组织清晰
- 🐛 **调试支持** - 内置状态监控和调试工具

## 与RDKit-MolStar集成

如果你已经安装了`rdkit_molstar`扩展，3D显示功能会自动尝试使用真正的MolStar查看器。你可以通过修改`custom3DDisplay.js`中的`tryUseExistingMolStarViewer`函数来自定义集成逻辑。

## 许可证

MIT License - 随意使用和修改

## 贡献

欢迎提交Issue和Pull Request！

---

⭐ **新功能亮点**: 现在你可以通过简单地设置`molstar_3d_display: True`来为任何节点添加3D显示功能！  
🏗️ **架构升级**: 采用三层模块化架构，代码组织更清晰，更易于维护和扩展！  
🛠️ **开发友好**: 详细的开发指南让你轻松添加自己的功能按钮！ 