"""
🚀 ALCHEM_PropBtn WebSocket实时同步服务器

专注于核心功能：
1. Molstar显示与内存的实时同步
2. 分子数据变更的即时推送
3. 简单的编辑功能支持

不包含多用户协作，专注于单用户实时同步的概念验证
"""

import asyncio
import json
import logging
import time
from typing import Dict, Set, Any, Optional
from aiohttp import web, WSMsgType
import server

# 获取日志记录器
logger = logging.getLogger(__name__)

# 全局WebSocket连接管理
class WebSocketManager:
    def __init__(self):
        self.connections: Set[web.WebSocketResponse] = set()
        self.client_info: Dict[web.WebSocketResponse, Dict[str, Any]] = {}
        
    async def add_connection(self, ws: web.WebSocketResponse, client_info: Dict[str, Any] = None):
        """添加WebSocket连接"""
        self.connections.add(ws)
        self.client_info[ws] = client_info or {
            'connected_at': time.time(),
            'last_ping': time.time()
        }
        logger.info(f"🔗 WebSocket客户端连接，当前连接数: {len(self.connections)}")
        
        # 发送欢迎消息
        await self.send_to_client(ws, {
            'type': 'welcome',
            'message': '🧪 ALCHEM分子实时同步已连接',
            'server_time': time.time()
        })
    
    async def remove_connection(self, ws: web.WebSocketResponse):
        """移除WebSocket连接"""
        self.connections.discard(ws)
        self.client_info.pop(ws, None)
        logger.info(f"❌ WebSocket客户端断开，当前连接数: {len(self.connections)}")
    
    async def send_to_client(self, ws: web.WebSocketResponse, message: Dict[str, Any]):
        """发送消息给特定客户端"""
        try:
            if ws.closed:
                await self.remove_connection(ws)
                return False
                
            await ws.send_str(json.dumps(message))
            return True
        except Exception as e:
            logger.warning(f"⚠️ 发送消息失败: {e}")
            await self.remove_connection(ws)
            return False
    
    async def broadcast(self, message: Dict[str, Any], exclude_ws: web.WebSocketResponse = None):
        """广播消息给所有连接的客户端"""
        if not self.connections:
            logger.debug("📡 没有WebSocket连接，跳过广播")
            return
        
        logger.info(f"📡 广播消息给 {len(self.connections)} 个客户端: {message.get('type', 'unknown')}")
        
        # 并发发送给所有客户端
        tasks = []
        for ws in list(self.connections):  # 创建副本避免迭代时修改
            if ws != exclude_ws:
                tasks.append(self.send_to_client(ws, message))
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            success_count = sum(1 for r in results if r is True)
            logger.debug(f"📡 广播完成: {success_count}/{len(results)} 成功")
    
    def get_connection_count(self) -> int:
        """获取当前连接数"""
        return len(self.connections)
    
    def get_connection_info(self) -> Dict[str, Any]:
        """获取连接信息"""
        return {
            'total_connections': len(self.connections),
            'clients': [
                {
                    'connected_at': info.get('connected_at'),
                    'last_ping': info.get('last_ping'),
                    'uptime': time.time() - info.get('connected_at', time.time())
                }
                for info in self.client_info.values()
            ]
        }

# 全局WebSocket管理器实例
ws_manager = WebSocketManager()

async def handle_websocket(request: web.Request) -> web.WebSocketResponse:
    """处理WebSocket连接"""
    ws = web.WebSocketResponse(heartbeat=30)  # 30秒心跳
    await ws.prepare(request)
    
    # 获取客户端信息
    client_ip = request.remote
    client_info = {
        'ip': client_ip,
        'connected_at': time.time(),
        'last_ping': time.time()
    }
    
    # 添加到连接管理器
    await ws_manager.add_connection(ws, client_info)
    
    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    await handle_websocket_message(ws, data)
                except json.JSONDecodeError as e:
                    logger.warning(f"⚠️ WebSocket收到无效JSON: {e}")
                    await ws_manager.send_to_client(ws, {
                        'type': 'error',
                        'message': f'无效的JSON格式: {str(e)}'
                    })
            elif msg.type == WSMsgType.ERROR:
                logger.error(f'❌ WebSocket错误: {ws.exception()}')
                break
    except Exception as e:
        logger.exception(f"❌ WebSocket处理异常: {e}")
    finally:
        await ws_manager.remove_connection(ws)
    
    return ws

