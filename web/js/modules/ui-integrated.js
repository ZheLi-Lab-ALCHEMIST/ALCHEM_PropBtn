/**
 * ALCHEM UI集成模块 - 合并了面板管理、显示工具、拖拽缩放和样式功能
 * 从以下模块合并而来：
 * - panel-manager.js (面板管理)
 * - display-utils.js (显示工具)
 * - resize-controller.js (拖拽缩放)
 * - display-styles.js (样式定义)
 */

import { loadMolstarLibrary, MolstarViewer } from './molstar-core.js';
// DisplayUtils已删除 - 简化显示逻辑
import { EXTENSION_CONFIG, logger } from '../extensionMain.js';

// =================== 样式管理 ===================

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
        
        // QUIET: logger.debug("🎯 Added 8-direction resize borders to panel");
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
        
        // QUIET: logger.debug(`🎯 Started resizing panel from ${position}`);
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
        
        // QUIET: logger.debug("🎯 Stopped resizing panel");
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
        
        // QUIET: logger.debug(`🎯 Updated resize limits: ${minWidth}x${minHeight} to ${this.maxWidth}x${this.maxHeight}`);
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
        // QUIET: logger.debug("🎯 Resize controller destroyed");
    }
}

// DisplayUtils类已移至独立文件 display-utils.js

// =================== 3D面板管理器 ===================
export class ALCHEM3DPanelManager {
    constructor() {
        this.isVisible = false;
        this.currentData = null;
        this.panel = null;
        this.menuButton = null;
        this.isInitialized = false;
        
        // 🔑 追踪当前显示的节点ID
        this.currentDisplayNodeId = null;
        
        // MolStar相关属性
        this.molstarAvailable = false;
        this.molstarViewer = null;
        this.viewerContainer = null;
        
        // 集成的组件实例
        this.resizeController = new ResizeController();
        // DisplayUtils已删除
    }
    
    async initialize() {
        if (this.isInitialized) return;
        
        // QUIET: logger.debug("🧪 初始化ALCHEM独立MolStar集成...");
        
        // 应用样式
        this.applyStyles();
        
        // 直接加载ALCHEM自己的MolStar库
        this.molstarAvailable = await loadMolstarLibrary();
        
        await this.createMenuButton();
        this.createPanel();
        this.isInitialized = true;
        
        // QUIET: logger.debug(`🚀 ALCHEM 3D Panel Manager initialized (MolStar: ${this.molstarAvailable ? '可用' : '不可用'})`);
        if (this.molstarAvailable) {
            // QUIET: logger.debug("🎉 ALCHEM独立MolStar集成成功！");
        } else {
            // QUIET: logger.debug("⚠️ MolStar加载失败，使用演示模式");
        }
    }
    
    // 应用样式到文档
    applyStyles() {
        const linkElement = document.createElement('link');
        linkElement.rel = 'stylesheet';
        linkElement.type = 'text/css';
        linkElement.href = './extensions/ALCHEM_PropBtn/css/molstar-display.css';
        linkElement.onload = () => {
            // QUIET: logger.debug("🎨 Display styles loaded from CSS file");
        };
        linkElement.onerror = () => {
            logger.error("❌ Failed to load display styles CSS file");
        };
        document.head.appendChild(linkElement);
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
                
                // QUIET: logger.debug("🎯 Added ALCHEM 3D menu button to topbar");
                return;
            }
            
            attempts++;
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        // QUIET: logger.warn("⚠️ Could not find ComfyUI menubar, creating floating button");
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
        
        // QUIET: logger.debug("🎯 Created floating ALCHEM 3D button");
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
        
