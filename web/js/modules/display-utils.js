/**
 * 显示工具模块 - 负责HTML内容生成、UI组件创建和显示相关工具函数
 * 从custom3DDisplay.js重构而来
 */

/**
 * 显示工具类
 */
export class DisplayUtils {
    constructor() {
        this.progressBars = new Map();
    }
    
    // 生成分子信息显示的HTML内容
    generateMolecularDisplayHTML(molecularData, analysis, isFromBackend = false) {
        const title = analysis?.title || molecularData?.title || 'molecule';
        const dataSource = isFromBackend ? '后端内存' : (molecularData ? '前端内存' : '文件系统');
        const atomCount = analysis?.atoms || molecularData?.atoms || 'N/A';
        const format = analysis?.format || molecularData?.format || 'Unknown';
        
        return `
            <div class="molecular-display-container">
                <h3 style="color: #4fc3f7; margin-bottom: 16px; text-align: center;">
                    🧪 正在显示: ${title}
                </h3>
                
                <div class="demo-3d-display">
                    <div class="molecule-title">${title}</div>
                    <div class="molecule-info">格式: ${format}</div>
                    <div class="molecule-info">原子数: ${atomCount}</div>
                    <div class="molecule-info">数据源: ${dataSource}</div>
                    
                    <div style="margin: 20px 0; font-size: 14px; line-height: 1.6;">
                        🎯 <strong>3D分子结构显示</strong><br>
                        在真实应用中，这里会显示交互式的3D分子模型<br>
                        支持旋转、缩放、原子选择等操作
                    </div>
                    
                    <div style="position: absolute; bottom: 10px; right: 10px; font-size: 12px; opacity: 0.7;">
                        ALCHEM 3D Display
                    </div>
                </div>
                
                ${this.generateMolecularInfoSection(molecularData, analysis, isFromBackend)}
            </div>
        `;
    }
    
    // 生成分子信息详情部分
    generateMolecularInfoSection(molecularData, analysis, isFromBackend) {
        if (isFromBackend && molecularData) {
            return `
                <div class="status-info">
                    <h4>🚀 后端内存优化</h4>
                    <div class="info-grid">
                        <div>
                            <strong>文件名:</strong> ${molecularData.filename || '未知'}<br>
                            <strong>格式:</strong> ${molecularData.format_name || '未知'}<br>
                            <strong>原子数:</strong> ${molecularData.atoms || 0}
                        </div>
                        <div>
                            <strong>缓存时间:</strong> ${new Date(molecularData.cached_at * 1000).toLocaleTimeString()}<br>
                            <strong>访问次数:</strong> ${molecularData.access_count || 0}<br>
                            <strong>节点ID:</strong> ${molecularData.node_id || '未知'}
                        </div>
                    </div>
                    <p style="margin: 8px 0 0 0; font-size: 12px; line-height: 1.4;">
                        🚀 <strong>性能优化</strong>: 分子数据已在后端内存中缓存<br>
                        📊 <strong>数据来源</strong>: 直接从后端内存读取，毫秒级响应<br>
                        ⚡ <strong>响应速度</strong>: 比文件读取快数百倍，支持高频访问<br>
                        💾 <strong>持久化</strong>: 数据在后端持久保存，重启后仍可用
                    </p>
                </div>
            `;
        } else if (molecularData && !isFromBackend) {
            return `
                <div class="status-info">
                    <h4>💡 前端内存优化</h4>
                    <div class="info-grid">
                        <div>
                            <strong>原始文件名:</strong> ${molecularData.originalName || '未知'}<br>
                            <strong>服务器路径:</strong> ${molecularData.filename || '未知'}<br>
                            <strong>文件大小:</strong> ${(molecularData.fileSize / 1024 || 0).toFixed(1)} KB
                        </div>
                        <div>
                            <strong>上传时间:</strong> ${new Date(molecularData.uploadTime || 0).toLocaleTimeString()}<br>
                            <strong>内容长度:</strong> ${molecularData.content?.length || 0} 字符<br>
                            <strong>格式:</strong> ${molecularData.format || '未知'}
                        </div>
                    </div>
                    <p style="margin: 8px 0 0 0; font-size: 12px; line-height: 1.4;">
                        🚀 <strong>性能优化</strong>: 分子数据已在上传时解析并加载到前端内存中<br>
                        📊 <strong>数据来源</strong>: 直接从前端内存读取，无需重复的文件I/O操作<br>
                        ⚡ <strong>响应速度</strong>: 毫秒级别的数据访问，比文件读取快数百倍<br>
                        ⚠️ <strong>建议</strong>: 推荐升级到后端内存存储以获得更好的数据持久性
                    </p>
                </div>
            `;
        } else {
            return `
                <div class="status-info">
                    <h4>${analysis?.isDemo ? '💡 演示说明' : '⚠️ 性能提示'}</h4>
                    <p style="margin: 8px 0 0 0; font-size: 12px; line-height: 1.4;">
                        ${analysis?.isDemo ? 
                            '这是一个演示性的3D显示功能！使用内置演示数据。' : 
                            '当前从文件系统读取数据，性能较慢。建议重新上传文件以启用内存加载优化。'
                        }
                        <br>在实际应用中，这里会显示真正的MolStar 3D分子查看器。
                    </p>
                </div>
            `;
        }
    }
    
