"""Strategy-related API endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from models import Strategy, StrategyType, RiskLevel, StrategyStatus
from utils.db import get_db

router = APIRouter()


class StrategyRequest(BaseModel):
    """Strategy generation request."""
    name: str
    description: Optional[str] = None
    strategy_type: str = "momentum"
    risk_level: str = "moderate"
    instruments: Optional[List[str]] = None
    research_id: Optional[str] = None
    target_return: Optional[float] = None


class StrategyResponse(BaseModel):
    """Strategy response model."""
    strategy_id: str
    name: str
    status: str
    created_at: datetime
    details: Optional[Dict[str, Any]] = None


@router.post("/generate", response_model=StrategyResponse)
async def generate_strategy(request: StrategyRequest):
    """Generate a new investment strategy using AI."""
    try:
        import uuid
        
        # Default instruments based on strategy type
        default_instruments = {
            "momentum": ["AAPL", "MSFT", "NVDA", "TSLA", "META", "GOOGL", "AMZN"],
            "value": ["BRK-B", "JPM", "BAC", "WMT", "JNJ", "PG", "XOM"],
            "growth": ["NVDA", "META", "AMZN", "CRM", "ADBE", "NOW", "SHOP"],
            "market_neutral": ["SPY", "QQQ", "IWM", "DIA", "VTI"],
            "mean_reversion": ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
        }
        
        db = next(get_db())
        try:
            # Convert string values to enum values
            strategy_type_enum = StrategyType[request.strategy_type.upper()]
            risk_level_enum = RiskLevel[request.risk_level.upper()]
            
            # Use provided instruments or default based on strategy type
            instruments = request.instruments
            if not instruments:
                instruments = default_instruments.get(request.strategy_type, 
                                                    default_instruments["momentum"])
            
            # Generate entry and exit rules based on strategy type
            entry_rules, exit_rules = generate_strategy_rules(request.strategy_type)
            
            strategy = Strategy(
                id=f"strategy_{uuid.uuid4().hex[:8]}",
                name=request.name,
                description=request.description or f"AI-generated {request.strategy_type} strategy",
                strategy_type=strategy_type_enum,
                risk_level=risk_level_enum,
                status=StrategyStatus.ACTIVE,  # Set to ACTIVE instead of DRAFT
                instruments=instruments,
                entry_rules=entry_rules,
                exit_rules=exit_rules,
                max_positions=len(instruments),
                stop_loss=0.05 if risk_level_enum == RiskLevel.CONSERVATIVE else 0.08,
                created_by="api"
            )
            
            db.add(strategy)
            db.commit()
            
            return StrategyResponse(
                strategy_id=strategy.id,
                name=strategy.name,
                status="created",
                created_at=strategy.created_at or datetime.utcnow(),
                details={
                    "instruments": instruments,
                    "entry_rules": entry_rules,
                    "exit_rules": exit_rules
                }
            )
            
        except KeyError as e:
            raise HTTPException(status_code=400, detail=f"Invalid enum value: {str(e)}")
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def generate_strategy_rules(strategy_type: str) -> tuple:
    """Generate entry and exit rules based on strategy type."""
    
    rules_map = {
        "momentum": {
            "entry": {
                "conditions": [
                    "Price > 20-day SMA",
                    "RSI(14) between 50-70", 
                    "Volume > 20-day average",
                    "Positive MACD crossover"
                ],
                "indicators": ["SMA_20", "RSI_14", "VOLUME_AVG", "MACD"]
            },
            "exit": {
                "conditions": [
                    "Price < 10-day SMA",
                    "RSI(14) < 30 or > 80",
                    "Stop loss: -5%",
                    "Trailing stop: 3%"
                ],
                "indicators": ["SMA_10", "RSI_14", "STOP_LOSS", "TRAILING_STOP"]
            }
        },
        "value": {
            "entry": {
                "conditions": [
                    "P/E < Industry Average * 0.8",
                    "P/B < 1.5",
                    "Debt/Equity < 0.5",
                    "FCF Yield > 5%"
                ],
                "indicators": ["PE_RATIO", "PB_RATIO", "DEBT_EQUITY", "FCF_YIELD"]
            },
            "exit": {
                "conditions": [
                    "P/E > Industry Average * 1.2",
                    "Target price reached (+30%)",
                    "Fundamental deterioration",
                    "Stop loss: -10%"
                ],
                "indicators": ["PE_RATIO", "TARGET_PRICE", "FUNDAMENTALS", "STOP_LOSS"]
            }
        },
        "growth": {
            "entry": {
                "conditions": [
                    "Revenue growth > 20% YoY",
                    "Earnings growth > 15% YoY",
                    "Price above 50-day SMA",
                    "Relative strength > 80"
                ],
                "indicators": ["REVENUE_GROWTH", "EARNINGS_GROWTH", "SMA_50", "RS_RATING"]
            },
            "exit": {
                "conditions": [
                    "Growth deceleration",
                    "Price < 50-day SMA",
                    "Stop loss: -8%",
                    "Valuation extreme (P/E > 50)"
                ],
                "indicators": ["GROWTH_RATE", "SMA_50", "STOP_LOSS", "PE_RATIO"]
            }
        },
        "mean_reversion": {
            "entry": {
                "conditions": [
                    "Price < Lower Bollinger Band",
                    "RSI(14) < 30",
                    "Z-score < -2",
                    "Near support level"
                ],
                "indicators": ["BOLLINGER_BANDS", "RSI_14", "Z_SCORE", "SUPPORT_LEVEL"]
            },
            "exit": {
                "conditions": [
                    "Price > Middle Bollinger Band",
                    "RSI(14) > 50",
                    "Z-score > 0",
                    "Stop loss: -3%"
                ],
                "indicators": ["BOLLINGER_BANDS", "RSI_14", "Z_SCORE", "STOP_LOSS"]
            }
        },
        "market_neutral": {
            "entry": {
                "conditions": [
                    "Long: Strong relative strength",
                    "Short: Weak relative strength",
                    "Sector neutral exposure",
                    "Beta neutral portfolio"
                ],
                "indicators": ["RELATIVE_STRENGTH", "SECTOR_EXPOSURE", "PORTFOLIO_BETA"]
            },
            "exit": {
                "conditions": [
                    "Convergence of spreads",
                    "Risk limit breached",
                    "Rebalance monthly",
                    "Stop loss: -2% per pair"
                ],
                "indicators": ["SPREAD", "RISK_METRICS", "REBALANCE_SIGNAL", "STOP_LOSS"]
            }
        }
    }
    
    rules = rules_map.get(strategy_type, rules_map["momentum"])
    return rules["entry"], rules["exit"]


@router.get("/list")
async def list_strategies(
    limit: int = 10,
    offset: int = 0,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all strategies."""
    try:
        query = db.query(Strategy)
        
        if status:
            query = query.filter(Strategy.status == status)
        
        total = query.count()
        strategies = query.offset(offset).limit(limit).all()
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": [
                {
                    "id": s.id,
                    "name": s.name,
                    "type": s.strategy_type.value if s.strategy_type else "unknown",
                    "risk_level": s.risk_level.value if s.risk_level else "unknown",
                    "status": s.status.value if s.status else "draft",
                    "created_at": s.created_at.isoformat() if s.created_at else datetime.utcnow().isoformat()
                }
                for s in strategies
            ]
        }
    except Exception as e:
        print(f"Error in list_strategies: {str(e)}")
        return {
            "total": 0,
            "limit": limit,
            "offset": offset,
            "items": []
        }


