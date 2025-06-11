项目放在custom_nodes/ALCHEM_PropBtn_New
本项目是一个基于ComfyUI平台的智能分子编辑与可视化系统，专为计算化学、药物发现、材料科学等科研领域设计的创新工具。通过深度集成ComfyUI的节点化工作流架构，我们构建了一个高效、直观、功能强大的分子数据处理平台。
核心功能与特性
🎯 无缝分子文件管理
智能上传系统：支持PDB、SDF、MOL、XYZ等主流分子格式
格式自动识别：智能检测文件格式并提供相应的处理选项
后端内存优化：文件内容直接存储在服务器内存中，实现毫秒级访问
🧬 实时分子结构编辑
2D/3D协同编辑：同步的二维结构编辑器和三维预览窗口
原子级精确操作：支持添加、删除、修改原子和化学键
版本控制机制：完整的编辑历史追踪和回滚功能


## 🧪 **ComfyUI分子编辑系统完整架构设计**

### 1. **整体系统架构（修正版）**

```mermaid
graph TB
    subgraph "前端扩展层"
        A1[extensionMain.js<br/>主协调器] --> A2[Property检测系统]
        A3[Widget注册中心] --> A4[上传Widget]
        A3 --> A5[编辑Widget]
        A3 --> A6[3D显示Widget]
        
        A7[分子编辑界面] --> A8[2D编辑器]
        A7 --> A9[3D预览]
        A7 --> A10[属性面板]
    end
    
    subgraph "通信层"
        B1[REST API] --> B2[upload文件上传接口]
        B1 --> B3[molecular数据查询接口]
        B4[WebSocket] --> B5[实时编辑同步]
    end
    
    subgraph "后端内存管理"
        C1[MolecularMemoryManager] --> C2[molecular_cache字典]
        C3[数据生命周期管理] --> C4[版本控制]
        C5[执行时数据注入] --> C6[get_input_data拦截]
    end
    
    subgraph "ComfyUI执行层"
        D1[节点执行器] --> D2[输入数据获取]
        D2 --> D3[节点FUNCTION调用]
        D3 --> D4[分子数据处理]
    end
    
    A2 --> A3
    A4 --> B1
    A5 --> B4
    B2 --> C1
    B5 --> C1
    C6 --> D2
```

### 2. **单变量多Property机制详解**

```mermaid
graph TB
    subgraph "节点定义示例"
        A1[molecular_file输入字段] --> A2[包含多个Property属性]
        A2 --> A3[molecular_upload: True]
        A2 --> A4[molstar_editable: True]
        A2 --> A5[molstar_3d_display: True]
    end
    
    subgraph "Property检测与Widget生成"
        B1[beforeRegisterNodeDef] --> B2[isMolecularInput检测]
        B2 --> B3{Property类型检查}
        
        B3 -->|molecular_upload| B4[生成上传按钮]
        B3 -->|molstar_editable| B5[生成编辑按钮]
        B3 -->|molstar_3d_display| B6[生成3D显示按钮]
        
        B4 --> B7[MOLECULARUPLOAD Widget]
        B5 --> B8[MOLECULAREDITOR Widget]
        B6 --> B9[MOLSTAR3DDISPLAY Widget]
    end
    
    subgraph "用户交互界面"
        C1[molecular_file下拉框] --> C2[文件选择]
        C3[上传新文件按钮] --> C4[文件选择器]
        C5[编辑结构按钮] --> C6[编辑界面]
        C7[3D显示按钮] --> C8[3D查看器]
    end
    
    A1 --> B1
    B7 --> C3
    B8 --> C5
    B9 --> C7
```

### 3. **数据生命周期和存储策略**

