/**
 * 🔧 ALCHEM_PropBtn 统一JavaScript Logging系统
 * 
 * 解决前端JavaScript极度混乱的logging问题：
 * - 5种不同的console.log实现 → 统一为1种标准格式
 * - 表情符号滥用 → 规范化表情符号使用  
 * - 模块标识混乱 → 统一命名规范
 * 
 * 使用方法：
 *   import { ALCHEMLogger } from './utils/logger.js';
 *   const logger = new ALCHEMLogger('DataProcessor');
 *   logger.debug("调试信息");
 *   logger.success("操作成功");
 *   logger.molecular("分子数据处理中");
 */

/**
 * ALCHEM统一日志级别和表情符号标准
 */
const LOG_LEVELS = {
    DEBUG: { level: 0, emoji: '🔧', name: 'DEBUG' },     // Debug/调试信息
    INFO: { level: 1, emoji: 'ℹ️', name: 'INFO' },       // Info/一般信息
    SUCCESS: { level: 2, emoji: '✅', name: 'SUCCESS' }, // Success/成功操作
    WARNING: { level: 3, emoji: '⚠️', name: 'WARNING' }, // Warning/警告
    ERROR: { level: 4, emoji: '❌', name: 'ERROR' },     // Error/错误
    CRITICAL: { level: 5, emoji: '💥', name: 'CRITICAL' }, // Critical/严重错误
    
    // 专用日志级别
    MOLECULAR: { level: 1, emoji: '🧪', name: 'MOLECULAR' }, // Molecular/分子相关
    NETWORK: { level: 1, emoji: '📡', name: 'NETWORK' },     // Network/网络通信
    STORAGE: { level: 1, emoji: '💾', name: 'STORAGE' },     // Storage/数据存储
    CONNECTION: { level: 1, emoji: '🔗', name: 'CONNECTION' }, // Connection/连接状态
    UI: { level: 1, emoji: '🎨', name: 'UI' },               // UI/界面操作
    WEBSOCKET: { level: 1, emoji: '⚡', name: 'WEBSOCKET' }, // WebSocket/实时通信
};

/**
 * ALCHEM统一Logger类
 */
export class ALCHEMLogger {
    constructor(moduleName, options = {}) {
        this.moduleName = moduleName;
        this.prefix = `[ALCHEM.${moduleName}]`;
        
        // 配置选项
        this.options = {
            level: options.level || 'DEBUG',           // 最小日志级别
            includeTimestamp: options.includeTimestamp || false, // 是否包含时间戳
            includeStackTrace: options.includeStackTrace || false, // 是否包含堆栈跟踪
            colorEnabled: options.colorEnabled !== false,          // 是否启用颜色 (默认启用)
            ...options
        };
        
        // 当前日志级别
        this.currentLevel = LOG_LEVELS[this.options.level]?.level || 0;
        
        // 绑定方法，确保this指向正确
        this.debug = this.debug.bind(this);
        this.info = this.info.bind(this);
        this.success = this.success.bind(this);
        this.warning = this.warning.bind(this);
        this.error = this.error.bind(this);
        this.critical = this.critical.bind(this);
        this.molecular = this.molecular.bind(this);
        this.network = this.network.bind(this);
        this.storage = this.storage.bind(this);
        this.connection = this.connection.bind(this);
        this.ui = this.ui.bind(this);
        this.websocket = this.websocket.bind(this);
    }
    
    /**
     * 内部日志方法
     */
    _log(levelName, message, data = null) {
        const logLevel = LOG_LEVELS[levelName];
        if (!logLevel || logLevel.level < this.currentLevel) {
            return; // 级别不够，跳过
        }
        
        // 构建日志消息
        let formattedMessage = `${this.prefix} ${logLevel.emoji} ${message}`;
        
        // 添加时间戳 (如果启用)
        if (this.options.includeTimestamp) {
            const timestamp = new Date().toLocaleTimeString();
            formattedMessage = `${timestamp} ${formattedMessage}`;
        }
        
        // 选择合适的console方法
        const consoleMethod = this._getConsoleMethod(levelName);
        
        // 输出日志
        if (data !== null) {
            consoleMethod(formattedMessage, data);
        } else {
            consoleMethod(formattedMessage);
        }
        
        // 堆栈跟踪 (如果启用且是错误级别)
        if (this.options.includeStackTrace && logLevel.level >= LOG_LEVELS.ERROR.level) {
            console.trace('Stack trace:');
        }
    }
    
    /**
     * 根据日志级别选择合适的console方法
     */
    _getConsoleMethod(levelName) {
        switch (levelName) {
            case 'DEBUG':
                return console.debug;
            case 'INFO':
            case 'SUCCESS':
            case 'MOLECULAR':
            case 'NETWORK':
            case 'STORAGE':
            case 'CONNECTION':
            case 'UI':
            case 'WEBSOCKET':
                return console.log;
            case 'WARNING':
                return console.warn;
            case 'ERROR':
            case 'CRITICAL':
                return console.error;
            default:
                return console.log;
        }
    }
    
