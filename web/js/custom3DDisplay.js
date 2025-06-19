/**
 * ALCHEM 3D显示模块协调器 - 重构版本
 * 整合所有拆分的模块，提供统一的API接口
 * 从1726行巨型文件重构为模块化架构
 */

import { app } from "../../../scripts/app.js";

// 导入合并后的模块
import { loadMolstarLibrary, MolstarViewer } from './modules/molstar-core.js';
import { applyStyles, ALCHEM3DPanelManager, ResizeController } from './modules/ui-integrated.js';
// DisplayUtils已删除 - 简化为直接显示分子数据
import { MolecularDataProcessor } from './modules/data-processor.js';
import { APIClient, apiClient } from './modules/api-client.js';
// 🚀 导入WebSocket客户端
import { webSocketClient } from './modules/websocket-client.js';

/**
 * 主协调器类 - 管理所有模块的交互
 */
class ALCHEM3DDisplayCoordinator {
    constructor() {
        this.panelManager = null;
        this.dataProcessor = null;
        this.displayUtils = null;
        this.isInitialized = false;
        
        // 🚀 WebSocket相关
        this.webSocketConnected = false;
        this.subscribedNodes = new Set();
    }
    
    // 初始化所有模块
    async initialize() {
        if (this.isInitialized) return;
        
        window.QUIET_LOG && window.QUIET_LOG("🚀 Initializing ALCHEM 3D Display Coordinator...");
        
        // 应用样式
        applyStyles();
        
        // 初始化各模块
        this.panelManager = new ALCHEM3DPanelManager();
        this.dataProcessor = new MolecularDataProcessor();
        // DisplayUtils已删除，简化为直接操作
        
        // 初始化面板管理器
        await this.panelManager.initialize();
        
        // 🚀 初始化WebSocket连接
        await this.initializeWebSocket();
        
        this.isInitialized = true;
        window.QUIET_LOG && window.QUIET_LOG("✅ ALCHEM 3D Display Coordinator initialized");
    }
    
    // 获取面板管理器
    getPanelManager() {
        return this.panelManager;
    }
    
    // 获取数据处理器
    getDataProcessor() {
        return this.dataProcessor;
    }
    
    // DisplayUtils已删除
    
    // 获取API客户端（简化版）
    getAPIClient() {
        return apiClient;
    }
    
    // 🚀 初始化WebSocket连接
    async initializeWebSocket() {
        try {
            // 设置事件监听器
            webSocketClient.on('connected', () => {
                this.webSocketConnected = true;
                console.log("🚀 3D显示模块：WebSocket连接成功");
                
                // 重新订阅所有节点
                for (const nodeId of this.subscribedNodes) {
                    webSocketClient.subscribeNode(nodeId);
                }
            });
            
            webSocketClient.on('disconnected', () => {
                this.webSocketConnected = false;
                console.warn("⚠️ 3D显示模块：WebSocket连接断开");
            });
            
            // 🔥 关键：监听分子数据变更
            webSocketClient.on('molecular_data_changed', (message) => {
                this.handleMolecularDataChange(message);
            });
            
            // 连接到WebSocket服务器
            await webSocketClient.connect();
            
        } catch (error) {
            console.error("❌ WebSocket初始化失败:", error);
        }
    }
    