```mermaid
sequenceDiagram
    participant User as 用户
    participant Upload as 上传按钮
    participant Edit as 编辑按钮
    participant Display as 3D显示
    participant API as REST API
    participant WS as WebSocket
    participant Memory as 后端内存
    participant Executor as 节点执行器
    
    Note over User,Executor: 阶段1: 文件上传
    User->>Upload: 点击上传按钮
    Upload->>Upload: 选择分子文件
    Upload->>API: POST upload接口
    API->>Memory: 解析并存储到molecular_cache
    Memory->>API: 返回存储结果
    API->>Upload: 更新按钮状态
    
    Note over User,Executor: 阶段2: 实时编辑
    User->>Edit: 点击编辑按钮
    Edit->>WS: 请求分子数据
    WS->>Memory: 获取当前分子数据
    Memory->>WS: 返回完整分子数据
    WS->>Edit: 显示编辑界面
    
    User->>Edit: 编辑分子结构
    Edit->>WS: 实时同步变更
    WS->>Memory: 更新分子数据
    Memory->>WS: 确认更新版本号
    WS->>Edit: 同步确认
    
    Note over User,Executor: 阶段3: 3D显示
    User->>Display: 点击3D显示
    Display->>Memory: 直接获取分子数据
    Memory->>Display: 返回最新数据
    Display->>Display: 渲染3D结构
    
    Note over User,Executor: 阶段4: 节点执行
    Executor->>Memory: get_input_data调用
    Memory->>Executor: 返回分子内容字符串
    Executor->>Executor: FUNCTION执行
```

### 4. **后端内存管理架构**

```mermaid
graph TB
    subgraph "内存管理器设计"
        A1[MolecularMemoryManager] --> A2[数据存储]
        A2 --> A3[molecular_cache字典]
        
        A4[操作接口] --> A5[store_molecular_data]
        A4 --> A6[get_molecular_data]
        A4 --> A7[update_molecular_data]
        A4 --> A8[delete_molecular_data]
        A4 --> A9[get_cache_status]
    end
    
    subgraph "数据结构"
        B1[节点ID为键] --> B2[分子数据对象]
        B2 --> B3[content: SDF或PDB内容]
        B2 --> B4[filename: 文件名]
        B2 --> B5[format: 格式类型]
        B2 --> B6[metadata: 元数据]
        B2 --> B7[version: 版本号]
        B2 --> B8[timestamps: 时间戳]
    end
    
    subgraph "执行时数据注入"
        C1[get_input_data函数拦截] --> C2{是否为分子输入?}
        C2 -->|是| C3[从molecular_cache获取]
        C2 -->|否| C4[原有ComfyUI逻辑]
        
        C3 --> C5[返回content字符串]
        C4 --> C6[返回文件路径或其他数据]
        
        C5 --> C7[FUNCTION调用]
        C6 --> C7
    end
    
    subgraph "内存优化策略"
        D1[LRU缓存管理] --> D2[自动清理过期数据]
        D3[版本控制] --> D4[支持编辑历史]
        D5[访问计数] --> D6[热点数据统计]
    end
    
    A3 --> B1
    A3 --> C1
    A5 --> D1
    A7 --> D3
    A6 --> D5
```

### 5. **前端扩展注册机制**

```mermaid
graph TB
    subgraph "extensionMain.js架构"
        A1[app.registerExtension] --> A2[扩展配置]
        A2 --> A3[模块初始化]
        A3 --> A4[initMolecularUpload]
        A3 --> A5[initMolecularEditor]
        A3 --> A6[init3DDisplay]
        
        A7[beforeRegisterNodeDef] --> A8[processMolecularNodes]
        A8 --> A9{检测Property}
        A9 -->|molecular_upload| A10[添加上传Widget]
        A9 -->|molstar_editable| A11[添加编辑Widget]
        A9 -->|molstar_3d_display| A12[添加3D Widget]
        
        A13[getCustomWidgets] --> A14[Widget注册表]
        A14 --> A15[MOLECULARUPLOAD]
        A14 --> A16[MOLECULAREDITOR]
        A14 --> A17[MOLSTAR3DDISPLAY]
    end
    
    subgraph "Property检测逻辑"
        B1[isMolecularInput函数] --> B2[检查molecular_upload属性]
        B1 --> B3[检查molstar_editable属性]
        B1 --> B4[检查molstar_3d_display属性]
        B2 --> B5[返回检测结果]
        B3 --> B5
        B4 --> B5
        
        B6[createMolecularWidgets] --> B7[根据Property创建对应Widget]
        B7 --> B8[保持原inputName关联]
    end
    
    A8 --> B1
    B7 --> A10
    B7 --> A11
    B7 --> A12
```