    // 生成欢迎界面HTML
    generateWelcomeHTML(molstarAvailable = false) {
        return `
            <div style="text-align: center; padding: 40px; color: var(--fg-color, #ccc);">
                <h2>🧪 ALCHEM 3D分子显示器</h2>
                <p style="margin: 20px 0; line-height: 1.6;">
                    欢迎使用ALCHEM 3D分子显示功能！<br>
                    上传分子文件并执行节点后，3D结构将在此处显示。
                </p>
                <div style="background: var(--comfy-input-bg, #2a2a2a); border: 1px solid var(--border-color, #444); border-radius: 6px; padding: 16px; margin: 20px 0; text-align: left;">
                    <h4 style="margin: 0 0 12px 0; color: var(--primary-color, #007bff);">支持的文件格式</h4>
                    <ul style="margin: 0; padding-left: 20px; line-height: 1.8;">
                        <li>PDB - 蛋白质数据库格式</li>
                        <li>MOL - 分子文件格式</li>
                        <li>SDF - 结构数据文件</li>
                        <li>XYZ - 笛卡尔坐标格式</li>
                        <li>更多格式...</li>
                    </ul>
                </div>
                <p style="font-size: 12px; opacity: 0.7; margin-top: 30px;">
                    ${molstarAvailable ? 
                        '🎉 MolStar 3D查看器已启用，将提供专业级分子可视化体验' : 
                        '💡 提示：安装MolStar库可以获得更好的3D显示效果'
                    }
                </p>
            </div>
        `;
    }
    
    // 生成加载状态HTML
    generateLoadingHTML(filename, progress = 0) {
        return `
            <div style="text-align: center; margin-bottom: 20px;">
                <h3 style="color: #4fc3f7; margin-bottom: 10px;">🔄 正在加载分子文件...</h3>
                <p style="color: #999;">文件: ${filename}</p>
                <div style="background: #333; height: 4px; border-radius: 2px; overflow: hidden; margin: 20px 0;">
                    <div style="background: linear-gradient(45deg, #4fc3f7, #81c784); height: 100%; width: ${progress}%; transition: width 0.3s;" id="loading-progress"></div>
                </div>
            </div>
        `;
    }
    
    // 生成错误信息HTML
    generateErrorHTML(error, suggestions = []) {
        const suggestionsList = suggestions.length > 0 ? 
            `<ul style="text-align: left; margin: 16px 0; padding-left: 20px;">
                ${suggestions.map(s => `<li>${s}</li>`).join('')}
            </ul>` : '';
            
        return `
            <div style="text-align: center; padding: 40px; color: var(--fg-color, #ccc);">
                <h3 style="color: #f44336; margin-bottom: 16px;">❌ 显示错误</h3>
                <p style="color: #999; margin-bottom: 20px;">${error}</p>
                ${suggestionsList}
                <p style="font-size: 12px; opacity: 0.7; margin-top: 30px;">
                    如果问题持续存在，请检查文件格式和上传过程
                </p>
            </div>
        `;
    }
    