    // 🔥 处理分子数据变更（自动刷新Molstar）
    async handleMolecularDataChange(message) {
        const { node_id, change_type, data, timestamp } = message;
        
        console.log(`[DEBUG] 收到WebSocket分子数据变更消息:`);
        console.log(`  - 节点ID: '${node_id}'`);
        console.log(`  - 变更类型: ${change_type}`);
        console.log(`  - 时间戳: ${timestamp}`);
        console.log(`  - 数据文件名: ${data?.filename || 'N/A'}`);
        
        try {
            // 🔑 关键修复：检查当前显示的是否是发生变更的节点
            if (this.panelManager && this.panelManager.isVisible) {
                // 获取当前显示的节点ID
                const currentDisplayNodeId = this.panelManager.getCurrentDisplayNodeId();
                
                console.log(`[DEBUG] 节点ID匹配检查:`);
                console.log(`  - 当前显示的节点ID: '${currentDisplayNodeId}'`);
                console.log(`  - 收到变更的节点ID: '${node_id}'`);
                console.log(`  - ID匹配: ${currentDisplayNodeId === node_id}`);
                
                if (currentDisplayNodeId === node_id) {
                    console.log(`[DEBUG] 节点ID匹配，开始自动刷新Molstar`);
                    
                    // 获取最新的分子数据
                    const backendData = await this.dataProcessor.fetchMolecularDataFromBackend(node_id);
                    
                    if (backendData && backendData.success) {
                        const molecularData = backendData.data;
                        
                        // 直接更新Molstar显示
                        if (molecularData.content) {
                            this.panelManager.displayData(molecularData.content);
                            console.log(`✅ Molstar已更新: ${molecularData.filename} (${molecularData.atoms} 原子)`);
                        }
                    } else {
                        console.warn("⚠️ 获取最新分子数据失败");
                    }
                } else {
                    console.log(`📝 节点 ${node_id} 数据变更，但当前显示的是节点 ${currentDisplayNodeId}，跳过刷新`);
                }
            } else {
                console.log(`📝 节点 ${node_id} 数据变更，但Molstar面板未显示，跳过刷新`);
            }
            
        } catch (error) {
            console.error("❌ 处理分子数据变更失败:", error);
        }
    }
    
    // 🚀 订阅节点的数据变更
    subscribeNodeUpdates(nodeId) {
        if (!nodeId) return;
        
        this.subscribedNodes.add(nodeId);
        
        if (this.webSocketConnected) {
            webSocketClient.subscribeNode(nodeId);
            console.log(`🔔 已订阅节点 ${nodeId} 的数据变更`);
        } else {
            console.log(`📝 节点 ${nodeId} 将在WebSocket连接后自动订阅`);
        }
    }
    
    // 取消订阅
    unsubscribeNodeUpdates(nodeId) {
        this.subscribedNodes.delete(nodeId);
        
        if (this.webSocketConnected) {
            webSocketClient.unsubscribeNode(nodeId);
        }
    }
    
    // 清理所有资源
    destroy() {
        // 断开WebSocket连接
        if (this.webSocketConnected) {
            webSocketClient.disconnect();
        }
        
        if (this.panelManager) {
            this.panelManager.destroy();
        }
        
        // DisplayUtils清理已删除
        
        if (this.dataProcessor) {
            this.dataProcessor.clearCache();
        }
        
        // 简化版API客户端无需清理缓存
        
        this.isInitialized = false;
    }
}

// 创建全局协调器实例
const alchem3DCoordinator = new ALCHEM3DDisplayCoordinator();

