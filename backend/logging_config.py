"""
🔧 ALCHEM_PropBtn 统一Logging配置模块

解决项目中极度混乱的logging问题：
- Python后端4种不同格式 → 统一为1种标准格式
- 表情符号滥用 → 规范化表情符号使用
- 模块标识混乱 → 统一命名规范

使用方法：
    from backend.logging_config import get_alchem_logger
    logger = get_alchem_logger('Memory')
    logger.debug("调试信息")
    logger.success("操作成功")
"""

import logging
import sys
from typing import Optional


class ALCHEMLogFormatter(logging.Formatter):
    """ALCHEM专用日志格式化器"""
    
    # 统一表情符号标准
    EMOJI_MAP = {
        'DEBUG': '🔧',      # Debug/调试信息
        'INFO': 'ℹ️',       # Info/一般信息  
        'WARNING': '⚠️',    # Warning/警告
        'ERROR': '❌',      # Error/错误
        'CRITICAL': '💥',   # Critical/严重错误
        'SUCCESS': '✅',    # Success/成功操作 (自定义级别)
        'MOLECULAR': '🧪',  # Molecular/分子相关 (自定义级别)
        'NETWORK': '📡',    # Network/网络通信 (自定义级别)
        'STORAGE': '💾',    # Storage/数据存储 (自定义级别)
        'CONNECTION': '🔗', # Connection/连接状态 (自定义级别)
    }
    
    def format(self, record):
        # 获取表情符号
        emoji = self.EMOJI_MAP.get(record.levelname, 'ℹ️')
        
        # 统一格式：[ALCHEM.模块名] 🔧 消息内容
        module_name = getattr(record, 'module_name', 'Unknown')
        formatted_message = f"[ALCHEM.{module_name}] {emoji} {record.getMessage()}"
        
        # 添加时间戳（在开发模式下）
        if hasattr(record, 'include_timestamp') and record.include_timestamp:
            timestamp = self.formatTime(record, '%H:%M:%S')
            formatted_message = f"{timestamp} {formatted_message}"
            
        return formatted_message


class ALCHEMLogger:
    """ALCHEM专用Logger包装器，提供额外的日志级别"""
    
    def __init__(self, logger: logging.Logger, module_name: str):
        self.logger = logger
        self.module_name = module_name
        
        # 添加自定义日志级别
        self._add_custom_levels()
    
    def _add_custom_levels(self):
        """添加自定义日志级别"""
        # SUCCESS级别 (介于INFO和WARNING之间)
        logging.addLevelName(25, 'SUCCESS')
        
        # MOLECULAR级别 (专门用于分子相关操作)
        logging.addLevelName(22, 'MOLECULAR')
        
        # NETWORK级别 (专门用于网络通信)  
        logging.addLevelName(23, 'NETWORK')
        
        # STORAGE级别 (专门用于存储操作)
        logging.addLevelName(24, 'STORAGE')
        
        # CONNECTION级别 (专门用于连接状态)
        logging.addLevelName(21, 'CONNECTION')
    
    def _log(self, level, message, include_timestamp=False):
        """内部日志方法"""
        extra = {
            'module_name': self.module_name,
            'include_timestamp': include_timestamp
        }
        self.logger.log(level, message, extra=extra)
    
    # 标准日志方法
    def debug(self, message, include_timestamp=False):
        """调试信息 🔧"""
        self._log(logging.DEBUG, message, include_timestamp)
    
    def info(self, message, include_timestamp=False):
        """一般信息 ℹ️"""
        self._log(logging.INFO, message, include_timestamp)
    
    def warning(self, message, include_timestamp=False):
        """警告信息 ⚠️"""
        self._log(logging.WARNING, message, include_timestamp)
    
    def error(self, message, include_timestamp=False):
        """错误信息 ❌"""
        self._log(logging.ERROR, message, include_timestamp)
    
    def critical(self, message, include_timestamp=False):
        """严重错误 💥"""
        self._log(logging.CRITICAL, message, include_timestamp)
    
    # 自定义日志方法
    def success(self, message, include_timestamp=False):
        """成功操作 ✅"""
        self._log(25, message, include_timestamp)
    
    def molecular(self, message, include_timestamp=False):
        """分子相关操作 🧪"""
        self._log(22, message, include_timestamp)
    
    def network(self, message, include_timestamp=False):
        """网络通信 📡"""
        self._log(23, message, include_timestamp)
    
    def storage(self, message, include_timestamp=False):
        """存储操作 💾"""
        self._log(24, message, include_timestamp)
    
    def connection(self, message, include_timestamp=False):
        """连接状态 🔗"""
        self._log(21, message, include_timestamp)