### 6. **WebSocket实时同步机制**

```mermaid
sequenceDiagram
    participant Editor as 编辑界面
    participant WS as WebSocket服务器
    participant Memory as 内存管理器
    participant API as REST API
    
    Note over Editor,API: 建立连接
    Editor->>WS: 连接WebSocket
    WS->>Editor: 连接确认
    
    Note over Editor,API: 获取初始数据
    Editor->>WS: get_molecular消息
    WS->>Memory: get_molecular_data调用
    Memory->>WS: 返回完整分子数据
    WS->>Editor: molecular_data响应
    
    Note over Editor,API: 实时编辑同步
    Editor->>WS: edit_molecular消息
    WS->>Memory: update_molecular_data调用
    Memory->>Memory: 应用变更并版本递增
    Memory->>WS: 返回新版本号
    WS->>Editor: edit_confirmed响应
    
    Note over Editor,API: 保存到持久化
    Editor->>WS: save_molecular消息
    WS->>API: 内部调用持久化接口
    API->>Memory: 标记为已保存状态
    Memory->>API: 确认保存
    API->>WS: 保存完成
    WS->>Editor: save_confirmed响应
    
    Note over Editor,API: 错误处理
    Editor->>WS: 无效操作消息
    WS->>Editor: error响应
```

### 7. **分子编辑界面架构**

```mermaid
graph TB
    subgraph "编辑界面组件结构"
        A1[分子编辑器模态框] --> A2[标题栏]
        A2 --> A3[节点ID和分子名称显示]
        
        A1 --> A4[工具栏区域]
        A4 --> A5[添加原子工具]
        A4 --> A6[连接工具]
        A4 --> A7[编辑工具]
        A4 --> A8[操作工具]
        
        A1 --> A9[主编辑区]
        A9 --> A10[2D分子结构编辑器]
        A9 --> A11[实时3D预览窗口]
        
        A1 --> A12[侧边栏]
        A12 --> A13[分子属性面板]
        A12 --> A14[原子列表]
        A12 --> A15[键列表]
        A12 --> A16[分子统计信息]
        
        A1 --> A17[底部操作栏]
        A17 --> A18[保存到后端内存]
        A17 --> A19[取消编辑]
        A17 --> A20[重置为原始状态]
        A17 --> A21[导出为文件]
    end
    
    subgraph "实时同步机制"
        B1[编辑操作事件] --> B2[防抖处理300ms]
        B2 --> B3[构建变更对象]
        B3 --> B4[WebSocket发送]
        B4 --> B5[后端确认]
        B5 --> B6[更新界面状态]
        B6 --> B7[显示版本号]
    end
    
    subgraph "数据状态管理"
        C1[编辑器状态] --> C2[当前分子数据]
        C1 --> C3[编辑历史栈]
        C1 --> C4[是否有未保存更改]
        C1 --> C5[WebSocket连接状态]
        C1 --> C6[当前版本号]
    end
    
    A10 --> B1
    A5 --> B1
    A6 --> B1
    A7 --> B1
    B6 --> C1
    C2 --> A13
    C3 --> A8
```

### 8. **关键代码实现架构**

