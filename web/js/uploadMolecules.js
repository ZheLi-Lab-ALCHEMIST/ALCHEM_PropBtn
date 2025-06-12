import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

/**
 * 🧪 分子文件上传模块 (uploadMolecules.js)
 * 
 * 专门处理分子文件格式的上传功能，支持多种化学文件格式
 * 提供分子文件验证、预览和智能分类功能
 * 
 * 支持的分子格式:
 * - PDB: Protein Data Bank格式 (最常用的蛋白质结构格式)
 * - MOL/SDF: MDL Molfile格式 (小分子结构格式)
 * - XYZ: 笛卡尔坐标格式 (简单几何结构)
 * - MOL2: Tripos Mol2格式 (包含电荷信息)
 * - CIF: 晶体信息文件 (晶体结构格式)
 * - MMCIF: MacroMolecular CIF (大分子晶体格式)
 * - GRO: GROMACS格式 (分子动力学)
 * - FASTA: 序列格式 (蛋白质/DNA序列)
 */

// 分子上传相关的样式
export const molecularUploadStyles = `
.molecular-upload-button {
    background: linear-gradient(45deg, #e91e63 0%, #f06292 50%, #ff9800 100%);
    border: none;
    border-radius: 8px;
    color: white;
    padding: 10px 18px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    margin: 3px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(233, 30, 99, 0.3);
}

.molecular-upload-button::before {
    content: '🧪';
    margin-right: 8px;
    font-size: 14px;
}

.molecular-upload-button:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 6px 16px rgba(233, 30, 99, 0.4);
    background: linear-gradient(45deg, #ad1457 0%, #e91e63 50%, #ff5722 100%);
}

.molecular-upload-button:active {
    transform: translateY(0) scale(0.98);
    box-shadow: 0 2px 8px rgba(233, 30, 99, 0.3);
}

.molecular-upload-progress {
    width: 100%;
    height: 6px;
    background: linear-gradient(90deg, #f5f5f5 0%, #e0e0e0 100%);
    border-radius: 3px;
    overflow: hidden;
    margin-top: 6px;
    position: relative;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
}

.molecular-upload-progress-bar {
    height: 100%;
    background: linear-gradient(45deg, #e91e63 0%, #f06292 25%, #ff9800 50%, #4caf50 100%);
    background-size: 200% 100%;
    width: 0%;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    border-radius: 3px;
    position: relative;
    animation: shimmer 2s infinite linear;
}

@keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

.molecular-upload-info {
    background: rgba(233, 30, 99, 0.1);
    border: 1px solid rgba(233, 30, 99, 0.2);
    border-radius: 6px;
    padding: 8px 12px;
    margin-top: 6px;
    font-size: 11px;
    color: #ad1457;
    display: none;
}

.molecular-format-indicator {
    display: inline-block;
    background: #4caf50;
    color: white;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: bold;
    margin-left: 8px;
}

.molecular-validation-error {
    background: rgba(244, 67, 54, 0.1);
    border: 1px solid rgba(244, 67, 54, 0.3);
    color: #d32f2f;
    padding: 8px 12px;
    border-radius: 6px;
    margin-top: 6px;
    font-size: 11px;
    display: none;
}
`;

