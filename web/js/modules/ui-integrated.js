/**
 * ALCHEM UI集成模块 - 合并了面板管理、显示工具、拖拽缩放和样式功能
 * 从以下模块合并而来：
 * - panel-manager.js (面板管理)
 * - display-utils.js (显示工具)
 * - resize-controller.js (拖拽缩放)
 * - display-styles.js (样式定义)
 */

import { loadMolstarLibrary, MolstarViewer } from './molstar-core.js';

// =================== 样式定义 ===================
export const display3DStyles = `
/* ComfyUI样式变量兼容 */
:root {
    --comfy-menu-bg: #202020;
    --comfy-input-bg: #2a2a2a;
    --comfy-input-bg-hover: #333;
    --comfy-input-bg-active: #3a3a3a;
    --bg-color: #1a1a1a;
    --fg-color: #ccc;
    --border-color: #444;
    --primary-color: #007bff;
    --primary-color-hover: #0056b3;
    --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.custom-3d-display-button {
    background: var(--comfy-input-bg, #2a2a2a);
    border: 1px solid var(--border-color, #444);
    border-radius: 4px;
    color: var(--fg-color, #ccc);
    padding: 6px 12px;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    margin: 2px;
    font-family: inherit;
}

.custom-3d-display-button:hover {
    background: var(--comfy-input-bg-hover, #333);
    border-color: var(--primary-color, #007bff);
}

.custom-3d-display-button:active {
    background: var(--comfy-input-bg-active, #3a3a3a);
}

.custom-3d-viewer {
    position: fixed;
    top: 40px;
    left: 36px;
    width: calc(100% - 36px);
    height: 40%;
    background: var(--comfy-menu-bg, #202020);
    border: 1px solid var(--border-color, #444);
    border-top: none;
    z-index: 8;
    display: none;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    transition: all 0.3s ease;
    font-family: var(--font-family, sans-serif);
}

.custom-3d-viewer-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: var(--comfy-menu-bg, #202020);
    border-bottom: 1px solid var(--border-color, #444);
    position: sticky;
    top: 0;
    z-index: 10;
}

.custom-3d-viewer-title {
    color: var(--fg-color, #ccc);
    font-size: 14px;
    font-weight: 500;
    margin: 0;
}

.custom-3d-viewer-close {
    background: transparent;
    border: 1px solid var(--border-color, #444);
    color: var(--fg-color, #ccc);
    padding: 4px 8px;
    border-radius: 3px;
    cursor: pointer;
    font-size: 12px;
    transition: all 0.2s ease;
}

.custom-3d-viewer-close:hover {
    background: var(--comfy-input-bg-hover, #333);
    border-color: var(--primary-color, #007bff);
}

.custom-3d-viewer-content {
    background: var(--bg-color, #1a1a1a);
    padding: 16px;
    height: calc(100% - 60px);
    overflow-y: auto;
    overflow-x: hidden;
    color: var(--fg-color, #ccc);
    font-family: var(--font-family, sans-serif);
    line-height: 1.5;
}

.info-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin: 12px 0;
    padding: 12px;
    background: var(--comfy-input-bg, #2a2a2a);
    border-radius: 6px;
    border: 1px solid var(--border-color, #444);
}

.info-grid div {
    line-height: 1.6;
}

.status-info {
    background: var(--comfy-input-bg, #2a2a2a);
    border: 1px solid var(--border-color, #444);
    border-radius: 6px;
    padding: 16px;
    margin: 12px 0;
}

.status-info h4 {
    margin: 0 0 12px 0;
    color: var(--primary-color, #007bff);
    font-size: 14px;
}

.viewer-container {
    width: 100%;
    height: 400px;
    border: 1px solid var(--border-color, #444);
    border-radius: 4px;
    background: var(--bg-color, #1a1a1a);
}

.resize-border {
    position: absolute;
    z-index: 20;
}

.resize-border:hover {
    background-color: rgba(0, 123, 255, 0.3);
}

.resize-border.resizing {
    background-color: rgba(0, 123, 255, 0.5);
}

.resize-border.top {
    top: -3px;
    left: 0;
    right: 0;
    height: 6px;
    cursor: n-resize;
}

.resize-border.bottom {
    bottom: -3px;  
    left: 0;
    right: 0;
    height: 6px;
    cursor: s-resize;
}

.resize-border.left {
    left: -3px;
    top: 0;
    bottom: 0;
    width: 6px;
    cursor: w-resize;
}

.resize-border.right {
    right: -3px;
    top: 0;
    bottom: 0;
    width: 6px;
    cursor: e-resize;
}

.resize-border.top-left {
    top: -3px;
    left: -3px;
    width: 10px;
    height: 10px;
    cursor: nw-resize;
}

.resize-border.top-right {
    top: -3px;
    right: -3px;
    width: 10px;
    height: 10px;
    cursor: ne-resize;
}

.resize-border.bottom-left {
    bottom: -3px;
    left: -3px;
    width: 10px;
    height: 10px;
    cursor: sw-resize;
    background-color: rgba(0, 255, 0, 0.4);
}

.resize-border.bottom-left:hover {
    background-color: rgba(0, 255, 0, 0.7);
}

.resize-border.bottom-right {
    bottom: -3px;
    right: -3px;
    width: 10px;
    height: 10px;
    cursor: se-resize;
}

.loading-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(26, 26, 26, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--fg-color, #ccc);
    z-index: 1000;
}

.demo-3d-display {
    width: 100%;
    height: 300px;
    background: linear-gradient(45deg, #1a1a1a, #2a2a2a);
    border: 2px dashed var(--border-color, #444);
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: var(--fg-color, #ccc);
    text-align: center;
    position: relative;
    overflow: hidden;
}

.molecule-title {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 8px;
    color: var(--primary-color, #007bff);
}

.molecule-info {
    font-size: 12px;
    opacity: 0.8;
    margin: 4px 0;
}

.loading-spinner {
    border: 3px solid var(--border-color, #444);
    border-top: 3px solid var(--primary-color, #007bff);
    border-radius: 50%;
    width: 30px;
    height: 30px;
    animation: spin 1s linear infinite;
    margin-bottom: 12px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.progress-bar {
    width: 200px;
    height: 4px;
    background: var(--border-color, #444);
    border-radius: 2px;
    overflow: hidden;
    margin: 12px 0;
}

.progress-fill {
    height: 100%;
    background: var(--primary-color, #007bff);
    border-radius: 2px;
    transition: width 0.3s ease;
}
`;

