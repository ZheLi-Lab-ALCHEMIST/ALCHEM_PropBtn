import os
import json
import time
import traceback
from typing import Dict, Any

class ALCHEM_SystemTestNode:
    """
    ALCHEM_PropBtn 系统测试节点
    在ComfyUI环境内测试所有关键功能并输出详细报告
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "test_mode": (["全面测试", "内存管理", "API端点", "上传功能", "缓存系统"], {"default": "全面测试"}),
                "verbose": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("test_report",)
    FUNCTION = "run_system_test"
    CATEGORY = "ALCHEM_PropBtn/Testing"

    def run_system_test(self, test_mode, verbose):
        """运行系统测试并返回详细报告"""
        
        report = []
        report.append("🚀 ALCHEM_PropBtn 系统测试报告")
        report.append("=" * 50)
        report.append(f"🕐 测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"🎯 测试模式: {test_mode}")
        report.append("")
        
        # 测试计数器
        total_tests = 0
        passed_tests = 0
        
        try:
            if test_mode in ["全面测试", "内存管理"]:
                total_tests += 1
                if self._test_molecular_memory(report, verbose):
                    passed_tests += 1
                    
            if test_mode in ["全面测试", "API端点"]:
                total_tests += 1
                if self._test_api_endpoints(report, verbose):
                    passed_tests += 1
                    
            if test_mode in ["全面测试", "上传功能"]:
                total_tests += 1
                if self._test_upload_functionality(report, verbose):
                    passed_tests += 1
                    
            if test_mode in ["全面测试", "缓存系统"]:
                total_tests += 1
                if self._test_cache_system(report, verbose):
                    passed_tests += 1
                    
        except Exception as e:
            report.append(f"❌ 测试异常: {str(e)}")
            if verbose:
                report.append(f"堆栈追踪: {traceback.format_exc()}")
        
        # 测试总结
        report.append("")
        report.append("📊 测试总结")
        report.append("=" * 30)
        report.append(f"总测试数: {total_tests}")
        report.append(f"通过测试: {passed_tests}")
        report.append(f"失败测试: {total_tests - passed_tests}")
        report.append(f"成功率: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
        
        if passed_tests == total_tests:
            report.append("🎉 所有测试通过！")
        else:
            report.append("⚠️ 部分测试失败，需要检查相关模块")
            
        return ("\n".join(report),)
    
    def _test_molecular_memory(self, report, verbose):
        """测试分子内存管理"""
        report.append("🧪 测试1: 分子内存管理")
        report.append("-" * 30)
        
        try:
            # 尝试导入分子内存管理器
            from .molecular_memory import (
                store_molecular_data, 
                get_molecular_data, 
                get_cache_status,
                MOLECULAR_DATA_CACHE
            )
            report.append("✅ 分子内存管理器导入成功")
            
            # 测试存储功能
            test_node_id = "test_node_123"
            test_filename = "test_molecule.pdb"
            test_content = """ATOM      1  N   ALA A   1      20.154  16.967  27.462  1.00 11.18           N  
ATOM      2  CA  ALA A   1      19.030  16.101  27.938  1.00 10.38           C"""
            
            store_molecular_data(test_node_id, test_filename, content=test_content)
            report.append(f"✅ 测试数据存储成功: {test_filename}")
            
            # 测试检索功能
            retrieved_data = get_molecular_data(test_node_id)
            if retrieved_data and retrieved_data.get('content') == test_content:
                report.append("✅ 测试数据检索成功")
            else:
                report.append(f"❌ 测试数据检索失败 - 返回数据: {type(retrieved_data)}")
                if retrieved_data:
                    report.append(f"   检索到的内容长度: {len(retrieved_data.get('content', ''))}")
                    report.append(f"   预期内容长度: {len(test_content)}")
                return False
                
            # 测试缓存状态
            cache_status = get_cache_status()
            if verbose:
                report.append(f"📋 缓存状态: {json.dumps(cache_status, indent=2, ensure_ascii=False)}")
            report.append(f"✅ 缓存状态获取成功 (缓存节点数: {cache_status.get('cached_nodes', 0)})")
            
            return True
            
        except ImportError as e:
            report.append(f"❌ 分子内存管理器导入失败: {e}")
            return False
        except Exception as e:
            report.append(f"❌ 内存管理测试异常: {e}")
            if verbose:
                report.append(f"详细错误: {traceback.format_exc()}")
            return False
    
    def _test_api_endpoints(self, report, verbose):
        """测试API端点"""
        report.append("")
        report.append("📡 测试2: API端点")
        report.append("-" * 30)
        
        try:
            # 尝试导入API模块
            from .molecular_api import MolecularAPI
            report.append("✅ 分子API模块导入成功")
            
            # 检查API类是否正确定义
            if hasattr(MolecularAPI, 'handle_request'):
                report.append("✅ API处理器定义正常")
            else:
                report.append("❌ API处理器定义异常")
                return False
                
            # 这里可以添加更多API测试，但在节点内部有限制
            report.append("✅ API端点基础检查通过")
            return True
            
        except ImportError as e:
            report.append(f"❌ API模块导入失败: {e}")
            return False
        except Exception as e:
            report.append(f"❌ API测试异常: {e}")
            if verbose:
                report.append(f"详细错误: {traceback.format_exc()}")
            return False
    
    def _test_upload_functionality(self, report, verbose):
        """测试上传功能"""
        report.append("")
        report.append("📤 测试3: 上传功能")
        report.append("-" * 30)
        
        try:
            # 检查执行钩子
            from .execution_hook import MolecularExecutionHook
            report.append("✅ 执行钩子模块导入成功")
            
            # 检查钩子类是否正确定义
            if hasattr(MolecularExecutionHook, 'install_hook'):
                report.append("✅ 执行钩子类定义正常")
            else:
                report.append("⚠️ 执行钩子类定义不完整")
            
            return True
            
        except ImportError as e:
            report.append(f"❌ 执行钩子导入失败: {e}")
            return False
        except Exception as e:
            report.append(f"❌ 上传功能测试异常: {e}")
            if verbose:
                report.append(f"详细错误: {traceback.format_exc()}")
            return False
    
    def _test_cache_system(self, report, verbose):
        """测试缓存系统"""
        report.append("")
        report.append("💾 测试4: 缓存系统")
        report.append("-" * 30)
        
        try:
            from .molecular_memory import MOLECULAR_DATA_CACHE, molecular_memory
            
            # 检查缓存结构
            if isinstance(MOLECULAR_DATA_CACHE, dict):
                report.append("✅ 全局缓存结构正常")
            else:
                report.append("❌ 全局缓存结构异常")
                return False
            
            # 检查内存管理器
            if hasattr(molecular_memory, 'get_memory_usage'):
                usage = molecular_memory.get_memory_usage()
                if verbose:
                    report.append(f"📊 内存使用情况: {json.dumps(usage, indent=2, ensure_ascii=False)}")
                report.append("✅ 内存使用监控正常")
            else:
                report.append("⚠️ 内存使用监控不可用")
            
            # 检查缓存大小
            cache_size = len(MOLECULAR_DATA_CACHE)
            report.append(f"✅ 当前缓存节点数: {cache_size}")
            
            return True
            
        except Exception as e:
            report.append(f"❌ 缓存系统测试异常: {e}")
            if verbose:
                report.append(f"详细错误: {traceback.format_exc()}")
            return False

# ComfyUI节点映射
NODE_CLASS_MAPPINGS = {
    "ALCHEM_SystemTestNode": ALCHEM_SystemTestNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ALCHEM_SystemTestNode": "🧪 ALCHEM系统测试",
}