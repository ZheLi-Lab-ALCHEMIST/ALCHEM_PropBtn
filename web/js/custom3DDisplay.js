import { app } from "../../../scripts/app.js";

// 3D显示相关的样式
const display3DStyles = `
.custom-3d-display-button {
    background: linear-gradient(45deg, #ff6b6b 0%, #ee5a52 100%);
    border: none;
    border-radius: 6px;
    color: white;
    padding: 8px 16px;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    margin: 2px;
    font-weight: bold;
}

.custom-3d-display-button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(255,107,107,0.3);
    background: linear-gradient(45deg, #ff5252 0%, #f44336 100%);
}

.custom-3d-display-button:active {
    transform: translateY(0);
    box-shadow: 0 2px 4px rgba(255,107,107,0.2);
}

.custom-3d-viewer {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 80%;
    height: 80%;
    background: #1a1a1a;
    border: 2px solid #ff6b6b;
    border-radius: 10px;
    z-index: 9999;
    display: none;
    padding: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.custom-3d-viewer-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 1px solid #333;
}

.custom-3d-viewer-title {
    color: #ff6b6b;
    font-size: 18px;
    font-weight: bold;
}

.custom-3d-viewer-close {
    background: #ff6b6b;
    border: none;
    color: white;
    padding: 8px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
}

.custom-3d-viewer-content {
    background: #2a2a2a;
    border-radius: 5px;
    padding: 20px;
    height: calc(100% - 60px);
    overflow: auto;
    color: #ccc;
    font-family: monospace;
    line-height: 1.4;
}
`;

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

// 集成现有MolStar查看器的函数
const tryUseExistingMolStarViewer = async (node, inputName) => {
    try {
        // 检查是否存在全局MolStar查看器
        if (typeof window !== 'undefined' && window.globalViewer) {
            console.log("🎯 Found existing MolStar viewer, attempting to use it...");
            
            // 检查节点是否有showInGlobalViewer方法
            if (typeof node.showInGlobalViewer === 'function') {
                await node.showInGlobalViewer();
                return true;
            }
            
            // 尝试手动设置活跃节点
            if (window.globalViewer.show && typeof window.globalViewer.show === 'function') {
                window.globalViewer.show();
                
                // 尝试设置节点ID
                if (node.id) {
                    console.log(`🎯 Setting active node to ${node.id}`);
                    window.globalViewer.activeNodeId = node.id;
                    window.globalViewer.setTitle(`活跃节点: ${node.id}`);
                    
                    // 尝试刷新显示
                    if (window.globalViewer.refreshFromActiveNode) {
                        await window.globalViewer.refreshFromActiveNode();
                    }
                }
                return true;
            }
        }
        
        return false;
    } catch (error) {
        console.warn("🎯 Failed to use existing MolStar viewer:", error);
        return false;
    }
};