// =================== 拖拽缩放控制器 ===================
export class ResizeController {
    constructor() {
        this.isResizing = false;
        this.currentPanel = null;
        this.resizeData = null;
        this.minWidth = 300;
        this.minHeight = 200;
        this.maxWidth = null;
        this.maxHeight = null;
    }
    
    // 添加可拖动边框用于调整面板大小
    addResizeBorders(panel) {
        // 创建拖动边框的配置
        const borders = [
            { position: 'top', cursor: 'ns-resize' },
            { position: 'bottom', cursor: 'ns-resize' },
            { position: 'left', cursor: 'ew-resize' },
            { position: 'right', cursor: 'ew-resize' },
            { position: 'top-left', cursor: 'nw-resize' },
            { position: 'top-right', cursor: 'ne-resize' },
            { position: 'bottom-left', cursor: 'sw-resize' },
            { position: 'bottom-right', cursor: 'se-resize' }
        ];
        
        borders.forEach(border => {
            const borderElement = document.createElement('div');
            borderElement.className = `resize-border ${border.position}`;
            borderElement.style.cssText = this.getResizeBorderStyles(border.position, border.cursor);
            
            // 添加鼠标按下事件
            borderElement.addEventListener('mousedown', (e) => {
                this.startResize(e, border.position, panel);
            });
            
            panel.appendChild(borderElement);
        });
        
        console.log("🎯 Added 8-direction resize borders to panel");
    }
    
    // 获取拖动边框的样式
    getResizeBorderStyles(position, cursor) {
        const base = `
            position: absolute;
            cursor: ${cursor};
            background: transparent;
            transition: background 0.2s ease;
            z-index: 20;
        `;
        
        switch (position) {
            case 'top':
                return base + `
                    top: -3px; left: 0; right: 0; height: 6px;
                `;
            case 'bottom':
                return base + `
                    bottom: -3px; left: 0; right: 0; height: 6px;
                `;
            case 'left':
                return base + `
                    left: -3px; top: 0; bottom: 0; width: 6px;
                `;
            case 'right':
                return base + `
                    right: -3px; top: 0; bottom: 0; width: 6px;
                `;
            case 'top-left':
                return base + `
                    top: -3px; left: -3px; width: 10px; height: 10px;
                `;
            case 'top-right':
                return base + `
                    top: -3px; right: -3px; width: 10px; height: 10px;
                `;
            case 'bottom-left':
                return base + `
                    bottom: -3px; left: -3px; width: 10px; height: 10px;
                    background: rgba(76, 175, 80, 0.3); /* 高亮左下角 */
                `;
            case 'bottom-right':
                return base + `
                    bottom: -3px; right: -3px; width: 10px; height: 10px;
                `;
            default:
                return base;
        }
    }
    