```mermaid
graph TB
    subgraph "Property检测机制"
        A1[isMolecularInput函数] --> A2[检查molecular_upload]
        A1 --> A3[检查molstar_editable]
        A1 --> A4[检查molstar_3d_display]
        
        A2 --> A5[返回检测结果]
        A3 --> A5
        A4 --> A5
    end
    
    subgraph "Widget创建流程"
        B1[processMolecularNodes] --> B2[遍历所有输入]
        B2 --> B3[调用isMolecularInput]
        B3 --> B4{有分子Property?}
        
        B4 -->|molecular_upload| B5[创建MOLECULARUPLOAD]
        B4 -->|molstar_editable| B6[创建MOLECULAREDITOR]
        B4 -->|molstar_3d_display| B7[创建MOLSTAR3DDISPLAY]
        
        B5 --> B8[返回Widget增强定义]
        B6 --> B8
        B7 --> B8
    end
    
    subgraph "后端内存接口"
        C1[MolecularMemoryManager类] --> C2[store_molecular_data方法]
        C1 --> C3[get_molecular_data方法]
        C1 --> C4[update_molecular_data方法]
        
        C2 --> C5[解析分子内容]
        C2 --> C6[存储到molecular_cache]
        
        C3 --> C7[增加访问计数]
        C3 --> C8[返回分子数据]
        
        C4 --> C9[更新内容]
        C4 --> C10[版本号递增]
    end
    
    subgraph "执行时拦截机制"
        D1[get_input_data函数] --> D2[检查节点和输入类型]
        D2 --> D3{是否为分子输入?}
        
        D3 -->|是| D4[调用molecular_manager]
        D3 -->|否| D5[原有ComfyUI逻辑]
        
        D4 --> D6[获取molecular_data]
        D6 --> D7[返回content字符串]
        
        D5 --> D8[返回原始数据]
        
        D7 --> D9[传递给节点FUNCTION]
        D8 --> D9
    end
    
    A5 --> B3
    B8 --> C1
    C6 --> D4
    C8 --> D6
```

### 9. **WebSocket通信协议架构**

```mermaid
graph TB
    subgraph "WebSocket消息类型"
        A1[客户端消息] --> A2[get_molecular]
        A1 --> A3[edit_molecular]
        A1 --> A4[save_molecular]
        A1 --> A5[ping]
        
        A6[服务器消息] --> A7[molecular_data]
        A6 --> A8[edit_confirmed]
        A6 --> A9[save_confirmed]
        A6 --> A10[error]
        A6 --> A11[pong]
    end
    
    subgraph "消息处理流程"
        B1[WebSocket接收消息] --> B2[解析JSON格式]
        B2 --> B3{消息类型判断}
        
        B3 -->|get_molecular| B4[查询分子数据]
        B3 -->|edit_molecular| B5[更新分子数据]
        B3 -->|save_molecular| B6[持久化数据]
        
        B4 --> B7[构建响应消息]
        B5 --> B7
        B6 --> B7
        
        B7 --> B8[发送JSON响应]
    end
    
    subgraph "错误处理机制"
        C1[消息验证] --> C2[JSON格式检查]
        C1 --> C3[必需字段检查]
        C1 --> C4[数据类型验证]
        
        C5[业务逻辑错误] --> C6[节点不存在]
        C5 --> C7[数据格式错误]
        C5 --> C8[权限检查失败]
        
        C2 --> C9[返回格式错误]
        C3 --> C9
        C4 --> C9
        C6 --> C10[返回业务错误]
        C7 --> C10
        C8 --> C10
    end
    
    subgraph "连接管理"
        D1[连接建立] --> D2[身份验证]
        D2 --> D3[注册客户端]
        
        D4[连接维护] --> D5[心跳检测]
        D4 --> D6[断线重连]
        
        D7[连接关闭] --> D8[清理资源]
        D7 --> D9[保存未完成编辑]
    end
    
    B2 --> C1
    C9 --> B8
    C10 --> B8
    D3 --> B1
    D6 --> B1
```

### 10. **数据流状态转换图**

