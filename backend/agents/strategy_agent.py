"""Strategy agent for generating investment strategies."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import uuid

from langchain.tools import Tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from .base_agent import BaseAgent
from config import settings
from models.strategy_models import Strategy, StrategyType, RiskLevel, StrategyStatus
from models.postgres_models import Research
from services.cache_service import cache_service
from utils.db import get_db

logger = logging.getLogger(__name__)


class StrategyAgent(BaseAgent):
    """Agent for generating and managing investment strategies."""
    
    def __init__(self, mcp_servers: Optional[List[str]] = None):
        super().__init__(
            name="StrategyAgent",
            description="Generates data-driven investment strategies",
            model_name="gemini-1.5-pro",  # Use more powerful model for strategy generation
            mcp_servers=mcp_servers or []
        )
        
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=settings.google_api_key
        )
    
    def get_system_prompt(self) -> str:
        """System prompt for strategy generation."""
        return """You are an expert investment strategist and portfolio manager with deep knowledge of quantitative finance.

## Your Role:
Generate sophisticated, data-driven investment strategies based on research findings and market conditions.

## Strategy Types You Can Create:

1. **Long Only**: Buy and hold quality stocks
2. **Long/Short**: Buy winners, short losers
3. **Market Neutral**: Balance long/short for zero market exposure
4. **Momentum**: Follow trends and price momentum
5. **Value**: Buy undervalued stocks
6. **Growth**: Focus on high-growth companies
7. **Mean Reversion**: Trade extremes back to mean
8. **Pairs Trading**: Exploit relative mispricings

## Key Considerations:

**Risk Management:**
- Position sizing (Kelly Criterion, Equal Weight, Risk Parity)
- Stop losses and take profits
- Maximum drawdown limits
- Diversification requirements

**Entry Rules:**
- Technical indicators (RSI, MACD, Moving Averages)
- Fundamental metrics (P/E, P/B, Revenue Growth)
- Market regime filters
- Sentiment indicators

**Exit Rules:**
- Profit targets
- Stop losses
- Time-based exits
- Reversal signals

**Portfolio Construction:**
- Number of positions
- Sector allocation
- Market cap distribution
- Rebalancing frequency