    // 开始拖动调整大小
    startResize(e, position, panel) {
        e.preventDefault();
        e.stopPropagation();
        
        this.isResizing = true;
        this.currentPanel = panel;
        
        const startX = e.clientX;
        const startY = e.clientY;
        const startWidth = parseInt(window.getComputedStyle(panel).width, 10);
        const startHeight = parseInt(window.getComputedStyle(panel).height, 10);
        const startLeft = parseInt(window.getComputedStyle(panel).left, 10);
        const startTop = parseInt(window.getComputedStyle(panel).top, 10);
        
        this.resizeData = {
            position,
            startX,
            startY,
            startWidth,
            startHeight,
            startLeft,
            startTop
        };
        
        // 添加全局鼠标事件
        const onMouseMove = (e) => {
            this.doResize(e);
        };
        
        const onMouseUp = () => {
            this.stopResize();
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
        };
        
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
        
        // 设置全局样式
        document.body.style.cursor = this.getCursorForPosition(position);
        document.body.style.userSelect = 'none';
        
        // 添加拖拽状态样式
        panel.classList.add('resizing');
        
        console.log(`🎯 Started resizing panel from ${position}`);
    }
    
    // 执行拖动调整
    doResize(e) {
        if (!this.isResizing || !this.currentPanel || !this.resizeData) return;
        
        const { position, startX, startY, startWidth, startHeight, startLeft, startTop } = this.resizeData;
        const deltaX = e.clientX - startX;
        const deltaY = e.clientY - startY;
        
        // 尺寸限制
        const minWidth = this.minWidth;
        const minHeight = this.minHeight;
        const maxWidth = this.maxWidth || (window.innerWidth - 50);
        const maxHeight = this.maxHeight || (window.innerHeight - 50);
        
        let newWidth = startWidth;
        let newHeight = startHeight;
        let newLeft = startLeft;
        let newTop = startTop;
        
        // 根据拖动位置计算新尺寸
        switch (position) {
            case 'right':
                newWidth = Math.max(minWidth, Math.min(maxWidth, startWidth + deltaX));
                break;
            case 'left':
                newWidth = Math.max(minWidth, Math.min(maxWidth, startWidth - deltaX));
                newLeft = startLeft + (startWidth - newWidth);
                break;
            case 'bottom':
                newHeight = Math.max(minHeight, Math.min(maxHeight, startHeight + deltaY));
                break;
            case 'top':
                newHeight = Math.max(minHeight, Math.min(maxHeight, startHeight - deltaY));
                newTop = startTop + (startHeight - newHeight);
                break;
            case 'bottom-right':
                newWidth = Math.max(minWidth, Math.min(maxWidth, startWidth + deltaX));
                newHeight = Math.max(minHeight, Math.min(maxHeight, startHeight + deltaY));
                break;
            case 'bottom-left':
                newWidth = Math.max(minWidth, Math.min(maxWidth, startWidth - deltaX));
                newLeft = startLeft + (startWidth - newWidth);
                newHeight = Math.max(minHeight, Math.min(maxHeight, startHeight + deltaY));
                break;
            case 'top-right':
                newWidth = Math.max(minWidth, Math.min(maxWidth, startWidth + deltaX));
                newHeight = Math.max(minHeight, Math.min(maxHeight, startHeight - deltaY));
                newTop = startTop + (startHeight - newHeight);
                break;
            case 'top-left':
                newWidth = Math.max(minWidth, Math.min(maxWidth, startWidth - deltaX));
                newLeft = startLeft + (startWidth - newWidth);
                newHeight = Math.max(minHeight, Math.min(maxHeight, startHeight - deltaY));
                newTop = startTop + (startHeight - newHeight);
                break;
        }
        
        // 应用新尺寸和位置
        this.currentPanel.style.width = newWidth + 'px';
        this.currentPanel.style.height = newHeight + 'px';
        this.currentPanel.style.left = newLeft + 'px';
        this.currentPanel.style.top = newTop + 'px';
    }
    
    // 停止拖动调整
    stopResize() {
        if (!this.isResizing) return;
        
        this.isResizing = false;
        
        // 恢复全局样式
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        
        // 移除拖拽状态样式
        if (this.currentPanel) {
            this.currentPanel.classList.remove('resizing');
        }
        
        // 清理状态
        this.currentPanel = null;
        this.resizeData = null;
        
        console.log("🎯 Stopped resizing panel");
    }
    
