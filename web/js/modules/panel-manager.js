import { loadMolstarLibrary, MolstarViewer } from './molstar-core.js';
import { ResizeController } from './resize-controller.js';

/**
 * ALCHEM 3D面板管理器 - 负责3D显示面板的创建、显示、隐藏和管理
 * 从custom3DDisplay.js重构而来
 */
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
        
        // 拖拽缩放控制器
        this.resizeController = new ResizeController();
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
            content.innerHTML = `
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
                        ${this.molstarAvailable ? 
                            '🎉 MolStar 3D查看器已启用，将提供专业级分子可视化体验' : 
                            '💡 提示：安装MolStar库可以获得更好的3D显示效果'
                        }
                    </p>
                </div>
            `;
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