async def handle_websocket_message(ws: web.WebSocketResponse, data: Dict[str, Any]):
    """处理WebSocket消息"""
    message_type = data.get('type', 'unknown')
    
    logger.debug(f"📨 收到WebSocket消息: {message_type}")
    
    try:
        if message_type == 'ping':
            # 处理心跳
            ws_manager.client_info[ws]['last_ping'] = time.time()
            await ws_manager.send_to_client(ws, {
                'type': 'pong',
                'server_time': time.time()
            })
            
        elif message_type == 'subscribe_node':
            # 订阅特定节点的更新
            node_id = data.get('node_id')
            if node_id:
                ws_manager.client_info[ws]['subscribed_nodes'] = \
                    ws_manager.client_info[ws].get('subscribed_nodes', set())
                ws_manager.client_info[ws]['subscribed_nodes'].add(node_id)
                
                await ws_manager.send_to_client(ws, {
                    'type': 'subscribed',
                    'node_id': node_id,
                    'message': f'已订阅节点 {node_id} 的更新'
                })
                logger.info(f"🔔 客户端订阅节点 {node_id}")
            
        elif message_type == 'unsubscribe_node':
            # 取消订阅
            node_id = data.get('node_id')
            if node_id and ws in ws_manager.client_info:
                subscribed_nodes = ws_manager.client_info[ws].get('subscribed_nodes', set())
                subscribed_nodes.discard(node_id)
                
                await ws_manager.send_to_client(ws, {
                    'type': 'unsubscribed',
                    'node_id': node_id,
                    'message': f'已取消订阅节点 {node_id}'
                })
                logger.info(f"🔕 客户端取消订阅节点 {node_id}")
                
        elif message_type == 'get_status':
            # 获取服务器状态
            await ws_manager.send_to_client(ws, {
                'type': 'status',
                'data': ws_manager.get_connection_info()
            })
            
        else:
            logger.warning(f"⚠️ 未知的WebSocket消息类型: {message_type}")
            await ws_manager.send_to_client(ws, {
                'type': 'error',
                'message': f'未知的消息类型: {message_type}'
            })
            
    except Exception as e:
        logger.exception(f"❌ 处理WebSocket消息异常: {e}")
        await ws_manager.send_to_client(ws, {
            'type': 'error',
            'message': f'服务器处理错误: {str(e)}'
        })

# 🔥 核心功能：分子数据变更通知
async def notify_molecular_data_change(node_id: str, change_type: str, data: Dict[str, Any]):
    """
    通知所有订阅的客户端分子数据发生变更
    
    Args:
        node_id: 节点ID
        change_type: 变更类型 ('update', 'delete', 'edit')
        data: 变更的数据
    """
    if not ws_manager.connections:
        logger.debug(f"📡 没有WebSocket连接，跳过分子数据变更通知: {node_id}")
        return
    
    message = {
        'type': 'molecular_data_changed',
        'node_id': node_id,
        'change_type': change_type,
        'data': data,
        'timestamp': time.time()
    }
    
    # 只发送给订阅了该节点的客户端
    subscribers = []
    for ws, client_info in ws_manager.client_info.items():
        subscribed_nodes = client_info.get('subscribed_nodes', set())
        if node_id in subscribed_nodes:
            subscribers.append(ws)
    
    if subscribers:
        logger.info(f"🧪 通知 {len(subscribers)} 个订阅者：节点 {node_id} 的分子数据发生 {change_type}")
        
        # 并发发送给所有订阅者
        tasks = [ws_manager.send_to_client(ws, message) for ws in subscribers]
        await asyncio.gather(*tasks, return_exceptions=True)
    else:
        logger.debug(f"📡 节点 {node_id} 没有订阅者，跳过通知")

def register_websocket_routes():
    """注册WebSocket路由到ComfyUI服务器"""
    try:
        # 添加WebSocket路由
        server.PromptServer.instance.routes.get("/alchem_propbtn/ws")(handle_websocket)
        
        logger.info("🚀 WebSocket路由注册成功:")
        logger.info("   - GET /alchem_propbtn/ws (WebSocket连接)")
        
    except Exception as e:
        logger.exception(f"❌ WebSocket路由注册失败: {e}")

def get_websocket_manager() -> WebSocketManager:
    """获取WebSocket管理器实例"""
    return ws_manager

# 便捷函数
def notify_molecular_update(node_id: str, molecular_data: Dict[str, Any]):
    """便捷函数：通知分子数据更新"""
    return asyncio.create_task(notify_molecular_data_change(
        node_id, 'update', molecular_data
    ))

def notify_molecular_edit(node_id: str, edit_info: Dict[str, Any]):
    """便捷函数：通知分子数据编辑"""
    return asyncio.create_task(notify_molecular_data_change(
        node_id, 'edit', edit_info
    ))

def notify_molecular_delete(node_id: str):
    """便捷函数：通知分子数据删除"""
    return asyncio.create_task(notify_molecular_data_change(
        node_id, 'delete', {}
    ))