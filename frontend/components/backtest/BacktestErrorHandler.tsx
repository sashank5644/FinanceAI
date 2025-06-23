import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AlertTriangle } from "lucide-react";

interface BacktestErrorHandlerProps {
  strategyId: string;
  strategyName: string;
  onClose: () => void;
  errorMessage?: string;
}

export function BacktestErrorHandler({ 
  strategyId, 
  strategyName, 
  onClose,
  errorMessage = "An error occurred while running the backtest"
}: BacktestErrorHandlerProps) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <Card className="w-full max-w-md">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <AlertTriangle className="h-6 w-6 text-red-500" />
            <CardTitle>Backtest Error</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="font-medium text-lg">{strategyName}</h3>
            <p className="text-red-600 mt-2">{errorMessage}</p>
            
            <div className="mt-4 bg-gray-50 p-3 rounded-md border border-gray-200">
              <h4 className="text-sm font-medium text-gray-700">Troubleshooting Tips:</h4>
              <ul className="mt-2 text-sm text-gray-600 space-y-1">
                <li>• Check if the strategy has valid instruments configured</li>
                <li>• Verify the date range has sufficient historical data</li>
                <li>• Ensure your API keys for market data are valid</li>
                <li>• Try with a different date range or instruments</li>
              </ul>
            </div>
          </div>
          
          <div className="flex justify-end space-x-3 pt-2">
            <Button onClick={onClose}>
              Close
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}