```mermaid
stateDiagram-v2
    [*] --> 未上传: 节点创建
    未上传 --> 上传中: 用户点击上传按钮
    上传中 --> 已上传: 文件解析成功
    上传中 --> 上传失败: 文件解析失败
    上传失败 --> 上传中: 重新上传
    
    已上传 --> 编辑中: 用户点击编辑按钮
    编辑中 --> 已修改: 用户编辑分子结构
    已修改 --> 保存中: 用户点击保存
    保存中 --> 已保存: 保存成功
    保存中 --> 保存失败: 保存失败
    保存失败 --> 已修改: 重新保存
    
    已上传 --> 显示中: 用户点击3D显示
    已修改 --> 显示中: 用户点击3D显示
    已保存 --> 显示中: 用户点击3D显示
    显示中 --> 已上传: 关闭3D显示无修改
    显示中 --> 已修改: 关闭3D显示有修改
    显示中 --> 已保存: 关闭3D显示已保存
    
    已上传 --> 执行中: 工作流执行
    已修改 --> 执行中: 工作流执行
    已保存 --> 执行中: 工作流执行
    执行中 --> 执行完成: 节点处理完成
    
    note right of 执行中
        此时从后端内存获取
        分子内容传递给FUNCTION
    end note
```

### 11. **性能优化和错误处理**

```mermaid
graph TB
    subgraph "性能优化策略"
        A1[内存管理] --> A2[LRU缓存自动清理]
        A1 --> A3[大文件分块传输]
        A1 --> A4[压缩存储优化]
        
        A5[网络优化] --> A6[WebSocket连接池]
        A5 --> A7[防抖批量同步]
        A5 --> A8[断线重连机制]
        
        A9[界面优化] --> A10[虚拟滚动大分子]
        A9 --> A11[Canvas渲染缓存]
        A9 --> A12[分片加载3D模型]
    end
    
    subgraph "错误处理机制"
        B1[前端错误] --> B2[网络异常重试]
        B1 --> B3[数据格式验证]
        B1 --> B4[用户友好提示]
        
        B5[后端错误] --> B6[内存不足降级]
        B5 --> B7[文件解析失败回退]
        B5 --> B8[数据一致性检查]
        
        B9[同步错误] --> B10[版本冲突解决]
        B9 --> B11[数据丢失恢复]
        B9 --> B12[状态同步修复]
    end
    
    subgraph "监控和日志"
        C1[性能监控] --> C2[内存使用统计]
        C1 --> C3[API响应时间]
        C1 --> C4[WebSocket连接数]
        
        C5[操作日志] --> C6[分子编辑记录]
        C5 --> C7[错误日志收集]
        C5 --> C8[用户行为分析]
    end
```

### 12. **系统集成与扩展性**

```mermaid
graph TB
    subgraph "与ComfyUI核心集成"
        A1[无侵入式设计] --> A2[扩展机制兼容]
        A2 --> A3[原有节点不受影响]
        A3 --> A4[渐进式功能增强]
        
        A5[API兼容性] --> A6[RESTful接口设计]
        A5 --> A7[标准HTTP状态码]
        A5 --> A8[JSON数据格式]
    end
    
    subgraph "扩展性设计"
        B1[模块化架构] --> B2[新分子格式支持]
        B2 --> B3[新编辑功能插件]
        B3 --> B4[自定义Property支持]
        
        B5[开放接口] --> B6[第三方编辑器集成]
        B5 --> B7[外部工具链接]
        B5 --> B8[数据导入导出]
    end
    
    subgraph "未来发展方向"
        C1[AI集成] --> C2[分子生成建议]
        C2 --> C3[结构优化推荐]
        C3 --> C4[自动错误修正]
        
        C5[协作功能] --> C6[版本分支管理]
        C5 --> C7[评论和标注]
    end
```

这个完整的架构设计涵盖了：

**核心优势**：
1. **🎯 单变量多Property**：简洁一致的用户体验
2. **🚀 后端内存优先**：毫秒级数据访问，无I/O瓶颈
3. **🔄 实时同步机制**：WebSocket保证前后端数据一致性
4. **🧩 模块化设计**：易于维护和扩展
5. **💪 高性能优化**：多层缓存和优化策略
6. **🛡️ 错误处理完善**：容错性强，用户体验好
7. **🔗 ComfyUI原生集成**：无侵入式设计，完美兼容
