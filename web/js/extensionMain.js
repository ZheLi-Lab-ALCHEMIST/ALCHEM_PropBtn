import { app } from "../../../scripts/app.js";

// 导入分子文件上传模块
import {
    initMolecularUpload,
    createMolecularUploadWidget,
    processMolecularUploadNodes
} from "./uploadMolecules.js";

// 导入3D显示模块
import { 
    init3DDisplay, 
    createMolstar3DDisplayWidget, 
    process3DDisplayNodes,
    handle3DDisplayNodeCreated
} from "./custom3DDisplay.js";

/**
 * ComfyUI Custom Extension 主协调器
 * 
 * 职责：
 * 1. 协调各个功能模块
 * 2. 处理ComfyUI扩展注册
 * 3. 管理节点生命周期
 * 4. 统一日志和错误处理
 */

// 扩展配置 - 定义扩展的基本信息和模块管理
const EXTENSION_CONFIG = {
    // 扩展标识和基本信息
    name: "ComfyUI.CustomWidgets",           // ComfyUI官方扩展注册名称
    displayName: "Custom Widgets Extension", // 用户友好的显示名称  
    version: "1.0.0",
    description: "A modular extension that adds custom widgets like upload buttons and 3D displays to ComfyUI nodes",
    author: "Custom Extension Team",
    
    // 功能模块注册表 - 每个模块有独立的标识和显示名称
    modules: {
        molecularUpload: {
            name: "🧪 Molecular Upload",
            description: "Specialized molecular file upload with format validation",
            version: "1.0.0"
        },
        display3D: {
            name: "🧪 3D Display", 
            description: "3D molecular structure display integration",
            version: "1.0.0"
        }
        // 未来可以轻松添加新模块：
        // dataViz: {
        //     name: "📊 Data Visualization",
        //     description: "Chart and graph display widgets",
        //     version: "1.0.0"
        // }
    },
    
    // 扩展设置
    settings: {
        debugMode: false,             // 调试模式 - 默认关闭
        logLevel: 'warn',            // 日志级别: 'debug', 'info', 'warn', 'error' 
                                     // debug: 显示所有日志（包括QUIET注释）
                                     // info: 显示信息级别以上  
                                     // warn: 只显示警告和错误（默认）
                                     // error: 只显示错误
        autoRefresh: true,           // 自动刷新ComfyUI组件
        enableMetrics: false,        // 启用性能监控 - 默认关闭
        verboseLogging: false        // 详细日志 - 默认关闭
    }
};

// 统一日志处理系统
const logger = {
    debug: (message, module = 'MAIN') => {
        if (EXTENSION_CONFIG.settings.logLevel === 'debug') {
            console.debug(`[${EXTENSION_CONFIG.modules[module]?.name || module}] 🐛 ${message}`);
        }
    },
    info: (message, module = 'MAIN') => {
        if (['debug', 'info'].includes(EXTENSION_CONFIG.settings.logLevel)) {
            console.log(`[${EXTENSION_CONFIG.modules[module]?.name || module}] ℹ️ ${message}`);
        }
    },
    warn: (message, module = 'MAIN') => {
        if (['debug', 'info', 'warn'].includes(EXTENSION_CONFIG.settings.logLevel)) {
            console.warn(`[${EXTENSION_CONFIG.modules[module]?.name || module}] ⚠️ ${message}`);
        }
    },
    error: (message, module = 'MAIN') => {
        console.error(`[${EXTENSION_CONFIG.modules[module]?.name || module}] ❌ ${message}`);
    },
    
    // 简单日志函数 - 供其他文件使用，在debug模式下显示QUIET注释
    quiet: (message) => {
        if (EXTENSION_CONFIG.settings.logLevel === 'debug') {
            console.log(`🗿 ${message}`);
        }
    }
};

// 初始化所有模块
const initializeModules = () => {
    try {
        logger.info(`Initializing ${EXTENSION_CONFIG.displayName} v${EXTENSION_CONFIG.version}`);
        
        // 初始化分子文件上传模块
        initMolecularUpload();
        logger.info("Molecular upload module initialized", 'molecularUpload');
        
        // 初始化3D显示模块
        init3DDisplay();
        logger.info("3D display module initialized", 'display3D');
        
        logger.info(`Extension ${EXTENSION_CONFIG.displayName} initialized successfully`);
    } catch (error) {
        logger.error(`Failed to initialize modules: ${error.message}`);
        throw error;
    }
};