// 分子文件格式配置
export const MOLECULAR_FORMATS = {
    // 蛋白质和大分子结构
    'pdb': {
        name: 'Protein Data Bank',
        description: '蛋白质结构数据库格式，最常用的生物大分子结构格式',
        category: 'protein',
        mimeType: 'chemical/x-pdb',
        icon: '🧬',
        color: '#2196f3',
        validator: validatePDBFormat
    },
    'cif': {
        name: 'Crystallographic Information File',
        description: '晶体学信息文件，现代晶体结构标准格式',
        category: 'crystal',
        mimeType: 'chemical/x-cif',
        icon: '💎',
        color: '#9c27b0',
        validator: validateCIFFormat
    },
    'mmcif': {
        name: 'MacroMolecular CIF',
        description: '大分子晶体信息文件，PDB的标准替代格式',
        category: 'protein',
        mimeType: 'chemical/x-mmcif',
        icon: '🧬',
        color: '#3f51b5',
        validator: validateMMCIFFormat
    },
    
    // 小分子结构
    'mol': {
        name: 'MDL Molfile',
        description: 'MDL分子文件格式，广泛用于小分子结构',
        category: 'small_molecule',
        mimeType: 'chemical/x-mdl-molfile',
        icon: '⚛️',
        color: '#4caf50',
        validator: validateMOLFormat
    },
    'sdf': {
        name: 'Structure Data File',
        description: 'SDF结构数据文件，可包含多个分子结构',
        category: 'small_molecule',
        mimeType: 'chemical/x-mdl-sdfile',
        icon: '📊',
        color: '#ff9800',
        validator: validateSDFFormat
    },
    'mol2': {
        name: 'Tripos Mol2',
        description: 'Tripos Mol2格式，包含原子类型和电荷信息',
        category: 'small_molecule',
        mimeType: 'chemical/x-mol2',
        icon: '⚡',
        color: '#e91e63',
        validator: validateMOL2Format
    },
    
    // 坐标和几何结构
    'xyz': {
        name: 'XYZ Coordinate',
        description: 'XYZ笛卡尔坐标格式，简单的原子坐标表示',
        category: 'coordinates',
        mimeType: 'chemical/x-xyz',
        icon: '📍',
        color: '#607d8b',
        validator: validateXYZFormat
    },
    
    // 分子动力学
    'gro': {
        name: 'GROMACS',
        description: 'GROMACS分子动力学格式',
        category: 'md',
        mimeType: 'chemical/x-gro',
        icon: '🌊',
        color: '#795548',
        validator: validateGROFormat
    },
    
    // 序列格式
    'fasta': {
        name: 'FASTA Sequence',
        description: 'FASTA序列格式，蛋白质或DNA序列',
        category: 'sequence',
        mimeType: 'chemical/x-fasta',
        icon: '🧾',
        color: '#009688',
        validator: validateFASTAFormat
    },
    'fa': {
        name: 'FASTA Sequence',
        description: 'FASTA序列格式 (简写)',
        category: 'sequence',
        mimeType: 'chemical/x-fasta',
        icon: '🧾',
        color: '#009688',
        validator: validateFASTAFormat
    }
};

// 分子文件格式验证函数
function validatePDBFormat(content) {
    const lines = content.split('\n');
    const hasHeader = lines.some(line => line.startsWith('HEADER'));
    const hasAtom = lines.some(line => line.startsWith('ATOM') || line.startsWith('HETATM'));
    const hasEnd = lines.some(line => line.startsWith('END'));
    
    if (!hasAtom) return { valid: false, error: 'PDB文件缺少ATOM记录' };
    return { valid: true, atoms: lines.filter(l => l.startsWith('ATOM')).length };
}

function validateMOLFormat(content) {
    const lines = content.split('\n').filter(line => line.trim());
    if (lines.length < 4) return { valid: false, error: 'MOL文件结构不完整' };
    
    const countsLine = lines[3];
    const atomCount = parseInt(countsLine.substr(0, 3));
    const bondCount = parseInt(countsLine.substr(3, 3));
    
    if (isNaN(atomCount) || atomCount <= 0) {
        return { valid: false, error: 'MOL文件原子数量信息无效' };
    }
    
    return { valid: true, atoms: atomCount, bonds: bondCount };
}

function validateSDFFormat(content) {
    const molBlocks = content.split('$$$$');
    if (molBlocks.length < 1) return { valid: false, error: 'SDF文件格式错误' };
    
    let totalAtoms = 0;
    for (const block of molBlocks) {
        if (block.trim()) {
            const molResult = validateMOLFormat(block);
            if (molResult.valid) totalAtoms += molResult.atoms;
        }
    }
    
    return { valid: totalAtoms > 0, molecules: molBlocks.length - 1, atoms: totalAtoms };
}

function validateXYZFormat(content) {
    const lines = content.split('\n').filter(line => line.trim());
    if (lines.length < 2) return { valid: false, error: 'XYZ文件结构不完整' };
    
    const atomCount = parseInt(lines[0]);
    if (isNaN(atomCount) || atomCount <= 0) {
        return { valid: false, error: 'XYZ文件原子数量无效' };
    }
    
    return { valid: true, atoms: atomCount };
}

