import os
import json
import torch
import folder_paths
from PIL import Image, ImageOps
import numpy as np
import hashlib

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


# 节点映射
NODE_CLASS_MAPPINGS = {
    "CustomUploadTextNode": CustomUploadTextNode,
    "CustomUploadConfigNode": CustomUploadConfigNode,
    "Demo3DDisplayNode": Demo3DDisplayNode,  # 🎯 新增的3D显示演示节点
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CustomUploadTextNode": "Custom Upload Text File",
    "CustomUploadConfigNode": "Custom Upload Config File", 
    "Demo3DDisplayNode": "🧪 Demo 3D Display Node",  # 🎯 新增
}

# Web目录 - 告诉ComfyUI我们有前端扩展
WEB_DIRECTORY = "./web" 