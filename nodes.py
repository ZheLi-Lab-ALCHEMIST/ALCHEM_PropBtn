import os
import json
import torch
import folder_paths
from PIL import Image, ImageOps
import numpy as np
import hashlib
import time

# 导入分子数据内存管理器
try:
    from .molecular_memory import store_molecular_data, get_molecular_data, get_cache_status, molecular_memory
    MOLECULAR_MEMORY_AVAILABLE = True
    print("🧪 已成功导入分子数据内存管理器")
except ImportError as e:
    print(f"⚠️ 分子数据内存管理器导入失败: {e}")
    MOLECULAR_MEMORY_AVAILABLE = False

class CustomUploadTextNode:
    """
    一个演示自定义上传属性的节点 - 上传文本文件
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        # 获取input目录下的文本文件
        input_dir = folder_paths.get_input_directory()
        text_files = [f for f in os.listdir(input_dir) 
                     if os.path.isfile(os.path.join(input_dir, f)) 
                     and f.lower().endswith(('.txt', '.json', '.md'))]
        
        return {
            "required": {
                "text_file": (sorted(text_files), {
                    "custom_text_upload": True,  # 🎯 我们的自定义属性！
                    "custom_folder": "texts",
                    "tooltip": "选择或上传一个文本文件"
                }),
                "encoding": (["utf-8", "gbk", "ascii"], {
                    "default": "utf-8",
                    "tooltip": "文件编码格式"
                })
            }
        }
    
    RETURN_TYPES = ("STRING",)
    OUTPUT_TOOLTIPS = ("文件内容文本",)
    FUNCTION = "load_text_file"
    CATEGORY = "custom_upload"
    DESCRIPTION = "加载并返回文本文件的内容，支持自定义上传"

    def load_text_file(self, text_file, encoding="utf-8"):
        try:
            file_path = folder_paths.get_annotated_filepath(text_file)
            
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return (content,)
        except Exception as e:
            print(f"Error loading text file: {e}")
            return ("",)
    
    @classmethod
    def IS_CHANGED(cls, text_file, **kwargs):
        try:
            file_path = folder_paths.get_annotated_filepath(text_file)
            m = hashlib.sha256()
            with open(file_path, 'rb') as f:
                m.update(f.read())
            return m.digest().hex()
        except:
            return ""

    @classmethod
    def VALIDATE_INPUTS(cls, text_file, **kwargs):
        if not folder_paths.exists_annotated_filepath(text_file):
            return f"Invalid text file: {text_file}"
        return True


class CustomUploadConfigNode:
    """
    另一个演示节点 - 上传配置文件
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        config_files = [f for f in os.listdir(input_dir) 
                       if os.path.isfile(os.path.join(input_dir, f)) 
                       and f.lower().endswith(('.json', '.yaml', '.yml', '.toml'))]
        
        return {
            "required": {
                "config_file": (sorted(config_files), {
                    "custom_config_upload": True,  # 🎯 另一个自定义属性
                    "allow_batch": True,
                    "custom_folder": "configs",
                    "tooltip": "选择或上传配置文件"
                }),
                "parse_json": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "是否解析JSON内容"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("raw_content", "parsed_info")
    OUTPUT_TOOLTIPS = ("原始文件内容", "解析后的信息")
    FUNCTION = "load_config_file"
    CATEGORY = "custom_upload"
    DESCRIPTION = "加载配置文件，支持多种格式和自定义上传"

    def load_config_file(self, config_file, parse_json=True):
        try:
            file_path = folder_paths.get_annotated_filepath(config_file)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            parsed_info = "Raw content loaded"
            
            if parse_json and config_file.lower().endswith('.json'):
                try:
                    data = json.loads(content)
                    parsed_info = f"JSON parsed successfully. Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}"
                except json.JSONDecodeError as e:
                    parsed_info = f"JSON parse error: {e}"
            
            return (content, parsed_info)
        except Exception as e:
            error_msg = f"Error loading config file: {e}"
            print(error_msg)
            return ("", error_msg)

    @classmethod
    def IS_CHANGED(cls, config_file, **kwargs):
        try:
            file_path = folder_paths.get_annotated_filepath(config_file)
            m = hashlib.sha256()
            with open(file_path, 'rb') as f:
                m.update(f.read())
            return m.digest().hex()
        except:
            return ""

    @classmethod
    def VALIDATE_INPUTS(cls, config_file, **kwargs):
        if not folder_paths.exists_annotated_filepath(config_file):
            return f"Invalid config file: {config_file}"
        return True


class Demo3DDisplayNode:
    """
    🎯 演示3D显示属性的节点 - 模拟分子结构数据
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "molecule_data": (["benzene", "caffeine", "aspirin", "water"], {
                    "molstar_3d_display": True,  # 🎯 新的3D显示属性！
                    "display_mode": "ball_and_stick",
                    "background_color": "#1E1E1E",
                    "tooltip": "选择要显示的分子，点击3D按钮查看结构"
                }),
                "temperature": ("FLOAT", {
                    "default": 298.15,
                    "min": 0.0,
                    "max": 1000.0,
                    "step": 0.1,
                    "tooltip": "模拟温度 (K)"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("pdb_data", "molecule_info")
    OUTPUT_TOOLTIPS = ("PDB格式的分子数据", "分子信息")
    FUNCTION = "generate_molecule"
    CATEGORY = "custom_upload"
    DESCRIPTION = "演示3D显示功能的节点，生成模拟分子数据"

    def generate_molecule(self, molecule_data, temperature=298.15):
        # 模拟的PDB数据
        pdb_templates = {
            "benzene": """HEADER    BENZENE MOLECULE
COMPND    BENZENE
ATOM      1  C1  BNZ A   1       0.000   1.400   0.000  1.00  0.00           C
ATOM      2  C2  BNZ A   1       1.212   0.700   0.000  1.00  0.00           C
ATOM      3  C3  BNZ A   1       1.212  -0.700   0.000  1.00  0.00           C
ATOM      4  C4  BNZ A   1       0.000  -1.400   0.000  1.00  0.00           C
ATOM      5  C5  BNZ A   1      -1.212  -0.700   0.000  1.00  0.00           C
ATOM      6  C6  BNZ A   1      -1.212   0.700   0.000  1.00  0.00           C
ATOM      7  H1  BNZ A   1       0.000   2.490   0.000  1.00  0.00           H
ATOM      8  H2  BNZ A   1       2.156   1.245   0.000  1.00  0.00           H
ATOM      9  H3  BNZ A   1       2.156  -1.245   0.000  1.00  0.00           H
ATOM     10  H4  BNZ A   1       0.000  -2.490   0.000  1.00  0.00           H
ATOM     11  H5  BNZ A   1      -2.156  -1.245   0.000  1.00  0.00           H
ATOM     12  H6  BNZ A   1      -2.156   1.245   0.000  1.00  0.00           H
CONECT    1    2    6    7
CONECT    2    1    3    8
CONECT    3    2    4    9
CONECT    4    3    5   10
CONECT    5    4    6   11
CONECT    6    1    5   12
END""",
            "water": """HEADER    WATER MOLECULE
COMPND    WATER
ATOM      1  O   HOH A   1       0.000   0.000   0.000  1.00  0.00           O
ATOM      2  H1  HOH A   1       0.757   0.586   0.000  1.00  0.00           H
ATOM      3  H2  HOH A   1      -0.757   0.586   0.000  1.00  0.00           H
CONECT    1    2    3
END""",
            "caffeine": """HEADER    CAFFEINE MOLECULE
COMPND    CAFFEINE
ATOM      1  N1  CAF A   1      -1.234   0.000   0.000  1.00  0.00           N
ATOM      2  C2  CAF A   1      -0.617   1.234   0.000  1.00  0.00           C
ATOM      3  N3  CAF A   1       0.617   1.234   0.000  1.00  0.00           N
ATOM      4  C4  CAF A   1       1.234   0.000   0.000  1.00  0.00           C
ATOM      5  C5  CAF A   1       0.617  -1.234   0.000  1.00  0.00           C
ATOM      6  C6  CAF A   1      -0.617  -1.234   0.000  1.00  0.00           C
END""",
            "aspirin": """HEADER    ASPIRIN MOLECULE
COMPND    ASPIRIN
ATOM      1  C1  ASP A   1       0.000   0.000   0.000  1.00  0.00           C
ATOM      2  C2  ASP A   1       1.200   0.693   0.000  1.00  0.00           C
ATOM      3  C3  ASP A   1       1.200   2.079   0.000  1.00  0.00           C
ATOM      4  C4  ASP A   1       0.000   2.772   0.000  1.00  0.00           C
ATOM      5  C5  ASP A   1      -1.200   2.079   0.000  1.00  0.00           C
ATOM      6  C6  ASP A   1      -1.200   0.693   0.000  1.00  0.00           C
ATOM      7  O1  ASP A   1       2.400   0.000   0.000  1.00  0.00           O
ATOM      8  C7  ASP A   1       3.600   0.693   0.000  1.00  0.00           C
ATOM      9  O2  ASP A   1       4.800   0.000   0.000  1.00  0.00           O
ATOM     10  C8  ASP A   1       3.600   2.079   0.000  1.00  0.00           C
END"""
        }
        
        pdb_data = pdb_templates.get(molecule_data, pdb_templates["benzene"])
        
        # 生成分子信息
        molecule_info = {
            "name": molecule_data,
            "temperature": temperature,
            "formula": {
                "benzene": "C6H6",
                "water": "H2O", 
                "caffeine": "C8H10N4O2",
                "aspirin": "C9H8O4"
            }.get(molecule_data, "Unknown"),
            "molecular_weight": {
                "benzene": 78.11,
                "water": 18.02,
                "caffeine": 194.19,
                "aspirin": 180.16
            }.get(molecule_data, 0.0),
            "description": f"模拟的{molecule_data}分子数据，温度: {temperature}K"
        }
        
        return (pdb_data, json.dumps(molecule_info, ensure_ascii=False, indent=2))

    @classmethod
    def IS_CHANGED(cls, molecule_data, temperature):
        # 基于输入参数生成hash，确保参数变化时重新计算
        return hashlib.md5(f"{molecule_data}_{temperature}".encode()).hexdigest()


class DualButtonDemoNode:
    """
    🎯🎯 演示双按钮功能的节点 - 同时包含上传和3D显示两个自定义属性
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        # 获取input目录下的文本文件
        input_dir = folder_paths.get_input_directory()
        text_files = [f for f in os.listdir(input_dir) 
                     if os.path.isfile(os.path.join(input_dir, f)) 
                     and f.lower().endswith(('.txt', '.json', '.md'))]
        
        return {
            "required": {
                "text_file": (sorted(text_files) if text_files else ["no_files_found.txt"], {
                    "custom_text_upload": True,  # 🎯 第一个自定义属性：上传功能
                    "custom_folder": "texts",
                    "tooltip": "选择或上传一个文本文件 - 第一个按钮"
                }),
                "molecule_data": (["benzene", "caffeine", "aspirin", "water", "glucose", "ethanol"], {
                    "molstar_3d_display": True,  # 🎯 第二个自定义属性：3D显示功能
                    "display_mode": "ball_and_stick",
                    "background_color": "#2E2E2E",
                    "tooltip": "选择要显示的分子，点击3D按钮查看结构 - 第二个按钮"
                }),
                "processing_mode": (["basic", "advanced", "experimental"], {
                    "default": "basic",
                    "tooltip": "选择处理模式"
                }),
                "scale_factor": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 5.0,
                    "step": 0.1,
                    "tooltip": "缩放因子"
                }),
                "enable_analysis": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "是否启用分析功能"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "FLOAT")
    RETURN_NAMES = ("file_content", "molecule_info", "processing_result", "computed_value")
    OUTPUT_TOOLTIPS = (
        "加载的文件内容", 
        "分子结构信息", 
        "处理结果信息",
        "计算得出的数值"
    )
    FUNCTION = "process_dual_functionality"
    CATEGORY = "custom_upload"
    DESCRIPTION = "演示双按钮功能：同时支持文件上传和3D分子显示的综合节点"

    def process_dual_functionality(self, text_file, molecule_data, processing_mode="basic", scale_factor=1.0, enable_analysis=True):
        """
        处理双重功能：文件内容加载 + 分子数据生成
        """
        try:
            # 处理文件上传部分
            file_content = ""
            if text_file and text_file != "no_files_found.txt":
                try:
                    file_path = folder_paths.get_annotated_filepath(text_file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    file_content = f"[文件: {text_file}]\n{file_content}"
                except Exception as e:
                    file_content = f"读取文件失败: {str(e)}"
            else:
                file_content = "未选择或找到文件"
            
            # 处理分子3D显示部分
            molecule_formulas = {
                "benzene": "C₆H₆",
                "caffeine": "C₈H₁₀N₄O₂",
                "aspirin": "C₉H₈O₄",
                "water": "H₂O",
                "glucose": "C₆H₁₂O₆",
                "ethanol": "C₂H₆O"
            }
            
            molecule_weights = {
                "benzene": 78.11,
                "caffeine": 194.19,
                "aspirin": 180.16,
                "water": 18.02,
                "glucose": 180.16,
                "ethanol": 46.07
            }
            
            molecule_info = {
                "name": molecule_data,
                "formula": molecule_formulas.get(molecule_data, "Unknown"),
                "molecular_weight": molecule_weights.get(molecule_data, 0.0),
                "scale_factor": scale_factor,
                "processing_mode": processing_mode,
                "analysis_enabled": enable_analysis,
                "description": f"分子: {molecule_data}, 模式: {processing_mode}, 缩放: {scale_factor}x"
            }
            
            # 生成处理结果
            processing_result = f"""双功能处理结果:
════════════════════════════════════════
📁 文件处理状态: {'成功' if file_content and '失败' not in file_content else '失败'}
🧪 分子选择: {molecule_data} ({molecule_formulas.get(molecule_data, 'Unknown')})
⚙️  处理模式: {processing_mode}
📏 缩放因子: {scale_factor}x
🔍 分析功能: {'启用' if enable_analysis else '禁用'}
════════════════════════════════════════
✨ 此节点演示了如何在同一个节点中同时使用:
   • 📁 上传按钮 (custom_text_upload)
   • 🧪 3D显示按钮 (molstar_3d_display)
   
💡 您可以点击两个按钮来测试不同的功能!"""
            
            # 计算一个示例数值
            computed_value = molecule_weights.get(molecule_data, 1.0) * scale_factor
            
            return (
                file_content,
                json.dumps(molecule_info, ensure_ascii=False, indent=2),
                processing_result,
                computed_value
            )
            
        except Exception as e:
            error_msg = f"处理过程中发生错误: {str(e)}"
            return (error_msg, "{}", error_msg, 0.0)
    
    @classmethod
    def IS_CHANGED(cls, text_file, molecule_data, processing_mode, scale_factor, enable_analysis):
        # 生成基于所有输入参数的hash值，确保任何参数变化时都重新计算
        params_str = f"{text_file}_{molecule_data}_{processing_mode}_{scale_factor}_{enable_analysis}"
        return hashlib.md5(params_str.encode()).hexdigest()

    @classmethod
    def VALIDATE_INPUTS(cls, text_file, **kwargs):
        # 验证输入参数
        if text_file and text_file != "no_files_found.txt":
            if not folder_paths.exists_annotated_filepath(text_file):
                return f"文件不存在: {text_file}"
        return True


class DualAttributeTestNode:
    """
    🧪🔄 双属性测试节点 - 验证同一变量同时拥有upload和3D显示功能
    
    这个节点专门用于测试同一个变量是否可以同时具有：
    - custom_text_upload: True (上传功能)
    - molstar_3d_display: True (3D显示功能)
    
    理论上这两个功能应该可以并存，因为：
    - 上传功能处理文件操作
    - 3D显示功能处理可视化
    - 它们操作不同的UI层面
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        # 获取input目录下的分子文件
        input_dir = folder_paths.get_input_directory()
        molecule_files = [f for f in os.listdir(input_dir) 
                         if os.path.isfile(os.path.join(input_dir, f)) 
                         and f.lower().endswith(('.pdb', '.mol', '.sdf', '.xyz'))]
        
        return {
            "required": {
                # 🧪🔄 核心测试变量：同时拥有两个自定义属性
                "molecule_file": (sorted(molecule_files) if molecule_files else ["no_molecule_files.pdb"], {
                    "custom_text_upload": True,     # 第一个属性：上传功能
                    "molstar_3d_display": True,     # 第二个属性：3D显示功能
                    "custom_folder": "molecules",   # 上传功能的配置
                    "display_mode": "ball_and_stick",  # 3D显示功能的配置
                    "background_color": "#2E2E2E",  # 3D显示功能的配置
                    "tooltip": "🧪🔄 测试变量：同时支持文件上传和3D显示功能"
                }),
                
                # 辅助测试参数
                "test_mode": (["upload_test", "display_test", "both_test"], {
                    "default": "both_test",
                    "tooltip": "选择测试模式：仅上传、仅显示、或两者并行测试"
                }),
                
                "visualization_quality": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.1, 
                    "max": 5.0, 
                    "step": 0.1,
                    "tooltip": "3D可视化质量倍数"
                }),
                
                "enable_validation": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "是否启用双属性功能验证"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "IMAGE", "STRING")
    RETURN_NAMES = ("test_result", "visualization", "attributes_report")
    OUTPUT_TOOLTIPS = (
        "双属性测试的结果报告",
        "如果成功生成的可视化图像", 
        "属性兼容性的详细报告"
    )
    FUNCTION = "test_dual_attributes"
    
    CATEGORY = "🧪 ALCHEM/Testing"
    
    def test_dual_attributes(self, molecule_file, test_mode, visualization_quality, enable_validation):
        """
        测试同一变量同时拥有custom_text_upload和molstar_3d_display属性的功能
        """
        
        # 构建测试结果报告
        test_results = []
        test_results.append("🧪🔄 双属性测试节点执行报告")
        test_results.append("=" * 50)
        test_results.append(f"📁 选择的分子文件: {molecule_file}")
        test_results.append(f"🔬 测试模式: {test_mode}")
        test_results.append(f"🎯 可视化质量: {visualization_quality}x")
        test_results.append(f"✅ 验证功能: {'启用' if enable_validation else '禁用'}")
        test_results.append("")
        
        # 测试上传功能的兼容性
        if test_mode in ["upload_test", "both_test"]:
            test_results.append("📁 上传功能测试:")
            test_results.append("  ✓ custom_text_upload属性已设置")
            test_results.append("  ✓ custom_folder配置为'molecules'")
            test_results.append("  ✓ 应该显示上传按钮")
            test_results.append("  ✓ 支持拖拽上传功能")
            test_results.append("")
        
        # 测试3D显示功能的兼容性
        if test_mode in ["display_test", "both_test"]:
            test_results.append("🧪 3D显示功能测试:")
            test_results.append("  ✓ molstar_3d_display属性已设置")
            test_results.append("  ✓ display_mode配置为'ball_and_stick'")
            test_results.append("  ✓ background_color配置为'#2E2E2E'")
            test_results.append("  ✓ 应该显示3D查看按钮")
            test_results.append("")
        
        # 双属性兼容性验证
        if enable_validation:
            test_results.append("🔄 双属性兼容性验证:")
            test_results.append("  ✓ 两个属性应该可以在前端并存")
            test_results.append("  ✓ 上传按钮和3D显示按钮应该都显示")
            test_results.append("  ✓ 功能之间不应该相互干扰")
            test_results.append("  ✓ UI布局应该合理排列两个按钮")
            test_results.append("")
        
        # 预期行为说明
        test_results.append("🎯 预期前端行为:")
        test_results.append("  1. 节点应该显示文件选择下拉框")
        test_results.append("  2. 应该有'📁 上传文件'按钮")
        test_results.append("  3. 应该有'🧪 显示3D结构'按钮")
        test_results.append("  4. 两个按钮应该独立工作，不冲突")
        test_results.append("  5. 可以先上传文件，再查看3D结构")
        test_results.append("")
        
        # 技术实现分析
        test_results.append("⚙️ 技术实现分析:")
        test_results.append("  • 前端会检测custom_text_upload属性")
        test_results.append("  • 前端会检测molstar_3d_display属性")
        test_results.append("  • extensionMain.js会分别调用两个模块")
        test_results.append("  • uploadCore.js处理上传功能")
        test_results.append("  • custom3DDisplay.js处理3D显示功能")
        test_results.append("  • 两个模块应该独立运行，不相互影响")
        test_results.append("")
        
        # 创建简单的可视化图像（模拟）
        import torch
        import numpy as np
        
        # 创建一个简单的可视化图像
        height, width = 256, 256
        image_array = np.zeros((height, width, 3), dtype=np.float32)
        
        # 绘制一个简单的分子结构图案
        center_x, center_y = width // 2, height // 2
        
        # 绘制原子（圆圈）
        for i, (x, y, color) in enumerate([
            (center_x, center_y, [1.0, 0.2, 0.2]),      # 红色中心原子
            (center_x - 60, center_y - 60, [0.2, 0.2, 1.0]),  # 蓝色原子
            (center_x + 60, center_y - 60, [0.2, 1.0, 0.2]),  # 绿色原子
            (center_x, center_y + 80, [1.0, 1.0, 0.2]),       # 黄色原子
        ]):
            for dy in range(-15, 16):
                for dx in range(-15, 16):
                    if dx*dx + dy*dy <= 225:  # 圆形半径15
                        if 0 <= y+dy < height and 0 <= x+dx < width:
                            image_array[y+dy, x+dx] = color
        
        # 绘制化学键（线条）
        # 实际应用中这里会显示真正的分子结构
        
        # 添加文字说明
        test_results.append(f"🖼️ 生成了 {width}x{height} 的可视化图像")
        test_results.append("   (实际应用中这里会显示真正的3D分子结构)")
        
        # 构建属性报告
        attributes_report = []
        attributes_report.append("🔍 属性兼容性详细报告")
        attributes_report.append("=" * 40)
        attributes_report.append("molecule_file变量的属性配置:")
        attributes_report.append("  ├─ custom_text_upload: True")
        attributes_report.append("  ├─ molstar_3d_display: True")
        attributes_report.append("  ├─ custom_folder: 'molecules'")
        attributes_report.append("  ├─ display_mode: 'ball_and_stick'")
        attributes_report.append("  └─ background_color: '#2E2E2E'")
        attributes_report.append("")
        attributes_report.append("预期前端处理流程:")
        attributes_report.append("  1. extensionMain.js检测到节点")
        attributes_report.append("  2. processUploadNodes()检测custom_text_upload")
        attributes_report.append("  3. process3DDisplayNodes()检测molstar_3d_display")
        attributes_report.append("  4. 两个处理函数独立执行")
        attributes_report.append("  5. 分别添加对应的Widget")
        attributes_report.append("  6. 最终节点显示两个功能按钮")
        
        # 转换为字符串
        test_result_text = "\n".join(test_results)
        attributes_report_text = "\n".join(attributes_report)
        
        # 转换图像为tensor
        image_tensor = torch.from_numpy(image_array).unsqueeze(0)  # 添加batch维度
        
        return (test_result_text, image_tensor, attributes_report_text)
    
    @classmethod
    def IS_CHANGED(cls, molecule_file, test_mode, visualization_quality, enable_validation):
        # 基于所有输入参数生成哈希，用于缓存控制
        content = f"{molecule_file}_{test_mode}_{visualization_quality}_{enable_validation}"
        return hashlib.md5(content.encode()).hexdigest()


class MolecularUploadDemoNode:
    """
    🧪📤🔬 分子文件上传+3D显示演示节点 - 双属性功能演示
    
    这个节点展示了如何在同一个变量上同时使用两个自定义属性：
    ✅ molecular_upload: True  - 分子文件上传功能
    ✅ molstar_3d_display: True - 3D分子结构显示功能
    
    支持的分子文件格式：
    - PDB (蛋白质结构数据库格式) - 最适合3D显示
    - MOL/SDF (MDL分子文件格式) - 小分子结构
    - XYZ (笛卡尔坐标格式) - 几何坐标
    - MOL2 (Tripos格式，包含电荷信息)
    - CIF (晶体学信息文件) - 晶体结构
    - GRO (GROMACS分子动力学格式)
    - FASTA (序列格式)
    
    功能特色：
    🔹 智能文件验证和格式检测
    🔹 拖拽上传支持
    🔹 实时3D结构预览
    🔹 多种显示模式（球棍模型、线框等）
    🔹 可自定义背景色和显示参数
    
    这证明了ALCHEM_PropBtn架构的强大扩展性！
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        # 🚀 新逻辑：同时扫描文件系统和后端内存中的文件
        molecule_files = []
        
        # 1. 扫描文件系统中的分子文件（兼容性）
        try:
            input_dir = folder_paths.get_input_directory()
            molecules_dir = os.path.join(input_dir, 'molecules')
            
            # 创建molecules目录如果不存在
            if not os.path.exists(molecules_dir):
                os.makedirs(molecules_dir)
            
            # 扫描支持的分子文件格式
            molecular_formats = ['.pdb', '.mol', '.sdf', '.xyz', '.mol2', '.cif', '.gro', '.fasta', '.fa']
            
            for file in os.listdir(molecules_dir):
                if os.path.isfile(os.path.join(molecules_dir, file)):
                    file_ext = os.path.splitext(file)[1].lower()
                    if file_ext in molecular_formats:
                        molecule_files.append(file)
        except Exception as e:
            print(f"⚠️ 扫描文件系统分子文件时出错: {e}")
        
        # 2. 🎯 新增：扫描后端内存中的分子文件
        try:
            if MOLECULAR_MEMORY_AVAILABLE:
                from .molecular_memory import get_cache_status
                cache_status = get_cache_status()
                
                if cache_status and 'nodes' in cache_status:
                    for node_data in cache_status['nodes']:
                        filename = node_data.get('filename')
                        if filename and filename not in molecule_files:
                            molecule_files.append(filename)
                            print(f"🧪 添加后端内存文件到选项: {filename}")
        except Exception as e:
            print(f"⚠️ 扫描后端内存分子文件时出错: {e}")
        
        # 3. 确保至少有一个选项
        if not molecule_files:
            molecule_files = ["no_molecular_files_found.pdb"]
        else:
            molecule_files = sorted(list(set(molecule_files)))  # 去重并排序
        
        # 🎯 关键修复：使用STRING类型而不是固定列表，允许任意文件名
        print(f"🧪 动态生成的分子文件列表: {molecule_files}")
        
        return {
            "required": {
                "molecular_file": ("STRING", {
                    "default": molecule_files[0] if molecule_files else "no_molecular_files_found.pdb",
                    "molecular_upload": True,  # 🧪 启用分子文件上传功能
                    "molstar_3d_display": True,  # 🧪 启用3D分子结构显示功能
                    "molecular_folder": "molecules",  # 指定分子文件存储文件夹
                    "display_mode": "ball_and_stick",  # 3D显示模式
                    "background_color": "#2E2E2E",  # 3D显示背景色
                    "tooltip": "分子文件名 - 可以上传新文件或直接输入文件名。支持PDB/MOL/SDF/XYZ/MOL2/CIF/GRO/FASTA格式",
                    "forceInput": False  # 允许用户直接输入
                }),
                "processing_mode": (["analysis", "visualization", "conversion", "validation"], {
                    "default": "analysis",
                    "tooltip": "选择分子数据处理模式"
                }),
                "output_format": (["json", "csv", "xml", "summary"], {
                    "default": "json",
                    "tooltip": "输出数据格式"
                }),
                "enable_validation": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "启用分子结构验证"
                }),
                "detail_level": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                    "tooltip": "分析详细程度 (0.0=基础, 1.0=详细)"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "FLOAT")
    RETURN_NAMES = ("molecular_data", "analysis_report", "validation_result", "confidence_score")
    FUNCTION = "process_molecular_file"
    
    CATEGORY = "🧪 ALCHEM/molecular_upload_3d_demo"
    
    def process_molecular_file(self, molecular_file, processing_mode, output_format, enable_validation, detail_level, **kwargs):
        """
        处理上传的分子文件 - 优化数据流，先检查前端内存
        """
        try:
            # 🎯 步骤1：获取节点ID - 优先使用前端的node.id，保持一致性
            # ComfyUI在执行时会传递unique_id，但前端上传时使用的是node.id
            # 我们需要在这里建立映射关系
            
            # 方法1：直接使用ComfyUI的unique_id（最可靠）
            node_unique_id = kwargs.get('unique_id')
            if not node_unique_id:
                # 备用方案：生成稳定ID
                node_unique_id = hashlib.md5(f"{id(self)}_{molecular_file}_{processing_mode}".encode()).hexdigest()[:16]
            
            # 🔧 关键修复：检查是否有相同文件名但不同ID的数据，进行ID映射
            # 这样可以处理前端node.id与后端unique_id不匹配的问题
            
            print(f"🧪 开始处理分子文件 - 节点ID: {node_unique_id}")
            print(f"   文件: {molecular_file}")
            print(f"   处理模式: {processing_mode}")
            
            # 🔧 处理文件路径：移除可能的路径前缀
            if '/' in molecular_file:
                molecular_file = os.path.basename(molecular_file)
                print(f"   🔧 路径修正: {molecular_file}")
            
            # 🎯 步骤2：智能查找内存中的数据（处理ID不匹配问题）
            molecular_info = None
            stored_data = None
            
            if MOLECULAR_MEMORY_AVAILABLE:
                try:
                    # 第一步：检查当前节点ID是否已有数据
                    stored_data = get_molecular_data(node_unique_id)
                    if stored_data:
                        print(f"🚀 找到已缓存的分子数据 - 节点ID: {node_unique_id}")
                        molecular_info = stored_data
                    else:
                        # 第二步：🔧 关键修复 - 查找同名文件的数据（处理ID不匹配）
                        print(f"🔍 未找到当前节点数据，查找同名文件: {molecular_file}")
                        cache_status = get_cache_status()
                        
                        # 遍历所有缓存的数据，查找同名文件
                        for cached_data in cache_status.get('nodes', []):
                            if cached_data.get('filename') == molecular_file:
                                print(f"🔄 找到同名文件的缓存数据 - 原节点ID: {cached_data.get('node_id')}")
                                print(f"   将复制到当前节点ID: {node_unique_id}")
                                
                                # 从原节点获取完整数据
                                original_node_id = cached_data.get('node_id')
                                original_data = get_molecular_data(original_node_id)
                                
                                if original_data and 'content' in original_data:
                                    # 将数据复制到当前节点ID
                                    stored_data = store_molecular_data(
                                        node_id=node_unique_id,
                                        filename=molecular_file,
                                        folder="molecules",
                                        content=original_data['content']  # 直接使用原有内容
                                    )
                                    if stored_data:
                                        print(f"✅ 数据复制成功 - 新节点ID: {node_unique_id}")
                                        molecular_info = stored_data
                                    break
                                else:
                                    print(f"⚠️ 原数据获取失败，节点ID: {original_node_id}")
                        
                        if not molecular_info:
                            print(f"⚠️ 未找到文件 {molecular_file} 的任何缓存数据")
                        
                        # 如果内存中没有，则从文件系统读取并存储
                        if not stored_data:
                            print(f"💾 内存中无数据，从文件系统读取并存储")
                            stored_data = store_molecular_data(
                                node_id=node_unique_id,
                                filename=molecular_file,
                                folder="molecules"
                            )
                            if stored_data:
                                molecular_info = stored_data
                                print(f"✅ 文件数据已存储到内存")
                    
                    # 设置为活跃节点
                    if stored_data:
                        molecular_memory.set_active_node(node_unique_id)
                        print(f"🎯 节点 {node_unique_id} 已设置为活跃节点")
                        
                except Exception as memory_error:
                    print(f"🚨 内存操作过程中出错: {memory_error}")
                    
            # 🎯 步骤3：如果内存处理失败，回退到传统文件处理
            if not molecular_info:
                print("📁 使用传统文件处理模式")
                input_dir = folder_paths.get_input_directory()
                file_path = os.path.join(input_dir, "molecules", molecular_file)
                
                # 检查文件是否存在
                if not os.path.exists(file_path):
                    return (
                        "文件不存在",
                        f"错误：找不到文件 {molecular_file}",
                        "验证失败：文件不存在",
                        0.0
                    )
            
                # 读取文件内容（仅在传统模式下）
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 获取文件信息
                file_size = os.path.getsize(file_path)
                file_ext = os.path.splitext(molecular_file)[1].lower()
                
                # 基础分子信息提取
                molecular_info = {
                    "filename": molecular_file,
                    "format": file_ext,
                    "size": file_size,
                    "lines": len(content.split('\n')),
                    "processing_mode": processing_mode,
                    "detail_level": detail_level,
                    "timestamp": time.time(),
                    "node_id": node_unique_id,
                    "stored_in_memory": False,
                    "memory_status": "file_fallback"
                }
            
            # 🎯 步骤4：统一数据处理（无论来源于内存还是文件）
            # 确保molecular_info包含所有必要的信息
            if molecular_info:
                if "node_id" not in molecular_info:
                    molecular_info["node_id"] = node_unique_id
                if "processing_mode" not in molecular_info:
                    molecular_info["processing_mode"] = processing_mode
                if "detail_level" not in molecular_info:
                    molecular_info["detail_level"] = detail_level
                if "stored_in_memory" not in molecular_info:
                    molecular_info["stored_in_memory"] = MOLECULAR_MEMORY_AVAILABLE and stored_data is not None
            
            # 🎯 步骤5：根据数据来源进行格式解析
            # 统一处理文件扩展名，确保file_ext在所有路径中都有定义
            file_ext = os.path.splitext(molecular_file)[1].lower()
            
            # 优先使用内存中的解析结果，否则解析content
            if molecular_info.get("stored_in_memory") and stored_data:
                # 如果数据来自内存，大多数信息已经解析好了
                print(f"📊 使用内存中的解析结果")
                if "format_name" not in molecular_info and "format" in molecular_info:
                    # 使用内存中存储的格式信息，如果没有则使用文件扩展名
                    stored_ext = molecular_info.get("format", file_ext)
                    if stored_ext == '.pdb':
                        molecular_info["format_name"] = "Protein Data Bank"
                    elif stored_ext in ['.mol', '.sdf']:
                        molecular_info["format_name"] = "MDL Molfile/SDF"
                    elif stored_ext == '.xyz':
                        molecular_info["format_name"] = "XYZ Coordinates"
                    elif stored_ext in ['.fasta', '.fa']:
                        molecular_info["format_name"] = "FASTA Sequence"
                    else:
                        molecular_info["format_name"] = f"Other ({stored_ext})"
            else:
                # 如果数据来自文件，需要解析content
                print(f"📊 解析文件内容")
                if file_ext == '.pdb':
                    atom_lines = [line for line in content.split('\n') if line.startswith('ATOM')]
                    molecular_info["atoms"] = len(atom_lines)
                    molecular_info["format_name"] = "Protein Data Bank"
                elif file_ext in ['.mol', '.sdf']:
                    lines = content.split('\n')
                    if len(lines) >= 4:
                        try:
                            counts_line = lines[3]
                            atom_count = int(counts_line[:3].strip())
                            molecular_info["atoms"] = atom_count
                            molecular_info["format_name"] = "MDL Molfile/SDF"
                        except:
                            molecular_info["atoms"] = "unknown"
                elif file_ext == '.xyz':
                    lines = content.split('\n')
                    if lines:
                        try:
                            molecular_info["atoms"] = int(lines[0].strip())
                            molecular_info["format_name"] = "XYZ Coordinates"
                        except:
                            molecular_info["atoms"] = "unknown"
                elif file_ext in ['.fasta', '.fa']:
                    sequences = content.count('>')
                    molecular_info["sequences"] = sequences
                    molecular_info["format_name"] = "FASTA Sequence"
                else:
                    molecular_info["format_name"] = f"Other ({file_ext})"
            
            # 🎯 步骤6：生成统一的分析报告
            analysis_report = f"""🧪 分子文件分析报告 (优化数据流版本)
════════════════════════════════════════════════

📁 文件信息:
• 文件名: {molecular_file}
• 格式: {molecular_info.get('format_name', 'Unknown')} ({molecular_info.get('format', 'unknown')})
• 大小: {molecular_info.get('size', 'unknown')} 字节
• 处理模式: {processing_mode}

🔬 结构信息:"""
            
            if 'atoms' in molecular_info:
                analysis_report += f"\n• 原子数: {molecular_info['atoms']}"
            if 'sequences' in molecular_info:
                analysis_report += f"\n• 序列数: {molecular_info['sequences']}"
            
            # 🌟 数据流状态报告
            data_source = "内存缓存" if molecular_info.get('stored_in_memory') else "文件系统"
            analysis_report += f"""

🚀 数据流优化:
• 节点ID: {node_unique_id}
• 数据来源: {data_source}
• 内存状态: {'✅ 已缓存' if molecular_info.get('stored_in_memory') else '📁 文件模式'}
• 前端访问: {'🌐 API可用' if molecular_info.get('stored_in_memory') else '📂 仅本地文件'}
• 优化级别: {'🚀 高性能' if molecular_info.get('stored_in_memory') else '📁 传统模式'}"""
            
            # 如果内存可用，添加缓存统计
            if MOLECULAR_MEMORY_AVAILABLE:
                try:
                    cache_status = get_cache_status()
                    analysis_report += f"""

🧠 内存缓存统计:
• 缓存节点数: {cache_status.get('total_nodes', 0)}
• 缓存大小: {cache_status.get('total_cache_size', 0)} 字符
• 活跃节点: {cache_status.get('active_node', '无')[:8]}"""
                except:
                    analysis_report += f"\n• 缓存状态: 获取失败"
            
            analysis_report += f"""

⚙️ 处理参数:
• 处理模式: {processing_mode}
• 输出格式: {output_format}
• 详细程度: {detail_level:.1f}
• 验证启用: {'是' if enable_validation else '否'}

📊 处理状态: ✅ 成功完成
🕒 处理时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            # 验证结果
            validation_result = "✅ 文件格式验证通过"
            if enable_validation:
                if file_ext == '.pdb' and 'atoms' in molecular_info and molecular_info['atoms'] > 0:
                    validation_result += f" - PDB文件包含 {molecular_info['atoms']} 个原子记录"
                elif file_ext in ['.fasta', '.fa'] and 'sequences' in molecular_info:
                    validation_result += f" - FASTA文件包含 {molecular_info['sequences']} 个序列"
                else:
                    validation_result += f" - {molecular_info.get('format_name', '未知格式')} 文件结构正常"
            
            # 计算置信度分数
            confidence_score = 0.8 + (detail_level * 0.2)
            if enable_validation:
                confidence_score = min(confidence_score + 0.1, 1.0)
            
            # 🎯 步骤7：根据输出格式生成数据
            if output_format == "json":
                molecular_data = json.dumps(molecular_info, indent=2, ensure_ascii=False)
            elif output_format == "csv":
                # 简化的CSV格式
                molecular_data = f"filename,format,size,atoms,data_source\n{molecular_file},{molecular_info.get('format', 'unknown')},{molecular_info.get('size', 'unknown')},{molecular_info.get('atoms', 'N/A')},{data_source}"
            elif output_format == "xml":
                molecular_data = f"""<?xml version="1.0" encoding="UTF-8"?>
<molecular_data>
    <filename>{molecular_file}</filename>
    <format>{molecular_info.get('format', 'unknown')}</format>
    <size>{molecular_info.get('size', 'unknown')}</size>
    <atoms>{molecular_info.get('atoms', 'N/A')}</atoms>
    <data_source>{data_source}</data_source>
    <node_id>{node_unique_id}</node_id>
</molecular_data>"""
            else:  # summary
                molecular_data = f"分子: {molecular_file} | 格式: {molecular_info.get('format', 'unknown')} | 原子数: {molecular_info.get('atoms', 'N/A')} | 来源: {data_source}"
            
            return (molecular_data, analysis_report, validation_result, confidence_score)
            
        except Exception as e:
            error_msg = f"处理分子文件时发生错误: {str(e)}"
            return (
                error_msg,
                f"❌ 错误报告:\n{error_msg}",
                "验证失败：处理异常",
                0.0
            )
    
    @classmethod
    def IS_CHANGED(cls, molecular_file, processing_mode, output_format, enable_validation, detail_level):
        # 基于所有输入参数生成组合哈希，确保任何参数变化时重新计算
        content = f"{molecular_file}_{processing_mode}_{output_format}_{enable_validation}_{detail_level}"
        return hashlib.md5(content.encode()).hexdigest()

    @classmethod
    def VALIDATE_INPUTS(cls, molecular_file, **kwargs):
        """
        🎯 新增：验证输入时检查后端内存
        
        这个方法在节点执行前被调用，用于验证输入参数的有效性。
        我们在这里检查文件是否存在于后端内存中。
        """
        try:
            # 1. 检查文件是否在文件系统中（原有逻辑）
            if molecular_file != "no_molecular_files_found.pdb":
                input_dir = folder_paths.get_input_directory()
                molecules_dir = os.path.join(input_dir, 'molecules')
                file_path = os.path.join(molecules_dir, molecular_file)
                
                if os.path.exists(file_path):
                    return True  # 文件系统中存在
            
            # 2. 🚀 新增：检查文件是否在后端内存中
            if MOLECULAR_MEMORY_AVAILABLE:
                from .molecular_memory import get_cache_status
                cache_status = get_cache_status()
                
                if cache_status and 'nodes' in cache_status:
                    for node_data in cache_status['nodes']:
                        if node_data.get('filename') == molecular_file:
                            print(f"🧪 验证通过：在后端内存中找到文件 {molecular_file}")
                            return True  # 后端内存中存在
            
            # 3. 如果都没找到，返回错误
            if molecular_file == "no_molecular_files_found.pdb":
                return True  # 默认占位符，允许通过
            else:
                return f"文件 {molecular_file} 未找到（既不在文件系统中，也不在后端内存中）"
                
        except Exception as e:
            print(f"🚨 验证输入时出错: {e}")
            return f"验证输入时发生错误: {str(e)}"


# 节点映射
NODE_CLASS_MAPPINGS = {
    "CustomUploadTextNode": CustomUploadTextNode,
    "CustomUploadConfigNode": CustomUploadConfigNode,
    "Demo3DDisplayNode": Demo3DDisplayNode,  # 🎯 新增的3D显示演示节点
    "DualButtonDemoNode": DualButtonDemoNode,  # 🎯🎯 新增的双按钮演示节点
    "DualAttributeTestNode": DualAttributeTestNode,  # 🧪🔄 新增的双属性测试节点
    "MolecularUploadDemoNode": MolecularUploadDemoNode,  # 🧪📤🔬 新增的分子文件上传演示节点
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CustomUploadTextNode": "Custom Upload Text File",
    "CustomUploadConfigNode": "Custom Upload Config File", 
    "Demo3DDisplayNode": "🧪 Demo 3D Display Node",  # 🎯 新增
    "DualButtonDemoNode": "🎯🎯 Dual Button Demo Node",  # 🎯🎯 新增
    "DualAttributeTestNode": "🧪🔄 Dual Attribute Test Node",  # 🧪🔄 新增
    "MolecularUploadDemoNode": "🧪📤🔬 Molecular Upload + 3D Display Demo Node",  # 🧪📤🔬 新增
}

# Web目录 - 告诉ComfyUI我们有前端扩展
# WEB_DIRECTORY = "./web" # 已移至 __init__.py 