// 注册所有自定义Widgets
const getCustomWidgets = () => {
    try {
        // 延迟调用，确保模块已完全初始化
        const widgets = {};
        
        // 安全地获取widget创建函数
        if (typeof createMolecularUploadWidget === 'function') {
            widgets.MOLECULARUPLOAD = createMolecularUploadWidget();
        }
        
        if (typeof createMolstar3DDisplayWidget === 'function') {
            widgets.MOLSTAR3DDISPLAY = createMolstar3DDisplayWidget();
        }
        
        logger.info(`Registered ${Object.keys(widgets).length} custom widgets: ${Object.keys(widgets).join(', ')}`);
        return widgets;
    } catch (error) {
        logger.error(`Failed to register custom widgets: ${error.message}`);
        return {};
    }
};

// 处理节点定义注册前的逻辑
const beforeRegisterNodeDef = (nodeType, nodeData) => {
    try {
        const { input } = nodeData ?? {};
        const { required } = input ?? {};
        if (!required) return;

        let processed = false;

        // 处理分子文件上传节点
        const molecularUploadResult = processMolecularUploadNodes(nodeType, nodeData);
        if (molecularUploadResult) {
            required.molecular_upload = molecularUploadResult.molecular_upload;
            logger.debug(`Processed molecular upload node: ${nodeData.name}`, 'molecularUpload');
            processed = true;
        }
        
        // 处理3D显示节点
        const display3DResult = process3DDisplayNodes(nodeType, nodeData);
        if (display3DResult) {
            required.molstar_3d = display3DResult.molstar_3d;
            logger.debug(`Processed 3D display node: ${nodeData.name}`, 'display3D');
            processed = true;
        }

        if (processed) {
            logger.info(`Enhanced node definition: ${nodeData.name}`);
        }
    } catch (error) {
        logger.error(`Error processing node definition ${nodeData?.name}: ${error.message}`);
    }
};

// 处理节点创建后的逻辑
const nodeCreated = (node) => {
    try {
        // 处理3D显示节点
        handle3DDisplayNodeCreated(node);
        
        // 记录节点创建
        if (node.type && (
            node.type.includes('CustomUpload') || 
            node.type.includes('Demo3DDisplay')
        )) {
            logger.debug(`Enhanced node created: ${node.type} (ID: ${node.id})`);
        }
    } catch (error) {
        logger.error(`Error handling node creation for ${node.type}: ${error.message}`);
    }
};

// 扩展状态监控 - 用于调试和性能分析
const extensionStatus = {
    initialized: false,
    modulesLoaded: [],
    nodesProcessed: 0,
    widgetsRegistered: 0,
    startTime: Date.now(),
    lastActivity: Date.now()
};

// 更新扩展状态
const updateStatus = (action, details) => {
    extensionStatus.lastActivity = Date.now();
    
    switch (action) {
        case 'init':
            extensionStatus.initialized = true;
            extensionStatus.modulesLoaded = details.modules || [];
            break;
        case 'widget_registered':
            extensionStatus.widgetsRegistered++;
            break;
        case 'node_processed':
            extensionStatus.nodesProcessed++;
            break;
    }
    
    if (EXTENSION_CONFIG.settings.enableMetrics) {
        logger.debug(`Status updated: ${action}`, 'MAIN');
    }
};

// 获取扩展详细状态（用于调试和监控）
const getExtensionStatus = () => {
    const runtime = Date.now() - extensionStatus.startTime;
    return {
        ...extensionStatus,
        config: {
            name: EXTENSION_CONFIG.name,
            displayName: EXTENSION_CONFIG.displayName,
            version: EXTENSION_CONFIG.version,
            modules: Object.keys(EXTENSION_CONFIG.modules)
        },
        runtime: {
            uptime: runtime,
            uptimeFormatted: `${Math.floor(runtime / 1000)}秒`
        },
        timestamp: new Date().toISOString()
    };
};

// 全局调试接口
window.getCustomWidgetStatus = () => {
    const status = getExtensionStatus();
    status.multitab_fix_enabled = true;  // 🔧 标记多tab修复已启用
    return status;
};

