/**
 * API客户端模块 - 简化版本
 * 移除了过度设计的HTTP客户端和rdkit集成
 * 只保留核心的后端API通信功能
 */

/**
 * 简化的API客户端 - 只包含实际需要的功能
 */
export class APIClient {
    constructor() {
        this.baseURL = '';
    }
    
    // 设置基础URL（如果需要）
    setBaseURL(url) {
        this.baseURL = url;
    }
    
    // 简单的请求方法 - 删除了过度复杂的重试和缓存机制
    async request(url, options = {}) {
        const fullURL = this.baseURL + url;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
            ...options
        };
        
        try {
            const response = await fetch(fullURL, defaultOptions);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }
    
    // GET请求
    async get(url) {
        return this.request(url, { method: 'GET' });
    }
    
    // POST请求
    async post(url, data) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
}

// 创建默认实例
export const apiClient = new APIClient();

// 模块加载日志
console.log("🔌 简化API客户端模块已加载");