    // 标准日志方法
    debug(message, data = null) {
        this._log('DEBUG', message, data);
    }
    
    info(message, data = null) {
        this._log('INFO', message, data);
    }
    
    success(message, data = null) {
        this._log('SUCCESS', message, data);
    }
    
    warning(message, data = null) {
        this._log('WARNING', message, data);
    }
    
    error(message, data = null) {
        this._log('ERROR', message, data);
    }
    
    critical(message, data = null) {
        this._log('CRITICAL', message, data);
    }
    
    // 专用日志方法
    molecular(message, data = null) {
        this._log('MOLECULAR', message, data);
    }
    
    network(message, data = null) {
        this._log('NETWORK', message, data);
    }
    
    storage(message, data = null) {
        this._log('STORAGE', message, data);
    }
    
    connection(message, data = null) {
        this._log('CONNECTION', message, data);
    }
    
    ui(message, data = null) {
        this._log('UI', message, data);
    }
    
    websocket(message, data = null) {
        this._log('WEBSOCKET', message, data);
    }
    
    /**
     * 设置日志级别
     */
    setLevel(level) {
        if (LOG_LEVELS[level]) {
            this.options.level = level;
            this.currentLevel = LOG_LEVELS[level].level;
            this.info(`日志级别设置为: ${level}`);
        } else {
            this.warning(`无效的日志级别: ${level}`);
        }
    }
    
    /**
     * 获取当前配置
     */
    getConfig() {
        return {
            moduleName: this.moduleName,
            currentLevel: this.options.level,
            options: { ...this.options }
        };
    }
}

/**
 * 预定义的常用Logger (可选，方便直接导入)
 */
export function getExtensionLogger() {
    return new ALCHEMLogger('Extension');
}

export function getUploadLogger() {
    return new ALCHEMLogger('Upload');
}

export function get3DDisplayLogger() {
    return new ALCHEMLogger('3DDisplay');
}

export function getDataProcessorLogger() {
    return new ALCHEMLogger('DataProcessor');
}

export function getAPIClientLogger() {
    return new ALCHEMLogger('APIClient');
}

export function getWebSocketLogger() {
    return new ALCHEMLogger('WebSocketClient');
}

export function getMolstarLogger() {
    return new ALCHEMLogger('Molstar');
}

export function getUILogger() {
    return new ALCHEMLogger('UI');
}

/**
 * 全局Logger管理器
 */
export class ALCHEMLoggerManager {
    constructor() {
        this.loggers = new Map();
        this.globalLevel = 'DEBUG';
    }
    
    /**
     * 获取或创建Logger
     */
    getLogger(moduleName, options = {}) {
        if (!this.loggers.has(moduleName)) {
            const logger = new ALCHEMLogger(moduleName, {
                level: this.globalLevel,
                ...options
            });
            this.loggers.set(moduleName, logger);
        }
        return this.loggers.get(moduleName);
    }
    
    /**
     * 设置全局日志级别
     */
    setGlobalLevel(level) {
        this.globalLevel = level;
        for (const logger of this.loggers.values()) {
            logger.setLevel(level);
        }
    }
    
    /**
     * 获取所有Logger状态
     */
    getAllLoggers() {
        const result = {};
        for (const [name, logger] of this.loggers.entries()) {
            result[name] = logger.getConfig();
        }
        return result;
    }
}

// 创建全局Logger管理器实例
const globalLoggerManager = new ALCHEMLoggerManager();

/**
 * 便捷函数：获取Logger
 */
export function getALCHEMLogger(moduleName, options = {}) {
    return globalLoggerManager.getLogger(moduleName, options);
}

/**
 * 便捷函数：设置全局日志级别
 */
export function setGlobalLogLevel(level) {
    globalLoggerManager.setGlobalLevel(level);
}

/**
 * 便捷函数：获取所有Logger状态 (调试用)
 */
export function getAllLoggerStatus() {
    return globalLoggerManager.getAllLoggers();
}

/**
 * 调试工具：输出Logger使用示例
 */
export function showLoggerDemo() {
    console.log('🧪 ALCHEM统一Logging系统演示');
    
    const demoLogger = getALCHEMLogger('Demo');
    
    demoLogger.debug('这是调试信息');
    demoLogger.info('这是一般信息');
    demoLogger.success('操作成功完成');
    demoLogger.molecular('正在处理分子数据');
    demoLogger.network('网络请求发送中');
    demoLogger.storage('数据已保存到内存');
    demoLogger.connection('WebSocket连接建立');
    demoLogger.ui('UI组件已渲染');
    demoLogger.websocket('收到实时更新消息');
    demoLogger.warning('这是警告信息');
    demoLogger.error('这是错误信息');
    
    console.log('✅ Logger演示完成');
}

// 如果在浏览器环境中，添加到window对象方便调试
if (typeof window !== 'undefined') {
    window.ALCHEMLogger = ALCHEMLogger;
    window.getALCHEMLogger = getALCHEMLogger;
    window.showLoggerDemo = showLoggerDemo;
    window.getAllLoggerStatus = getAllLoggerStatus;
    window.setGlobalLogLevel = setGlobalLogLevel;
}