## Output Format:
Always structure strategies with clear, actionable rules that can be backtested and implemented.
Include specific metrics, thresholds, and parameters."""
    
    async def get_custom_tools(self) -> List[Tool]:
        """Get strategy-specific tools."""
        
        def analyze_market_conditions() -> Dict[str, Any]:
            """Analyze current market conditions for strategy generation."""
            try:
                # Get market overview
                snapshot = cache_service.get_market_snapshot()
                
                # Get sector performance
                # This would analyze various market indicators
                
                conditions = {
                    "trend": "bullish",  # or bearish, neutral
                    "volatility": "moderate",  # low, moderate, high
                    "momentum": "positive",
                    "market_regime": "risk_on",  # or risk_off
                    "recommended_strategies": [
                        "momentum",
                        "growth",
                        "long_only"
                    ]
                }
                
                return {
                    "success": True,
                    "data": conditions
                }
                
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        def get_research_insights(research_id: str = None) -> Dict[str, Any]:
            """Get insights from previous research for strategy generation."""
            db = next(get_db())
            try:
                if research_id:
                    research = db.query(Research).filter(Research.id == research_id).first()
                    if research:
                        return {
                            "success": True,
                            "data": {
                                "query": research.query,
                                "findings": research.key_findings,
                                "entities": research.entities_extracted
                            }
                        }
                
                # Get recent research
                recent = db.query(Research).order_by(Research.created_at.desc()).limit(5).all()
                
                insights = []
                for r in recent:
                    insights.append({
                        "id": r.id,
                        "query": r.query,
                        "created": r.created_at.isoformat()
                    })
                
                return {
                    "success": True,
                    "data": insights
                }
                
            except Exception as e:
                return {"success": False, "error": str(e)}
            finally:
                db.close()
        
        def calculate_position_sizing(
            risk_level: str,
            num_positions: int,
            strategy_type: str
        ) -> Dict[str, Any]:
            """Calculate position sizing based on risk parameters."""
            
            risk_multipliers = {
                "conservative": 0.5,
                "moderate": 1.0,
                "aggressive": 1.5
            }
            
            base_position_size = 1.0 / num_positions
            risk_mult = risk_multipliers.get(risk_level, 1.0)
            
            # Adjust for strategy type
            if strategy_type == "long_short":
                gross_exposure = 2.0  # 100% long + 100% short
                net_exposure = 0.0    # Market neutral
            else:
                gross_exposure = 1.0
                net_exposure = 1.0
            
            return {
                "success": True,
                "data": {
                    "base_position_size": round(base_position_size, 3),
                    "risk_adjusted_size": round(base_position_size * risk_mult, 3),
                    "max_position_size": round(min(0.25, base_position_size * risk_mult * 1.5), 3),
                    "gross_exposure": gross_exposure,
                    "net_exposure": net_exposure,
                    "stop_loss": round(0.02 / risk_mult, 3),  # 2% base, adjusted for risk
                    "position_limits": {
                        "min_positions": max(5, num_positions // 2),
                        "max_positions": min(30, num_positions * 2),
                        "sector_limit": 0.3  # 30% max in one sector
                    }
                }
            }
        
        def generate_entry_exit_rules(
            strategy_type: str,
            instruments: List[str]
        ) -> Dict[str, Any]:
            """Generate specific entry and exit rules for a strategy."""
            
            # Define rules based on strategy type
            rules_map = {
                "momentum": {
                    "entry": [
                        "Price > 50-day moving average",
                        "RSI(14) between 50 and 70",
                        "Volume > 20-day average volume",
                        "52-week high within 10%"
                    ],
                    "exit": [
                        "Price < 20-day moving average",
                        "RSI(14) < 30 or > 80",
                        "Stop loss: -5% from entry",
                        "Trailing stop: 3% from peak"
                    ]
                },
                "value": {
                    "entry": [
                        "P/E ratio < sector average * 0.8",
                        "P/B ratio < 1.5",
                        "Debt/Equity < 0.5",
                        "Positive earnings growth"
                    ],
                    "exit": [
                        "P/E ratio > sector average * 1.2",
                        "Fundamental deterioration",
                        "Stop loss: -10% from entry",
                        "Target price reached (+30%)"
                    ]
                },
                "mean_reversion": {
                    "entry": [
                        "Price < lower Bollinger Band (20, 2)",
                        "RSI(14) < 30 (oversold)",
                        "Z-score < -2",
                        "Support level nearby"
                    ],
                    "exit": [
                        "Price > middle Bollinger Band",
                        "RSI(14) > 50",
                        "Z-score > 0",
                        "Stop loss: -3% from entry"
                    ]
                }
            }
            
            rules = rules_map.get(strategy_type, rules_map["momentum"])
            
            return {
                "success": True,
                "data": {
                    "strategy_type": strategy_type,
                    "entry_rules": rules["entry"],
                    "exit_rules": rules["exit"],
                    "risk_rules": [
                        "Maximum 10% allocation per position",
                        "Sector limit: 30% of portfolio",
                        "Correlation limit: 0.7 between positions"
                    ]
                }
            }
        
        return [
            Tool(
                name="analyze_market_conditions",
                func=analyze_market_conditions,
                description="Analyze current market conditions for strategy generation"
            ),
            Tool(
                name="get_research_insights",
                func=get_research_insights,
                description="Get insights from research to inform strategy"
            ),
            Tool(
                name="calculate_position_sizing",
                func=calculate_position_sizing,
                description="Calculate position sizing and risk parameters"
            ),
            Tool(
                name="generate_entry_exit_rules",
                func=generate_entry_exit_rules,
                description="Generate specific entry and exit rules for strategies"
            )
        ]
    
    async def create_strategy(
        self,
        name: str,
        description: str,
        strategy_type: str,
        risk_level: str,
        instruments: List[str] = None,
        research_id: str = None
    ) -> str:
        """Create a new investment strategy."""
        
        db = next(get_db())
        try:
            # Generate strategy using AI
            prompt = f"""Create a detailed investment strategy with the following parameters:
            
            Name: {name}
            Description: {description}
            Type: {strategy_type}
            Risk Level: {risk_level}
            Instruments: {instruments or 'To be determined'}
            
            Provide specific, actionable rules and parameters."""
            
            result = await self.run(prompt)
            
            if result.get("success"):
                # Create strategy in database
                strategy = Strategy(
                    id=f"strategy_{uuid.uuid4().hex[:8]}",
                    name=name,
                    description=description,
                    strategy_type=StrategyType[strategy_type.upper()],
                    risk_level=RiskLevel[risk_level.upper()],
                    instruments=instruments or [],
                    research_id=research_id,
                    created_by="strategy_agent"
                )
                
                db.add(strategy)
                db.commit()
                
                logger.info(f"Created strategy: {strategy.id}")
                return strategy.id
            else:
                raise Exception(f"Failed to generate strategy: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Strategy creation error: {e}")
            db.rollback()
            raise
        finally:
            db.close()
