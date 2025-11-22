"""
AI 智能分析器
提供交易风格、策略识别、风险评估等智能分析功能
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from .deepseek_service import deepseek_service


class AIAnalyzer:
    """AI 智能分析器"""
    
    def __init__(self):
        self.deepseek = deepseek_service
    
    async def analyze_trading_style(self, wallet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析交易风格
        
        Args:
            wallet_data: 钱包数据
            
        Returns:
            {
                "style": "激进型/稳健型/保守型",
                "characteristics": ["高频交易", "短线操作"],
                "risk_preference": "高风险偏好",
                "description": "详细描述",
                "confidence": 0.85
            }
        """
        try:
            logger.info(f"开始分析交易风格: {wallet_data.get('address', 'unknown')}")
            
            # 构建提示词
            prompt = self._build_style_prompt(wallet_data)
            
            # 调用 AI
            messages = [
                {
                    "role": "system",
                    "content": "你是一位专业的加密货币交易分析师，擅长分析交易者的交易风格和行为特征。请以 JSON 格式返回分析结果。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = await self.deepseek.chat_completion(messages, max_tokens=1500)
            
            # 解析结果
            result = self._parse_response(response)
            
            logger.info(f"交易风格分析完成: {result.get('style', 'unknown')}")
            
            return result
            
        except Exception as e:
            logger.error(f"交易风格分析失败: {e}")
            return {
                "error": str(e),
                "style": "未知",
                "confidence": 0
            }
    
    async def identify_strategy(self, wallet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        识别交易策略
        
        Args:
            wallet_data: 钱包数据
            
        Returns:
            {
                "primary_strategy": "趋势跟踪",
                "secondary_strategies": ["网格交易", "套利"],
                "strategy_details": "详细说明",
                "effectiveness": 0.78,
                "suggestions": ["建议1", "建议2"]
            }
        """
        try:
            logger.info(f"开始识别交易策略: {wallet_data.get('address', 'unknown')}")
            
            # 构建提示词
            prompt = self._build_strategy_prompt(wallet_data)
            
            # 调用 AI
            messages = [
                {
                    "role": "system",
                    "content": "你是一位专业的交易策略分析师，擅长识别和评估各种交易策略。请以 JSON 格式返回分析结果。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = await self.deepseek.chat_completion(messages, max_tokens=1500)
            
            # 解析结果
            result = self._parse_response(response)
            
            logger.info(f"交易策略识别完成: {result.get('primary_strategy', 'unknown')}")
            
            return result
            
        except Exception as e:
            logger.error(f"交易策略识别失败: {e}")
            return {
                "error": str(e),
                "primary_strategy": "未知",
                "effectiveness": 0
            }
    
    async def assess_risk(self, wallet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        风险评估
        
        Args:
            wallet_data: 钱包数据
            
        Returns:
            {
                "risk_level": "低/中/高",
                "risk_score": 65,
                "risk_factors": ["杠杆使用过高", "集中度风险"],
                "strengths": ["止损及时", "仓位控制好"],
                "weaknesses": ["过度交易", "追涨杀跌"],
                "suggestions": ["降低杠杆", "分散投资"]
            }
        """
        try:
            logger.info(f"开始风险评估: {wallet_data.get('address', 'unknown')}")
            
            # 构建提示词
            prompt = self._build_risk_prompt(wallet_data)
            
            # 调用 AI
            messages = [
                {
                    "role": "system",
                    "content": "你是一位专业的风险管理分析师，擅长评估交易风险和提供风险控制建议。请以 JSON 格式返回分析结果。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = await self.deepseek.chat_completion(messages, max_tokens=1500)
            
            # 解析结果
            result = self._parse_response(response)
            
            logger.info(f"风险评估完成: {result.get('risk_level', 'unknown')}")
            
            return result
            
        except Exception as e:
            logger.error(f"风险评估失败: {e}")
            return {
                "error": str(e),
                "risk_level": "未知",
                "risk_score": 0
            }
    
    async def analyze_market_trend(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        市场趋势分析
        
        Args:
            market_data: 市场数据
            
        Returns:
            {
                "trend": "上涨/下跌/震荡",
                "strength": 0.75,
                "key_factors": ["成交量增加", "多头占优"],
                "outlook": "短期看涨",
                "timeframe": "1-3天",
                "confidence": 0.80
            }
        """
        try:
            logger.info("开始市场趋势分析")
            
            # 构建提示词
            prompt = self._build_market_prompt(market_data)
            
            # 调用 AI
            messages = [
                {
                    "role": "system",
                    "content": "你是一位专业的市场分析师，擅长分析市场趋势和预测价格走向。请以 JSON 格式返回分析结果。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = await self.deepseek.chat_completion(messages, max_tokens=1500)
            
            # 解析结果
            result = self._parse_response(response)
            
            logger.info(f"市场趋势分析完成: {result.get('trend', 'unknown')}")
            
            return result
            
        except Exception as e:
            logger.error(f"市场趋势分析失败: {e}")
            return {
                "error": str(e),
                "trend": "未知",
                "confidence": 0
            }
    
    async def comprehensive_analysis(
        self,
        wallet_data: Dict[str, Any],
        analysis_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        综合分析
        
        Args:
            wallet_data: 钱包数据
            analysis_types: 分析类型列表 ['style', 'strategy', 'risk']
            
        Returns:
            包含所有分析结果的字典
        """
        if analysis_types is None:
            analysis_types = ['style', 'strategy', 'risk']
        
        results = {
            'wallet_address': wallet_data.get('address', 'unknown'),
            'analyzed_at': datetime.now().isoformat(),
            'analyses': {}
        }
        
        # 执行各项分析
        if 'style' in analysis_types:
            results['analyses']['style'] = await self.analyze_trading_style(wallet_data)
        
        if 'strategy' in analysis_types:
            results['analyses']['strategy'] = await self.identify_strategy(wallet_data)
        
        if 'risk' in analysis_types:
            results['analyses']['risk'] = await self.assess_risk(wallet_data)
        
        return results
    
    def _build_style_prompt(self, wallet_data: Dict[str, Any]) -> str:
        """构建交易风格分析提示词"""
        metrics = wallet_data.get('metrics', {})
        
        prompt = f"""
请分析以下交易者的交易风格：

## 基本信息
- 钱包地址: {wallet_data.get('address', 'N/A')}
- 总交易次数: {metrics.get('total_trades', 0)}
- 交易天数: {metrics.get('trading_days', 0)}
- 总盈亏: ${metrics.get('total_pnl', 0):.2f}

## 交易表现
- 胜率: {metrics.get('win_rate', 0):.2f}%
- 盈亏比: {metrics.get('profit_loss_ratio', 0):.2f}
- 平均持仓时间: {metrics.get('avg_holding_time', 0):.2f} 小时
- 最大回撤: {metrics.get('max_drawdown', 0):.2f}%
- 夏普比率: {metrics.get('sharpe_ratio', 0):.2f}

## 资金管理
- 平均仓位: {metrics.get('avg_position_size', 0):.2f}%
- 最大仓位: {metrics.get('max_position_size', 0):.2f}%
- 平均杠杆: {metrics.get('avg_leverage', 1):.2f}x

## 交易习惯
- 日均交易次数: {metrics.get('trades_per_day', 0):.2f}
- 最活跃时段: {metrics.get('most_active_hour', 'N/A')}
- 交易品种数: {metrics.get('traded_symbols', 0)}

请从以下维度分析：
1. 交易风格类型（激进型/稳健型/保守型）
2. 主要特征（3-5个关键特征）
3. 风险偏好（高/中/低）
4. 详细描述（100字以内）
5. 置信度（0-1）

返回 JSON 格式：
{{
    "style": "风格类型",
    "characteristics": ["特征1", "特征2", "特征3"],
    "risk_preference": "风险偏好",
    "description": "详细描述",
    "confidence": 0.85
}}
"""
        return prompt
    
    def _build_strategy_prompt(self, wallet_data: Dict[str, Any]) -> str:
        """构建交易策略识别提示词"""
        metrics = wallet_data.get('metrics', {})
        
        prompt = f"""
请识别以下交易者的交易策略：

## 交易数据
- 总交易次数: {metrics.get('total_trades', 0)}
- 胜率: {metrics.get('win_rate', 0):.2f}%
- 盈亏比: {metrics.get('profit_loss_ratio', 0):.2f}
- 平均持仓时间: {metrics.get('avg_holding_time', 0):.2f} 小时
- 最大连胜: {metrics.get('max_consecutive_wins', 0)}
- 最大连亏: {metrics.get('max_consecutive_losses', 0)}

## 交易模式
- 做多次数: {metrics.get('long_trades', 0)}
- 做空次数: {metrics.get('short_trades', 0)}
- 平均交易间隔: {metrics.get('avg_trade_interval', 0):.2f} 小时
- 交易时段分布: {metrics.get('time_distribution', 'N/A')}

## 盈利特征
- 最大单笔盈利: ${metrics.get('max_profit', 0):.2f}
- 最大单笔亏损: ${metrics.get('max_loss', 0):.2f}
- 平均盈利: ${metrics.get('avg_profit', 0):.2f}
- 平均亏损: ${metrics.get('avg_loss', 0):.2f}

请识别：
1. 主要交易策略
2. 辅助策略（如有）
3. 策略详细说明
4. 策略有效性评分（0-1）
5. 改进建议（3-5条）

返回 JSON 格式：
{{
    "primary_strategy": "主要策略",
    "secondary_strategies": ["辅助策略1", "辅助策略2"],
    "strategy_details": "详细说明",
    "effectiveness": 0.78,
    "suggestions": ["建议1", "建议2", "建议3"]
}}
"""
        return prompt
    
    def _build_risk_prompt(self, wallet_data: Dict[str, Any]) -> str:
        """构建风险评估提示词"""
        metrics = wallet_data.get('metrics', {})
        
        prompt = f"""
请评估以下交易者的风险状况：

## 风险指标
- 最大回撤: {metrics.get('max_drawdown', 0):.2f}%
- 波动率: {metrics.get('volatility', 0):.2f}%
- 夏普比率: {metrics.get('sharpe_ratio', 0):.2f}
- 索提诺比率: {metrics.get('sortino_ratio', 0):.2f}

## 仓位管理
- 平均仓位: {metrics.get('avg_position_size', 0):.2f}%
- 最大仓位: {metrics.get('max_position_size', 0):.2f}%
- 平均杠杆: {metrics.get('avg_leverage', 1):.2f}x
- 最大杠杆: {metrics.get('max_leverage', 1):.2f}x

## 亏损控制
- 最大连续亏损: {metrics.get('max_consecutive_losses', 0)}
- 最大单笔亏损: ${metrics.get('max_loss', 0):.2f}
- 止损执行率: {metrics.get('stop_loss_rate', 0):.2f}%

## 集中度风险
- 交易品种数: {metrics.get('traded_symbols', 0)}
- 最大品种占比: {metrics.get('max_symbol_ratio', 0):.2f}%

请评估：
1. 风险等级（低/中/高）
2. 风险评分（0-100）
3. 主要风险因素（3-5个）
4. 优势（2-3个）
5. 劣势（2-3个）
6. 风险控制建议（3-5条）

返回 JSON 格式：
{{
    "risk_level": "风险等级",
    "risk_score": 65,
    "risk_factors": ["因素1", "因素2"],
    "strengths": ["优势1", "优势2"],
    "weaknesses": ["劣势1", "劣势2"],
    "suggestions": ["建议1", "建议2", "建议3"]
}}
"""
        return prompt
    
    def _build_market_prompt(self, market_data: Dict[str, Any]) -> str:
        """构建市场趋势分析提示词"""
        prompt = f"""
请分析当前市场趋势：

## 市场数据
- 活跃钱包数: {market_data.get('active_wallets', 0)}
- 总交易量: ${market_data.get('total_volume', 0):,.2f}
- 多空比: {market_data.get('long_short_ratio', 1):.2f}
- 平均盈利率: {market_data.get('avg_profit_rate', 0):.2f}%

## 趋势指标
- 盈利钱包占比: {market_data.get('profitable_ratio', 0):.2f}%
- 新增钱包数: {market_data.get('new_wallets', 0)}
- 交易活跃度: {market_data.get('activity_index', 0):.2f}

请分析：
1. 市场趋势（上涨/下跌/震荡）
2. 趋势强度（0-1）
3. 关键因素（3-5个）
4. 市场展望
5. 时间框架
6. 置信度（0-1）

返回 JSON 格式：
{{
    "trend": "趋势",
    "strength": 0.75,
    "key_factors": ["因素1", "因素2"],
    "outlook": "展望",
    "timeframe": "时间框架",
    "confidence": 0.80
}}
"""
        return prompt
    
    def _parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """解析 AI 响应"""
        try:
            # 获取内容
            content = response['choices'][0]['message']['content']
            
            # 尝试解析 JSON
            # 移除可能的 markdown 代码块标记
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            # 解析 JSON
            result = json.loads(content)
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {e}, 内容: {content[:200]}")
            return {
                "error": "JSON 解析失败",
                "raw_content": content
            }
        
        except Exception as e:
            logger.error(f"响应解析失败: {e}")
            return {
                "error": str(e)
            }


# 全局 AI 分析器实例
ai_analyzer = AIAnalyzer()


# 导出
__all__ = ['AIAnalyzer', 'ai_analyzer']