function validateMOL2Format(content) {
    const hasAtomSection = content.includes('@<TRIPOS>ATOM');
    if (!hasAtomSection) return { valid: false, error: 'MOL2文件缺少原子部分' };
    
    const atomLines = content.split('@<TRIPOS>ATOM')[1]?.split('@<TRIPOS>')[0]?.split('\n') || [];
    const atomCount = atomLines.filter(line => line.trim() && !line.startsWith('#')).length;
    
    return { valid: atomCount > 0, atoms: atomCount };
}

function validateCIFFormat(content) {
    const hasCIFHeader = content.includes('data_') || content.includes('_cell_length_a');
    if (!hasCIFHeader) return { valid: false, error: '不是有效的CIF格式' };
    
    return { valid: true };
}

function validateMMCIFFormat(content) {
    const hasMMCIFTags = content.includes('_atom_site.') || content.includes('_entity.');
    if (!hasMMCIFTags) return { valid: false, error: '不是有效的mmCIF格式' };
    
    return { valid: true };
}

function validateGROFormat(content) {
    const lines = content.split('\n').filter(line => line.trim());
    if (lines.length < 3) return { valid: false, error: 'GRO文件结构不完整' };
    
    const atomCount = parseInt(lines[1]);
    if (isNaN(atomCount) || atomCount <= 0) {
        return { valid: false, error: 'GRO文件原子数量无效' };
    }
    
    return { valid: true, atoms: atomCount };
}

function validateFASTAFormat(content) {
    const sequences = content.split('>').filter(seq => seq.trim());
    if (sequences.length === 0) return { valid: false, error: 'FASTA文件没有序列' };
    
    let totalLength = 0;
    for (const seq of sequences) {
        const lines = seq.split('\n');
        const sequence = lines.slice(1).join('').replace(/\s/g, '');
        totalLength += sequence.length;
    }
    
    return { valid: totalLength > 0, sequences: sequences.length, length: totalLength };
}

// 检测分子上传属性的函数
export const isMolecularUploadInput = (inputSpec) => {
    const [inputName, inputOptions] = inputSpec;
    if (!inputOptions) return false;
    
    return !!(inputOptions['molecular_upload']);
};

// 获取分子文件类型
export const getMolecularFileType = (filename) => {
    const extension = filename.split('.').pop().toLowerCase();
    return MOLECULAR_FORMATS[extension] || null;
};

// 获取支持的分子文件类型
export const getSupportedMolecularTypes = () => {
    return Object.keys(MOLECULAR_FORMATS).map(ext => `.${ext}`).join(',');
};

// 获取分子文件夹路径
export const getMolecularFolder = (inputOptions) => {
    return inputOptions['molecular_folder'] || inputOptions['custom_folder'] || 'molecules';
};

// 创建分子上传输入定义
export const createMolecularUploadInput = (inputName, inputSpec) => [
    'MOLECULARUPLOAD',
    {
        ...inputSpec[1],
        originalInputName: inputName,
        uploadType: 'molecular',
        molecularFolder: getMolecularFolder(inputSpec[1])
    }
];

// 分析分子文件内容
export const analyzeMolecularFile = async (file) => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const content = e.target.result;
            const fileType = getMolecularFileType(file.name);
            
            if (!fileType) {
                resolve({ 
                    valid: false, 
                    error: '不支持的分子文件格式',
                    format: 'unknown'
                });
                return;
            }
            
            try {
                const validation = fileType.validator(content);
                resolve({
                    ...validation,
                    format: fileType.name,
                    category: fileType.category,
                    icon: fileType.icon,
                    color: fileType.color,
                    size: file.size,
                    filename: file.name
                });
            } catch (error) {
                resolve({
                    valid: false,
                    error: `文件分析失败: ${error.message}`,
                    format: fileType.name
                });
            }
        };
        reader.onerror = () => reject(new Error('文件读取失败'));
        reader.readAsText(file);
    });
};

