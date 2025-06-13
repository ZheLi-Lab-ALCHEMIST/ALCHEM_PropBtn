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
        debugMode: true,              // 调试模式
        logLevel: 'info',            // 日志级别: 'debug', 'info', 'warn', 'error'
        autoRefresh: true,           // 自动刷新ComfyUI组件
        enableMetrics: true          // 启用性能监控
    }
};

// 统一日志处理系统
const logger = {
    debug: (message, module = 'MAIN') => {
        if (EXTENSION_CONFIG.settings.debugMode && EXTENSION_CONFIG.settings.logLevel === 'debug') {
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
        const widgets = {
            MOLECULARUPLOAD: createMolecularUploadWidget(),
            MOLSTAR3DDISPLAY: createMolstar3DDisplayWidget()
        };
        
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
window.getCustomWidgetStatus = getExtensionStatus;

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