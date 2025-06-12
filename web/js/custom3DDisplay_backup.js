import { app } from "../../../scripts/app.js";

// ComfyUI原生风格的3D显示样式
const display3DStyles = `
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

/* ComfyUI原生风格菜单栏按钮 */
.alchem-menu-button {
    background: var(--comfy-input-bg, #2a2a2a);
    border: 1px solid var(--border-color, #444);
    border-radius: 4px;
    color: var(--fg-color, #ccc);
    padding: 6px 12px;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    margin: 0 2px;
    font-family: inherit;
    display: flex;
    align-items: center;
    gap: 4px;
    white-space: nowrap;
}

.alchem-menu-button:hover {
    background: var(--comfy-input-bg-hover, #333);
    border-color: var(--primary-color, #007bff);
}

.alchem-menu-button:active {
    background: var(--comfy-input-bg-active, #3a3a3a);
}

.alchem-menu-button.active {
    background: var(--primary-color, #007bff);
    color: white;
    border-color: var(--primary-color, #007bff);
}

.alchem-menu-button.active:hover {
    background: var(--primary-color-hover, #0056b3);
}

/* 面板显示动画 */
.custom-3d-viewer.panel-showing {
    animation: slideDown 0.2s ease-out;
}

.custom-3d-viewer.panel-hiding {
    animation: slideUp 0.2s ease-in;
}

/* 🎯 新增：拖动边框样式 */
.resize-border {
    z-index: 1000;
}

.resize-border:hover {
    background: rgba(76, 175, 80, 0.2) !important;
}

.resize-bottom-left {
    border-radius: 4px;
}

.resize-bottom-left:hover {
    background: rgba(76, 175, 80, 0.5) !important;
    box-shadow: 0 0 4px rgba(76, 175, 80, 0.8);
}

@keyframes slideDown {
    from {
        transform: translateY(-100%);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

@keyframes slideUp {
    from {
        transform: translateY(0);
        opacity: 1;
    }
    to {
        transform: translateY(-100%);
        opacity: 0;
    }
}

/* 内容区域样式 */
.custom-3d-viewer-content h3 {
    color: var(--fg-color, #ccc);
    margin: 0 0 8px 0;
    font-size: 16px;
    font-weight: 500;
}

.custom-3d-viewer-content h4 {
    color: var(--fg-color, #ccc);
    margin: 16px 0 8px 0;
    font-size: 14px;
    font-weight: 500;
}

.custom-3d-viewer-content .info-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    padding: 12px;
    background: var(--comfy-input-bg, #2a2a2a);
    border: 1px solid var(--border-color, #444);
    border-radius: 4px;
    margin: 8px 0;
}

.custom-3d-viewer-content .info-panel {
    padding: 12px;
    background: var(--comfy-input-bg, #2a2a2a);
    border: 1px solid var(--border-color, #444);
    border-radius: 4px;
    margin: 8px 0;
}

.custom-3d-viewer-content .control-panel {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin: 8px 0;
}

.custom-3d-viewer-content .control-button {
    background: var(--comfy-input-bg, #2a2a2a);
    border: 1px solid var(--border-color, #444);
    color: var(--fg-color, #ccc);
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    transition: all 0.2s ease;
}

.custom-3d-viewer-content .control-button:hover {
    background: var(--comfy-input-bg-hover, #333);
    border-color: var(--primary-color, #007bff);
}

.custom-3d-viewer-content pre {
    background: var(--comfy-input-bg, #2a2a2a);
    border: 1px solid var(--border-color, #444);
    padding: 12px;
    border-radius: 4px;
    overflow-x: auto;
    font-family: 'Courier New', monospace;
    font-size: 11px;
    line-height: 1.4;
    color: var(--fg-color, #ccc);
    margin: 8px 0;
}

.custom-3d-viewer-content .status-info {
    padding: 12px;
    background: var(--comfy-input-bg, #2a2a2a);
    border: 1px solid var(--border-color, #444);
    border-radius: 4px;
    margin: 8px 0;
    font-size: 12px;
}

.custom-3d-viewer-content .welcome-message {
    text-align: center;
    padding: 40px 20px;
}

.custom-3d-viewer-content .feature-list {
    text-align: left;
    margin: 16px 0;
}

.custom-3d-viewer-content .feature-list ul {
    margin: 0;
    padding-left: 20px;
}

.custom-3d-viewer-content .feature-list li {
    margin: 4px 0;
    color: var(--fg-color, #ccc);
}
`;

// MolStar库加载函数 - ALCHEM独立版本
async function loadMolstarLibrary() {
    return new Promise((resolve) => {
        // 检查是否已加载
        if (window.molstar) {
            console.log("🧪 MolStar库已存在");
            resolve(true);
            return;
        }
        
        console.log("🧪 正在加载ALCHEM集成的MolStar库...");
        
        // 从ALCHEM自己的lib目录加载
        const molstarCSSPath = "./extensions/ALCHEM_PropBtn/lib/molstar.css";
        const molstarJSPath = "./extensions/ALCHEM_PropBtn/lib/molstar.js";
        
        // 加载CSS
        const link = document.createElement("link");
        link.rel = "stylesheet";
        link.href = molstarCSSPath;
        document.head.appendChild(link);
        console.log("🧪 加载MolStar CSS:", molstarCSSPath);
        
        // 加载JS
        const script = document.createElement("script");
        script.src = molstarJSPath;
        script.onload = () => {
            console.log("🧪 ALCHEM MolStar库加载完成！");
            console.log("🧪 window.molstar可用:", !!window.molstar);
            resolve(true);
        };
        script.onerror = (error) => {
            console.error("🧪 ALCHEM MolStar库加载失败:", error);
            console.log("🧪 回退到演示模式");
            resolve(false);
        };
        document.head.appendChild(script);
        console.log("🧪 开始加载MolStar JS:", molstarJSPath);
    });
}