// 上传分子文件到后端内存（新架构）
export const uploadMolecularFileToBackend = async (file, molecularFolder, nodeId) => {
    const formData = new FormData();
    formData.append('file', file);  // 分子文件
    formData.append('node_id', nodeId);  // 节点ID
    formData.append('folder', molecularFolder);  // 存储文件夹

    try {
        console.log(`🧪 Uploading molecular file to backend memory: ${file.name} -> node ${nodeId}`);
        
        const response = await fetch('/alchem_propbtn/api/upload_molecular', {
            method: 'POST',
            body: formData
        });

        if (response.status === 200) {
            const result = await response.json();
            if (result.success) {
                console.log(`🚀 Successfully uploaded to backend memory:`, result.data);
                return result;
            } else {
                throw new Error(result.error || 'Backend storage failed');
            }
        } else {
            const errorText = await response.text();
            throw new Error(`Upload failed: ${response.status} ${response.statusText} - ${errorText}`);
        }
    } catch (error) {
        console.error('🧪 Backend molecular upload error:', error);
        throw error;
    }
};

// 原有的文件系统上传（兼容性保留）
export const uploadMolecularFile = async (file, molecularFolder) => {
    const formData = new FormData();
    formData.append('image', file); // ComfyUI的上传端点期望'image'字段
    formData.append('subfolder', molecularFolder);

    try {
        const response = await api.fetchApi('/upload/image', {
            method: 'POST',
            body: formData
        });

        if (response.status === 200) {
            const result = await response.json();
            return result.subfolder ? `${result.subfolder}/${result.name}` : result.name;
        } else {
            throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
        }
    } catch (error) {
        console.error('🧪 Molecular upload error:', error);
        throw error;
    }
};

// 创建分子文件上传处理器
export const createMolecularUploadHandler = (molecularFolder, comboWidget, progressContainer, progressBar, infoContainer) => {
    return async (file) => {
        try {
            console.log(`🧪 Starting molecular upload: ${file.name}`);
            
            // 🎯 获取节点ID - 这是关键！
            const node = findNodeByWidget(comboWidget);
            if (!node || !node.id) {
                throw new Error('无法获取节点ID，上传失败');
            }
            
            console.log(`🎯 Uploading for node ID: ${node.id}`);
            
            // 显示进度条和信息容器
            progressContainer.style.display = 'block';
            infoContainer.style.display = 'block';
            progressBar.style.width = '15%';
            
            // 分析文件格式
            infoContainer.innerHTML = '🔍 正在分析分子文件格式...';
            const analysis = await analyzeMolecularFile(file);
            progressBar.style.width = '35%';
            
            if (!analysis.valid) {
                throw new Error(analysis.error);
            }
            
            // 显示分析结果
            const formatInfo = `${analysis.icon} ${analysis.format}` + 
                (analysis.atoms ? ` (${analysis.atoms} 原子)` : '') +
                (analysis.molecules ? ` (${analysis.molecules} 分子)` : '') +
                (analysis.sequences ? ` (${analysis.sequences} 序列)` : '');
            
            infoContainer.innerHTML = `✅ 格式验证通过: <span class="molecular-format-indicator">${formatInfo}</span>`;
            progressBar.style.width = '50%';
            
            // 🚀 步骤1：上传到后端内存（快速访问）
            infoContainer.innerHTML = `🚀 正在上传到后端内存 ${analysis.icon} ${analysis.format} 文件...`;
            const uploadResult = await uploadMolecularFileToBackend(file, molecularFolder, node.id);
            progressBar.style.width = '70%';
            
            // 🚀 后端内存上传完成，获取结果信息
            const backendData = uploadResult.data;
            infoContainer.innerHTML = `🎉 已存储到后端内存: ${backendData.format} (${backendData.atoms} 原子)`;
            
            // 🚀 步骤2：同时上传到文件系统（持久化保存）
            infoContainer.innerHTML = `💾 正在保存到文件系统 ${analysis.icon} ${analysis.format} 文件...`;
            const fileSystemResult = await uploadMolecularFile(file, molecularFolder);
            progressBar.style.width = '90%';
            
            console.log(`✅ 文件已保存到文件系统: ${fileSystemResult}`);
            
            // 刷新combo选项（用于显示）
            await app.refreshComboInNodes();
            
            // 更新combo widget的值 - 使用后端返回的文件名
            comboWidget.value = backendData.filename;
            if (comboWidget.callback) {
                comboWidget.callback(backendData.filename);
            }
            progressBar.style.width = '100%';
            
            // 显示成功信息（双重上传完成）
            infoContainer.innerHTML = `🎉 双重上传成功: <span class="molecular-format-indicator">${formatInfo}</span>
                <br><small style="color: #4fc3f7;">🚀 内存: 节点 ${node.id} | 💾 文件: ${fileSystemResult}</small>
                <br><small style="color: #81c784;">大小: ${(backendData.file_size / 1024).toFixed(1)} KB | 原子数: ${backendData.atoms}</small>`;
            
            // 隐藏进度条，保留信息显示一段时间
            setTimeout(() => {
                progressContainer.style.display = 'none';
                progressBar.style.width = '0%';
            }, 1000);
            
            setTimeout(() => {
                infoContainer.style.display = 'none';
            }, 3000);
            
            console.log(`🚀 Successfully completed dual upload:`);
            console.log(`   💾 File system: ${fileSystemResult}`);
            console.log(`   🚀 Backend memory: ${backendData.filename} -> node ${node.id}`);
            
        } catch (error) {
            console.error('🧪 Molecular upload failed:', error);
            
            // 显示错误信息
            progressContainer.style.display = 'none';
            infoContainer.className = 'molecular-validation-error';
            infoContainer.style.display = 'block';
            infoContainer.innerHTML = `❌ 上传失败: ${error.message}`;
            
            setTimeout(() => {
                infoContainer.style.display = 'none';
                infoContainer.className = 'molecular-upload-info';
            }, 5000);
        }
    };
};