    // 获取对应位置的光标样式
    getCursorForPosition(position) {
        const cursors = {
            'top': 'ns-resize',
            'bottom': 'ns-resize',
            'left': 'ew-resize',
            'right': 'ew-resize',
            'top-left': 'nw-resize',
            'top-right': 'ne-resize',
            'bottom-left': 'sw-resize',
            'bottom-right': 'se-resize'
        };
        return cursors[position] || 'default';
    }
    
    // 设置面板的最小和最大尺寸限制
    setResizeLimits(minWidth = 300, minHeight = 200, maxWidth = null, maxHeight = null) {
        this.minWidth = minWidth;
        this.minHeight = minHeight;
        this.maxWidth = maxWidth || (window.innerWidth - 50);
        this.maxHeight = maxHeight || (window.innerHeight - 50);
        
        console.log(`🎯 Updated resize limits: ${minWidth}x${minHeight} to ${this.maxWidth}x${this.maxHeight}`);
    }
    
    // 获取当前是否正在拖拽
    isCurrentlyResizing() {
        return this.isResizing;
    }
    
    // 清理事件监听器
    destroy() {
        if (this.isResizing) {
            this.stopResize();
        }
        console.log("🎯 Resize controller destroyed");
    }
}

// =================== 显示工具类 ===================
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

// =================== 3D面板管理器 ===================
export class ALCHEM3DPanelManager {
    constructor() {
        this.isVisible = false;
        this.currentData = null;
        this.panel = null;
        this.menuButton = null;
        this.isInitialized = false;
        
        // MolStar相关属性
        this.molstarAvailable = false;
        this.molstarViewer = null;
        this.viewerContainer = null;
        
        // 集成的组件实例
        this.resizeController = new ResizeController();
        this.displayUtils = new DisplayUtils();
    }
    
    async initialize() {
        if (this.isInitialized) return;
        
        console.log("🧪 初始化ALCHEM独立MolStar集成...");
        
        // 应用样式
        this.applyStyles();
        
        // 直接加载ALCHEM自己的MolStar库
        this.molstarAvailable = await loadMolstarLibrary();
        
        await this.createMenuButton();
        this.createPanel();
        this.isInitialized = true;
        
        console.log(`🚀 ALCHEM 3D Panel Manager initialized (MolStar: ${this.molstarAvailable ? '可用' : '不可用'})`);
        if (this.molstarAvailable) {
            console.log("🎉 ALCHEM独立MolStar集成成功！");
        } else {
            console.log("⚠️ MolStar加载失败，使用演示模式");
        }
    }
    
    // 应用样式到文档
    applyStyles() {
        const styleElement = document.createElement('style');
        styleElement.textContent = display3DStyles;
        document.head.appendChild(styleElement);
        console.log("🎨 Display styles applied");
    }
    