        // QUIET: logger.debug(`🎯 Created ALCHEM 3D overlay panel (${this.molstarAvailable ? 'MolStar模式' : '演示模式'})`);
    }
    
    // 初始化MolStar查看器
    async initializeMolstarViewer() {
        if (!this.molstarAvailable || !window.molstar || !this.viewerContainer) {
            // QUIET: logger.warn("🧪 MolStar不可用，无法初始化3D查看器");
            return false;
        }
        
        try {
            // QUIET: logger.debug("🧪 正在初始化MolStar查看器...");
            
            // 创建MolStar查看器实例
            this.molstarViewer = new MolstarViewer();
            const success = await this.molstarViewer.initialize(this.viewerContainer);
            
            if (!success) {
                this.molstarAvailable = false;
                // 静默失败，不显示错误信息
                // QUIET: logger.warn("🧪 MolStar初始化失败，已静默回退");
                return false;
            }
            
            // QUIET: logger.debug("🧪 MolStar查看器初始化成功");
            return true;
        } catch (error) {
            logger.error("🧪 初始化MolStar查看器失败:", error);
            this.molstarAvailable = false;
            // 静默失败，不显示错误信息
            // QUIET: logger.warn("🧪 MolStar初始化异常，已静默回退");
            return false;
        }
    }
    
    showPanel(data = null) {
        if (!this.isInitialized) {
            // QUIET: logger.warn("⚠️ Panel manager not initialized");
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
        
        // QUIET: logger.debug("🎯 ALCHEM 3D panel shown");
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
        
        // QUIET: logger.debug("🎯 ALCHEM 3D panel hidden");
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
            // QUIET: logger.warn("⚠️ Panel manager not initialized");
            return;
        }
        
        const content = document.getElementById('alchem-3d-content');
        if (!content) return;
        
        if (this.molstarAvailable && this.molstarViewer) {
            // MolStar模式 - 直接渲染分子数据
            // QUIET: logger.debug("🧪 使用MolStar渲染分子数据");
            this.molstarViewer.displayMolecularData(htmlContent);
        } else {
            // 文本模式 - 显示HTML内容
            // QUIET: logger.debug("🧪 使用文本模式显示数据");
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
            // QUIET: logger.debug("🧪 MolStar模式 - 默认分子已显示");
        } else {
            content.style.padding = '16px';
            content.innerHTML = `<div style="text-align: center; padding: 40px; color: #ccc;">
                <h2>🧪 ALCHEM 3D分子显示器</h2>
                <p>上传分子文件并执行节点后，3D结构将在此处显示。</p>
            </div>`;
        }
    }
    
    // 获取当前显示状态
    isShowing() {
        return this.isVisible;
    }
    
    // 🔑 设置当前显示的节点ID
    setCurrentDisplayNodeId(nodeId) {
        this.currentDisplayNodeId = nodeId;
        console.log(`[DEBUG] setCurrentDisplayNodeId:`);
        console.log(`  - 设置的节点ID: '${nodeId}'`);
        console.log(`  - 节点ID类型: ${typeof nodeId}`);
        console.log(`  - 之前的节点ID: '${this.currentDisplayNodeId || 'none'}'`);
    }
    
    // 🔑 获取当前显示的节点ID  
    getCurrentDisplayNodeId() {
        console.log(`[DEBUG] getCurrentDisplayNodeId:`);
        console.log(`  - 返回的节点ID: '${this.currentDisplayNodeId}'`);
        console.log(`  - 节点ID类型: ${typeof this.currentDisplayNodeId}`);
        return this.currentDisplayNodeId;
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
        
        // DisplayUtils清理已删除
        
        if (this.panel) {
            this.panel.remove();
        }
        
        if (this.menuButton) {
            this.menuButton.remove();
        }
        
        this.isInitialized = false;
        this.isVisible = false;
        // QUIET: logger.debug("🧪 ALCHEM 3D Panel Manager destroyed");
    }
}

// =================== 样式应用函数 ===================
export function applyStyles() {
    const linkElement = document.createElement('link');
    linkElement.rel = 'stylesheet';
    linkElement.type = 'text/css';
    linkElement.href = './extensions/ALCHEM_PropBtn/css/molstar-display.css';
    linkElement.onload = () => {
        // QUIET: logger.debug("🎨 Display styles loaded from CSS file");
    };
    linkElement.onerror = () => {
        logger.error("❌ Failed to load display styles CSS file");
    };
    document.head.appendChild(linkElement);
}

// =================== 向后兼容的导出 ===================
// 保持所有原有的类和函数导出，确保向后兼容
export { ALCHEM3DPanelManager as default };

// 统一错误处理
function handleError(error, context = 'Unknown') {
    logger.error(`🧪 ALCHEM UI集成模块错误 [${context}]:`, error);
    
    // 可以在这里添加统一的错误报告逻辑
    if (window.ALCHEM_ERROR_HANDLER) {
        window.ALCHEM_ERROR_HANDLER(error, context);
    }
}

// 统一日志记录
function logInfo(message, data = null) {
    // QUIET: logger.debug(`🧪 ${message}`, data || '');
    
    // 可以在这里添加统一的日志记录逻辑
    if (window.ALCHEM_LOGGER) {
        window.ALCHEM_LOGGER('info', message, data);
    }
}

// 模块初始化日志
// QUIET: logger.debug("🧪 ALCHEM UI集成模块已加载 - 包含面板管理、显示工具、拖拽缩放和样式功能");