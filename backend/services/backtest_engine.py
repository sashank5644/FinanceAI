"""Backtesting engine for strategy evaluation."""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Trade:
    """Represents a single trade."""
    symbol: str
    entry_date: datetime
    entry_price: float
    quantity: float
    exit_date: Optional[datetime] = None
    exit_price: Optional[float] = None
    pnl: Optional[float] = None
    return_pct: Optional[float] = None
    entry_reason: str = ""
    exit_reason: str = ""


class BacktestEngine:
    """Engine for backtesting trading strategies."""
    
    def __init__(
        self,
        initial_capital: float = 100000,
        commission: float = 0.001,
        slippage: float = 0.0005
    ):
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.reset()
    
    def reset(self):
        """Reset the engine state."""
        self.current_capital = self.initial_capital
        self.positions = {}  # symbol -> Trade
        self.closed_trades = []
        self.equity_curve = [self.initial_capital]
        self.dates = []
        self.daily_returns = []
    
    def run_backtest(
        self,
        strategy: Dict[str, Any],
        price_data: pd.DataFrame,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Run backtest for a strategy."""
        logger.info(f"Starting backtest from {start_date} to {end_date}")
        
        # Filter data to date range
        mask = (price_data.index >= start_date) & (price_data.index <= end_date)
        test_data = price_data.loc[mask]
        
        if test_data.empty:
            return {"error": "No data available for the specified date range"}
        
        # Simulate trading for each day
        for date, day_data in test_data.iterrows():
            self.dates.append(date)
            
            # Generate signals for this day
            signals = self._generate_signals(strategy, day_data, test_data[:date])
            
            # Execute trades based on signals
            self._execute_trades(signals, day_data, date)
            
            # Update portfolio value
            portfolio_value = self._calculate_portfolio_value(day_data)
            self.equity_curve.append(portfolio_value)
            
            # Calculate daily return
            if len(self.equity_curve) > 1:
                daily_return = (self.equity_curve[-1] - self.equity_curve[-2]) / self.equity_curve[-2]
                self.daily_returns.append(daily_return)
        
        # Close all remaining positions
        self._close_all_positions(test_data.iloc[-1], test_data.index[-1])
        
        # Calculate performance metrics
        metrics = self._calculate_metrics(test_data)
        
        return {
            "metrics": metrics,
            "trades": [self._trade_to_dict(t) for t in self.closed_trades],
            "equity_curve": self.equity_curve,
            "dates": [d.isoformat() for d in self.dates]
        }
    
    def _generate_signals(
        self,
        strategy: Dict[str, Any],
        current_data: pd.Series,
        historical_data: pd.DataFrame
    ) -> List[Dict[str, Any]]:
        """Generate trading signals based on strategy rules."""
        signals = []
        
        # Simple momentum strategy example
        if strategy.get("type") == "momentum":
            if len(historical_data) < 20:
                return signals
            
            # Calculate 20-day moving average
            ma_20 = historical_data["close"].rolling(window=20).mean().iloc[-1]
            current_price = current_data["close"]
            
            # Buy signal
            if current_price > ma_20 * 1.02:  # Price 2% above MA
                signals.append({
                    "symbol": current_data.name,
                    "action": "buy",
                    "reason": "Price above 20-day MA"
                })
            
            # Sell signal
            elif current_price < ma_20 * 0.98:  # Price 2% below MA
                signals.append({
                    "symbol": current_data.name,
                    "action": "sell",
                    "reason": "Price below 20-day MA"
                })
        
        return signals
    
    def _execute_trades(
        self,
        signals: List[Dict[str, Any]],
        current_data: pd.Series,
        date: datetime
    ):
        """Execute trades based on signals."""
        for signal in signals:
            symbol = signal["symbol"]
            action = signal["action"]
            
            if action == "buy" and symbol not in self.positions:
                # Calculate position size (equal weight for simplicity)
                position_size = self.current_capital * 0.1  # 10% per position
                price = current_data["close"] * (1 + self.slippage)
                quantity = position_size / price
                commission = position_size * self.commission
                
                if self.current_capital >= position_size + commission:
                    # Create new position
                    trade = Trade(
                        symbol=symbol,
                        entry_date=date,
                        entry_price=price,
                        quantity=quantity,
                        entry_reason=signal["reason"]
                    )
                    
                    self.positions[symbol] = trade
                    self.current_capital -= (position_size + commission)
            
            elif action == "sell" and symbol in self.positions:
                # Close position
                trade = self.positions[symbol]
                exit_price = current_data["close"] * (1 - self.slippage)
                self._close_position(symbol, exit_price, date, signal["reason"])
    
    def _close_position(
        self,
        symbol: str,
        exit_price: float,
        exit_date: datetime,
        reason: str
    ):
        """Close a position and record the trade."""
        if symbol not in self.positions:
            return
        
        trade = self.positions[symbol]
        trade.exit_price = exit_price
        trade.exit_date = exit_date
        trade.exit_reason = reason
        
        # Calculate P&L
        gross_pnl = (trade.exit_price - trade.entry_price) * trade.quantity
        exit_value = trade.exit_price * trade.quantity
        commission = exit_value * self.commission
        trade.pnl = gross_pnl - commission
        trade.return_pct = (trade.exit_price - trade.entry_price) / trade.entry_price
        
        # Update capital
        self.current_capital += exit_value - commission
        
        # Move to closed trades
        self.closed_trades.append(trade)
        del self.positions[symbol]
    
    def _close_all_positions(self, last_data: pd.Series, date: datetime):
        """Close all remaining positions."""
        symbols_to_close = list(self.positions.keys())
        for symbol in symbols_to_close:
            price = last_data.get("close", self.positions[symbol].entry_price)
            self._close_position(symbol, price, date, "End of backtest")
    
    def _calculate_portfolio_value(self, current_data: pd.Series) -> float:
        """Calculate total portfolio value."""
        positions_value = 0
        for symbol, trade in self.positions.items():
            current_price = current_data.get("close", trade.entry_price)
            positions_value += current_price * trade.quantity
        
        return self.current_capital + positions_value
    
    def _calculate_metrics(self, price_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate performance metrics."""
        if not self.daily_returns:
            return {"error": "No trades executed"}
        
        returns = np.array(self.daily_returns)
        equity = np.array(self.equity_curve[1:])  # Skip initial capital
        
        # Basic metrics
        total_return = (equity[-1] - self.initial_capital) / self.initial_capital
        trading_days = len(returns)
        years = trading_days / 252
        
        if years > 0:
            annualized_return = (1 + total_return) ** (1/years) - 1
        else:
            annualized_return = 0
        
        # Risk metrics
        volatility = np.std(returns) * np.sqrt(252) if len(returns) > 1 else 0
        sharpe_ratio = (annualized_return - 0.02) / volatility if volatility > 0 else 0
        
        # Drawdown calculation
        peak = np.maximum.accumulate(equity)
        drawdown = (equity - peak) / peak
        max_drawdown = np.min(drawdown) if len(drawdown) > 0 else 0
        
        # Trade statistics
        winning_trades = [t for t in self.closed_trades if t.pnl > 0]
        losing_trades = [t for t in self.closed_trades if t.pnl <= 0]
        
        win_rate = len(winning_trades) / len(self.closed_trades) if self.closed_trades else 0
        avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0
        
        return {
            "total_return": round(total_return * 100, 2),
            "annualized_return": round(annualized_return * 100, 2),
            "volatility": round(volatility * 100, 2),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "max_drawdown": round(max_drawdown * 100, 2),
            "total_trades": len(self.closed_trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": round(win_rate * 100, 2),
            "average_win": round(avg_win, 2),
            "average_loss": round(avg_loss, 2),
            "final_value": round(equity[-1], 2)
        }
    
    def _trade_to_dict(self, trade: Trade) -> Dict[str, Any]:
        """Convert Trade object to dictionary."""
        return {
            "symbol": trade.symbol,
            "entry_date": trade.entry_date.isoformat(),
            "entry_price": round(trade.entry_price, 2),
            "exit_date": trade.exit_date.isoformat() if trade.exit_date else None,
            "exit_price": round(trade.exit_price, 2) if trade.exit_price else None,
            "quantity": round(trade.quantity, 2),
            "pnl": round(trade.pnl, 2) if trade.pnl else None,
            "return_pct": round(trade.return_pct * 100, 2) if trade.return_pct else None,
            "entry_reason": trade.entry_reason,
            "exit_reason": trade.exit_reason
        }