@router.get("/types/available")
async def get_strategy_types():
    """Get available strategy types and their descriptions."""
    return {
        "types": [
            {
                "id": "momentum",
                "name": "Momentum",
                "description": "Follow price trends and momentum",
                "risk_level": "moderate",
                "typical_return": "12-18%",
                "suitable_for": "Trending markets"
            },
            {
                "id": "value",
                "name": "Value Investing",
                "description": "Buy undervalued stocks",
                "risk_level": "moderate",
                "typical_return": "10-15%",
                "suitable_for": "Patient investors"
            },
            {
                "id": "growth",
                "name": "Growth",
                "description": "Focus on high-growth companies",
                "risk_level": "aggressive",
                "typical_return": "15-25%",
                "suitable_for": "Long-term investors"
            },
            {
                "id": "market_neutral",
                "name": "Market Neutral",
                "description": "Balance long and short positions",
                "risk_level": "conservative",
                "typical_return": "6-10%",
                "suitable_for": "Risk-averse investors"
            },
            {
                "id": "mean_reversion",
                "name": "Mean Reversion",
                "description": "Trade extremes back to average",
                "risk_level": "moderate",
                "typical_return": "8-12%",
                "suitable_for": "Range-bound markets"
            }
        ]
    }


@router.delete("/{strategy_id}")
async def delete_strategy(strategy_id: str, db: Session = Depends(get_db)):
    """Delete a strategy by ID."""
    try:
        strategy = db.query(Strategy).filter_by(id=strategy_id).first()
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        db.delete(strategy)
        db.commit()
        return {"success": True, "message": f"Strategy {strategy_id} deleted"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()