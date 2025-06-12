// ComfyUI原生风格的3D显示样式
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

// 应用样式到文档
export function applyStyles() {
    const styleElement = document.createElement('style');
    styleElement.textContent = display3DStyles;
    document.head.appendChild(styleElement);
    console.log("🎨 Display styles applied");
}