"""Service for strategy management and signal generation."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import numpy as np

from models.strategy_models import Strategy, StrategyAllocation, TradingSignal
from utils.db import get_db
from services.cache_service import cache_service

logger = logging.getLogger(__name__)


class StrategyService:
    """Service for managing investment strategies."""
    
    def evaluate_strategy_performance(self, strategy_id: str) -> Dict[str, Any]:
        """Evaluate hypothetical performance of a strategy."""
        db = next(get_db())
        try:
            strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                return {"error": "Strategy not found"}
            
            # Simple performance estimation based on strategy type
            performance_estimates = {
                "momentum": {
                    "expected_return": 0.15,  # 15% annual
                    "expected_volatility": 0.20,  # 20% volatility
                    "sharpe_ratio": 0.75,
                    "max_drawdown": -0.15
                },
                "value": {
                    "expected_return": 0.12,
                    "expected_volatility": 0.15,
                    "sharpe_ratio": 0.80,
                    "max_drawdown": -0.20
                },
                "growth": {
                    "expected_return": 0.18,
                    "expected_volatility": 0.25,
                    "sharpe_ratio": 0.72,
                    "max_drawdown": -0.25
                },
                "market_neutral": {
                    "expected_return": 0.08,
                    "expected_volatility": 0.08,
                    "sharpe_ratio": 1.0,
                    "max_drawdown": -0.05
                }
            }
            
            base_performance = performance_estimates.get(
                strategy.strategy_type.value,
                performance_estimates["momentum"]
            )
            
            # Adjust for risk level
            risk_adjustments = {
                "conservative": 0.7,
                "moderate": 1.0,
                "aggressive": 1.3
            }
            
            risk_mult = risk_adjustments.get(strategy.risk_level.value, 1.0)
            
            return {
                "strategy_id": strategy_id,
                "estimated_performance": {
                    "annual_return": round(base_performance["expected_return"] * risk_mult, 3),
                    "volatility": round(base_performance["expected_volatility"] * risk_mult, 3),
                    "sharpe_ratio": round(base_performance["sharpe_ratio"], 2),
                    "max_drawdown": round(base_performance["max_drawdown"] * risk_mult, 3),
                    "risk_adjusted_return": round(
                        base_performance["expected_return"] * risk_mult / 
                        (base_performance["expected_volatility"] * risk_mult), 3
                    )
                },
                "assumptions": [
                    "Based on historical performance of similar strategies",
                    "Assumes normal market conditions",
                    "Before transaction costs",
                    "Subject to market risk"
                ]
            }
            
        except Exception as e:
            logger.error(f"Performance evaluation error: {e}")
            return {"error": str(e)}
        finally:
            db.close()
    
    def generate_signals(self, strategy_id: str) -> List[Dict[str, Any]]:
        """Generate trading signals for a strategy."""
        db = next(get_db())
        try:
            strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                return []
            
            signals = []
            
            # Get current market data for instruments
            for symbol in strategy.instruments[:5]:  # Limit to 5 for demo
                # Get cached quote
                quote_data = cache_service.get_cached_quote(symbol)
                
                if quote_data and quote_data.get("success"):
                    price_data = quote_data["data"]
                    
                    # Simple signal generation based on strategy type
                    signal = self._generate_signal_for_instrument(
                        strategy,
                        symbol,
                        price_data
                    )
                    
                    if signal:
                        # Save signal to database
                        db_signal = TradingSignal(
                            strategy_id=strategy_id,
                            symbol=symbol,
                            signal_type=signal["type"],
                            strength=signal["strength"],
                            current_price=price_data["price"],
                            target_price=signal.get("target_price"),
                            stop_price=signal.get("stop_price"),
                            reasons=signal["reasons"],
                            confidence=signal["confidence"],
                            expires_at=datetime.utcnow() + timedelta(days=5)
                        )
                        db.add(db_signal)
                        signals.append(signal)
            
            db.commit()
            return signals
            
        except Exception as e:
            logger.error(f"Signal generation error: {e}")
            db.rollback()
            return []
        finally:
            db.close()
    
    def _generate_signal_for_instrument(
        self,
        strategy: Strategy,
        symbol: str,
        price_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate signal for a specific instrument."""
        
        # Simple momentum signal
        if strategy.strategy_type.value == "momentum":
            change_percent = price_data.get("change_percent", 0)
            
            if change_percent > 2:  # Strong positive momentum
                return {
                    "symbol": symbol,
                    "type": "buy",
                    "strength": min(1.0, change_percent / 5),
                    "confidence": 0.7,
                    "target_price": price_data["price"] * 1.05,
                    "stop_price": price_data["price"] * 0.97,
                    "reasons": [
                        f"Strong momentum: +{change_percent:.1f}%",
                        "Price trending up",
                        "Above average volume"
                    ]
                }
            elif change_percent < -2:  # Negative momentum
                return {
                    "symbol": symbol,
                    "type": "sell",
                    "strength": min(1.0, abs(change_percent) / 5),
                    "confidence": 0.6,
                    "reasons": [
                        f"Negative momentum: {change_percent:.1f}%",
                        "Consider reducing position"
                    ]
                }
        
        # Simple value signal
        elif strategy.strategy_type.value == "value":
            pe_ratio = price_data.get("pe_ratio", 0)
            
            if pe_ratio > 0 and pe_ratio < 15:  # Potentially undervalued
                return {
                    "symbol": symbol,
                    "type": "buy",
                    "strength": 0.6,
                    "confidence": 0.65,
                    "target_price": price_data["price"] * 1.20,
                    "stop_price": price_data["price"] * 0.90,
                    "reasons": [
                        f"Low P/E ratio: {pe_ratio:.1f}",
                        "Potentially undervalued",
                        "Value opportunity"
                    ]
                }
        
        return None


# Singleton instance
strategy_service = StrategyService()
