/**
 * API客户端模块 - 负责与后端API的通信和rdkit_molstar的集成
 * 从custom3DDisplay.js重构而来
 */

/**
 * API客户端类
 */
export class APIClient {
    constructor() {
        this.baseURL = '';
        this.timeout = 10000; // 10秒超时
        this.retryCount = 3;
        this.cache = new Map();
    }
    
    // 设置基础URL
    setBaseURL(url) {
        this.baseURL = url;
    }
    
    // 设置超时时间
    setTimeout(timeout) {
        this.timeout = timeout;
    }
    
    // 通用请求方法
    async request(url, options = {}) {
        const fullURL = this.baseURL + url;
        const defaultOptions = {
            timeout: this.timeout,
            headers: {
                'Content-Type': 'application/json',
            },
            ...options
        };
        
        let lastError;
        for (let i = 0; i < this.retryCount; i++) {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), this.timeout);
                
                const response = await fetch(fullURL, {
                    ...defaultOptions,
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                return await response.json();
            } catch (error) {
                lastError = error;
                if (i < this.retryCount - 1) {
                    console.warn(`🔄 Request failed, retrying... (${i + 1}/${this.retryCount})`, error);
                    await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1))); // 指数退避
                }
            }
        }
        
        throw lastError;
    }
    
    // 获取分子数据
    async getMolecularData(nodeId) {
        const cacheKey = `molecular_${nodeId}`;
        
        // 检查缓存
        if (this.cache.has(cacheKey)) {
            console.log(`📦 Using cached molecular data for node: ${nodeId}`);
            return this.cache.get(cacheKey);
        }
        
        try {
            console.log(`🚀 Fetching molecular data for node: ${nodeId}`);
            
            const response = await this.request('/alchem_propbtn/api/molecular', {
                method: 'POST',
                body: JSON.stringify({
                    request_type: 'get_molecular_data',
                    node_id: nodeId
                })
            });
            
            if (response.success) {
                console.log(`✅ Successfully retrieved molecular data from backend`);
                console.log(`   - Node ID: ${response.data.node_id}`);
                console.log(`   - Filename: ${response.data.filename}`);
                console.log(`   - Format: ${response.data.format_name}`);
                console.log(`   - Atoms: ${response.data.atoms}`);
                
                // 缓存结果
                this.cache.set(cacheKey, response);
            }
            
            return response;
            
        } catch (error) {
            console.error('🚨 Error fetching molecular data from backend:', error);
            return {
                success: false,
                error: `Network error: ${error.message}`,
                data: null
            };
        }
    }
    
    // 获取缓存状态
    async getCacheStatus() {
        const cacheKey = 'cache_status';
        
        try {
            const response = await this.request('/alchem_propbtn/api/molecular', {
                method: 'POST',
                body: JSON.stringify({
                    request_type: 'get_cache_status'
                })
            });
            
            console.log(`📊 Cache status:`, response);
            
            // 缓存结果（短时间）
            this.cache.set(cacheKey, response);
            setTimeout(() => this.cache.delete(cacheKey), 5000); // 5秒后清除缓存
            
            return response;
            
        } catch (error) {
            console.error('🚨 Error fetching cache status:', error);
            return {
                success: false,
                error: error.message,
                data: null
            };
        }
    }
    
    // 获取系统状态
    async getSystemStatus() {
        try {
            const response = await this.request('/alchem_propbtn/api/status', {
                method: 'GET'
            });
            
            console.log(`🔧 System status:`, response);
            return response;
            
        } catch (error) {
            console.error('🚨 Error fetching system status:', error);
            return {
                success: false,
                error: error.message,
                data: null
            };
        }
    }
    
    // 上传分子文件
    async uploadMolecularFile(file, nodeId, customFilename = null) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('node_id', nodeId);
            if (customFilename) {
                formData.append('custom_filename', customFilename);
            }
            
            const response = await fetch('/alchem_propbtn/api/upload_molecular', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            console.log(`📤 Upload result:`, result);
            
            // 清除相关缓存
            this.clearCacheForNode(nodeId);
            
            return result;
            
        } catch (error) {
            console.error('🚨 Error uploading molecular file:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }
    
    // 读取文件内容
    async readFileContent(filename) {
        try {
            const fileUrl = `/view?filename=${encodeURIComponent(filename)}&type=input`;
            console.log(`🧪 Reading file: ${fileUrl}`);
            
            const response = await fetch(fileUrl);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const content = await response.text();
            console.log(`🧪 Successfully read ${content.length} characters from ${filename}`);
            
            return content;
        } catch (error) {
            console.error(`🧪 Failed to read file ${filename}:`, error);
            throw error;
        }
    }
    
    // 清除特定节点的缓存
    clearCacheForNode(nodeId) {
        const keys = Array.from(this.cache.keys());
        const nodeKeys = keys.filter(key => key.includes(nodeId));
        nodeKeys.forEach(key => this.cache.delete(key));
        
        if (nodeKeys.length > 0) {
            console.log(`🧹 Cleared cache for node ${nodeId}: ${nodeKeys.length} entries`);
        }
    }
    
    // 清除所有缓存
    clearAllCache() {
        const size = this.cache.size;
        this.cache.clear();
        console.log(`🧹 Cleared all API cache: ${size} entries`);
    }
    
    // 获取缓存统计信息
    getCacheStats() {
        return {
            size: this.cache.size,
            keys: Array.from(this.cache.keys()),
            memoryUsage: JSON.stringify(Array.from(this.cache.entries())).length
        };
    }
}

/**
 * rdkit_molstar集成工具
 */
export class RDKitMolstarIntegration {
    constructor() {
        this.isAvailable = false;
        this.globalViewer = null;
        this.checkAvailability();
    }
    
    // 检查rdkit_molstar是否可用
    checkAvailability() {
        this.isAvailable = !!(
            typeof window !== 'undefined' && 
            window.globalViewer && 
            window.globalViewer.isInitialized
        );
        
        if (this.isAvailable) {
            this.globalViewer = window.globalViewer;
            console.log("🎯 rdkit_molstar viewer is available");
        } else {
            console.log("🎯 rdkit_molstar viewer is not available");
        }
        
        return this.isAvailable;
    }
    
    // 尝试使用现有的MolStar查看器
    async tryUseExistingMolStarViewer(node, inputName) {
        if (!this.isAvailable) {
            console.log("🎯 rdkit_molstar not available, using ALCHEM viewer");
            return false;
        }
        
        // 只有当用户明确希望使用rdkit_molstar时才尝试
        if (typeof node.showInGlobalViewer === 'function') {
            console.log("🎯 Found and using rdkit_molstar viewer (user preference)");
            try {
                await node.showInGlobalViewer();
                return true;
            } catch (error) {
                console.warn("🎯 Failed to use rdkit_molstar viewer:", error);
            }
        }
        
        // 默认使用ALCHEM自己的MolStar集成
        console.log("🎯 Using ALCHEM independent MolStar viewer");
        return false;
    }
    
    // 检查是否有全局查看器
    hasGlobalViewer() {
        return this.isAvailable && this.globalViewer;
    }
    
    // 获取全局查看器状态
    getGlobalViewerStatus() {
        if (!this.isAvailable) {
            return {
                available: false,
                reason: 'rdkit_molstar not loaded'
            };
        }
        
        return {
            available: true,
            initialized: this.globalViewer.isInitialized,
            viewer: this.globalViewer
        };
    }
}

// 创建全局API客户端实例
export const apiClient = new APIClient();
export const rdkitIntegration = new RDKitMolstarIntegration();