// 模拟3D显示功能
export const show3DMolecularView = async (node, inputName) => {
    try {
        // 首先尝试使用现有的MolStar查看器
        const usedExisting = await tryUseExistingMolStarViewer(node, inputName);
        if (usedExisting) {
            console.log("🎯 Successfully used existing MolStar viewer");
            return;
        }
        
        console.log("🎯 Using fallback 3D display modal");
        
        // 获取当前选中的分子数据
        const molInput = node.widgets.find(w => w.name === inputName);
        const moleculeType = molInput ? molInput.value : 'benzene';
        
        // 创建模态框
        let modal = document.getElementById('custom-3d-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'custom-3d-modal';
            modal.className = 'custom-3d-viewer';
            
            const header = document.createElement('div');
            header.className = 'custom-3d-viewer-header';
            
            const title = document.createElement('div');
            title.className = 'custom-3d-viewer-title';
            title.textContent = '🧪 3D分子结构查看器';
            
            const closeBtn = document.createElement('button');
            closeBtn.className = 'custom-3d-viewer-close';
            closeBtn.textContent = '关闭';
            closeBtn.onclick = () => {
                modal.style.display = 'none';
            };
            
            header.appendChild(title);
            header.appendChild(closeBtn);
            
            const content = document.createElement('div');
            content.className = 'custom-3d-viewer-content';
            content.id = 'custom-3d-content';
            
            modal.appendChild(header);
            modal.appendChild(content);
            document.body.appendChild(modal);
        }
        
        // 更新内容
        const content = document.getElementById('custom-3d-content');
        content.innerHTML = `
            <div style="text-align: center; margin-bottom: 20px;">
                <h3 style="color: #ff6b6b; margin-bottom: 10px;">正在显示: ${moleculeType.toUpperCase()}</h3>
                <p style="color: #999; margin-bottom: 20px;">节点ID: ${node.id} | 输入字段: ${inputName}</p>
            </div>
            
            <div style="background: #1a1a1a; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <h4 style="color: #4fc3f7; margin-bottom: 15px;">🔬 分子信息</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div>
                        <strong style="color: #81c784;">分子名称:</strong> ${moleculeType}<br>
                        <strong style="color: #81c784;">分子式:</strong> ${getMolecularFormula(moleculeType)}<br>
                        <strong style="color: #81c784;">相对分子质量:</strong> ${getMolecularWeight(moleculeType)}
                    </div>
                    <div>
                        <strong style="color: #81c784;">显示模式:</strong> 球棍模型<br>
                        <strong style="color: #81c784;">背景颜色:</strong> #1E1E1E<br>
                        <strong style="color: #81c784;">渲染状态:</strong> 就绪
                    </div>
                </div>
            </div>
            
            <div style="background: #2a2a2a; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <h4 style="color: #ffb74d; margin-bottom: 15px;">🎛️ 控制面板</h4>
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <button onclick="alert('切换到空间填充模型')" style="padding: 8px 16px; background: #4fc3f7; border: none; border-radius: 4px; color: white; cursor: pointer;">空间填充</button>
                    <button onclick="alert('切换到线框模型')" style="padding: 8px 16px; background: #81c784; border: none; border-radius: 4px; color: white; cursor: pointer;">线框模型</button>
                    <button onclick="alert('旋转分子')" style="padding: 8px 16px; background: #ffb74d; border: none; border-radius: 4px; color: white; cursor: pointer;">旋转</button>
                    <button onclick="alert('重置视角')" style="padding: 8px 16px; background: #f06292; border: none; border-radius: 4px; color: white; cursor: pointer;">重置视角</button>
                </div>
            </div>
            
            <div style="background: #1a1a1a; padding: 20px; border-radius: 8px;">
                <h4 style="color: #9575cd; margin-bottom: 15px;">📋 PDB数据预览</h4>
                <pre style="background: #0a0a0a; padding: 15px; border-radius: 4px; color: #4fc3f7; font-size: 12px; overflow-x: auto; max-height: 200px;">${getPDBData(moleculeType)}</pre>
            </div>
            
            <div style="margin-top: 20px; padding: 15px; background: rgba(255,107,107,0.1); border-radius: 8px; border: 1px solid #ff6b6b;">
                <h4 style="color: #ff6b6b; margin-bottom: 10px;">💡 演示说明</h4>
                <p style="margin: 0; color: #ccc;">
                    这是一个演示性的3D显示功能！在实际应用中，这里会显示真正的MolStar 3D分子查看器。
                    你可以通过设置 <code>molstar_3d_display: True</code> 属性来为任何节点添加这个3D按钮。
                    ${window.globalViewer ? '<br><br>⚠️ 检测到已安装MolStar查看器，但当前节点未正确配置。' : '<br><br>💡 提示：安装rdkit_molstar扩展可以显示真实的3D分子结构。'}
                </p>
            </div>
        `;
        
        // 显示模态框
        modal.style.display = 'block';
        
        console.log(`🎯 3D Display triggered for node ${node.id}, input: ${inputName}, molecule: ${moleculeType}`);
        
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