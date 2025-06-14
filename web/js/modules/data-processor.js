/**
 * 数据处理器 - 负责分子数据的获取、分析和格式化
 * 从custom3DDisplay.js重构而来
 */

// 简单默认PDB数据
const DEFAULT_PDB = `HEADER    DEFAULT MOLECULE
COMPND    DEFAULT
ATOM      1  C1  DEF A   1       0.000   1.000   0.000  1.00  0.00           C
ATOM      2  C2  DEF A   1       1.000   0.000   0.000  1.00  0.00           C
END`;

/**
 * 数据处理器类
 */
export class MolecularDataProcessor {
    constructor() {
        this.cache = new Map();
    }
    
    // 从后端API获取分子数据
    async fetchMolecularDataFromBackend(nodeId) {
        try {
            
            const apiUrl = '/alchem_propbtn/api/molecular';
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
            
            if (responseData.success) {
            }
            
            return responseData;
            
        } catch (error) {
            console.error('🚨 Error fetching molecular data from backend:', error);
            return {
                success: false,
                error: `Network error: ${error.message}`,
                data: null
            };
        }
    }
    
    // 获取后端缓存状态
    async fetchCacheStatusFromBackend() {
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
            
            return responseData;
            
        } catch (error) {
            console.error('🚨 Error fetching cache status:', error);
            return {
                success: false,
                error: error.message,
                data: null
            };
        }
    }
    
    // 通过文件名查找分子数据
    async findMolecularDataByFilename(filename) {
        try {
            
            const cacheStatus = await this.fetchCacheStatusFromBackend();
            if (cacheStatus && cacheStatus.success && cacheStatus.data.nodes) {
                for (const cachedNode of cacheStatus.data.nodes) {
                    if (cachedNode.filename === filename) {
                        // 使用找到的节点ID获取完整数据
                        const backendData = await this.fetchMolecularDataFromBackend(cachedNode.node_id);
                        if (backendData && backendData.success) {
                            return backendData;
                        }
                    }
                }
            }
            
            return null;
            
        } catch (error) {
            console.error('🚨 Error finding molecular data by filename:', error);
            return null;
        }
    }
    
    // 读取分子文件内容（从文件系统）
    async readMolecularFileContent(filename) {
        try {
            const fileUrl = `/view?filename=${encodeURIComponent(filename)}&type=input`;
            
            const response = await fetch(fileUrl);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const content = await response.text();
            
            return content;
        } catch (error) {
            console.error(`🧪 Failed to read molecular file ${filename}:`, error);
            throw error;
        }
    }
    
    // 分析分子文件内容
    analyzeMolecularContent(content, filename) {
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
        }
        
        return analysis;
    }
    
    // 获取默认数据
    getDefaultMoleculeData() {
        return { pdb: DEFAULT_PDB };
    }
    
    // 从HTML数据中提取分子信息
    extractMolecularInfoFromHTML(htmlData) {
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
            return null;
        }
    }
    
    // 生成唯一节点ID (支持多tab)
    generateUniqueNodeId(node) {
        // 🔧 关键修复：生成tab感知的唯一ID
        const tabId = this.getTabId(node);
        
        // 🎯 改进的节点ID生成策略：使用稳定的节点标识符
        
        // 优先级1: ComfyUI的运行时唯一标识符（最稳定）
        if (node.graph && node.graph.runningContext && node.graph.runningContext.unique_id) {
            const baseId = node.graph.runningContext.unique_id;
            const tabAwareId = `${tabId}_${baseId}`;
            console.log(`🔧 节点ID生成: ${node.id} → ${tabAwareId} (runningContext)`);
            return tabAwareId;
        }
        
        // 优先级2: 节点的内部ID
        if (node._id) {
            const tabAwareId = `${tabId}_${node._id}`;
            console.log(`🔧 节点ID生成: ${node.id} → ${tabAwareId} (node._id)`);
            return tabAwareId;
        }
        
        // 优先级3: 基于节点的稳定属性生成确定性ID
        const stableNodeId = this._generateStableNodeId(node);
        const tabAwareId = `${tabId}_${stableNodeId}`;
        console.log(`🔧 节点ID生成: ${node.id} → ${tabAwareId} (stable)`);
        return tabAwareId;
    }
    
    // 🎯 生成稳定的节点ID（基于节点的不变属性）
    _generateStableNodeId(node) {
        // 收集节点的稳定属性
        const stableProps = {
            // 基础属性
            id: node.id,                    // 节点在当前图中的ID
            type: node.type,                // 节点类型
            title: node.title || node.type, // 节点标题
            
            // 位置信息（相对稳定）
            pos: node.pos ? `${Math.round(node.pos[0])}_${Math.round(node.pos[1])}` : 'pos_unknown',
            
            // 大小信息
            size: node.size ? `${node.size[0]}x${node.size[1]}` : 'size_default',
            
            // 输入输出结构（这些是最稳定的）
            inputs_count: node.inputs ? node.inputs.length : 0,
            outputs_count: node.outputs ? node.outputs.length : 0
        };
        
        // 如果有widgets，添加widgets的结构信息（不包含值，只包含结构）
        if (node.widgets && node.widgets.length > 0) {
            stableProps.widgets_structure = node.widgets.map(w => `${w.name}:${w.type}`).join('|');
        }
        
        // 生成确定性hash
        const propsString = JSON.stringify(stableProps);
        const stableHash = this.hashString(propsString);
        
        // 使用节点ID作为主要标识，hash作为唯一化后缀
        return `node_${node.id}_${stableHash}`;
    }
    
    // 🎯 获取当前tab的唯一标识（基于Pinia store）
    getTabId(node) {
        try {
            // 方法1: 通过Pinia workflowStore获取当前活跃工作流信息
            if (window.app && window.app.$stores && window.app.$stores.workflow) {
                try {
                    const workflowStore = window.app.$stores.workflow;
                    const activeWorkflow = workflowStore.activeWorkflow;
                    if (activeWorkflow && activeWorkflow.key) {
                        console.log(`🔧 从Pinia workflowStore获取tab标识: ${activeWorkflow.key}`);
                        return `workflow_${this.hashString(activeWorkflow.key)}`;
                    }
                } catch (error) {
                    console.warn('🔧 无法从Pinia workflowStore获取tab信息:', error);
                }
            }
            
            // 方法2: 通过ComfyUI的全局app对象
            if (window.app && window.app.ui && window.app.ui.settings) {
                try {
                    // 尝试获取当前工作流名称
                    const currentWorkflow = window.app.ui.settings.getSettingValue('Comfy.DevMode.EnableDebug');
                    if (currentWorkflow) {
                        console.log(`🔧 从app.ui获取工作流信息`);
                    }
                } catch (error) {
                    console.warn('🔧 无法从app.ui获取工作流信息:', error);
                }
            }
            
            // 方法3: 通过DOM查找活跃tab的稳定名称
            const activeTabButton = document.querySelector('.comfy-tab-button.active, .tab-button.active, [data-tab-active="true"]');
            if (activeTabButton) {
                const tabText = activeTabButton.textContent.trim();
                console.log(`🔧 从DOM获取tab名: ${tabText}`);
                return `workflow_${this.hashString(tabText)}`;
            }
            
            // 方法4: 通过window.title或document.title获取工作流名称
            if (document.title && document.title !== 'ComfyUI') {
                const titleParts = document.title.split(' - ');
                if (titleParts.length > 1) {
                    const workflowName = titleParts[0];
                    console.log(`🔧 从document.title获取工作流名: ${workflowName}`);
                    return `workflow_${this.hashString(workflowName)}`;
                }
            }
            
            // 方法5: 回退到graph对象信息（最不稳定）
            if (node.graph && node.graph.canvas && node.graph.canvas.canvas) {
                const canvasId = node.graph.canvas.canvas.id || 'default';
                return `canvas_${canvasId}`;
            }
            
            // 最后回退
            console.warn('🔧 无法获取稳定的tab信息，使用默认值');
            return 'workflow_default';
            
        } catch (error) {
            console.warn('🔧 获取tab ID失败，使用默认值:', error);
            return 'workflow_default';
        }
    }
    
    // 🆕 简单字符串hash函数
    hashString(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // 转换为32位整数
        }
        return Math.abs(hash).toString(36).substr(0, 8);
    }
    
    // 检查是否是3D显示输入
    isMolstar3DDisplayInput(inputSpec) {
        const [inputName, inputOptions] = inputSpec;
        if (!inputOptions) return false;
        
        return !!(inputOptions['molstar_3d_display']);
    }
    
    // 创建3D显示输入定义
    createMolstar3DDisplayInput(inputName, inputSpec) {
        return [
            'MOLSTAR3DDISPLAY',
            {
                ...inputSpec[1],
                originalInputName: inputName,
                displayType: '3d_molecular'
            }
        ];
    }
    
    // 清理缓存
    clearCache() {
        this.cache.clear();
    }
    
    // 获取缓存统计
    getCacheStats() {
        return {
            size: this.cache.size,
            keys: Array.from(this.cache.keys())
        };
    }
}