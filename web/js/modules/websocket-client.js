/**
 * 🚀 ALCHEM WebSocket客户端
 * 
 * 专注于核心功能：
 * 1. 连接管理（自动重连、心跳）
 * 2. 分子数据变更监听
 * 3. Molstar显示自动同步
 * 
 * 不包含多用户协作，专注于单用户实时同步
 */

// 简单的日志函数
const logger = {
    info: (message) => console.log(`[WebSocket] ℹ️ ${message}`),
    warn: (message) => console.warn(`[WebSocket] ⚠️ ${message}`),
    error: (message) => console.error(`[WebSocket] ❌ ${message}`),
    debug: (message) => {
        if (window.ALCHEM_DEBUG) {
            console.log(`[WebSocket] 🔧 ${message}`);
        }
    }
};

/**
 * WebSocket客户端类
 */
class ALCHEMWebSocketClient {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectDelay = 1000; // 1秒
        this.heartbeatInterval = null;
        this.heartbeatTimeout = null;
        
        // 订阅的节点
        this.subscribedNodes = new Set();
        
        // 事件监听器
        this.eventListeners = {
            'connected': [],
            'disconnected': [],
            'molecular_data_changed': [],
            'error': []
        };
        
        // 连接状态
        this.connectionStatus = {
            connected: false,
            lastConnected: null,
            lastDisconnected: null,
            reconnectAttempts: 0
        };
    }
    
    /**
     * 连接到WebSocket服务器
     */
    async connect() {
        if (this.isConnected) {
            logger.warn("已经连接到WebSocket服务器");
            return;
        }
        
        try {
            // 构建WebSocket URL
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const host = window.location.host;
            const wsUrl = `${protocol}//${host}/alchem_propbtn/ws`;
            
            logger.info(`正在连接到WebSocket服务器: ${wsUrl}`);
            
            this.ws = new WebSocket(wsUrl);
            
            // 设置事件处理器
            this.ws.onopen = this.onOpen.bind(this);
            this.ws.onmessage = this.onMessage.bind(this);
            this.ws.onclose = this.onClose.bind(this);
            this.ws.onerror = this.onError.bind(this);
            
        } catch (error) {
            logger.error(`连接WebSocket失败: ${error.message}`);
            this.handleReconnect();
        }
    }
    
    /**
     * 断开连接
     */
    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
        this.clearHeartbeat();
        this.isConnected = false;
        this.connectionStatus.connected = false;
        this.connectionStatus.lastDisconnected = new Date().toISOString();
        
        logger.info("已断开WebSocket连接");
    }
    
    /**
     * WebSocket连接打开事件
     */
    onOpen() {
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.connectionStatus.connected = true;
        this.connectionStatus.lastConnected = new Date().toISOString();
        this.connectionStatus.reconnectAttempts = 0;
        
        logger.info("🎉 WebSocket连接建立成功");
        
        // 开始心跳
        this.startHeartbeat();
        
        // 重新订阅之前的节点
        this.resubscribeNodes();
        
        // 触发连接事件
        this.emit('connected');
    }
    
    /**
     * 处理WebSocket消息
     */
    onMessage(event) {
        try {
            const message = JSON.parse(event.data);
            logger.debug(`收到消息: ${message.type}`);
            
            this.handleMessage(message);
            
        } catch (error) {
            logger.error(`解析WebSocket消息失败: ${error.message}`);
        }
    }
    
    /**
     * WebSocket连接关闭事件
     */
    onClose(event) {
        this.isConnected = false;
        this.connectionStatus.connected = false;
        this.connectionStatus.lastDisconnected = new Date().toISOString();
        
        this.clearHeartbeat();
        
        logger.warn(`WebSocket连接关闭: ${event.code} - ${event.reason}`);
        
        // 触发断开事件
        this.emit('disconnected', { code: event.code, reason: event.reason });
        
        // 尝试重连
        if (event.code !== 1000) { // 不是正常关闭
            this.handleReconnect();
        }
    }
    
    /**
     * WebSocket错误事件
     */
    onError(error) {
        logger.error(`WebSocket错误: ${error}`);
        this.emit('error', error);
    }
    
    /**
     * 处理消息
     */
    handleMessage(message) {
        switch (message.type) {
            case 'welcome':
                logger.info(`服务器欢迎消息: ${message.message}`);
                break;
                
            case 'pong':
                // 心跳响应
                this.clearHeartbeatTimeout();
                break;
                
            case 'molecular_data_changed':
                logger.info(`分子数据变更: 节点 ${message.node_id}, 类型 ${message.change_type}`);
                this.emit('molecular_data_changed', message);
                break;
                
            case 'subscribed':
                logger.info(`订阅成功: ${message.message}`);
                break;
                
            case 'unsubscribed':
                logger.info(`取消订阅: ${message.message}`);
                break;
                
            case 'error':
                logger.error(`服务器错误: ${message.message}`);
                this.emit('error', message);
                break;
                
            default:
                logger.warn(`未知消息类型: ${message.type}`);
        }
    }
    
    /**
     * 发送消息到服务器
     */
    send(message) {
        if (!this.isConnected || !this.ws) {
            logger.warn("WebSocket未连接，无法发送消息");
            return false;
        }
        
        try {
            this.ws.send(JSON.stringify(message));
            logger.debug(`发送消息: ${message.type}`);
            return true;
        } catch (error) {
            logger.error(`发送消息失败: ${error.message}`);
            return false;
        }
    }
    
    /**
     * 订阅节点数据变更
     */
    subscribeNode(nodeId) {
        if (!nodeId) {
            logger.warn("节点ID为空，无法订阅");
            return false;
        }
        
        this.subscribedNodes.add(nodeId);
        
        if (this.isConnected) {
            return this.send({
                type: 'subscribe_node',
                node_id: nodeId
            });
        } else {
            logger.info(`WebSocket未连接，节点 ${nodeId} 将在连接后自动订阅`);
            return true;
        }
    }
    
    /**
     * 取消订阅节点
     */
    unsubscribeNode(nodeId) {
        this.subscribedNodes.delete(nodeId);
        
        if (this.isConnected) {
            return this.send({
                type: 'unsubscribe_node',
                node_id: nodeId
            });
        }
        return true;
    }
    
    /**
     * 重新订阅所有节点
     */
    resubscribeNodes() {
        for (const nodeId of this.subscribedNodes) {
            this.send({
                type: 'subscribe_node',
                node_id: nodeId
            });
        }
    }
    
    /**
     * 开始心跳
     */
    startHeartbeat() {
        this.clearHeartbeat();
        
        this.heartbeatInterval = setInterval(() => {
            if (this.isConnected) {
                this.send({ type: 'ping' });
                
                // 设置心跳超时
                this.heartbeatTimeout = setTimeout(() => {
                    logger.warn("心跳超时，准备重连");
                    this.ws.close();
                }, 10000); // 10秒超时
            }
        }, 30000); // 30秒心跳间隔
    }
    
    /**
     * 清除心跳
     */
    clearHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
        this.clearHeartbeatTimeout();
    }
    
    /**
     * 清除心跳超时
     */
    clearHeartbeatTimeout() {
        if (this.heartbeatTimeout) {
            clearTimeout(this.heartbeatTimeout);
            this.heartbeatTimeout = null;
        }
    }
    
    /**
     * 处理重连
     */
    handleReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            logger.error(`重连失败，已达到最大尝试次数 ${this.maxReconnectAttempts}`);
            return;
        }
        
        this.reconnectAttempts++;
        this.connectionStatus.reconnectAttempts = this.reconnectAttempts;
        
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
        logger.info(`${delay/1000}秒后尝试第 ${this.reconnectAttempts} 次重连...`);
        
        setTimeout(() => {
            this.connect();
        }, delay);
    }
    
    /**
     * 添加事件监听器
     */
    on(event, callback) {
        if (this.eventListeners[event]) {
            this.eventListeners[event].push(callback);
        }
    }
    
    /**
     * 移除事件监听器
     */
    off(event, callback) {
        if (this.eventListeners[event]) {
            const index = this.eventListeners[event].indexOf(callback);
            if (index > -1) {
                this.eventListeners[event].splice(index, 1);
            }
        }
    }
    
    /**
     * 触发事件
     */
    emit(event, data = null) {
        if (this.eventListeners[event]) {
            this.eventListeners[event].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    logger.error(`事件回调执行失败: ${error.message}`);
                }
            });
        }
    }
    
    /**
     * 获取连接状态
     */
    getStatus() {
        return {
            ...this.connectionStatus,
            subscribedNodes: Array.from(this.subscribedNodes),
            isConnected: this.isConnected,
            reconnectAttempts: this.reconnectAttempts
        };
    }
}

// 创建全局WebSocket客户端实例
const webSocketClient = new ALCHEMWebSocketClient();

// 🔥 自动连接（可选）
// webSocketClient.connect();

// 导出
export { ALCHEMWebSocketClient, webSocketClient };
export default webSocketClient;