// 主3D显示函数 - 重构版本
export const show3DMolecularView = async (node, inputName) => {
    // 确保协调器已初始化
    if (!alchem3DCoordinator.isInitialized) {
        await alchem3DCoordinator.initialize();
    }
    
    const panelManager = alchem3DCoordinator.getPanelManager();
    const dataProcessor = alchem3DCoordinator.getDataProcessor();
    
    try {
        window.QUIET_LOG && window.QUIET_LOG("🎯 Using ALCHEM modular display system");
        
        // 获取分子输入数据
        const molInput = node.widgets.find(w => w.name === inputName);
        const selectedFile = molInput ? molInput.value : 'benzene';
        
        window.QUIET_LOG && window.QUIET_LOG(`🧪 Processing molecular display: ${inputName} = ${selectedFile}`);
        
        // 生成唯一节点ID
        const nodeId = dataProcessor.generateUniqueNodeId(node);
        
        console.log(`[DEBUG] show3DMolecularView:`);
        console.log(`  - 生成的节点ID: '${nodeId}'`);
        console.log(`  - 节点对象ID: ${node.id}`);
        console.log(`  - 输入名称: ${inputName}`);
        console.log(`  - 文件名: ${selectedFile}`);
        
        // 🔑 关键修复：设置节点的_alchem_node_id参数为正确的tab感知ID
        const alchemNodeIdWidget = node.widgets?.find(w => w.name === '_alchem_node_id');
        if (alchemNodeIdWidget) {
            alchemNodeIdWidget.value = nodeId;
            console.log(`✅ 3D显示设置节点参数 _alchem_node_id = ${nodeId}`);
        } else {
            console.warn(`⚠️ 3D显示未找到_alchem_node_id widget，节点执行时可能无法获取正确的tab感知ID`);
        }
        
        // 🚀 订阅该节点的WebSocket更新
        alchem3DCoordinator.subscribeNodeUpdates(nodeId);
        
        // 🔑 设置当前显示的节点ID
        panelManager.setCurrentDisplayNodeId(nodeId);
        
        // 显示面板
        panelManager.showPanel();
        
        // 步骤1：尝试从后端内存获取分子数据
        let molecularData = null;
        let backendData = null;
        let isFromBackend = false;
        
        try {
            backendData = await dataProcessor.fetchMolecularDataFromBackend(nodeId);
            
            if (backendData && backendData.success) {
                molecularData = backendData.data;
                isFromBackend = true;
            } else {
                // 🔑 严格节点ID绑定：移除文件名回退逻辑，避免数据混乱
                console.warn(`⚠️ 节点 ${nodeId} 的数据不存在，不使用文件名回退避免数据混乱`);
            }
        } catch (error) {
            console.error(`❌ 获取节点 ${nodeId} 数据失败:`, error);
        }
        
        // 步骤2：回退到前端内存（兼容性）
        if (!molecularData && node.molecularData && node.molecularData[inputName]) {
            molecularData = node.molecularData[inputName];
        }
        
        // 简化：直接显示分子数据，删除复杂的HTML生成
        
        // 显示面板
        panelManager.showPanel();
        
        // 获取分子内容
        let molstarContent = null;
        if (molecularData && molecularData.content) {
            // 使用实际分子数据
            molstarContent = molecularData.content;
            console.log(`🧪 显示分子: ${molecularData.filename || selectedFile}`);
        } else {
            // 使用默认数据
            const defaultData = dataProcessor.getDefaultMoleculeData();
            molstarContent = defaultData.pdb;
            console.log(`🧪 显示默认分子`);
        }
        
        // 直接显示分子数据（无论MolStar是否可用）
        panelManager.displayData(molstarContent);
        
        
    } catch (error) {
        console.error('🚨 Error in 3D display:', error);
        
        // 简化错误处理：直接显示错误消息
        const errorMessage = `❌ 3D显示错误: ${error.message}`;
        panelManager.displayData(`<div style="padding: 20px; color: #f44336; text-align: center;">${errorMessage}</div>`);
    }
};

// 🧪 执行分子数据编辑
export const editMolecularData = async (node, inputName, editType) => {
    try {
        console.log(`[DEBUG] editMolecularData开始:`);
        console.log(`  - 节点ID: ${node.id}`);
        console.log(`  - 输入名称: ${inputName}`);
        console.log(`  - 编辑类型: ${editType}`);
        
        // 🔑 关键修复：查找实际存储数据的节点ID
        const dataProcessor = alchem3DCoordinator.getDataProcessor();
        const currentNodeId = dataProcessor.generateUniqueNodeId(node);
        
        console.log(`[DEBUG] 编辑操作节点ID处理:`);
        console.log(`  - 生成的唯一节点ID: '${currentNodeId}'`);
        console.log(`  - 节点对象ID: ${node.id}`);
        
        // 首先尝试使用当前节点ID
        let targetNodeId = currentNodeId;
        
        // 🔑 修复：严格使用当前节点ID，不允许按文件名查找
        // 这确保每个节点的编辑功能只操作自己的数据
        console.log(`[DEBUG] 严格节点ID绑定: 编辑操作将使用节点ID '${targetNodeId}'`);
        
        // 调用后端编辑API
        const response = await fetch('/alchem_propbtn/api/molecular', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                request_type: 'edit_molecular_data',
                node_id: targetNodeId,  // 使用找到的目标节点ID
                edit_type: editType
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log(`✅ 编辑成功: ${result.message}`);
            console.log(`   原子数量: ${result.data.atoms_count}`);
            
            // WebSocket会自动推送更新，无需手动刷新
            return result;
        } else {
            console.error(`❌ 编辑失败: ${result.error}`);
            throw new Error(result.error);
        }
        
    } catch (error) {
        console.error('🚨 编辑分子数据失败:', error);
        throw error;
    }
};