// 辅助函数：从文件对象读取内容
const readFileContent = (file) => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = () => reject(new Error('文件读取失败'));
        reader.readAsText(file);
    });
};

// 辅助函数：通过widget找到对应的节点
const findNodeByWidget = (widget) => {
    // 尝试多种方式找到节点
    if (widget.node) return widget.node;
    
    // 在所有节点中查找包含这个widget的节点
    const allNodes = app.graph?.nodes || [];
    for (const node of allNodes) {
        if (node.widgets && node.widgets.includes(widget)) {
            return node;
        }
    }
    
    console.warn('🧪 Could not find node for widget:', widget);
    return null;
};

// 创建分子文件选择器
export const createMolecularFileSelector = (onFileSelected) => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = getSupportedMolecularTypes();
    input.style.display = 'none';
    
    input.onchange = (e) => {
        const file = e.target.files[0];
        if (file) {
            onFileSelected(file);
        }
    };
    
    // 触发文件选择
    document.body.appendChild(input);
    input.click();
    document.body.removeChild(input);
};

// 创建分子上传Widget
export const createMolecularUploadWidget = () => {
    return (node, inputName, inputData) => {
        const inputOptions = inputData[1] ?? {};
        const { originalInputName, molecularFolder } = inputOptions;
        
        // 找到关联的combo widget
        const comboWidget = node.widgets.find(w => w.name === originalInputName);
        if (!comboWidget) {
            console.error(`🧪 Could not find combo widget for ${originalInputName}`);
            return { widget: null };
        }

        // 创建进度条元素
        const progressContainer = document.createElement('div');
        progressContainer.className = 'molecular-upload-progress';
        progressContainer.style.display = 'none';
        
        const progressBar = document.createElement('div');
        progressBar.className = 'molecular-upload-progress-bar';
        progressContainer.appendChild(progressBar);

        // 创建信息显示容器
        const infoContainer = document.createElement('div');
        infoContainer.className = 'molecular-upload-info';
        infoContainer.style.display = 'none';

        // 创建分子文件上传处理函数
        const handleFileUpload = createMolecularUploadHandler(
            molecularFolder, comboWidget, progressContainer, progressBar, infoContainer
        );

        // 创建上传按钮
        const uploadWidget = node.addWidget(
            'button',
            inputName,
            '🧪 上传分子文件',
            () => {
                createMolecularFileSelector(handleFileUpload);
            },
            { 
                serialize: false
            }
        );

        // 创建容器元素来包含进度条和信息
        const containerElement = document.createElement('div');
        containerElement.appendChild(progressContainer);
        containerElement.appendChild(infoContainer);
        
        uploadWidget.element = containerElement;
        
        console.log(`🧪 Added molecular upload widget for ${originalInputName} (folder: ${molecularFolder}) on node ${node.type}`);
        
        return { widget: uploadWidget };
    };
};

