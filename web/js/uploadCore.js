import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

// 上传相关的样式
export const uploadStyles = `
.custom-upload-button {
    background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
    border: none;
    border-radius: 6px;
    color: white;
    padding: 8px 16px;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
    margin: 2px;
}

.custom-upload-button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.custom-upload-button:active {
    transform: translateY(0);
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.custom-upload-progress {
    width: 100%;
    height: 4px;
    background: #f0f0f0;
    border-radius: 2px;
    overflow: hidden;
    margin-top: 4px;
}

.custom-upload-progress-bar {
    height: 100%;
    background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
    width: 0%;
    transition: width 0.3s ease;
}
`;

// 检测自定义上传属性的函数
export const isCustomUploadInput = (inputSpec) => {
    const [inputName, inputOptions] = inputSpec;
    if (!inputOptions) return false;
    
    return !!(
        inputOptions['custom_text_upload'] || 
        inputOptions['custom_config_upload']
    );
};

// 获取上传类型
export const getUploadType = (inputOptions) => {
    if (inputOptions['custom_text_upload']) return 'text';
    if (inputOptions['custom_config_upload']) return 'config';
    return 'unknown';
};

// 获取接受的文件类型
export const getAcceptedTypes = (uploadType) => {
    switch (uploadType) {
        case 'text':
            return '.txt,.json,.md';
        case 'config':
            return '.json,.yaml,.yml,.toml';
        default:
            return '*';
    }
};

// 创建自定义上传输入定义
export const createCustomUploadInput = (inputName, inputSpec) => [
    'CUSTOMUPLOAD',
    {
        ...inputSpec[1],
        originalInputName: inputName,
        uploadType: getUploadType(inputSpec[1])
    }
];

// 上传文件到服务器的核心函数
export const uploadFile = async (file, uploadType) => {
    const formData = new FormData();
    formData.append('image', file); // ComfyUI的上传端点期望'image'字段
    
    // 根据类型添加子文件夹
    const subfolders = {
        'text': 'texts',
        'config': 'configs'
    };
    
    if (subfolders[uploadType]) {
        formData.append('subfolder', subfolders[uploadType]);
    }

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
        console.error('📁 Upload error:', error);
        throw error;
    }
};

// 创建文件上传处理器
export const createFileUploadHandler = (uploadType, comboWidget, progressContainer, progressBar) => {
    return async (file) => {
        try {
            console.log(`📁 Starting upload for ${uploadType} file: ${file.name}`);
            
            // 显示进度条
            progressContainer.style.display = 'block';
            progressBar.style.width = '20%';
            
            // 上传文件
            progressBar.style.width = '60%';
            const filename = await uploadFile(file, uploadType);
            
            // 更新进度
            progressBar.style.width = '80%';
            
            // 刷新combo选项
            await app.refreshComboInNodes();
            
            // 更新combo widget的值
            comboWidget.value = filename;
            if (comboWidget.callback) {
                comboWidget.callback(filename);
            }
            
            // 完成
            progressBar.style.width = '100%';
            
            // 隐藏进度条
            setTimeout(() => {
                progressContainer.style.display = 'none';
                progressBar.style.width = '0%';
            }, 1000);
            
            console.log(`📁 Successfully uploaded ${uploadType} file: ${filename}`);
            
        } catch (error) {
            console.error('📁 Upload failed:', error);
            alert(`上传失败: ${error.message}`);
            progressContainer.style.display = 'none';
            progressBar.style.width = '0%';
        }
    };
};

// 创建文件选择器
export const createFileSelector = (uploadType, onFileSelected) => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = getAcceptedTypes(uploadType);
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

