/**
 * MolStar核心模块 - 负责MolStar库加载、初始化和3D分子渲染
 * 从custom3DDisplay.js重构而来
 */

// MolStar库加载函数 - ALCHEM独立版本
export async function loadMolstarLibrary() {
    return new Promise(async (resolve) => {
        
        // 强制加载CSS，不管molstar是否已存在
        const molstarCSSPath = "./extensions/ALCHEM_PropBtn/lib/molstar.css";
        
        // 检查CSS是否已加载
        const existingCSS = document.querySelector('link[href*="molstar.css"]');
        if (!existingCSS) {
            
            const link = document.createElement("link");
            link.rel = "stylesheet";
            link.href = molstarCSSPath;
            link.id = "molstar-main-css";
            
            // 等待CSS加载完成
            const cssLoadPromise = new Promise((cssResolve) => {
                link.onload = () => {
                    cssResolve(true);
                };
                link.onerror = () => {
                    console.error("🧪 MolStar CSS加载失败:", molstarCSSPath);
                    cssResolve(false);
                };
            });
            
            document.head.appendChild(link);
            await cssLoadPromise;
        } else {
        }
        
        // 检查是否已加载molstar JS
        if (window.molstar) {
            resolve(true);
            return;
        }
        
        // 加载JS部分
        const molstarJSPath = "./extensions/ALCHEM_PropBtn/lib/molstar.js";
        
        // 加载JS
        const script = document.createElement("script");
        script.src = molstarJSPath;
        script.onload = () => {
            resolve(true);
        };
        script.onerror = (error) => {
            console.error("🧪 ALCHEM MolStar库加载失败:", error);
            resolve(false);
        };
        document.head.appendChild(script);
    });
}

// MolStar查看器类
export class MolstarViewer {
    constructor() {
        this.plugin = null;
        this.container = null;
        this.isInitialized = false;
    }
    
    // 初始化MolStar查看器
    async initialize(container) {
        if (!window.molstar || !container) {
            return false;
        }
        
        this.container = container;
        
        try {
            
            // 创建MolStar查看器实例
            const viewer = await window.molstar.Viewer.create(container, {
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
            
            this.plugin = viewer.plugin;
            this.isInitialized = true;
            
            // 加载默认分子
            await this.loadDefaultMolecule();
            
            return true;
        } catch (error) {
            console.error("🧪 初始化MolStar查看器失败:", error);
            this.isInitialized = false;
            this.showInitializationError(container, error);
            return false;
        }
    }
    
    // 加载默认分子
    async loadDefaultMolecule() {
        if (!this.plugin) return;
        
        try {
            const defaultPDB = `HEADER    BENZENE MOLECULE
COMPND    BENZENE  
ATOM      1  C1  BNZ A   1       0.000   1.400   0.000  1.00  0.00           C
ATOM      2  C2  BNZ A   1       1.212   0.700   0.000  1.00  0.00           C
ATOM      3  C3  BNZ A   1       1.212  -0.700   0.000  1.00  0.00           C
ATOM      4  C4  BNZ A   1       0.000  -1.400   0.000  1.00  0.00           C
ATOM      5  C5  BNZ A   1      -1.212  -0.700   0.000  1.00  0.00           C
ATOM      6  C6  BNZ A   1      -1.212   0.700   0.000  1.00  0.00           C
CONNECT    1    2    6
CONNECT    2    1    3
CONNECT    3    2    4
CONNECT    4    3    5
CONNECT    5    4    6
CONNECT    6    1    5
END`;
            
            await this.plugin.clear();
            
            const dataObj = await this.plugin.builders.data.rawData({
                data: defaultPDB,
                label: 'benzene_default'
            });
            
            const trajectory = await this.plugin.builders.structure.parseTrajectory(dataObj, 'pdb');
            await this.plugin.builders.structure.hierarchy.applyPreset(trajectory, 'default');
            
        } catch (error) {
        }
    }
    
    // 显示分子数据
    async displayMolecularData(molecularContent, analysis = null) {
        if (!this.plugin || !this.container) {
            return;
        }
        
        try {
            let pdbData = null;
            let molecularInfo = null;
            
            // 智能检测数据类型
            if (typeof molecularContent === 'string') {
                if (molecularContent.includes('HEADER') || molecularContent.includes('ATOM') || molecularContent.includes('HETATM')) {
                    // 直接PDB数据
                    pdbData = molecularContent;
                    molecularInfo = {
                        pdbData: pdbData,
                        title: analysis?.title || analysis?.filename || 'molecule',
                        originalContent: molecularContent
                    };
                } else {
                    // HTML数据，需要提取
                    molecularInfo = this.extractMolecularInfo(molecularContent);
                    pdbData = molecularInfo?.pdbData;
                }
            } else {
                return;
            }
            
            if (pdbData && pdbData.trim()) {
                
                // 清除当前显示
                await this.plugin.clear();
                
                // 创建数据对象
                const dataObj = await this.plugin.builders.data.rawData({
                    data: pdbData,
                    label: molecularInfo.title || 'molecule'
                });
                
                // 解析轨迹
                const trajectory = await this.plugin.builders.structure.parseTrajectory(dataObj, 'pdb');
                
                // 应用预设
                await this.plugin.builders.structure.hierarchy.applyPreset(trajectory, 'default');
                
                
            } else {
                // 不显示错误信息，直接跳过
            }
            
        } catch (error) {
            console.error("🧪 MolStar渲染失败:", error);
            // 不显示错误信息，让MolStar继续显示默认内容
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
            return null;
        }
    }
    
    // 在查看器中显示错误 - 已禁用，不显示错误信息
    showErrorInViewer(errorMessage) {
        // 什么都不做，避免错误信息挡住界面
    }
    
    // 显示初始化错误 - 已禁用，不显示错误信息
    showInitializationError(container, error) {
        // 什么都不做，避免错误信息挡住界面
    }
    
    // 重置视角
    resetView() {
        if (this.plugin && this.plugin.canvas3d) {
            try {
                this.plugin.canvas3d.requestCameraReset();
            } catch (error) {
            }
        }
    }
    
    // 切换线框模式（简化实现）
    toggleWireframe() {
        if (this.plugin) {
            try {
                // 这是一个简化的实现，真实的线框切换需要更复杂的逻辑
                // 在实际应用中，这里需要访问MolStar的representation系统
            } catch (error) {
            }
        }
    }
    
    // 清理资源
    destroy() {
        if (this.plugin) {
            try {
                this.plugin.dispose();
            } catch (error) {
            }
        }
        this.plugin = null;
        this.container = null;
        this.isInitialized = false;
    }
}