    async createMenuButton() {
        // 等待ComfyUI完全加载
        let attempts = 0;
        const maxAttempts = 50;
        
        while (attempts < maxAttempts) {
            const menubar = document.querySelector(".comfyui-menu");
            if (menubar) {
                // 创建按钮
                this.menuButton = document.createElement("button");
                this.menuButton.className = "alchem-menu-button";
                this.menuButton.innerHTML = `
                    <span>🧪</span>
                    <span>3D分子显示</span>
                `;
                
                this.menuButton.onclick = () => this.togglePanel();
                
                // 找到合适的位置插入按钮 (类似rdkit_molstar的方式)
                const menuRight = menubar.querySelector(".comfyui-menu-right");
                if (menuRight && menuRight.nextElementSibling) {
                    // 插入到菜单右侧区域旁边
                    menuRight.parentNode.insertBefore(this.menuButton, menuRight.nextElementSibling);
                } else {
                    // 回退方案：添加到菜单栏末尾
                    menubar.appendChild(this.menuButton);
                }
                
                console.log("🎯 Added ALCHEM 3D menu button to topbar");
                return;
            }
            
            attempts++;
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        console.warn("⚠️ Could not find ComfyUI menubar, creating floating button");
        this.createFloatingButton();
    }
    
    createFloatingButton() {
        // 创建悬浮按钮作为回退方案
        this.menuButton = document.createElement("button");
        this.menuButton.className = "alchem-menu-button";
        this.menuButton.style.position = "fixed";
        this.menuButton.style.top = "10px";
        this.menuButton.style.right = "10px";
        this.menuButton.style.zIndex = "9999";
        this.menuButton.innerHTML = `
            <span>🧪</span>
            <span>3D分子显示</span>
        `;
        
        this.menuButton.onclick = () => this.togglePanel();
        document.body.appendChild(this.menuButton);
        
        console.log("🎯 Created floating ALCHEM 3D button");
    }
    
    createPanel() {
        if (this.panel) return;
        
        this.panel = document.createElement('div');
        this.panel.id = 'alchem-3d-overlay-panel';
        this.panel.className = 'custom-3d-viewer';
        
        const header = document.createElement('div');
        header.className = 'custom-3d-viewer-header';
        
        const title = document.createElement('div');
        title.className = 'custom-3d-viewer-title';
        title.textContent = this.molstarAvailable ? 
            '🧪 ALCHEM MolStar 3D查看器' : 
            '🧪 ALCHEM 3D分子显示器';
        
        // 状态指示器
        const statusIndicator = document.createElement('div');
        statusIndicator.style.cssText = `
            width: 8px; height: 8px; border-radius: 50%; 
            background: ${this.molstarAvailable ? '#4CAF50' : '#FFC107'}; 
            margin-left: 8px; display: inline-block;
        `;
        statusIndicator.title = this.molstarAvailable ? 'MolStar已启用' : '演示模式';
        
        const titleContainer = document.createElement('div');
        titleContainer.style.display = 'flex';
        titleContainer.style.alignItems = 'center';
        titleContainer.appendChild(title);
        titleContainer.appendChild(statusIndicator);
        
        const closeBtn = document.createElement('button');
        closeBtn.className = 'custom-3d-viewer-close';
        closeBtn.textContent = '关闭';
        closeBtn.onclick = () => this.hidePanel();
        
        header.appendChild(titleContainer);
        header.appendChild(closeBtn);
        
        // 创建内容容器
        const content = document.createElement('div');
        content.className = 'custom-3d-viewer-content';
        content.id = 'alchem-3d-content';
        content.style.padding = '0'; // 移除padding以便MolStar占满空间
        
        if (this.molstarAvailable) {
            // 创建MolStar查看器容器
            this.viewerContainer = document.createElement('div');
            this.viewerContainer.id = 'alchem-molstar-container';
            this.viewerContainer.style.cssText = `
                width: 100%; 
                height: 100%; 
                background: var(--bg-color, #1a1a1a);
                position: relative;
            `;
            content.appendChild(this.viewerContainer);
            
            // 初始化MolStar查看器
            this.initializeMolstarViewer();
        } else {
            // 使用原有的文本显示模式
            content.style.padding = '16px';
        }
        
        this.panel.appendChild(header);
        this.panel.appendChild(content);
        
        // 添加拖拽缩放边框
        this.resizeController.addResizeBorders(this.panel);
        
        document.body.appendChild(this.panel);
        
        console.log(`🎯 Created ALCHEM 3D overlay panel (${this.molstarAvailable ? 'MolStar模式' : '演示模式'})`);
    }
    
    // 初始化MolStar查看器
    async initializeMolstarViewer() {
        if (!this.molstarAvailable || !window.molstar || !this.viewerContainer) {
            console.warn("🧪 MolStar不可用，无法初始化3D查看器");
            return false;
        }
        
        try {
            console.log("🧪 正在初始化MolStar查看器...");
            
            // 创建MolStar查看器实例
            this.molstarViewer = new MolstarViewer();
            const success = await this.molstarViewer.initialize(this.viewerContainer);
            
            if (!success) {
                this.molstarAvailable = false;
                // 静默失败，不显示错误信息
                console.warn("🧪 MolStar初始化失败，已静默回退");
                return false;
            }
            
            console.log("🧪 MolStar查看器初始化成功");
            return true;
        } catch (error) {
            console.error("🧪 初始化MolStar查看器失败:", error);
            this.molstarAvailable = false;
            // 静默失败，不显示错误信息
            console.warn("🧪 MolStar初始化异常，已静默回退");
            return false;
        }
    }
    
    showPanel(data = null) {
        if (!this.isInitialized) {
            console.warn("⚠️ Panel manager not initialized");
            return;
        }
        
        this.currentData = data;
        this.isVisible = true;
        
        // 更新按钮状态
        if (this.menuButton) {
            this.menuButton.classList.add('active');
        }
        
        // 显示面板
        this.panel.classList.remove('panel-hiding');
        this.panel.classList.add('panel-showing');
        this.panel.style.display = 'block';
        
        // 如果有数据，立即显示
        if (data) {
            this.displayData(data);
        } else {
            this.showWelcome();
        }
        
        console.log("🎯 ALCHEM 3D panel shown");
    }
    
    hidePanel() {
        if (!this.isVisible) return;
        
        this.isVisible = false;
        
        // 更新按钮状态
        if (this.menuButton) {
            this.menuButton.classList.remove('active');
        }
        
        // 隐藏面板
        this.panel.classList.remove('panel-showing');
        this.panel.classList.add('panel-hiding');
        
        // 延迟隐藏，等待动画完成
        setTimeout(() => {
            this.panel.style.display = 'none';
            this.panel.classList.remove('panel-hiding');
        }, 300);
        
        console.log("🎯 ALCHEM 3D panel hidden");
    }
    
    togglePanel() {
        if (this.isVisible) {
            this.hidePanel();
        } else {
            this.showPanel();
        }
    }
    
    // 显示数据
    displayData(htmlContent) {
        if (!this.isInitialized) {
            console.warn("⚠️ Panel manager not initialized");
            return;
        }
        
        const content = document.getElementById('alchem-3d-content');
        if (!content) return;
        
        if (this.molstarAvailable && this.molstarViewer) {
            // MolStar模式 - 直接渲染分子数据
            console.log("🧪 使用MolStar渲染分子数据");
            this.molstarViewer.displayMolecularData(htmlContent);
        } else {
            // 文本模式 - 显示HTML内容
            console.log("🧪 使用文本模式显示数据");
            content.style.padding = '16px';
            content.innerHTML = htmlContent;
        }
        
        this.showPanel();
    }
    
    // 显示欢迎信息
    showWelcome() {
        const content = document.getElementById('alchem-3d-content');
        if (!content) return;
        
        if (this.molstarAvailable) {
            // MolStar模式已在初始化时加载默认分子
            console.log("🧪 MolStar模式 - 默认分子已显示");
        } else {
            content.style.padding = '16px';
            content.innerHTML = this.displayUtils.generateWelcomeHTML(this.molstarAvailable);
        }
    }
    
    // 获取当前显示状态
    isShowing() {
        return this.isVisible;
    }
    
    // 获取MolStar状态
    isMolstarAvailable() {
        return this.molstarAvailable;
    }
    
    // 重置视角（MolStar模式）
    resetView() {
        if (this.molstarViewer) {
            this.molstarViewer.resetView();
        }
    }
    
    // 切换线框模式（MolStar模式）
    toggleWireframe() {
        if (this.molstarViewer) {
            this.molstarViewer.toggleWireframe();
        }
    }
    
    // 清理资源
    destroy() {
        if (this.molstarViewer) {
            this.molstarViewer.destroy();
        }
        
        if (this.resizeController) {
            this.resizeController.destroy();
        }
        
        if (this.displayUtils) {
            this.displayUtils.cleanup();
        }
        
        if (this.panel) {
            this.panel.remove();
        }
        
        if (this.menuButton) {
            this.menuButton.remove();
        }
        
        this.isInitialized = false;
        this.isVisible = false;
        console.log("🧪 ALCHEM 3D Panel Manager destroyed");
    }
}

// =================== 样式应用函数 ===================
export function applyStyles() {
    const styleElement = document.createElement('style');
    styleElement.textContent = display3DStyles;
    document.head.appendChild(styleElement);
    console.log("🎨 Display styles applied");
}

// =================== 向后兼容的导出 ===================
// 保持所有原有的类和函数导出，确保向后兼容
export { ALCHEM3DPanelManager as default };

// 统一错误处理
function handleError(error, context = 'Unknown') {
    console.error(`🧪 ALCHEM UI集成模块错误 [${context}]:`, error);
    
    // 可以在这里添加统一的错误报告逻辑
    if (window.ALCHEM_ERROR_HANDLER) {
        window.ALCHEM_ERROR_HANDLER(error, context);
    }
}

// 统一日志记录
function logInfo(message, data = null) {
    console.log(`🧪 ${message}`, data || '');
    
    // 可以在这里添加统一的日志记录逻辑
    if (window.ALCHEM_LOGGER) {
        window.ALCHEM_LOGGER('info', message, data);
    }
}

// 模块初始化日志
console.log("🧪 ALCHEM UI集成模块已加载 - 包含面板管理、显示工具、拖拽缩放和样式功能");