// 创建自定义上传Widget
export const createCustomUploadWidget = () => {
    return (node, inputName, inputData) => {
        const inputOptions = inputData[1] ?? {};
        const { originalInputName, uploadType } = inputOptions;
        
        // 找到关联的combo widget
        const comboWidget = node.widgets.find(w => w.name === originalInputName);
        if (!comboWidget) {
            console.error(`📁 Could not find combo widget for ${originalInputName}`);
            return { widget: null };
        }

        // 创建进度条元素
        const progressContainer = document.createElement('div');
        progressContainer.className = 'custom-upload-progress';
        progressContainer.style.display = 'none';
        
        const progressBar = document.createElement('div');
        progressBar.className = 'custom-upload-progress-bar';
        progressContainer.appendChild(progressBar);

        // 创建文件上传处理函数
        const handleFileUpload = createFileUploadHandler(uploadType, comboWidget, progressContainer, progressBar);

        // 创建上传按钮
        const uploadWidget = node.addWidget(
            'button',
            inputName,
            `📁 上传${uploadType === 'text' ? '文本' : '配置'}文件`,
            () => {
                createFileSelector(uploadType, handleFileUpload);
            },
            { 
                serialize: false
            }
        );

        // 设置按钮样式
        uploadWidget.element = progressContainer;
        
        console.log(`📁 Added upload widget for ${originalInputName} (${uploadType}) on node ${node.type}`);
        
        return { widget: uploadWidget };
    };
};

// 检查文件类型是否匹配
export const isFileTypeMatching = (file, uploadType) => {
    const acceptedTypes = getAcceptedTypes(uploadType);
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    return acceptedTypes.includes(fileExtension) || acceptedTypes === '*';
};

// 添加拖拽支持到节点
export const addDragAndDropSupport = (node, uploadType) => {
    const canvas = node.graph?.canvas;
    if (!canvas) return;

    const originalOnDrop = canvas.onDrop;
    canvas.onDrop = function(e) {
        // 检查是否拖拽到了我们的节点上
        const canvasPos = app.clientPosToCanvasPos([e.clientX, e.clientY]);
        const nodeAtPos = this.graph.getNodeOnPos(canvasPos[0], canvasPos[1]);
        
        if (nodeAtPos === node && e.dataTransfer.files.length > 0) {
            const file = e.dataTransfer.files[0];
            
            // 检查文件类型
            if (isFileTypeMatching(file, uploadType)) {
                e.preventDefault();
                e.stopPropagation();
                
                console.log(`📁 Drag & drop detected for ${uploadType} file: ${file.name}`);
                
                // 找到上传widget并触发上传
                const uploadWidget = node.widgets.find(w => w.type === 'button' && w.name.includes('upload'));
                if (uploadWidget && uploadWidget.callback) {
                    // 直接处理文件而不是触发文件选择器
                    const comboWidget = node.widgets.find(w => w.name.includes(uploadType));
                    if (comboWidget) {
                        const progressContainer = uploadWidget.element;
                        const progressBar = progressContainer?.querySelector('.custom-upload-progress-bar');
                        if (progressContainer && progressBar) {
                            const handleFileUpload = createFileUploadHandler(uploadType, comboWidget, progressContainer, progressBar);
                            handleFileUpload(file);
                        }
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
    
    console.log(`📁 Added drag & drop support for ${uploadType} files to node ${node.id}`);
};

// 初始化上传功能
export const initUploadCore = () => {
    // 添加上传相关样式
    const styleElement = document.createElement('style');
    styleElement.textContent = uploadStyles;
    document.head.appendChild(styleElement);
    
    console.log("📁 Upload Core module initialized");
};

// 处理上传节点创建
export const handleUploadNodeCreated = (node) => {
    // 检查是否是我们的自定义上传节点
    if (node.type === 'CustomUploadTextNode' || node.type === 'CustomUploadConfigNode') {
        const uploadType = node.type === 'CustomUploadTextNode' ? 'text' : 'config';
        
        // 添加拖拽支持
        setTimeout(() => addDragAndDropSupport(node, uploadType), 100);
        
        console.log(`📁 Enhanced ${node.type} with drag&drop support`);
    }
};

// 检查是否有上传属性的节点并处理
export const processUploadNodes = (nodeType, nodeData) => {
    const { input } = nodeData ?? {};
    const { required } = input ?? {};
    if (!required) return null;

    // 查找带有自定义上传属性的输入
    const foundUpload = Object.entries(required).find(([_, inputSpec]) =>
        isCustomUploadInput(inputSpec)
    );

    if (foundUpload) {
        const [inputName, inputSpec] = foundUpload;
        console.log(`📁 Added custom upload for ${nodeData.name}: ${inputName}`);
        return {
            inputName,
            inputSpec,
            upload: createCustomUploadInput(inputName, inputSpec)
        };
    }
    
    return null;
}; 