// 🆕 多tab调试工具
window.debugMultiTabMemory = () => {
    console.log("🔧 多Tab内存调试工具");
    console.log("====================");
    
    // 显示当前所有节点的ID生成
    if (window.app && window.app.graph && window.app.graph.nodes) {
        console.log(`当前图中有 ${window.app.graph.nodes.length} 个节点:`);
        window.app.graph.nodes.forEach(node => {
            if (node.widgets && node.widgets.some(w => w.name && w.name.includes('molecular'))) {
                console.log(`  节点 ${node.id} (${node.type}): 包含分子上传功能`);
            }
        });
    }
    
    // 检查后端内存状态
    fetch('/alchem_propbtn/api/status')
        .then(r => r.json())
        .then(data => {
            if (data.success && data.data.cache) {
                const cache = data.data.cache;
                console.log(`\n后端内存状态:`);
                console.log(`  总节点数: ${cache.total_nodes || 0}`);
                console.log(`  缓存大小: ${(cache.total_cache_size || 0)} 字符`);
                if (cache.nodes && cache.nodes.length > 0) {
                    console.log(`  节点列表:`);
                    cache.nodes.forEach(node => {
                        console.log(`    - ${node.node_id}: ${node.filename} (${node.atoms} 原子)`);
                    });
                }
            }
        })
        .catch(e => console.error('获取后端状态失败:', e));
    
    console.log("\n使用方法:");
    console.log("1. 在tab_A中上传分子文件");
    console.log("2. 切换到tab_B，上传另一个分子文件");
    console.log("3. 切换回tab_A，点击3D显示按钮");
    console.log("4. 检查是否能正常显示tab_A的分子");
};

// 🧪 内存和节点ID调试工具
window.debugNodeIds = () => {
    console.log("🧪 节点ID和内存调试工具");
    console.log("========================");
    
    if (window.app && window.app.graph && window.app.graph.nodes) {
        console.log(`当前图中有 ${window.app.graph.nodes.length} 个节点:`);
        window.app.graph.nodes.forEach(node => {
            console.log(`  节点 ${node.id} (${node.type}):`);
            console.log(`    - node._id: ${node._id || '未设置'}`);
            console.log(`    - node._uniqueDisplayId: ${node._uniqueDisplayId || '未设置'}`);
            
            if (node.widgets && node.widgets.some(w => w.name && w.name.includes('molecular'))) {
                console.log(`    - 包含分子功能: ✅`);
            }
        });
    }
    
    // 检查后端内存状态
    fetch('/alchem_propbtn/api/status')
        .then(r => r.json())
        .then(data => {
            if (data.success && data.data.cache) {
                const cache = data.data.cache;
                console.log(`\n后端内存状态:`);
                console.log(`  总节点数: ${cache.total_nodes || 0}`);
                if (cache.nodes && cache.nodes.length > 0) {
                    console.log(`  内存中的节点ID列表:`);
                    cache.nodes.forEach(node => {
                        console.log(`    - ${node.node_id}: ${node.filename} (${node.atoms} 原子)`);
                    });
                }
            }
        })
        .catch(e => console.error('获取后端状态失败:', e));
};

// 🚀 WebSocket调试工具
window.debugWebSocket = () => {
    console.log("🚀 WebSocket实时同步调试工具");
    console.log("============================");
    
    // 检查WebSocket客户端状态
    if (window.webSocketClient) {
        const status = window.webSocketClient.getStatus();
        console.log("WebSocket客户端状态:");
        console.log(`  连接状态: ${status.isConnected ? '✅ 已连接' : '❌ 未连接'}`);
        console.log(`  订阅节点: ${status.subscribedNodes.length} 个`);
        console.log(`  重连尝试: ${status.reconnectAttempts} 次`);
        
        if (status.subscribedNodes.length > 0) {
            console.log("  订阅列表:");
            status.subscribedNodes.forEach(nodeId => {
                console.log(`    - ${nodeId}`);
            });
        }
    } else {
        console.warn("⚠️ WebSocket客户端未找到");
    }
    
    // 检查后端WebSocket状态
    fetch('/alchem_propbtn/api/status')
        .then(r => r.json())
        .then(data => {
            if (data.success && data.data.websocket) {
                const ws = data.data.websocket;
                console.log("\n后端WebSocket状态:");
                console.log(`  服务可用: ${data.data.websocket_available ? '✅ 是' : '❌ 否'}`);
                console.log(`  当前连接: ${ws.total_connections || 0} 个`);
                if (ws.clients && ws.clients.length > 0) {
                    console.log("  客户端列表:");
                    ws.clients.forEach((client, i) => {
                        console.log(`    ${i+1}. 连接时长: ${Math.floor(client.uptime || 0)}秒`);
                    });
                }
            }
        })
        .catch(e => console.error('获取WebSocket状态失败:', e));
    
    console.log("\n测试实时同步:");
    console.log("1. 上传一个PDB分子文件");
    console.log("2. 点击'🧪 显示3D结构'按钮");
    console.log("3. 点击'🔧 删除最后原子'按钮");
    console.log("4. 观察Molstar显示是否自动更新");
    console.log("\n调试命令:");
    console.log("debugNodeIds() - 查看节点ID和内存状态");
    console.log("webSocketClient.connect() - 手动连接WebSocket");
    console.log("testNodeIdConsistency() - 测试节点ID一致性");
};