// 全局面板管理器
class ALCHEM3DPanelManager {
    constructor() {
        this.isVisible = false;
        this.currentData = null;
        this.panel = null;
        this.menuButton = null;
        this.isInitialized = false;
        
        // MolStar相关属性
        this.molstarAvailable = false;
        this.molstarPlugin = null;
        this.molstarContainer = null;
        this.viewerContainer = null;
    }
    
    async initialize() {
        if (this.isInitialized) return;
        
        console.log("🧪 初始化ALCHEM独立MolStar集成...");
        
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
        
        // 🎯 新增：添加可拖动的边框用于调整面板大小
        this.addResizeBorders(this.panel);
        
        document.body.appendChild(this.panel);
        
        console.log(`🎯 Created ALCHEM 3D overlay panel (${this.molstarAvailable ? 'MolStar模式' : '演示模式'})`);
    }
    
    // 🎯 新增：添加可拖动边框用于调整面板大小
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
            borderElement.className = `resize-border resize-${border.position}`;
            borderElement.style.cssText = this.getResizeBorderStyles(border.position, border.cursor);
            
            // 添加鼠标按下事件
            borderElement.addEventListener('mousedown', (e) => {
                this.startResize(e, border.position, panel);
            });
            
            panel.appendChild(borderElement);
        });
    }
    
    // 获取拖动边框的样式
    getResizeBorderStyles(position, cursor) {
        const base = `
            position: absolute;
            cursor: ${cursor};
            background: transparent;
            transition: background 0.2s ease;
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
        
        const startX = e.clientX;
        const startY = e.clientY;
        const startWidth = parseInt(window.getComputedStyle(panel).width, 10);
        const startHeight = parseInt(window.getComputedStyle(panel).height, 10);
        const startLeft = parseInt(window.getComputedStyle(panel).left, 10);
        const startTop = parseInt(window.getComputedStyle(panel).top, 10);
        
        // 添加全局鼠标事件
        const onMouseMove = (e) => {
            this.doResize(e, position, panel, {
                startX, startY, startWidth, startHeight, startLeft, startTop
            });
        };
        
        const onMouseUp = () => {
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
        };
        
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
        document.body.style.cursor = this.getCursorForPosition(position);
        document.body.style.userSelect = 'none';
    }
    
    // 执行拖动调整
    doResize(e, position, panel, startValues) {
        const { startX, startY, startWidth, startHeight, startLeft, startTop } = startValues;
        const deltaX = e.clientX - startX;
        const deltaY = e.clientY - startY;
        
        // 最小尺寸限制
        const minWidth = 300;
        const minHeight = 200;
        
        // 最大尺寸限制（屏幕大小）
        const maxWidth = window.innerWidth - 50;
        const maxHeight = window.innerHeight - 50;
        
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
        panel.style.width = newWidth + 'px';
        panel.style.height = newHeight + 'px';
        panel.style.left = newLeft + 'px';
        panel.style.top = newTop + 'px';
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
    
    // 初始化MolStar查看器
    async initializeMolstarViewer() {
        if (!this.molstarAvailable || !window.molstar || !this.viewerContainer) {
            console.warn("🧪 MolStar不可用，无法初始化3D查看器");
            return false;
        }
        
        try {
            console.log("🧪 正在初始化MolStar查看器...");
            
            // 创建MolStar查看器实例
            const viewer = await window.molstar.Viewer.create(this.viewerContainer, {
                layoutIsExpanded: false,
                layoutShowControls: true,
                layoutShowRemoteState: false,
                layoutShowSequence: false,
                layoutShowLog: false,
                layoutShowLeftPanel: false,
                viewportShowExpand: false,
                viewportShowSelectionMode: false,
                viewportShowAnimation: false,
                preset: { id: 'molstar-dark', params: {} } // 使用暗色主题
            });
            
            this.molstarPlugin = viewer.plugin;
            console.log("🧪 MolStar查看器初始化成功");
            
            // 加载默认分子
            this.loadDefaultMolecule();
            
            return true;
        } catch (error) {
            console.error("🧪 初始化MolStar查看器失败:", error);
            this.molstarAvailable = false;
            // 回退到文本模式
            this.viewerContainer.innerHTML = `
                <div style="padding: 20px; text-align: center; color: var(--fg-color, #ccc);">
                    <h3>MolStar初始化失败</h3>
                    <p>将使用简化显示模式</p>
                    <p style="font-size: 12px; opacity: 0.7;">错误: ${error.message}</p>
                </div>
            `;
            return false;
        }
    }
    
    // 加载默认分子
    async loadDefaultMolecule() {
        if (!this.molstarPlugin) return;
        
        try {
            const defaultPDB = `HEADER    BENZENE MOLECULE
COMPND    BENZENE  
ATOM      1  C1  BNZ A   1       0.000   1.400   0.000  1.00  0.00           C
ATOM      2  C2  BNZ A   1       1.212   0.700   0.000  1.00  0.00           C
ATOM      3  C3  BNZ A   1       1.212  -0.700   0.000  1.00  0.00           C
ATOM      4  C4  BNZ A   1       0.000  -1.400   0.000  1.00  0.00           C
ATOM      5  C5  BNZ A   1      -1.212  -0.700   0.000  1.00  0.00           C
ATOM      6  C6  BNZ A   1      -1.212   0.700   0.000  1.00  0.00           C
CONECT    1    2    6
CONECT    2    1    3
CONECT    3    2    4
CONECT    4    3    5
CONECT    5    4    6
CONECT    6    1    5
END`;
            
            await this.molstarPlugin.clear();
            
            const dataObj = await this.molstarPlugin.builders.data.rawData({
                data: defaultPDB,
                label: 'benzene_default'
            });
            
            const trajectory = await this.molstarPlugin.builders.structure.parseTrajectory(dataObj, 'pdb');
            await this.molstarPlugin.builders.structure.hierarchy.applyPreset(trajectory, 'default');
            
            console.log("🧪 默认分子(苯环)加载成功");
        } catch (error) {
            console.warn("🧪 加载默认分子失败:", error);
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
    
    displayData(data) {
        const content = document.getElementById('alchem-3d-content');
        if (!content) return;
        
        if (this.molstarAvailable && this.molstarPlugin) {
            // MolStar模式：尝试解析并渲染3D分子
            this.displayMolecularData3D(data);
        } else {
            // 演示模式：显示HTML内容
            content.innerHTML = data;
        }
    }
    
    // 在MolStar中显示分子数据 - 支持直接PDB数据和HTML数据
    async displayMolecularData3D(molecularContent, analysis = null) {
        if (!this.molstarPlugin || !this.viewerContainer) {
            console.warn("🧪 MolStar插件未初始化");
            return;
        }
        
        try {
            let pdbData = null;
            let molecularInfo = null;
            
            // 🔧 关键修复：智能检测数据类型
            if (typeof molecularContent === 'string') {
                // 检查是否是直接的PDB数据（包含HEADER、ATOM等关键字）
                if (molecularContent.includes('HEADER') || molecularContent.includes('ATOM') || molecularContent.includes('HETATM')) {
                    // 直接PDB数据
                    console.log("🧪 检测到直接PDB数据");
                    pdbData = molecularContent;
                    molecularInfo = {
                        pdbData: pdbData,
                        title: analysis?.title || analysis?.filename || 'molecule',
                        originalContent: molecularContent
                    };
                } else {
                    // HTML数据，需要提取
                    console.log("🧪 检测到HTML数据，正在提取PDB信息");
                    molecularInfo = this.extractMolecularInfo(molecularContent);
                    pdbData = molecularInfo?.pdbData;
                }
            } else {
                console.warn("🧪 无效的分子数据格式");
                return;
            }
            
            if (pdbData && pdbData.trim()) {
                console.log("🧪 在MolStar中渲染分子数据...");
                
                // 清除当前显示
                await this.molstarPlugin.clear();
                
                // 创建数据对象
                const dataObj = await this.molstarPlugin.builders.data.rawData({
                    data: pdbData,
                    label: molecularInfo.title || 'molecule'
                });
                
                // 解析轨迹
                const trajectory = await this.molstarPlugin.builders.structure.parseTrajectory(dataObj, 'pdb');
                
                // 应用预设
                await this.molstarPlugin.builders.structure.hierarchy.applyPreset(trajectory, 'default');
                
                console.log("🧪 分子在MolStar中渲染成功");
                
                // 🔧 用户要求：不显示信息叠加层，避免挡住MolStar界面
                // this.showMolecularInfo(molecularInfo, analysis);
                
            } else {
                console.warn("🧪 无法提取PDB数据，显示原始内容");
                // 回退到文本显示
                this.viewerContainer.style.padding = '16px';
                this.viewerContainer.innerHTML = typeof molecularContent === 'string' ? molecularContent : '无效数据';
            }
            
        } catch (error) {
            console.error("🧪 MolStar渲染失败:", error);
            // 显示错误信息
            this.showErrorInViewer(`渲染失败: ${error.message}`);
        }
    }
    
    // 从HTML数据中提取分子信息
    extractMolecularInfo(htmlData) {
        try {
            // 创建临时DOM解析HTML
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = htmlData;
            
            // 查找PDB数据
            const preElements = tempDiv.querySelectorAll('pre');
            let pdbData = null;
            let title = '分子结构';
            
            for (const pre of preElements) {
                const content = pre.textContent;
                if (content.includes('HEADER') || content.includes('ATOM') || content.includes('HETATM')) {
                    pdbData = content;
                    break;
                }
            }
            
            // 查找标题
            const h3Elements = tempDiv.querySelectorAll('h3');
            if (h3Elements.length > 0) {
                title = h3Elements[0].textContent.replace('正在显示: ', '').replace('🧪', '').trim();
            }
            
            return {
                pdbData: pdbData,
                title: title,
                originalHtml: htmlData
            };
            
        } catch (error) {
            console.warn("🧪 解析分子信息失败:", error);
            return null;
        }
    }
    
    // 显示分子信息面板（叠加在MolStar之上）
    showMolecularInfo(molecularInfo, analysis = null) {
        // 创建信息叠加层
        const infoOverlay = document.createElement('div');
        infoOverlay.id = 'molstar-info-overlay';
        infoOverlay.style.cssText = `
            position: absolute;
            top: 10px;
            right: 10px;
            width: 300px;
            max-height: 200px;
            background: rgba(0, 0, 0, 0.8);
            color: var(--fg-color, #ccc);
            padding: 12px;
            border-radius: 6px;
            border: 1px solid var(--border-color, #444);
            font-size: 12px;
            overflow-y: auto;
            z-index: 100;
            backdrop-filter: blur(4px);
        `;
        
        // 🔧 改进：使用analysis信息增强显示内容
        const title = analysis?.title || molecularInfo.title || 'molecule';
        const dataSource = analysis?.is_backend ? '后端内存' : 
                          analysis?.stored_in_memory ? '前端内存' : '文件系统';
        const atomCount = analysis?.atoms || 'N/A';
        const format = analysis?.format || analysis?.format_name || 'Unknown';
        
        infoOverlay.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <strong>${title}</strong>
                <button onclick="this.parentElement.parentElement.remove()" 
                        style="background: none; border: none; color: #ccc; cursor: pointer; font-size: 16px;">×</button>
            </div>
            <div style="font-size: 11px; opacity: 0.8;">
                🧪 ALCHEM独立MolStar 3D渲染<br>
                💾 数据来源: ${dataSource}<br>
                🔬 格式: ${format} | 原子数: ${atomCount}<br>
                🎯 可拖拽旋转视角，滚轮缩放
            </div>
            <div style="margin-top: 8px; display: flex; gap: 4px; flex-wrap: wrap;">
                <button onclick="alchem3DManager.resetView()" style="padding: 2px 6px; font-size: 10px; background: var(--comfy-input-bg, #2a2a2a); border: 1px solid var(--border-color, #444); color: var(--fg-color, #ccc); border-radius: 3px; cursor: pointer;">重置视角</button>
                <button onclick="alchem3DManager.toggleWireframe()" style="padding: 2px 6px; font-size: 10px; background: var(--comfy-input-bg, #2a2a2a); border: 1px solid var(--border-color, #444); color: var(--fg-color, #ccc); border-radius: 3px; cursor: pointer;">线框模式</button>
            </div>
        `;
        
        // 移除已有的信息叠加层
        const existingOverlay = this.viewerContainer.querySelector('#molstar-info-overlay');
        if (existingOverlay) {
            existingOverlay.remove();
        }
        
        this.viewerContainer.appendChild(infoOverlay);
    }
    
    // 在查看器中显示错误
    showErrorInViewer(errorMessage) {
        if (this.viewerContainer) {
            this.viewerContainer.innerHTML = `
                <div style="padding: 20px; text-align: center; color: var(--fg-color, #ccc);">
                    <h3>🧪 MolStar渲染出错</h3>
                    <p>${errorMessage}</p>
                    <p style="font-size: 12px; opacity: 0.7;">将回退到简化显示模式</p>
                </div>
            `;
        }
    }
    
    showWelcome() {
        // 🔧 用户要求：删除所有欢迎信息和说明，保持MolStar界面完全干净
        // 不显示任何欢迎信息，让用户直接看到纯净的3D界面
        console.log("🧪 跳过欢迎信息显示，保持界面干净");
    }
    
    // 重置视角
    resetView() {
        if (this.molstarPlugin && this.molstarPlugin.canvas3d) {
            try {
                this.molstarPlugin.canvas3d.requestCameraReset();
                console.log("🧪 视角已重置");
            } catch (error) {
                console.warn("🧪 重置视角失败:", error);
            }
        }
    }
    
    // 切换线框模式（简化实现）
    toggleWireframe() {
        if (this.molstarPlugin) {
            try {
                // 这是一个简化的实现，真实的线框切换需要更复杂的逻辑
                console.log("🧪 线框模式切换（功能待完善）");
                // 在实际应用中，这里需要访问MolStar的representation系统
            } catch (error) {
                console.warn("🧪 切换线框模式失败:", error);
            }
        }
    }
}

// 创建全局面板管理器实例
const alchem3DManager = new ALCHEM3DPanelManager();

// 检测3D显示属性的函数
export const isMolstar3DDisplayInput = (inputSpec) => {
    const [inputName, inputOptions] = inputSpec;
    if (!inputOptions) return false;
    
    return !!(inputOptions['molstar_3d_display']);
};

// 创建3D显示输入定义
export const createMolstar3DDisplayInput = (inputName, inputSpec) => [
    'MOLSTAR3DDISPLAY',
    {
        ...inputSpec[1],
        originalInputName: inputName,
        displayType: '3d_molecular'
    }
];

// 辅助函数：获取分子式
const getMolecularFormula = (molecule) => {
    const formulas = {
        'benzene': 'C₆H₆',
        'water': 'H₂O',
        'caffeine': 'C₈H₁₀N₄O₂',
        'aspirin': 'C₉H₈O₄'
    };
    return formulas[molecule] || 'Unknown';
};

// 辅助函数：获取分子量
const getMolecularWeight = (molecule) => {
    const weights = {
        'benzene': '78.11 g/mol',
        'water': '18.02 g/mol',
        'caffeine': '194.19 g/mol',
        'aspirin': '180.16 g/mol'
    };
    return weights[molecule] || 'Unknown';
};

// 辅助函数：获取PDB数据
const getPDBData = (molecule) => {
    const pdbData = {
        'benzene': `HEADER    BENZENE MOLECULE
COMPND    BENZENE
ATOM      1  C1  BNZ A   1       0.000   1.400   0.000  1.00  0.00           C
ATOM      2  C2  BNZ A   1       1.212   0.700   0.000  1.00  0.00           C
ATOM      3  C3  BNZ A   1       1.212  -0.700   0.000  1.00  0.00           C
ATOM      4  C4  BNZ A   1       0.000  -1.400   0.000  1.00  0.00           C
ATOM      5  C5  BNZ A   1      -1.212  -0.700   0.000  1.00  0.00           C
ATOM      6  C6  BNZ A   1      -1.212   0.700   0.000  1.00  0.00           C
END`,
        'water': `HEADER    WATER MOLECULE
COMPND    WATER
ATOM      1  O   HOH A   1       0.000   0.000   0.000  1.00  0.00           O
ATOM      2  H1  HOH A   1       0.757   0.586   0.000  1.00  0.00           H
ATOM      3  H2  HOH A   1      -0.757   0.586   0.000  1.00  0.00           H
END`,
        'caffeine': `HEADER    CAFFEINE MOLECULE
COMPND    CAFFEINE
ATOM      1  N1  CAF A   1      -1.234   0.000   0.000  1.00  0.00           N
ATOM      2  C2  CAF A   1      -0.617   1.234   0.000  1.00  0.00           C
ATOM      3  N3  CAF A   1       0.617   1.234   0.000  1.00  0.00           N
END`,
        'aspirin': `HEADER    ASPIRIN MOLECULE
COMPND    ASPIRIN
ATOM      1  C1  ASP A   1       0.000   0.000   0.000  1.00  0.00           C
ATOM      2  C2  ASP A   1       1.200   0.693   0.000  1.00  0.00           C
ATOM      3  C3  ASP A   1       1.200   2.079   0.000  1.00  0.00           C
END`
    };
    return pdbData[molecule] || 'No PDB data available';
};

// 简化的查看器选择函数
const tryUseExistingMolStarViewer = async (node, inputName) => {
    // ALCHEM现在独立运行，不再依赖rdkit_molstar
    // 只有当用户明确希望使用rdkit_molstar时才尝试
    if (typeof window !== 'undefined' && window.globalViewer && 
        window.globalViewer.isInitialized && 
        typeof node.showInGlobalViewer === 'function') {
        
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
    return false; // 让ALCHEM处理
};

// 读取用户上传的分子文件内容
const readMolecularFileContent = async (filename) => {
    try {
        // 构建文件URL - ComfyUI的静态文件访问方式
        const fileUrl = `/view?filename=${encodeURIComponent(filename)}&type=input`;
        
        console.log(`🧪 Attempting to read molecular file: ${fileUrl}`);
        
        const response = await fetch(fileUrl);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const content = await response.text();
        console.log(`🧪 Successfully read ${content.length} characters from ${filename}`);
        
        return content;
    } catch (error) {
        console.error(`🧪 Failed to read molecular file ${filename}:`, error);
        throw error;
    }
};

// 🌟 新增：从后端内存获取分子数据的函数
const fetchMolecularDataFromBackend = async (nodeId) => {
    try {
        console.log(`🚀 Fetching molecular data for node: ${nodeId}`);
        
        // 构建请求URL - 使用ComfyUI的API路由
        const apiUrl = '/alchem_propbtn/api/molecular';
        
        // 发送POST请求到后端API
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                request_type: 'get_molecular_data',
                node_id: nodeId
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status} - ${response.statusText}`);
        }
        
        const responseData = await response.json();
        console.log(`📡 Backend API response:`, responseData);
        
        if (responseData.success) {
            console.log(`✅ Successfully retrieved molecular data from backend`);
            console.log(`   - Node ID: ${responseData.data.node_id}`);
            console.log(`   - Filename: ${responseData.data.filename}`);
            console.log(`   - Format: ${responseData.data.format_name}`);
            console.log(`   - Atoms: ${responseData.data.atoms}`);
            console.log(`   - Access count: ${responseData.data.access_count}`);
            
            return responseData;
        } else {
            console.warn(`⚠️ Backend returned error: ${responseData.error}`);
            return responseData;
        }
        
    } catch (error) {
        console.error('🚨 Error fetching molecular data from backend:', error);
        return {
            success: false,
            error: `Network error: ${error.message}`,
            data: null
        };
    }
};

// 🌟 新增：获取后端缓存状态的函数
const fetchCacheStatusFromBackend = async () => {
    try {
        const response = await fetch('/alchem_propbtn/api/molecular', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                request_type: 'get_cache_status'
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const responseData = await response.json();
        console.log(`📊 Cache status:`, responseData);
        
        return responseData;
        
    } catch (error) {
        console.error('🚨 Error fetching cache status:', error);
        return {
            success: false,
            error: error.message,
            data: null
        };
    }
};

// 分析分子文件内容并提取信息
const analyzeMolecularContent = (content, filename) => {
    const extension = filename.split('.').pop().toLowerCase();
    const lines = content.split('\n');
    
    let analysis = {
        filename: filename,
        format: extension.toUpperCase(),
        lines: lines.length,
        atoms: 0,
        bonds: 0,
        title: 'Unknown',
        formula: 'Unknown'
    };
    
    try {
        switch (extension) {
            case 'pdb':
                analysis.title = lines.find(line => line.startsWith('TITLE'))?.substring(6).trim() || 'PDB Structure';
                analysis.atoms = lines.filter(line => line.startsWith('ATOM') || line.startsWith('HETATM')).length;
                analysis.format = 'Protein Data Bank (PDB)';
                break;
                
            case 'mol':
                if (lines.length >= 4) {
                    analysis.title = lines[0].trim() || 'MOL Structure';
                    const countsLine = lines[3];
                    analysis.atoms = parseInt(countsLine.substr(0, 3)) || 0;
                    analysis.bonds = parseInt(countsLine.substr(3, 3)) || 0;
                    analysis.format = 'MDL Molfile (MOL)';
                }
                break;
                
            case 'xyz':
                if (lines.length >= 2) {
                    analysis.atoms = parseInt(lines[0]) || 0;
                    analysis.title = lines[1].trim() || 'XYZ Structure';
                    analysis.format = 'XYZ Coordinates';
                }
                break;
                
            case 'sdf':
                analysis.format = 'Structure Data File (SDF)';
                analysis.title = lines[0]?.trim() || 'SDF Structure';
                // SDF可能包含多个分子块
                const molBlocks = content.split('$$$$').length - 1;
                analysis.molecules = molBlocks;
                break;
                
            default:
                analysis.format = `${extension.toUpperCase()} format`;
                analysis.title = filename;
        }
    } catch (error) {
        console.warn('🧪 Error analyzing molecular content:', error);
    }
    
    return analysis;
};

// 模拟3D显示功能
export const show3DMolecularView = async (node, inputName) => {
    // 确保面板管理器已初始化
    if (!alchem3DManager.isInitialized) {
        await alchem3DManager.initialize();
    }
    
    try {
        // 首先尝试使用现有的MolStar查看器
        const usedExisting = await tryUseExistingMolStarViewer(node, inputName);
        if (usedExisting) {
            console.log("🎯 Successfully used existing MolStar viewer");
            return;
        }
        
        console.log("🎯 Using ALCHEM overlay panel display");
        
        // 🎯 关键优化：从后端内存读取分子数据
        const molInput = node.widgets.find(w => w.name === inputName);
        const selectedFile = molInput ? molInput.value : 'benzene';
        
        console.log(`🧪 Checking backend memory for molecular data: ${inputName}`);
        console.log(`🧪 Node ID: ${node.id}, Selected file: ${selectedFile}`);
        
        // 🔧 关键修复：获取正确的节点ID
        // ComfyUI在不同tab中可能给节点分配相同的node.id，但每个节点实例有唯一的标识
        let nodeId = node.id;
        
        // 检查是否有ComfyUI的唯一标识符
        if (node.graph && node.graph.runningContext && node.graph.runningContext.unique_id) {
            nodeId = node.graph.runningContext.unique_id;
            console.log(`🔧 Using ComfyUI unique_id: ${nodeId}`);
        } else if (node._id) {
            nodeId = node._id;
            console.log(`🔧 Using node._id: ${nodeId}`);
        } else {
            // 使用节点的内存地址或其他唯一标识
            if (!node._uniqueDisplayId) {
                node._uniqueDisplayId = `${node.id}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            }
            nodeId = node._uniqueDisplayId;
            console.log(`🔧 Generated unique display ID: ${nodeId}`);
        }
        
        // 🌟 步骤1：尝试从后端内存获取分子数据
        let molecularData = null;
        let backendData = null;
        
        try {
            // 🚀 关键修复：根据文件名查找数据，避免节点ID冲突
            console.log(`🧪 Attempting to fetch from backend memory using nodeId: ${nodeId}...`);
            backendData = await fetchMolecularDataFromBackend(nodeId);
            
            if (backendData && backendData.success) {
                molecularData = backendData.data;
                console.log(`🚀 Successfully fetched molecular data from backend memory:`, molecularData);
                console.log(`   - Filename: ${molecularData.filename}`);
                console.log(`   - Format: ${molecularData.format_name}`);
                console.log(`   - Atoms: ${molecularData.atoms}`);
                console.log(`   - Cached at: ${new Date(molecularData.cached_at * 1000).toLocaleString()}`);
            } else {
                console.log(`⚠️ No data for node ${nodeId}, trying filename-based lookup...`);
                
                // 🔧 备选方案：根据文件名查找数据（解决节点ID冲突）
                if (selectedFile && selectedFile !== 'benzene') {
                    console.log(`🔍 Searching for molecular data by filename: ${selectedFile}`);
                    
                    // 获取缓存状态，查找匹配的文件
                    const cacheStatus = await fetchCacheStatusFromBackend();
                    if (cacheStatus && cacheStatus.success && cacheStatus.data.nodes) {
                        for (const cachedNode of cacheStatus.data.nodes) {
                            if (cachedNode.filename === selectedFile) {
                                console.log(`🎯 Found matching file in cache: ${selectedFile} (node: ${cachedNode.node_id})`);
                                // 使用找到的节点ID重新获取数据
                                backendData = await fetchMolecularDataFromBackend(cachedNode.node_id);
                                if (backendData && backendData.success) {
                                    molecularData = backendData.data;
                                    console.log(`✅ Retrieved data by filename: ${molecularData.filename}`);
                                }
                                break;
                            }
                        }
                    }
                }
            }
        } catch (error) {
            console.warn(`🚨 Failed to fetch from backend memory:`, error);
        }
        
        // 🔄 步骤2：回退到前端内存（兼容性）
        if (!molecularData && node.molecularData && node.molecularData[inputName]) {
            molecularData = node.molecularData[inputName];
            console.log(`🧪 Found molecular data in frontend node memory:`, molecularData);
        }
        
        // 显示加载状态 - 使用新的面板管理器
        const content = document.getElementById('alchem-3d-content');
        if (!content) {
            console.error("🚨 Panel content not found, initializing...");
            await alchem3DManager.initialize();
            return;
        }
        
        // 显示面板
        alchem3DManager.showPanel();
        
        // 🔧 修复：对于MolStar模式，不显示任何加载界面，直接处理数据
        if (alchem3DManager.molstarAvailable) {
            console.log("🧪 MolStar模式：直接处理分子数据，跳过加载界面");
            // 不显示任何HTML内容，直接进入数据处理阶段
        } else {
            // 只在演示模式下显示加载状态
            content.innerHTML = `
                <div style="text-align: center; margin-bottom: 20px;">
                    <h3 style="color: #4fc3f7; margin-bottom: 10px;">🔄 正在加载分子文件...</h3>
                    <p style="color: #999;">文件: ${selectedFile}</p>
                    <div style="background: #333; height: 4px; border-radius: 2px; overflow: hidden; margin: 20px 0;">
                        <div style="background: linear-gradient(45deg, #4fc3f7, #81c784); height: 100%; width: 0%; transition: width 0.3s;" id="loading-progress"></div>
                    </div>
                </div>
            `;
        }
        
        // 更新进度（仅演示模式）
        const progressBar = document.getElementById('loading-progress');
        if (progressBar) progressBar.style.width = '30%';
        
        let molecularContent = '';
        let analysis = {};
        let fromMemory = false;
        
        if (molecularData && (molecularData.content || molecularData.isLoaded)) {
            // 🎯 使用后端内存或前端内存中的数据
            console.log(`🧪 Using molecular data from memory`);
            
            // 判断数据来源
            if (molecularData.node_id) {
                // 来自后端内存
                console.log(`🚀 Using backend memory data`);
                molecularContent = molecularData.content;
                analysis = {
                    filename: molecularData.filename,
                    format: molecularData.format,
                    format_name: molecularData.format_name,
                    title: molecularData.metadata?.title || molecularData.filename,
                    atoms: molecularData.atoms,
                    bonds: molecularData.bonds,
                    lines: molecularData.file_stats?.lines || 0,
                    cached_at: molecularData.cached_at,
                    access_count: molecularData.access_count,
                    is_backend: true
                };
                fromMemory = 'backend';
            } else {
                // 来自前端内存
                console.log(`🧪 Using frontend memory data`);
                molecularContent = molecularData.content;
                analysis = molecularData.analysis;
                fromMemory = 'frontend';
            }
            
            if (progressBar) progressBar.style.width = '100%';
            
        } else {
            // 🎯 回退到文件读取模式（兼容性）
            console.log(`🧪 No molecular data in node memory, falling back to file reading mode`);
            
            try {
                // 尝试读取用户上传的文件
                if (progressBar) progressBar.style.width = '60%';
                molecularContent = await readMolecularFileContent(selectedFile);
                analysis = analyzeMolecularContent(molecularContent, selectedFile);
                
                if (progressBar) progressBar.style.width = '100%';
                
            } catch (error) {
                console.warn('🧪 Failed to read user file, falling back to demo data:', error);
                // 如果读取失败，回退到演示数据
                const demoMolecule = selectedFile.includes('benzene') ? 'benzene' : 
                                    selectedFile.includes('caffeine') ? 'caffeine' : 
                                    selectedFile.includes('water') ? 'water' : 'benzene';
                
                molecularContent = getPDBData(demoMolecule);
                analysis = {
                    filename: selectedFile,
                    format: 'Demo Data',
                    title: demoMolecule.toUpperCase(),
                    atoms: demoMolecule === 'benzene' ? 12 : demoMolecule === 'caffeine' ? 14 : 3,
                    formula: getMolecularFormula(demoMolecule),
                    isDemo: true
                };
                
                if (progressBar) progressBar.style.width = '100%';
            }
        }
        
        // 🔧 关键修复：根据模式选择不同的处理流程
        console.log("🧪 准备显示分子数据...", {
            molstarAvailable: alchem3DManager.molstarAvailable,
            hasContent: !!molecularContent,
            analysisTitle: analysis.title
        });
        
        if (alchem3DManager.molstarAvailable && molecularContent) {
            // MolStar模式：直接调用3D渲染，无需任何延迟或HTML处理
            console.log("🧪 使用MolStar渲染3D分子");
            alchem3DManager.displayMolecularData3D(molecularContent, analysis);
        } else {
            // 演示模式：显示HTML内容，需要延迟等待进度条动画
            console.log("🧪 使用演示模式显示分子数据");
            
            // 只在演示模式下使用延迟
            setTimeout(() => {
                const displayContent = `
                <div style="text-align: center; margin-bottom: 16px;">
                    <h3>正在显示: ${analysis.title || analysis.filename || selectedFile}</h3>
                    <p style="font-size: 12px; opacity: 0.8;">节点ID: ${node.id} | 输入字段: ${inputName}</p>
                    ${fromMemory === 'backend' ? 
                        `<p style="font-size: 12px;">🚀 从后端内存加载 (访问次数: ${analysis.access_count || 0})</p>` :
                        fromMemory === 'frontend' ? 
                            `<p style="font-size: 12px;">⚡ 从前端内存加载 (${Math.round((Date.now() - (molecularData.uploadTime || 0)) / 1000)}秒前上传)</p>` :
                            analysis.isDemo ? 
                                '<p style="font-size: 12px;">⚠️ 使用演示数据 - 无法读取用户文件</p>' : 
                                '<p style="font-size: 12px;">⚠️ 从文件系统读取 - 建议重新上传以优化性能</p>'
                    }
                </div>
                
                <div class="info-panel">
                    <h4>🔬 分子信息</h4>
                    <div class="info-grid">
                        <div>
                            <strong>文件名:</strong> ${analysis.filename}<br>
                            <strong>格式:</strong> ${analysis.format}<br>
                            <strong>标题:</strong> ${analysis.title}
                        </div>
                        <div>
                            <strong>原子数:</strong> ${analysis.atoms || 'Unknown'}<br>
                            <strong>键数:</strong> ${analysis.bonds || 'Unknown'}<br>
                            <strong>行数:</strong> ${analysis.lines || 'Unknown'}
                        </div>
                    </div>
                </div>
                
                <div class="info-panel">
                    <h4>🎛️ 控制面板</h4>
                    <div class="control-panel">
                        <button onclick="alert('切换到空间填充模型')" class="control-button">空间填充</button>
                        <button onclick="alert('切换到线框模型')" class="control-button">线框模型</button>
                        <button onclick="alert('旋转分子')" class="control-button">旋转</button>
                        <button onclick="alert('重置视角')" class="control-button">重置视角</button>
                    </div>
                </div>
                
                <div class="info-panel">
                    <h4>📋 ${analysis.format} 数据预览</h4>
                    <pre style="max-height: 200px;">${molecularContent.substring(0, 2000)}${molecularContent.length > 2000 ? '\n... (数据被截断，显示前2000字符)' : ''}</pre>
                </div>
                
                ${fromMemory === 'backend' ? `
                <div class="status-info">
                    <h4>🚀 后端内存优化</h4>
                    <div class="info-grid">
                        <div>
                            <strong>文件名:</strong> ${molecularData.filename}<br>
                            <strong>格式:</strong> ${molecularData.format_name}<br>
                            <strong>文件大小:</strong> ${(molecularData.file_stats?.size / 1024 || 0).toFixed(1)} KB
                        </div>
                        <div>
                            <strong>缓存时间:</strong> ${new Date(molecularData.cached_at * 1000).toLocaleTimeString()}<br>
                            <strong>访问次数:</strong> ${molecularData.access_count}<br>
                            <strong>节点ID:</strong> ${molecularData.node_id}
                        </div>
                    </div>
                    <p style="margin: 8px 0 0 0; font-size: 12px; line-height: 1.4;">
                        🎯 <strong>新架构优势</strong>: 分子数据存储在后端内存中，支持节点间传递和持久化！<br>
                        🚀 <strong>即时访问</strong>: 执行节点后立即可用，无需等待上传<br>
                        🔄 <strong>数据流动</strong>: 支持在不同节点和会话间共享分子数据<br>
                        💾 <strong>内存管理</strong>: 后端统一管理，避免前端数据丢失问题
                        ${window.globalViewer ? '<br><br>⚠️ 检测到已安装MolStar查看器，但当前使用内置显示器。' : '<br><br>💡 提示：安装rdkit_molstar扩展可以显示真实的3D分子结构。'}
                    </p>
                </div>` : fromMemory === 'frontend' ? `
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
                        ${window.globalViewer ? '<br><br>⚠️ 检测到已安装MolStar查看器，但当前使用内置显示器。' : '<br><br>💡 提示：安装rdkit_molstar扩展可以显示真实的3D分子结构。'}
                    </p>
                </div>` : `
                <div class="status-info">
                    <h4>${analysis.isDemo ? '💡 演示说明' : '⚠️ 性能提示'}</h4>
                    <p style="margin: 8px 0 0 0; font-size: 12px; line-height: 1.4;">
                        ${analysis.isDemo ? 
                            '这是一个演示性的3D显示功能！使用内置演示数据。' : 
                            '当前从文件系统读取数据，性能较慢。建议重新上传文件以启用内存加载优化。'
                        }
                        <br>在实际应用中，这里会显示真正的MolStar 3D分子查看器。
                        ${window.globalViewer ? '<br><br>⚠️ 检测到已安装MolStar查看器，但当前使用内置显示器。' : '<br><br>💡 提示：安装rdkit_molstar扩展可以显示真实的3D分子结构。'}
                    </p>
                </div>`}
            `;
            
                // 使用面板管理器显示数据
                alchem3DManager.displayData(displayContent);
            }, 800); // 仅演示模式需要延迟
        }
        
        console.log(`🎯 3D Display triggered for node ${node.id}, input: ${inputName}, file: ${selectedFile}`);
        
    } catch (error) {
        console.error('Error in 3D display:', error);
        alert(`3D显示出错: ${error.message}`);
    }
};