    // 创建进度条
    createProgressBar(containerId, initialProgress = 0) {
        const container = document.getElementById(containerId);
        if (!container) return null;
        
        const progressBar = document.createElement('div');
        progressBar.className = 'progress-bar';
        progressBar.innerHTML = `
            <div class="progress-fill" style="width: ${initialProgress}%"></div>
        `;
        
        container.appendChild(progressBar);
        this.progressBars.set(containerId, progressBar);
        
        return progressBar;
    }
    
    // 更新进度条
    updateProgressBar(containerId, progress) {
        const progressBar = this.progressBars.get(containerId);
        if (progressBar) {
            const fill = progressBar.querySelector('.progress-fill');
            if (fill) {
                fill.style.width = `${Math.max(0, Math.min(100, progress))}%`;
            }
        }
        
        // 也尝试更新页面中的进度条
        const pageProgressBar = document.getElementById('loading-progress');
        if (pageProgressBar) {
            pageProgressBar.style.width = `${Math.max(0, Math.min(100, progress))}%`;
        }
    }
    
    // 创建加载覆盖层
    createLoadingOverlay(message = '加载中...') {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div>
                <div class="loading-spinner"></div>
                <p>${message}</p>
            </div>
        `;
        return overlay;
    }
    
    // 创建信息弹窗
    createInfoDialog(title, content, actions = []) {
        const dialog = document.createElement('div');
        dialog.className = 'info-dialog';
        dialog.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: var(--comfy-menu-bg, #202020);
            border: 1px solid var(--border-color, #444);
            border-radius: 8px;
            padding: 24px;
            max-width: 500px;
            z-index: 10000;
            box-shadow: 0 8px 32px rgba(0,0,0,0.6);
        `;
        
        const actionsHTML = actions.length > 0 ? 
            `<div style="margin-top: 20px; text-align: right;">
                ${actions.map(action => 
                    `<button onclick="${action.onclick}" style="margin-left: 8px; padding: 8px 16px; background: var(--primary-color, #007bff); border: none; border-radius: 4px; color: white; cursor: pointer;">
                        ${action.text}
                    </button>`
                ).join('')}
            </div>` : '';
        
        dialog.innerHTML = `
            <h3 style="margin: 0 0 16px 0; color: var(--primary-color, #007bff);">${title}</h3>
            <div style="color: var(--fg-color, #ccc); line-height: 1.6;">${content}</div>
            ${actionsHTML}
        `;
        
        return dialog;
    }
    
    // 显示通知
    showNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--comfy-menu-bg, #202020);
            border: 1px solid var(--border-color, #444);
            border-left: 4px solid ${type === 'error' ? '#f44336' : type === 'success' ? '#4caf50' : '#2196f3'};
            border-radius: 4px;
            padding: 12px 16px;
            color: var(--fg-color, #ccc);
            max-width: 300px;
            z-index: 10001;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
        `;
        
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // 显示动画
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 10);
        
        // 自动隐藏
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, duration);
        
        return notification;
    }
    
    // 格式化文件大小
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // 格式化时间
    formatTime(timestamp) {
        if (!timestamp) return 'Unknown';
        const date = new Date(timestamp * 1000);
        return date.toLocaleString();
    }
    
    // 清理所有UI元素
    cleanup() {
        this.progressBars.clear();
        
        // 清理通知
        document.querySelectorAll('.notification').forEach(el => el.remove());
        
        // 清理弹窗
        document.querySelectorAll('.info-dialog').forEach(el => el.remove());
        
        // 清理加载覆盖层
        document.querySelectorAll('.loading-overlay').forEach(el => el.remove());
        
        console.log("🧪 Display utils cleaned up");
    }
}