/**
 * 拖拽缩放控制器 - 负责面板的8方向拖拽缩放功能
 * 从custom3DDisplay.js重构而来
 */
export class ResizeController {
    constructor() {
        this.isResizing = false;
        this.currentPanel = null;
        this.resizeData = null;
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
        const minWidth = 300;
        const minHeight = 200;
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