// 创建3D显示Widget
export const createMolstar3DDisplayWidget = () => {
    return (node, inputName, inputData) => {
        const inputOptions = inputData[1] ?? {};
        const { originalInputName } = inputOptions;
        
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

        // 自定义按钮样式
        displayWidget.computeSize = function() {
            return [200, 30];
        };

        console.log(`🎯 Added 3D display widget for ${originalInputName} on node ${node.type}`);
        
        return { widget: displayWidget };
    };
};

// 初始化3D显示功能
export const init3DDisplay = () => {
    // 添加3D显示相关样式
    const styleElement = document.createElement('style');
    styleElement.textContent = display3DStyles;
    document.head.appendChild(styleElement);
    
    // 延迟初始化面板管理器，等待DOM完全加载
    setTimeout(async () => {
        try {
            await alchem3DManager.initialize();
            console.log("🚀 ALCHEM 3D Panel Manager initialized on startup");
        } catch (error) {
            console.warn("⚠️ Failed to initialize panel manager on startup:", error);
        }
    }, 1000);
    
    console.log("🧪 3D Display module initialized");
};

// 处理3D显示节点创建
export const handle3DDisplayNodeCreated = (node) => {
    if (node.type === 'Demo3DDisplayNode') {
        console.log(`🎯 Enhanced ${node.type} with 3D display support`);
    }
};

// 检查是否有3D显示属性的节点并处理
export const process3DDisplayNodes = (nodeType, nodeData) => {
    const { input } = nodeData ?? {};
    const { required } = input ?? {};
    if (!required) return null;

    // 查找带有3D显示属性的输入
    const found3DDisplay = Object.entries(required).find(([_, inputSpec]) =>
        isMolstar3DDisplayInput(inputSpec)
    );

    if (found3DDisplay) {
        const [inputName, inputSpec] = found3DDisplay;
        console.log(`🎯 Added 3D display for ${nodeData.name}: ${inputName}`);
        return {
            inputName,
            inputSpec,
            molstar_3d: createMolstar3DDisplayInput(inputName, inputSpec)
        };
    }
    
    return null;
}; 