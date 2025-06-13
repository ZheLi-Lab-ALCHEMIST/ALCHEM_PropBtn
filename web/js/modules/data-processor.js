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
            // QUIET: console.log(`🚀 Fetching molecular data for node: ${nodeId}`);
            
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
            // QUIET: console.log(`📡 Backend API response:`, responseData);
            
            if (responseData.success) {
                // QUIET: console.log(`✅ Successfully retrieved molecular data from backend`);
                // QUIET: console.log(`   - Node ID: ${responseData.data.node_id}`);
                // QUIET: console.log(`   - Filename: ${responseData.data.filename}`);
                // QUIET: console.log(`   - Format: ${responseData.data.format_name}`);
                // QUIET: console.log(`   - Atoms: ${responseData.data.atoms}`);
                // QUIET: console.log(`   - Access count: ${responseData.data.access_count}`);
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
            // QUIET: console.log(`📊 Cache status:`, responseData);
            
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
            // QUIET: console.log(`🔍 Searching for molecular data by filename: ${filename}`);
            
            const cacheStatus = await this.fetchCacheStatusFromBackend();
            if (cacheStatus && cacheStatus.success && cacheStatus.data.nodes) {
                for (const cachedNode of cacheStatus.data.nodes) {
                    if (cachedNode.filename === filename) {
                        // QUIET: console.log(`🎯 Found matching file in cache: ${filename} (node: ${cachedNode.node_id})`);
                        
                        // 使用找到的节点ID获取完整数据
                        const backendData = await this.fetchMolecularDataFromBackend(cachedNode.node_id);
                        if (backendData && backendData.success) {
                            // QUIET: console.log(`✅ Retrieved data by filename: ${backendData.data.filename}`);
                            return backendData;
                        }
                    }
                }
            }
            
            // QUIET: console.log(`❌ No data found for filename: ${filename}`);
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
            // QUIET: console.log(`🧪 Attempting to read molecular file: ${fileUrl}`);
            
            const response = await fetch(fileUrl);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const content = await response.text();
            // QUIET: console.log(`🧪 Successfully read ${content.length} characters from ${filename}`);
            
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
            // QUIET: console.warn('🧪 Error analyzing molecular content:', error);
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
            // QUIET: console.warn("🧪 解析分子信息失败:", error);
            return null;
        }
    }
    
    // 生成唯一节点ID
    generateUniqueNodeId(node) {
        // 检查是否有ComfyUI的唯一标识符
        if (node.graph && node.graph.runningContext && node.graph.runningContext.unique_id) {
            // QUIET: console.log(`🔧 Using ComfyUI unique_id: ${node.graph.runningContext.unique_id}`);
            return node.graph.runningContext.unique_id;
        } else if (node._id) {
            // QUIET: console.log(`🔧 Using node._id: ${node._id}`);
            return node._id;
        } else {
            // 使用节点的内存地址或其他唯一标识
            if (!node._uniqueDisplayId) {
                node._uniqueDisplayId = `${node.id}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            }
            // QUIET: console.log(`🔧 Generated unique display ID: ${node._uniqueDisplayId}`);
            return node._uniqueDisplayId;
        }
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
        // QUIET: console.log("🧪 Data processor cache cleared");
    }
    
    // 获取缓存统计
    getCacheStats() {
        return {
            size: this.cache.size,
            keys: Array.from(this.cache.keys())
        };
    }
}