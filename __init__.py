# 🧪 ALCHEM_PropBtn 节点注册 - 方案B架构
#
# 只导入有效的方案B节点：
# - test_simple_node.py: 测试和验证节点
# - standard_molecular_node.py: 标准开发模板

# 使用统一的ALCHEM日志系统
from .backend.logging_config import get_alchem_logger
logger = get_alchem_logger('Init')

# 初始化空的节点映射
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# 导入测试节点
try:
    from .nodes.test_simple_node import NODE_CLASS_MAPPINGS as SIMPLE_TEST_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as SIMPLE_TEST_DISPLAY_MAPPINGS
    NODE_CLASS_MAPPINGS.update(SIMPLE_TEST_MAPPINGS)
    NODE_DISPLAY_NAME_MAPPINGS.update(SIMPLE_TEST_DISPLAY_MAPPINGS)
    logger.success("测试节点加载成功")
except ImportError as e:
    logger.warning(f"测试节点导入失败: {e}")

# 导入标准分子节点模板
try:
    from .nodes.standard_molecular_node import NODE_CLASS_MAPPINGS as STANDARD_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as STANDARD_DISPLAY_MAPPINGS
    NODE_CLASS_MAPPINGS.update(STANDARD_MAPPINGS)
    NODE_DISPLAY_NAME_MAPPINGS.update(STANDARD_DISPLAY_MAPPINGS)
    logger.success("标准节点模板加载成功")
except ImportError as e:
    logger.warning(f"标准节点模板导入失败: {e}")

# 导入Tab感知处理节点
try:
    from .nodes.test_tab_aware_processing import NODE_CLASS_MAPPINGS as TAB_AWARE_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as TAB_AWARE_DISPLAY_MAPPINGS
    NODE_CLASS_MAPPINGS.update(TAB_AWARE_MAPPINGS)
    NODE_DISPLAY_NAME_MAPPINGS.update(TAB_AWARE_DISPLAY_MAPPINGS)
    logger.success("Tab感知处理节点加载成功")
except ImportError as e:
    logger.warning(f"Tab感知处理节点导入失败: {e}")

# 导入简化处理节点
try:
    from .nodes.simple_process_node import NODE_CLASS_MAPPINGS as SIMPLE_PROCESS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as SIMPLE_PROCESS_DISPLAY_MAPPINGS
    NODE_CLASS_MAPPINGS.update(SIMPLE_PROCESS_MAPPINGS)
    NODE_DISPLAY_NAME_MAPPINGS.update(SIMPLE_PROCESS_DISPLAY_MAPPINGS)
    logger.success("简化处理节点加载成功")
except ImportError as e:
    logger.warning(f"简化处理节点导入失败: {e}")

# 导入Mixin示例节点
try:
    from .nodes.examples_with_mixin import NODE_CLASS_MAPPINGS as MIXIN_EXAMPLES_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as MIXIN_EXAMPLES_DISPLAY_MAPPINGS
    NODE_CLASS_MAPPINGS.update(MIXIN_EXAMPLES_MAPPINGS)
    NODE_DISPLAY_NAME_MAPPINGS.update(MIXIN_EXAMPLES_DISPLAY_MAPPINGS)
    logger.success("Mixin示例节点加载成功 - 新架构演示")
except ImportError as e:
    logger.warning(f"Mixin示例节点导入失败: {e}")

# 🧪⚗️ 导入RDKit扩展节点 (条件导入)
try:
    from .rdkit_extension.nodes import NODE_CLASS_MAPPINGS as RDKIT_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS as RDKIT_DISPLAY_MAPPINGS
    NODE_CLASS_MAPPINGS.update(RDKIT_MAPPINGS)
    NODE_DISPLAY_NAME_MAPPINGS.update(RDKIT_DISPLAY_MAPPINGS)
    logger.success("🧪⚗️ RDKit扩展节点加载成功 - 专业分子编辑功能")
except ImportError as e:
    logger.info(f"🧪 RDKit扩展未加载: {e}")
    logger.info("💡 安装RDKit以启用高级分子编辑功能: conda install -c conda-forge rdkit")

logger.molecular(f"总共加载了 {len(NODE_CLASS_MAPPINGS)} 个节点")

# ====================================================================================================
# 注册Web API
# ====================================================================================================

# 🎯 ALCHEM_PropBtn 采用方案B架构：节点主动数据获取模式
logger.info("使用方案B架构 - 节点主动数据获取模式")

# 注册API路由
try:
    from .backend.api import register_api_routes
    register_api_routes()
    logger.success("API路由注册成功")
except ImportError as e:
    logger.error(f"API路由注册失败 - {e}")

# ====================================================================================================
# ComfyUI插件的标准导出
# ====================================================================================================
WEB_DIRECTORY = "./web"

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "WEB_DIRECTORY"
] 