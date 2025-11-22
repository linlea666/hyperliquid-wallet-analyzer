"""
DeepSeek API 服务
提供与 DeepSeek AI 的交互接口
"""
import httpx
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger

from app.database import db


class DeepSeekService:
    """DeepSeek API 服务"""
    
    def __init__(self):
        self.config = self._load_config()
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # 定价（元/1K tokens）
        self.pricing = {
            'input': 0.001,   # 输入 token 价格
            'output': 0.002   # 输出 token 价格
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        try:
            config_row = db.fetch_one(
                "SELECT config_value FROM system_configs WHERE config_key = ?",
                ("ai",)
            )
            
            if config_row:
                config = json.loads(config_row['config_value'])
                return config
            
            # 默认配置
            return {
                'enabled': True,
                'provider': 'deepseek',
                'api_key': 'sk-95468bc93340462e81772278f0ae6058',
                'api_url': 'https://api.deepseek.com/v1',
                'model': 'deepseek-chat',
                'max_tokens': 2000,
                'temperature': 0.7,
                'daily_limit': 1000,
                'cost_limit': 1.0,
                'score_threshold': 75
            }
        except Exception as e:
            logger.error(f"加载 AI 配置失败: {e}")
            return {
                'enabled': False,
                'api_key': '',
                'api_url': 'https://api.deepseek.com/v1',
                'model': 'deepseek-chat'
            }
    
    def reload_config(self):
        """重新加载配置"""
        self.config = self._load_config()
    
    def is_enabled(self) -> bool:
        """检查是否启用"""
        return self.config.get('enabled', False) and bool(self.config.get('api_key'))
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        调用 DeepSeek Chat Completion API
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            max_tokens: 最大 token 数
            temperature: 温度参数
            stream: 是否流式输出
            
        Returns:
            API 响应结果
        """
        if not self.is_enabled():
            raise Exception("AI 服务未启用或未配置 API Key")
        
        # 检查每日限制
        if not self._check_daily_limit():
            raise Exception("已达到每日调用限制")
        
        # 使用配置的默认值
        max_tokens = max_tokens or self.config.get('max_tokens', 2000)
        temperature = temperature or self.config.get('temperature', 0.7)
        
        # 构建请求
        url = f"{self.config['api_url']}/chat/completions"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.config['api_key']}"
        }
        
        payload = {
            'model': self.config.get('model', 'deepseek-chat'),
            'messages': messages,
            'max_tokens': max_tokens,
            'temperature': temperature,
            'stream': stream
        }
        
        try:
            logger.info(f"调用 DeepSeek API: {len(messages)} 条消息")
            
            response = await self.client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            # 记录使用情况
            self._record_usage(result)
            
            logger.info(f"DeepSeek API 调用成功")
            
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"DeepSeek API HTTP 错误: {e.response.status_code} - {e.response.text}")
            raise Exception(f"API 调用失败: {e.response.status_code}")
        
        except httpx.RequestError as e:
            logger.error(f"DeepSeek API 请求错误: {e}")
            raise Exception(f"API 请求失败: {str(e)}")
        
        except Exception as e:
            logger.error(f"DeepSeek API 调用失败: {e}")
            raise
    
    def _check_daily_limit(self) -> bool:
        """检查每日调用限制"""
        try:
            daily_limit = self.config.get('daily_limit', 1000)
            
            # 查询今日调用次数
            today = datetime.now().date().isoformat()
            result = db.fetch_one("""
                SELECT COUNT(*) as count FROM ai_usage_stats
                WHERE DATE(created_at) = ?
            """, (today,))
            
            today_count = result['count'] if result else 0
            
            if today_count >= daily_limit:
                logger.warning(f"已达到每日调用限制: {today_count}/{daily_limit}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"检查每日限制失败: {e}")
            return True  # 出错时允许调用
    
    def _record_usage(self, response: Dict[str, Any]):
        """记录使用情况"""
        try:
            usage = response.get('usage', {})
            
            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)
            total_tokens = usage.get('total_tokens', 0)
            
            # 计算成本
            cost = self.calculate_cost(prompt_tokens, completion_tokens)
            
            # 保存到数据库
            db.execute("""
                INSERT INTO ai_usage_stats
                (model, prompt_tokens, completion_tokens, total_tokens, cost, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                self.config.get('model', 'deepseek-chat'),
                prompt_tokens,
                completion_tokens,
                total_tokens,
                cost,
                datetime.now().isoformat()
            ))
            
            logger.info(f"记录 AI 使用: {total_tokens} tokens, 成本: ¥{cost:.4f}")
            
        except Exception as e:
            logger.error(f"记录使用情况失败: {e}")
    
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        计算成本
        
        Args:
            prompt_tokens: 输入 token 数
            completion_tokens: 输出 token 数
            
        Returns:
            成本（元）
        """
        input_cost = (prompt_tokens / 1000) * self.pricing['input']
        output_cost = (completion_tokens / 1000) * self.pricing['output']
        return input_cost + output_cost
    
    def get_usage_stats(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取使用统计
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            统计信息
        """
        try:
            # 构建查询条件
            conditions = []
            params = []
            
            if start_date:
                conditions.append("DATE(created_at) >= ?")
                params.append(start_date)
            
            if end_date:
                conditions.append("DATE(created_at) <= ?")
                params.append(end_date)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            # 总统计
            total_stats = db.fetch_one(f"""
                SELECT 
                    COUNT(*) as total_calls,
                    SUM(total_tokens) as total_tokens,
                    SUM(cost) as total_cost
                FROM ai_usage_stats
                WHERE {where_clause}
            """, tuple(params))
            
            # 今日统计
            today = datetime.now().date().isoformat()
            today_stats = db.fetch_one("""
                SELECT 
                    COUNT(*) as today_calls,
                    SUM(total_tokens) as today_tokens,
                    SUM(cost) as today_cost
                FROM ai_usage_stats
                WHERE DATE(created_at) = ?
            """, (today,))
            
            # 每日限制
            daily_limit = self.config.get('daily_limit', 1000)
            today_calls = today_stats['today_calls'] if today_stats else 0
            
            return {
                'total': {
                    'calls': total_stats['total_calls'] if total_stats else 0,
                    'tokens': total_stats['total_tokens'] if total_stats else 0,
                    'cost': round(total_stats['total_cost'] if total_stats else 0, 4)
                },
                'today': {
                    'calls': today_calls,
                    'tokens': today_stats['today_tokens'] if today_stats else 0,
                    'cost': round(today_stats['today_cost'] if today_stats else 0, 4)
                },
                'limits': {
                    'daily_limit': daily_limit,
                    'remaining': max(0, daily_limit - today_calls),
                    'cost_limit': self.config.get('cost_limit', 1.0)
                }
            }
            
        except Exception as e:
            logger.error(f"获取使用统计失败: {e}")
            return {
                'total': {'calls': 0, 'tokens': 0, 'cost': 0},
                'today': {'calls': 0, 'tokens': 0, 'cost': 0},
                'limits': {'daily_limit': 1000, 'remaining': 1000, 'cost_limit': 1.0}
            }
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


# 全局 DeepSeek 服务实例
deepseek_service = DeepSeekService()


# 导出
__all__ = ['DeepSeekService', 'deepseek_service']