// 检查分子文件类型是否匹配
export const isMolecularFileTypeMatching = (file) => {
    const supportedTypes = getSupportedMolecularTypes().split(',');
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    return supportedTypes.includes(fileExtension);
};

// 添加分子文件拖拽支持
export const addMolecularDragAndDropSupport = (node, molecularFolder) => {
    const canvas = node.graph?.canvas;
    if (!canvas) return;

    const originalOnDrop = canvas.onDrop;
    canvas.onDrop = function(e) {
        // 检查是否拖拽到了我们的节点上
        const canvasPos = app.clientPosToCanvasPos([e.clientX, e.clientY]);
        const nodeAtPos = this.graph.getNodeOnPos(canvasPos[0], canvasPos[1]);
        
        if (nodeAtPos === node && e.dataTransfer.files.length > 0) {
            const file = e.dataTransfer.files[0];
            
            // 检查是否是分子文件
            if (isMolecularFileTypeMatching(file)) {
                e.preventDefault();
                e.stopPropagation();
                
                console.log(`🧪 Molecular drag & drop detected: ${file.name}`);
                
                // 找到分子上传widget并触发上传
                const uploadWidget = node.widgets.find(w => 
                    w.type === 'button' && 
                    w.name.includes('molecular') || w.name.includes('upload')
                );
                
                if (uploadWidget && uploadWidget.element) {
                    const progressContainer = uploadWidget.element.querySelector('.molecular-upload-progress');
                    const progressBar = progressContainer?.querySelector('.molecular-upload-progress-bar');
                    const infoContainer = uploadWidget.element.querySelector('.molecular-upload-info');
                    
                    if (progressContainer && progressBar && infoContainer) {
                        const handleFileUpload = createMolecularUploadHandler(
                            molecularFolder, 
                            node.widgets.find(w => w.name.includes('molecular') || w.name.includes('molecule')),
                            progressContainer, 
                            progressBar, 
                            infoContainer
                        );
                        handleFileUpload(file);
                    }
                }
                return;
            }
        }
        
        // 如果不是我们处理的，调用原始处理函数
        if (originalOnDrop) {
            return originalOnDrop.call(this, e);
        }
    };
    
    console.log(`🧪 Added molecular drag & drop support to node ${node.id}`);
};

// 初始化分子上传功能
export const initMolecularUpload = () => {
    // 添加分子上传相关样式
    const styleElement = document.createElement('style');
    styleElement.textContent = molecularUploadStyles;
    document.head.appendChild(styleElement);
    
    console.log("🧪 Molecular Upload module initialized");
};

// 处理分子上传节点创建
export const handleMolecularUploadNodeCreated = (node) => {
    // 检查是否是包含分子上传的节点
    const hasMolecularUpload = node.widgets?.some(w => 
        w.name?.includes('molecular') || 
        w.options?.molecular_upload
    );
    
    if (hasMolecularUpload) {
        const molecularFolder = 'molecules'; // 默认文件夹
        
        // 添加拖拽支持
        setTimeout(() => addMolecularDragAndDropSupport(node, molecularFolder), 100);
        
        console.log(`🧪 Enhanced ${node.type} with molecular drag&drop support`);
    }
};

// 检查是否有分子上传属性的节点并处理
export const processMolecularUploadNodes = (nodeType, nodeData) => {
    const { input } = nodeData ?? {};
    const { required } = input ?? {};
    if (!required) return null;

    // 查找带有分子上传属性的输入
    const foundMolecularUpload = Object.entries(required).find(([_, inputSpec]) =>
        isMolecularUploadInput(inputSpec)
    );

    if (foundMolecularUpload) {
        const [inputName, inputSpec] = foundMolecularUpload;
        console.log(`🧪 Added molecular upload for ${nodeData.name}: ${inputName}`);
        return {
            inputName,
            inputSpec,
            molecular_upload: createMolecularUploadInput(inputName, inputSpec)
        };
    }
    
    return null;
}; 