// 🧪 测试节点ID一致性
window.testNodeIdConsistency = () => {
    console.log("🧪 测试节点ID生成一致性");
    console.log("========================");
    
    if (window.app && window.app.graph && window.app.graph.nodes) {
        const molecularNodes = window.app.graph.nodes.filter(node => 
            node.widgets && node.widgets.some(w => w.name && w.name.includes('molecular'))
        );
        
        if (molecularNodes.length === 0) {
            console.warn("⚠️ 没有找到包含分子功能的节点");
            return;
        }
        
        molecularNodes.forEach(node => {
            console.log(`\n节点 ${node.id} (${node.type}):`);
            
            // 模拟上传模块的ID生成
            try {
                // 这里需要手动复制上传模块的逻辑
                let uploadId = "模拟上传ID";
                console.log(`  上传模块ID: ${uploadId}`);
            } catch (e) {
                console.warn(`  上传模块ID生成失败: ${e.message}`);
            }
            
            // 模拟显示模块的ID生成
            try {
                // 这里需要手动复制显示模块的逻辑
                let displayId = "模拟显示ID";
                console.log(`  显示模块ID: ${displayId}`);
            } catch (e) {
                console.warn(`  显示模块ID生成失败: ${e.message}`);
            }
        });
    }
};

// 导出WebSocket客户端到全局作用域（用于调试）
if (typeof window !== 'undefined') {
    // 这里会在模块加载后通过动态导入设置
    import('./modules/websocket-client.js').then(module => {
        window.webSocketClient = module.webSocketClient;
    }).catch(e => console.warn('WebSocket客户端导入失败:', e));
}

// 全局QUIET日志函数 - 供所有模块使用
window.QUIET_LOG = (message) => {
    if (EXTENSION_CONFIG.settings.logLevel === 'debug') {
        console.log(`🗿 ${message}`);
    }
};

// 主扩展注册
app.registerExtension({
    name: EXTENSION_CONFIG.name,  // ComfyUI用这个名称注册扩展
    
    init() {
        try {
            initializeModules();
            updateStatus('init', { modules: Object.keys(EXTENSION_CONFIG.modules) });
            
            // 添加全局调试帮助
            if (typeof window !== 'undefined') {
                window.customWidgetsExtension = {
                    name: EXTENSION_CONFIG.displayName,
                    version: EXTENSION_CONFIG.version,
                    config: EXTENSION_CONFIG,
                    status: getExtensionStatus,
                    logger,
                    // 实用工具函数
                    utils: {
                        setLogLevel: (level) => {
                            EXTENSION_CONFIG.settings.logLevel = level;
                            logger.info(`Log level set to: ${level}`);
                            console.log("📝 日志级别说明:");
                            console.log("  debug: 显示所有日志（包括QUIET注释）");
                            console.log("  info: 显示信息级别以上");
                            console.log("  warn: 只显示警告和错误（默认）");
                            console.log("  error: 只显示错误");
                        },
                        toggleDebug: () => {
                            EXTENSION_CONFIG.settings.debugMode = !EXTENSION_CONFIG.settings.debugMode;
                            logger.info(`Debug mode: ${EXTENSION_CONFIG.settings.debugMode ? 'ON' : 'OFF'}`);
                        }
                    }
                };
            }
            
        } catch (error) {
            logger.error(`Extension initialization failed: ${error.message}`);
        }
    },
    
    async getCustomWidgets() {
        try {
            // 确保所有模块都已初始化
            await new Promise(resolve => setTimeout(resolve, 0));
            
            const widgets = getCustomWidgets();
            updateStatus('widget_registered', { count: Object.keys(widgets).length });
            return widgets;
        } catch (error) {
            logger.error(`Widget registration failed: ${error.message}`);
            return {};
        }
    },
    
    beforeRegisterNodeDef(nodeType, nodeData) {
        try {
            beforeRegisterNodeDef(nodeType, nodeData);
            updateStatus('node_processed');
        } catch (error) {
            logger.error(`Node definition processing failed: ${error.message}`);
        }
    },
    
    nodeCreated(node) {
        try {
            nodeCreated(node);
        } catch (error) {
            logger.error(`Node creation handling failed: ${error.message}`);
        }
    }
});

// 扩展加载完成日志
logger.info(`Extension ${EXTENSION_CONFIG.displayName} loaded successfully`);

// 导出配置和工具供其他模块使用
export { EXTENSION_CONFIG, logger }; 