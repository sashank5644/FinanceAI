"""Backtesting API endpoints."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import asyncio

from agents.backtest_agent import BacktestAgent
from models.backtest_models import BacktestResult, BacktestStatus
from utils.db import get_db

router = APIRouter()

# Global backtest agent
backtest_agent = None


class BacktestRequest(BaseModel):
    """Backtest request model."""
    strategy_id: str
    start_date: date
    end_date: date
    initial_capital: float = 100000.0
    benchmark: str = "SPY"
    include_transaction_costs: bool = True
    monte_carlo_simulations: int = 0


class BacktestResponse(BaseModel):
    """Backtest response model."""
    backtest_id: str
    strategy_id: str
    status: str
    created_at: datetime
    metrics: Optional[Dict[str, float]] = None
    error: Optional[str] = None


@router.post("/run", response_model=BacktestResponse)
async def run_backtest(
    request: BacktestRequest,
    background_tasks: BackgroundTasks
):
    """Run a backtest for a strategy."""
    global backtest_agent
    
    try:
        if backtest_agent is None:
            backtest_agent = BacktestAgent()
            await backtest_agent.initialize()
        
        # Run backtest
        backtest_id = await backtest_agent.run_backtest(
            strategy_id=request.strategy_id,
            start_date=datetime.combine(request.start_date, datetime.min.time()),
            end_date=datetime.combine(request.end_date, datetime.min.time()),
            initial_capital=request.initial_capital
        )
        
        return BacktestResponse(
            backtest_id=backtest_id,
            strategy_id=request.strategy_id,
            status="completed",
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        return BacktestResponse(
            backtest_id="error",
            strategy_id=request.strategy_id,
            status="failed",
            created_at=datetime.utcnow(),
            error=str(e)
        )


@router.get("/{backtest_id}", response_model=BacktestResponse)
async def get_backtest_result(backtest_id: str):
    """Get backtest results."""
    db = next(get_db())
    try:
        backtest = db.query(BacktestResult).filter(
            BacktestResult.id == backtest_id
        ).first()
        
        if not backtest:
            raise HTTPException(status_code=404, detail="Backtest not found")
        
        metrics = None
        if backtest.status == BacktestStatus.COMPLETED:
            metrics = {
                "total_return": backtest.total_return,
                "annualized_return": backtest.annualized_return,
                "volatility": backtest.volatility,
                "sharpe_ratio": backtest.sharpe_ratio,
                "max_drawdown": backtest.max_drawdown,
                "total_trades": backtest.total_trades,
                "win_rate": backtest.win_rate,
                "final_value": backtest.final_value
            }
        
        return BacktestResponse(
            backtest_id=backtest.id,
            strategy_id=backtest.strategy_id,
            status=backtest.status.value,
            created_at=backtest.created_at,
            metrics=metrics,
            error=backtest.error_message
        )
    finally:
        db.close()


@router.get("/{backtest_id}/report")
async def get_backtest_report(backtest_id: str):
    """Get detailed backtest report with charts data."""
    db = next(get_db())
    try:
        backtest = db.query(BacktestResult).filter(
            BacktestResult.id == backtest_id
        ).first()
        
        if not backtest:
            raise HTTPException(status_code=404, detail="Backtest not found")
        
        if backtest.status != BacktestStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Backtest not completed")
        
        # Prepare chart data
        equity_data = []
        if backtest.equity_curve:
            for i, value in enumerate(backtest.equity_curve):
                equity_data.append({
                    "day": i,
                    "value": round(value, 2),
                    "return": round((value / backtest.initial_capital - 1) * 100, 2)
                })
        
        # Trade analysis
        trade_analysis = {
            "total": backtest.total_trades or 0,
            "winners": backtest.winning_trades or 0,
            "losers": backtest.losing_trades or 0,
            "win_rate": backtest.win_rate or 0,
            "average_win": backtest.average_win or 0,
            "average_loss": backtest.average_loss or 0
        }
        
        return {
            "backtest_id": backtest_id,
            "strategy_id": backtest.strategy_id,
            "period": {
                "start": backtest.start_date.isoformat(),
                "end": backtest.end_date.isoformat()
            },
            "performance": {
                "initial_capital": backtest.initial_capital,
                "final_value": backtest.final_value,
                "total_return": backtest.total_return,
                "annualized_return": backtest.annualized_return,
                "volatility": backtest.volatility,
                "sharpe_ratio": backtest.sharpe_ratio,
                "max_drawdown": backtest.max_drawdown
            },
            "trade_analysis": trade_analysis,
            "equity_curve": equity_data,
            "trades": backtest.trades or []
        }
    finally:
        db.close()


@router.get("/strategy/{strategy_id}/history")
async def get_strategy_backtest_history(
    strategy_id: str,
    limit: int = 10
):
    """Get backtest history for a strategy."""
    db = next(get_db())
    try:
        backtests = db.query(BacktestResult).filter(
            BacktestResult.strategy_id == strategy_id
        ).order_by(BacktestResult.created_at.desc()).limit(limit).all()
        
        return {
            "strategy_id": strategy_id,
            "backtests": [
                {
                    "id": b.id,
                    "status": b.status.value,
                    "created_at": b.created_at.isoformat(),
                    "period": f"{b.start_date.date()} to {b.end_date.date()}",
                    "total_return": b.total_return,
                    "sharpe_ratio": b.sharpe_ratio
                }
                for b in backtests
            ]
        }
    finally:
        db.close()


@router.post("/analyze/{backtest_id}")
async def analyze_backtest(backtest_id: str):
    """Get AI analysis of backtest results."""
    global backtest_agent
    
    db = next(get_db())
    try:
        backtest = db.query(BacktestResult).filter(
            BacktestResult.id == backtest_id
        ).first()
        
        if not backtest:
            raise HTTPException(status_code=404, detail="Backtest not found")
        
        if backtest_agent is None:
            backtest_agent = BacktestAgent()
            await backtest_agent.initialize()
        
        # Create analysis prompt
        metrics = {
            "total_return": backtest.total_return,
            "annualized_return": backtest.annualized_return,
            "volatility": backtest.volatility,
            "sharpe_ratio": backtest.sharpe_ratio,
            "max_drawdown": backtest.max_drawdown,
            "win_rate": backtest.win_rate
        }
        
        prompt = f"""Analyze these backtest results and provide insights:
        
        Performance Metrics:
        - Total Return: {metrics['total_return']}%
        - Annualized Return: {metrics['annualized_return']}%
        - Volatility: {metrics['volatility']}%
        - Sharpe Ratio: {metrics['sharpe_ratio']}
        - Max Drawdown: {metrics['max_drawdown']}%
        - Win Rate: {metrics['win_rate']}%
        
        Provide:
        1. Overall assessment
        2. Key strengths and weaknesses
        3. Risk analysis
        4. Recommendations for improvement
        """
        
        result = await backtest_agent.run(prompt)
        
        return {
            "backtest_id": backtest_id,
            "analysis": result.get("output", "Analysis not available"),
            "metrics": metrics
        }
    finally:
        db.close()