def get_alchem_logger(module_name: str, level: Optional[str] = None) -> ALCHEMLogger:
    """
    获取ALCHEM统一格式的Logger
    
    Args:
        module_name: 模块名称 (如 'Memory', 'API', 'WebSocket')
        level: 日志级别 ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    
    Returns:
        ALCHEMLogger: 统一格式的日志记录器
    
    Example:
        logger = get_alchem_logger('Memory')
        logger.debug("内存缓存初始化完成")
        logger.success("分子文件上传成功")
        logger.molecular("开始解析PDB文件")
    """
    # 创建标准Logger
    logger_name = f'ALCHEM.{module_name}'
    logger = logging.getLogger(logger_name)
    
    # 设置日志级别
    if level:
        logger.setLevel(getattr(logging, level.upper()))
    else:
        # 默认级别：开发时DEBUG，生产时INFO
        logger.setLevel(logging.DEBUG)
    
    # 避免重复添加Handler
    if not logger.handlers:
        # 创建控制台Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ALCHEMLogFormatter())
        logger.addHandler(console_handler)
        
        # 防止日志传播到root logger (避免重复输出)
        logger.propagate = False
    
    # 返回包装后的Logger
    return ALCHEMLogger(logger, module_name)


# 预定义常用Logger (可选，方便直接导入)
def get_memory_logger() -> ALCHEMLogger:
    """获取内存管理模块Logger"""
    return get_alchem_logger('Memory')

def get_api_logger() -> ALCHEMLogger:
    """获取API模块Logger"""
    return get_alchem_logger('API')

def get_websocket_logger() -> ALCHEMLogger:
    """获取WebSocket模块Logger"""
    return get_alchem_logger('WebSocket')

def get_molecular_utils_logger() -> ALCHEMLogger:
    """获取分子工具模块Logger"""
    return get_alchem_logger('MolecularUtils')


# 全局配置函数
def configure_alchem_logging(level: str = 'DEBUG', enable_timestamp: bool = False):
    """
    全局配置ALCHEM日志系统
    
    Args:
        level: 全局日志级别
        enable_timestamp: 是否启用时间戳
    """
    # 设置全局级别
    logging.getLogger('ALCHEM').setLevel(getattr(logging, level.upper()))
    
    # 全局时间戳配置（如果需要的话）
    if enable_timestamp:
        # 这里可以添加全局时间戳配置逻辑
        pass


if __name__ == "__main__":
    # 测试统一logging系统
    print("🧪 测试ALCHEM统一Logging系统")
    
    # 创建测试Logger
    memory_logger = get_alchem_logger('Memory')
    api_logger = get_alchem_logger('API') 
    websocket_logger = get_alchem_logger('WebSocket')
    
    # 测试各种日志级别
    memory_logger.debug("内存缓存系统初始化")
    memory_logger.info("当前缓存状态：5个分子文件")
    memory_logger.success("分子数据存储成功")
    memory_logger.molecular("解析PDB文件：1abc.pdb")
    memory_logger.storage("数据写入文件系统完成")
    memory_logger.warning("内存使用率过高：85%")
    memory_logger.error("分子文件格式不支持")
    
    api_logger.network("WebSocket连接建立")
    api_logger.success("API路由注册完成")
    
    websocket_logger.connection("客户端连接：ws://localhost:8188")
    websocket_logger.network("发送分子更新通知")
    
    print("\n✅ 统一Logging系统测试完成！")