// 创建3D显示Widget - 重构版本
export const createMolstar3DDisplayWidget = () => {
    return (node, inputName, inputData) => {
        const inputOptions = inputData[1] ?? {};
        const { originalInputName } = inputOptions;
        
        // 🔑 关键修复：在Widget创建时就设置_alchem_node_id，确保节点执行时能获取到正确ID
        const dataProcessor = alchem3DCoordinator.getDataProcessor();
        const nodeId = dataProcessor.generateUniqueNodeId(node);
        
        // 查找并设置_alchem_node_id参数
        const alchemNodeIdWidget = node.widgets?.find(w => w.name === '_alchem_node_id');
        if (alchemNodeIdWidget) {
            alchemNodeIdWidget.value = nodeId;
            console.log(`✅ Widget创建时设置 _alchem_node_id = ${nodeId}`);
        } else {
            console.warn(`⚠️ Widget创建时未找到_alchem_node_id widget，节点: ${node.type}`);
        }
        
        // 创建3D显示按钮
        const displayWidget = node.addWidget(
            'button',
            `${inputName}_3d`,
            '🧪 显示3D结构',
            () => {
                show3DMolecularView(node, originalInputName);
            },
            { 
                serialize: false
            }
        );
        
        // 🧪 创建简单编辑按钮
        const editWidget = node.addWidget(
            'button',
            `${inputName}_edit`,
            '🔧 删除最后原子',
            async () => {
                try {
                    await editMolecularData(node, originalInputName, 'remove_last_atom');
                } catch (error) {
                    alert(`编辑失败: ${error.message}`);
                }
            },
            { 
                serialize: false
            }
        );

        // 自定义按钮样式
        displayWidget.computeSize = function() {
            return [200, 30];
        };
        
        editWidget.computeSize = function() {
            return [200, 30];
        };

        
        return { widget: displayWidget };
    };
};

// 初始化3D显示功能 - 重构版本
export const init3DDisplay = async () => {
    try {
        await alchem3DCoordinator.initialize();
    } catch (error) {
        console.error("❌ Failed to initialize modular 3D Display system:", error);
    }
};

// 处理3D显示节点创建 - 重构版本
export const handle3DDisplayNodeCreated = (node) => {
    if (node.type === 'Demo3DDisplayNode') {
    }
};

// 检查是否有3D显示属性的节点并处理 - 重构版本
export const process3DDisplayNodes = (nodeType, nodeData) => {
    const dataProcessor = alchem3DCoordinator.getDataProcessor();
    
    const { input } = nodeData ?? {};
    const { required } = input ?? {};
    if (!required) return null;

    // 查找带有3D显示属性的输入
    const found3DDisplay = Object.entries(required).find(([_, inputSpec]) =>
        dataProcessor.isMolstar3DDisplayInput(inputSpec)
    );

    if (found3DDisplay) {
        const [inputName, inputSpec] = found3DDisplay;
        return {
            inputName,
            inputSpec,
            molstar_3d: createMolstar3DDisplayInput(inputName, inputSpec)
        };
    }
    
    return null;
};

// 兼容性函数
export const isMolstar3DDisplayInput = (inputSpec) => {
    const dataProcessor = alchem3DCoordinator.getDataProcessor();
    return dataProcessor.isMolstar3DDisplayInput(inputSpec);
};

export const createMolstar3DDisplayInput = (inputName, inputSpec) => {
    const dataProcessor = alchem3DCoordinator.getDataProcessor();
    return dataProcessor.createMolstar3DDisplayInput(inputName, inputSpec);
};

// 导出协调器实例供外部使用
export { alchem3DCoordinator };

// 向后兼容性 - 导出原始的类和函数
export {
    loadMolstarLibrary,
    MolstarViewer,
    ALCHEM3DPanelManager,
    ResizeController,
    MolecularDataProcessor,
    APIClient
};

