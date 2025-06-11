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
    try {
        // 首先尝试使用现有的MolStar查看器
        const usedExisting = await tryUseExistingMolStarViewer(node, inputName);
        if (usedExisting) {
            console.log("🎯 Successfully used existing MolStar viewer");
            return;
        }
        
        console.log("🎯 Using fallback 3D display modal");
        
        // 🎯 关键优化：从后端内存读取分子数据
        const molInput = node.widgets.find(w => w.name === inputName);
        const selectedFile = molInput ? molInput.value : 'benzene';
        
        console.log(`🧪 Checking backend memory for molecular data: ${inputName}`);
        console.log(`🧪 Node ID: ${node.id}, Selected file: ${selectedFile}`);
        
        // 🌟 步骤1：尝试从后端内存获取分子数据
        let molecularData = null;
        let backendData = null;
        
        try {
            // 🚀 首先尝试从后端内存获取数据
            console.log(`🧪 Attempting to fetch from backend memory...`);
            backendData = await fetchMolecularDataFromBackend(node.id);
            
            if (backendData && backendData.success) {
                molecularData = backendData.data;
                console.log(`🚀 Successfully fetched molecular data from backend memory:`, molecularData);
                console.log(`   - Filename: ${molecularData.filename}`);
                console.log(`   - Format: ${molecularData.format_name}`);
                console.log(`   - Atoms: ${molecularData.atoms}`);
                console.log(`   - Cached at: ${new Date(molecularData.cached_at * 1000).toLocaleString()}`);
            } else {
                console.log(`⚠️ No backend memory data available: ${backendData?.error || 'Unknown error'}`);
            }
        } catch (error) {
            console.warn(`🚨 Failed to fetch from backend memory:`, error);
        }
        
        // 🔄 步骤2：回退到前端内存（兼容性）
        if (!molecularData && node.molecularData && node.molecularData[inputName]) {
            molecularData = node.molecularData[inputName];
            console.log(`🧪 Found molecular data in frontend node memory:`, molecularData);
        }
        
        // 显示加载状态
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
        
        // 显示加载状态
        const content = document.getElementById('custom-3d-content');
        content.innerHTML = `
            <div style="text-align: center; margin-bottom: 20px;">
                <h3 style="color: #4fc3f7; margin-bottom: 10px;">🔄 正在加载分子文件...</h3>
                <p style="color: #999;">文件: ${selectedFile}</p>
                <div style="background: #333; height: 4px; border-radius: 2px; overflow: hidden; margin: 20px 0;">
                    <div style="background: linear-gradient(45deg, #4fc3f7, #81c784); height: 100%; width: 0%; transition: width 0.3s;" id="loading-progress"></div>
                </div>
            </div>
        `;
        
        // 显示模态框
        modal.style.display = 'block';
        
        // 更新进度
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
        
        // 延迟一下显示结果
        setTimeout(() => {
            // 更新内容显示实际的分子数据
            content.innerHTML = `
                <div style="text-align: center; margin-bottom: 20px;">
                    <h3 style="color: #ff6b6b; margin-bottom: 10px;">正在显示: ${analysis.title || analysis.filename || selectedFile}</h3>
                    <p style="color: #999; margin-bottom: 10px;">节点ID: ${node.id} | 输入字段: ${inputName}</p>
                    ${fromMemory === 'backend' ? 
                        `<p style="color: #4fc3f7; font-size: 12px;">🚀 从后端内存加载 (访问次数: ${analysis.access_count || 0})</p>` :
                        fromMemory === 'frontend' ? 
                            `<p style="color: #81c784; font-size: 12px;">⚡ 从前端内存加载 (${Math.round((Date.now() - (molecularData.uploadTime || 0)) / 1000)}秒前上传)</p>` :
                            analysis.isDemo ? 
                                '<p style="color: #ffb74d; font-size: 12px;">⚠️ 使用演示数据 - 无法读取用户文件</p>' : 
                                '<p style="color: #ffb74d; font-size: 12px;">⚠️ 从文件系统读取 - 建议重新上传以优化性能</p>'
                    }
                </div>
                
                <div style="background: #1a1a1a; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h4 style="color: #4fc3f7; margin-bottom: 15px;">🔬 分子信息</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <div>
                            <strong style="color: #81c784;">文件名:</strong> ${analysis.filename}<br>
                            <strong style="color: #81c784;">格式:</strong> ${analysis.format}<br>
                            <strong style="color: #81c784;">标题:</strong> ${analysis.title}
                        </div>
                        <div>
                            <strong style="color: #81c784;">原子数:</strong> ${analysis.atoms || 'Unknown'}<br>
                            <strong style="color: #81c784;">键数:</strong> ${analysis.bonds || 'Unknown'}<br>
                            <strong style="color: #81c784;">行数:</strong> ${analysis.lines || 'Unknown'}
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
                    <h4 style="color: #9575cd; margin-bottom: 15px;">📋 ${analysis.format} 数据预览</h4>
                    <pre style="background: #0a0a0a; padding: 15px; border-radius: 4px; color: #4fc3f7; font-size: 12px; overflow-x: auto; max-height: 200px;">${molecularContent.substring(0, 2000)}${molecularContent.length > 2000 ? '\n... (数据被截断，显示前2000字符)' : ''}</pre>
                </div>
                
                ${fromMemory === 'backend' ? `
                <div style="margin-top: 20px; padding: 15px; background: rgba(33,150,243,0.1); border-radius: 8px; border: 1px solid #2196F3;">
                    <h4 style="color: #2196F3; margin-bottom: 10px;">🚀 后端内存优化</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 10px;">
                        <div>
                            <strong style="color: #4fc3f7;">文件名:</strong> ${molecularData.filename}<br>
                            <strong style="color: #4fc3f7;">格式:</strong> ${molecularData.format_name}<br>
                            <strong style="color: #4fc3f7;">文件大小:</strong> ${(molecularData.file_stats?.size / 1024 || 0).toFixed(1)} KB
                        </div>
                        <div>
                            <strong style="color: #4fc3f7;">缓存时间:</strong> ${new Date(molecularData.cached_at * 1000).toLocaleTimeString()}<br>
                            <strong style="color: #4fc3f7;">访问次数:</strong> ${molecularData.access_count}<br>
                            <strong style="color: #4fc3f7;">节点ID:</strong> ${molecularData.node_id}
                        </div>
                    </div>
                    <p style="margin: 0; color: #ccc;">
                        🎯 <strong>新架构优势</strong>: 分子数据存储在后端内存中，支持节点间传递和持久化！<br>
                        🚀 <strong>即时访问</strong>: 执行节点后立即可用，无需等待上传<br>
                        🔄 <strong>数据流动</strong>: 支持在不同节点和会话间共享分子数据<br>
                        💾 <strong>内存管理</strong>: 后端统一管理，避免前端数据丢失问题
                        ${window.globalViewer ? '<br><br>⚠️ 检测到已安装MolStar查看器，但当前使用内置显示器。' : '<br><br>💡 提示：安装rdkit_molstar扩展可以显示真实的3D分子结构。'}
                    </p>
                </div>` : fromMemory === 'frontend' ? `
                <div style="margin-top: 20px; padding: 15px; background: rgba(76,175,80,0.1); border-radius: 8px; border: 1px solid #4caf50;">
                    <h4 style="color: #4caf50; margin-bottom: 10px;">💡 前端内存优化</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 10px;">
                        <div>
                            <strong style="color: #81c784;">原始文件名:</strong> ${molecularData.originalName || '未知'}<br>
                            <strong style="color: #81c784;">服务器路径:</strong> ${molecularData.filename || '未知'}<br>
                            <strong style="color: #81c784;">文件大小:</strong> ${(molecularData.fileSize / 1024 || 0).toFixed(1)} KB
                        </div>
                        <div>
                            <strong style="color: #81c784;">上传时间:</strong> ${new Date(molecularData.uploadTime || 0).toLocaleTimeString()}<br>
                            <strong style="color: #81c784;">内容长度:</strong> ${molecularData.content?.length || 0} 字符<br>
                            <strong style="color: #81c784;">格式:</strong> ${molecularData.format || '未知'}
                        </div>
                    </div>
                    <p style="margin: 0; color: #ccc;">
                        🚀 <strong>性能优化</strong>: 分子数据已在上传时解析并加载到前端内存中<br>
                        📊 <strong>数据来源</strong>: 直接从前端内存读取，无需重复的文件I/O操作<br>
                        ⚡ <strong>响应速度</strong>: 毫秒级别的数据访问，比文件读取快数百倍<br>
                        ⚠️ <strong>建议</strong>: 推荐升级到后端内存存储以获得更好的数据持久性
                        ${window.globalViewer ? '<br><br>⚠️ 检测到已安装MolStar查看器，但当前使用内置显示器。' : '<br><br>💡 提示：安装rdkit_molstar扩展可以显示真实的3D分子结构。'}
                    </p>
                </div>` : `
                <div style="margin-top: 20px; padding: 15px; background: rgba(255,183,77,0.1); border-radius: 8px; border: 1px solid #ffb74d;">
                    <h4 style="color: #ffb74d; margin-bottom: 10px;">${analysis.isDemo ? '💡 演示说明' : '⚠️ 性能提示'}</h4>
                    <p style="margin: 0; color: #ccc;">
                        ${analysis.isDemo ? 
                            '这是一个演示性的3D显示功能！使用内置演示数据。' : 
                            '当前从文件系统读取数据，性能较慢。建议重新上传文件以启用内存加载优化。'
                        }
                        <br>在实际应用中，这里会显示真正的MolStar 3D分子查看器。
                        ${window.globalViewer ? '<br><br>⚠️ 检测到已安装MolStar查看器，但当前使用内置显示器。' : '<br><br>💡 提示：安装rdkit_molstar扩展可以显示真实的3D分子结构。'}
                    </p>
                </div>`}
            `;
        }, 800);
        
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