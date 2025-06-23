import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { apiClient } from "@/services/api";
import { formatCurrency, formatPercentage } from "@/lib/utils";
import { BacktestErrorHandler } from "./BacktestErrorHandler";
import {
  Calendar,
  DollarSign,
  TrendingUp,
  AlertTriangle,
  BarChart3
} from "lucide-react";

interface EnhancedBacktestModalProps {
  strategyId: string;
  strategyName: string;
  onClose: () => void;
}

export function EnhancedBacktestModal({ strategyId, strategyName, onClose }: EnhancedBacktestModalProps) {
  const [startDate, setStartDate] = useState("2023-01-01");
  const [endDate, setEndDate] = useState("2024-01-01");
  const [initialCapital, setInitialCapital] = useState("100000");
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState("");
  const [showErrorHandler, setShowErrorHandler] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const runBacktest = async () => {
    setIsRunning(true);
    setError("");
    setResults(null);
    setShowErrorHandler(false);

    try {
      const response = await apiClient.runBacktest({
        strategy_id: strategyId,
        start_date: startDate,
        end_date: endDate,
        initial_capital: parseFloat(initialCapital)
      });

      if (response.success && response.data) {
        // Check if the response contains an error indicator
        if (response.data.backtest_id === "error") {
          setErrorMessage(response.data.error || "Failed to run backtest");
          setShowErrorHandler(true);
          return;
        }
        
        // Wait a moment for processing
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Get results
        try {
          const resultResponse = await apiClient.getBacktestReport(response.data.backtest_id);
          if (resultResponse.success) {
            setResults(resultResponse.data);
          } else {
            setError("Failed to get backtest results");
          }
        } catch (reportErr) {
          setErrorMessage("Could not retrieve backtest report");
          setShowErrorHandler(true);
        }
      } else {
        setErrorMessage(response.error || "Failed to run backtest");
        setShowErrorHandler(true);
      }
    } catch (err) {
      setErrorMessage("An error occurred while running the backtest");
      setShowErrorHandler(true);
    } finally {
      setIsRunning(false);
    }
  };

  // If we need to show the error handler
  if (showErrorHandler) {
    return (
      <BacktestErrorHandler
        strategyId={strategyId}
        strategyName={strategyName}
        onClose={onClose}
        errorMessage={errorMessage}
      />
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-auto">
        <CardHeader>
          <CardTitle>Backtest Strategy: {strategyName}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {!results ? (
            <>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Start Date</label>
                  <Input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    disabled={isRunning}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">End Date</label>
                  <Input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    disabled={isRunning}
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium">Initial Capital</label>
                <Input
                  type="number"
                  value={initialCapital}
                  onChange={(e) => setInitialCapital(e.target.value)}
                  disabled={isRunning}
                  placeholder="100000"
                />
              </div>

              {error && (
                <div className="bg-red-50 text-red-800 p-3 rounded-lg">
                  {error}
                </div>
              )}

              <div className="flex justify-end space-x-3">
                <Button variant="outline" onClick={onClose} disabled={isRunning}>
                  Cancel
                </Button>
                <Button onClick={runBacktest} disabled={isRunning}>
                  {isRunning ? (
                    <>
                      <Spinner size="sm" className="mr-2" />
                      Running Backtest...
                    </>
                  ) : (
                    <>
                      <BarChart3 className="h-4 w-4 mr-2" />
                      Run Backtest
                    </>
                  )}
                </Button>
              </div>
            </>
          ) : (
            <>
              <div className="grid grid-cols-2 gap-4">
                <Card>
                  <CardContent className="pt-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Total Return</span>
                      <TrendingUp className="h-4 w-4 text-gray-400" />
                    </div>
                    <p className={`text-2xl font-bold ${results.performance?.total_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {formatPercentage(results.performance?.total_return || 0)}
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="pt-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Sharpe Ratio</span>
                      <BarChart3 className="h-4 w-4 text-gray-400" />
                    </div>
                    <p className="text-2xl font-bold">
                      {results.performance?.sharpe_ratio?.toFixed(2) || '0.00'}
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="pt-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Max Drawdown</span>
                      <AlertTriangle className="h-4 w-4 text-gray-400" />
                    </div>
                    <p className="text-2xl font-bold text-red-600">
                      {formatPercentage(results.performance?.max_drawdown || 0)}
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="pt-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Win Rate</span>
                      <DollarSign className="h-4 w-4 text-gray-400" />
                    </div>
                    <p className="text-2xl font-bold">
                      {formatPercentage(results.trade_analysis?.win_rate || 0)}
                    </p>
                  </CardContent>
                </Card>
              </div>

              <div className="border-t pt-4">
                <h3 className="font-semibold mb-2">Performance Summary</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Initial Capital</span>
                    <span>{formatCurrency(results.performance?.initial_capital || 0)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Final Value</span>
                    <span className="font-medium">{formatCurrency(results.performance?.final_value || 0)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Trades</span>
                    <span>{results.trade_analysis?.total || 0}</span>
                  </div>
                </div>
              </div>

              <div className="flex justify-end space-x-3">
                <Button variant="outline" onClick={() => setResults(null)}>
                  Run Again
                </Button>
                <Button onClick={onClose}>
                  Close
                </Button>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}