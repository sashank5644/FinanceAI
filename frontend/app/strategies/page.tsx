"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Spinner } from "@/components/ui/spinner";
import { apiClient } from "@/services/api";
import { EnhancedBacktestModal } from "@/components/backtest";
import { StrategySettingsModal } from "@/components/strategy/StrategySettingsModal";
import { 
  TrendingUp, 
  Target,
  Shield,
  BarChart3,
  AlertCircle,
  Sparkles,
  Plus,
  CheckCircle,
  Play,
  FileText,
  Settings,
  Zap,
  Brain,
  BookOpen,
  ArrowUpRight,
  ArrowDownRight,
  Activity,
  ChevronRight
} from "lucide-react";

interface StrategyType {
  id: string;
  name: string;
  description: string;
  risk_level: string;
  typical_return: string;
  suitable_for: string;
}

interface Strategy {
  id: string;
  name: string;
  type: string;
  risk_level: string;
  created_at: string;
  last_backtest?: {
    total_return: number;
    sharpe_ratio: number;
    win_rate: number;
  };
}

export default function StrategiesPage() {
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [strategyName, setStrategyName] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [strategyTypes, setStrategyTypes] = useState<StrategyType[]>([]);
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [successMessage, setSuccessMessage] = useState("");
  const [selectedStrategy, setSelectedStrategy] = useState<Strategy | null>(null);
  const [showBacktestModal, setShowBacktestModal] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);

  useEffect(() => {
    loadStrategyTypes();
    loadStrategies();
  }, []);

  const loadStrategyTypes = async () => {
    const response = await apiClient.getStrategyTypes();
    if (response.success && response.data) {
      setStrategyTypes(response.data.types || []);
    }
  };

  const loadStrategies = async () => {
    const response = await apiClient.getStrategies();
    if (response.success && response.data) {
      setStrategies(response.data.items || []);
    }
  };

  const handleGenerateStrategy = async () => {
    if (!selectedType || !strategyName.trim()) return;

    setIsGenerating(true);
    setSuccessMessage("");
    
    try {
      const response = await apiClient.generateStrategy({
        name: strategyName,
        strategy_type: selectedType,
        risk_level: "moderate"
      });
      
      if (response.success) {
        setSuccessMessage(`Strategy "${strategyName}" created successfully!`);
        setSelectedType(null);
        setStrategyName("");
        loadStrategies();
        setTimeout(() => setSuccessMessage(""), 5000);
      }
    } catch (error) {
      console.error("Failed to generate strategy:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleBacktest = (strategy: Strategy) => {
    setSelectedStrategy(strategy);
    setShowBacktestModal(true);
  };

  const handleStrategyDetails = (strategy: Strategy) => {
    alert(`Strategy Details:\n\nName: ${strategy.name}\nType: ${strategy.type}\nRisk Level: ${strategy.risk_level}\nCreated: ${new Date(strategy.created_at).toLocaleDateString()}\n\nInstruments: Coming soon...`);
  };

  const handleStrategySettings = (strategy: Strategy) => {
    setSelectedStrategy(strategy);
    setShowSettingsModal(true);
  };

  const handleDeleteStrategy = async (strategyId: string) => {
    try {
      const response = await apiClient.deleteStrategy(strategyId);
      if (response.success) {
        loadStrategies();
        return Promise.resolve();
      } else {
        return Promise.reject(new Error(response.error || "Failed to delete strategy"));
      }
    } catch (error) {
      console.error("Error deleting strategy:", error);
      return Promise.reject(error);
    }
  };

  const getIconForType = (typeId: string) => {
    const icons: { [key: string]: any } = {
      momentum: TrendingUp,
      value: Target,
      growth: Sparkles,
      market_neutral: Shield,
      mean_reversion: BarChart3
    };
    return icons[typeId] || TrendingUp;
  };

  const getTypeGradient = (typeId: string) => {
    const gradients: { [key: string]: string } = {
      momentum: "from-blue-500 to-blue-600",
      value: "from-green-500 to-green-600",
      growth: "from-purple-500 to-purple-600",
      market_neutral: "from-gray-500 to-gray-600",
      mean_reversion: "from-orange-500 to-orange-600"
    };
    return gradients[typeId] || "from-gray-500 to-gray-600";
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case "conservative": return "bg-green-100 text-green-700 border-0";
      case "moderate": return "bg-yellow-100 text-yellow-700 border-0";
      case "aggressive": return "bg-red-100 text-red-700 border-0";
      default: return "";
    }
  };

  return (
    <div className="space-y-8 mt-20">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-cyan-600 via-blue-600 to-purple-600 p-8 md:p-12">
        <div className="absolute inset-0 bg-black/20" />
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-white/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-white/10 rounded-full blur-3xl" />
        
        <div className="relative">
          <div className="flex items-center space-x-2 mb-4">
            <Brain className="h-5 w-5 text-yellow-300 animate-pulse" />
            <Badge className="bg-white/20 text-white border-white/30">
              AI Strategy Generation
            </Badge>
          </div>
          
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Investment Strategy Builder
          </h1>
          <p className="text-xl text-white/80 max-w-2xl">
            Create, backtest, and optimize AI-powered investment strategies 
            tailored to your risk profile and market outlook.
          </p>
          
          <div className="flex flex-wrap gap-4 mt-8">
            <Button 
              size="lg"
              className="bg-white text-gray-900 hover:bg-gray-100"
              onClick={() => document.getElementById('create-strategy')?.scrollIntoView({ behavior: 'smooth' })}
            >
              <Plus className="h-5 w-5 mr-2" />
              Create Strategy
            </Button>
            <Button 
              size="lg" 
              variant="outline" 
              className="bg-white/10 text-white border-white/30 hover:bg-white/20"
            >
              <BarChart3 className="h-5 w-5 mr-2" />
              View Performance
            </Button>
          </div>
        </div>
      </div>

      {/* Success Message */}
      {successMessage && (
        <div className="glass-card rounded-xl p-4 bg-green-50 border border-green-200 appear-animation">
          <div className="flex items-center space-x-3">
            <CheckCircle className="h-5 w-5 text-green-600" />
            <p className="text-green-800 font-medium">{successMessage}</p>
          </div>
        </div>
      )}

      <Tabs defaultValue="create" className="space-y-6">
        <TabsList className="grid grid-cols-3 w-full max-w-md mx-auto glass-card p-1">
          <TabsTrigger value="create">Create</TabsTrigger>
          <TabsTrigger value="manage">Manage</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
        </TabsList>

        <TabsContent value="create" className="space-y-6" id="create-strategy">
          <div className="glass-card rounded-xl p-8 appear-animation">
            <div className="max-w-4xl mx-auto">
              <h3 className="text-2xl font-bold mb-2">Create New Strategy</h3>
              <p className="text-gray-600 mb-8">
                Choose a strategy type and let our AI generate optimized trading rules
              </p>

              {/* Strategy Name */}
              <div className="mb-8">
                <label className="text-sm font-medium text-gray-700 mb-2 block">
                  Strategy Name
                </label>
                <Input
                  placeholder="e.g., Tech Growth Portfolio"
                  value={strategyName}
                  onChange={(e) => setStrategyName(e.target.value)}
                  className="bg-white/50 backdrop-blur-sm border-gray-200/50 focus:bg-white text-lg"
                />
              </div>

              {/* Strategy Type Selection */}
              <div>
                <label className="text-sm font-medium text-gray-700 mb-4 block">
                  Choose Strategy Type
                </label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {strategyTypes.map((type, index) => {
                    const Icon = getIconForType(type.id);
                    const gradient = getTypeGradient(type.id);
                    return (
                      <button
                        key={type.id}
                        onClick={() => setSelectedType(type.id)}
                        className={`group relative p-6 rounded-xl text-left transition-all duration-300 hover-lift appear-animation ${
                          selectedType === type.id
                            ? "glass-card border-2 border-blue-500"
                            : "glass-card hover:shadow-lg"
                        }`}
                        style={{ animationDelay: `${0.1 + index * 0.1}s` }}
                      >
                        <div className="flex items-start space-x-4">
                          <div className={`p-3 rounded-xl bg-gradient-to-br ${gradient} group-hover:scale-110 transition-transform duration-200`}>
                            <Icon className="h-6 w-6 text-white" />
                          </div>
                          <div className="flex-1">
                            <h3 className="font-semibold text-lg mb-2">{type.name}</h3>
                            <p className="text-sm text-gray-600 mb-3">
                              {type.description}
                            </p>
                            <div className="flex items-center space-x-3">
                              <Badge className={getRiskColor(type.risk_level)}>
                                {type.risk_level} risk
                              </Badge>
                              <span className="text-xs text-gray-500">
                                {type.typical_return}
                              </span>
                            </div>
                          </div>
                        </div>
                        {selectedType === type.id && (
                          <div className="absolute top-4 right-4">
                            <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                            </div>
                          </div>
                        )}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Generate Button */}
              <div className="flex justify-center mt-8">
                <Button
                  onClick={handleGenerateStrategy}
                  disabled={!selectedType || !strategyName.trim() || isGenerating}
                  className="btn-premium text-white px-8 py-3 text-lg"
                  size="lg"
                >
                  {isGenerating ? (
                    <>
                      <Spinner size="sm" className="mr-2" />
                      Generating Strategy...
                    </>
                  ) : (
                    <>
                      <Zap className="h-5 w-5 mr-2" />
                      Generate Strategy
                    </>
                  )}
                </Button>
              </div>
            </div>
          </div>

          {/* Strategy Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="glass-card rounded-xl p-6 text-center appear-animation" style={{ animationDelay: "0.6s" }}>
              <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 mb-4">
                <Brain className="h-7 w-7 text-white" />
              </div>
              <h4 className="font-semibold text-lg mb-2">AI-Powered Rules</h4>
              <p className="text-sm text-gray-600">
                Advanced algorithms generate entry and exit rules based on market conditions
              </p>
            </div>

            <div className="glass-card rounded-xl p-6 text-center appear-animation" style={{ animationDelay: "0.7s" }}>
              <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-gradient-to-br from-green-500 to-green-600 mb-4">
                <Shield className="h-7 w-7 text-white" />
              </div>
              <h4 className="font-semibold text-lg mb-2">Risk Management</h4>
              <p className="text-sm text-gray-600">
                Built-in position sizing, stop losses, and drawdown protection
              </p>
            </div>

            <div className="glass-card rounded-xl p-6 text-center appear-animation" style={{ animationDelay: "0.8s" }}>
              <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-gradient-to-br from-purple-500 to-purple-600 mb-4">
                <Target className="h-7 w-7 text-white" />
              </div>
              <h4 className="font-semibold text-lg mb-2">Performance Tracking</h4>
              <p className="text-sm text-gray-600">
                Real-time monitoring with detailed analytics and reports
              </p>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="manage">
          <div className="glass-card rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold">My Strategies</h3>
              <Badge variant="secondary">{strategies.length} strategies</Badge>
            </div>
            {strategies.length > 0 ? (
              <div className="space-y-4">
                {strategies.map((strategy, index) => {
                  const Icon = getIconForType(strategy.type);
                  const gradient = getTypeGradient(strategy.type);
                  return (
                    <div
                      key={strategy.id}
                      className="group flex items-center justify-between p-6 rounded-xl border border-gray-100 hover:border-gray-200 hover:shadow-lg transition-all duration-200 appear-animation"
                      style={{ animationDelay: `${index * 0.1}s` }}
                    >
                      <div className="flex items-center space-x-4 flex-1">
                        <div className={`p-3 rounded-xl bg-gradient-to-br ${gradient} group-hover:scale-110 transition-transform duration-200`}>
                          <Icon className="h-6 w-6 text-white" />
                        </div>
                        <div className="flex-1">
                          <h3 className="font-semibold text-lg mb-1">{strategy.name}</h3>
                          <div className="flex items-center space-x-4 text-sm">
                            <Badge variant="outline">{strategy.type}</Badge>
                            <Badge className={getRiskColor(strategy.risk_level)}>
                              {strategy.risk_level}
                            </Badge>
                            <span className="text-gray-500">
                              Created {new Date(strategy.created_at).toLocaleDateString()}
                            </span>
                          </div>
                          {strategy.last_backtest && (
                            <div className="flex items-center space-x-6 mt-3 text-sm">
                              <div className="flex items-center space-x-1">
                                <span className="text-gray-600">Return:</span>
                                <span className={`font-semibold flex items-center ${
                                  strategy.last_backtest.total_return >= 0 ? 'text-green-600' : 'text-red-600'
                                }`}>
                                  {strategy.last_backtest.total_return >= 0 ? (
                                    <ArrowUpRight className="h-3.5 w-3.5 mr-0.5" />
                                  ) : (
                                    <ArrowDownRight className="h-3.5 w-3.5 mr-0.5" />
                                  )}
                                  {Math.abs(strategy.last_backtest.total_return).toFixed(2)}%
                                </span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <span className="text-gray-600">Sharpe:</span>
                                <span className="font-semibold">{strategy.last_backtest.sharpe_ratio.toFixed(2)}</span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <span className="text-gray-600">Win Rate:</span>
                                <span className="font-semibold">{strategy.last_backtest.win_rate.toFixed(1)}%</span>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => handleBacktest(strategy)}
                          className="hover:bg-gray-100"
                        >
                          <Play className="h-4 w-4 mr-1" />
                          Backtest
                        </Button>
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => handleStrategyDetails(strategy)}
                          className="hover:bg-gray-100"
                        >
                          <FileText className="h-4 w-4 mr-1" />
                          Details
                        </Button>
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => handleStrategySettings(strategy)}
                          className="hover:bg-gray-100"
                        >
                          <Settings className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-16">
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-gray-100 to-gray-200 mb-6">
                  <TrendingUp className="h-10 w-10 text-gray-400" />
                </div>
                <h3 className="text-xl font-semibold mb-2">No strategies yet</h3>
                <p className="text-gray-500 mb-6">
                  Create your first AI-powered investment strategy
                </p>
              </div>
            )}
          </div>
        </TabsContent>

        <TabsContent value="performance">
          <div className="glass-card rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-6">Strategy Performance Overview</h3>
            {strategies.filter(s => s.last_backtest).length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {strategies.filter(s => s.last_backtest).map((strategy, index) => {
                  const Icon = getIconForType(strategy.type);
                  const gradient = getTypeGradient(strategy.type);
                  const isPositive = strategy.last_backtest!.total_return >= 0;
                  
                  return (
                    <div 
                      key={strategy.id} 
                      className="glass-card rounded-xl p-6 hover-lift appear-animation"
                      style={{ animationDelay: `${index * 0.1}s` }}
                    >
                      <div className="flex items-center justify-between mb-4">
                        <div className={`p-2.5 rounded-lg bg-gradient-to-br ${gradient}`}>
                          <Icon className="h-5 w-5 text-white" />
                        </div>
                        <Badge variant="outline" className="text-xs">
                          {strategy.type}
                        </Badge>
                      </div>
                      
                      <h4 className="font-semibold text-lg mb-4">{strategy.name}</h4>
                      
                      <div className="space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Total Return</span>
                          <span className={`text-lg font-bold flex items-center ${
                            isPositive ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {isPositive ? (
                              <ArrowUpRight className="h-4 w-4 mr-1" />
                            ) : (
                              <ArrowDownRight className="h-4 w-4 mr-1" />
                            )}
                            {Math.abs(strategy.last_backtest!.total_return).toFixed(2)}%
                          </span>
                        </div>
                        
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Sharpe Ratio</span>
                          <span className="text-lg font-semibold">
                            {strategy.last_backtest!.sharpe_ratio.toFixed(2)}
                          </span>
                        </div>
                        
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Win Rate</span>
                          <span className="text-lg font-semibold">
                            {strategy.last_backtest!.win_rate.toFixed(1)}%
                          </span>
                        </div>
                        
                        <div className="h-2 bg-gray-100 rounded-full overflow-hidden mt-4">
                          <div 
                            className={`h-full ${isPositive ? 'bg-green-500' : 'bg-red-500'}`}
                            style={{ width: `${Math.min(strategy.last_backtest!.win_rate, 100)}%` }}
                          />
                        </div>
                      </div>
                      
                      <div className="mt-6 pt-4 border-t">
                        <Button 
                          variant="outline" 
                          size="sm" 
                          className="w-full hover:bg-gray-50"
                          onClick={() => handleBacktest(strategy)}
                        >
                          <Activity className="h-4 w-4 mr-2" />
                          Run New Backtest
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-16">
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-gray-100 to-gray-200 mb-6">
                  <BarChart3 className="h-10 w-10 text-gray-400" />
                </div>
                <h3 className="text-xl font-semibold mb-2">No performance data yet</h3>
                <p className="text-gray-500 mb-6">
                  Run backtests on your strategies to see performance metrics
                </p>
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>

      {/* Info Section */}
      <div className="glass-card rounded-xl p-8 bg-gradient-to-br from-blue-50 to-purple-50 border-blue-200">
        <div className="flex items-start space-x-4">
          <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex-shrink-0">
            <AlertCircle className="h-6 w-6 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-lg mb-2">How Strategy Generation Works</h3>
            <p className="text-gray-700 leading-relaxed">
              Our AI analyzes market conditions, historical patterns, and risk parameters 
              to create customized trading strategies. Each strategy includes specific 
              rules for entering and exiting positions, position sizing, and risk management. 
              The system continuously learns from market data to improve strategy performance.
            </p>
            <div className="flex items-center mt-4 space-x-4">
              <Button variant="outline" size="sm" className="hover:bg-white">
                <BookOpen className="h-4 w-4 mr-2" />
                Learn More
              </Button>
              <Button variant="ghost" size="sm">
                <ChevronRight className="h-4 w-4 mr-1" />
                View Documentation
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Backtest Modal */}
      {showBacktestModal && selectedStrategy && (
        <EnhancedBacktestModal
          strategyId={selectedStrategy.id}
          strategyName={selectedStrategy.name}
          onClose={() => {
            setShowBacktestModal(false);
            setSelectedStrategy(null);
            loadStrategies();
          }}
        />
      )}

      {/* Settings Modal */}
      {showSettingsModal && selectedStrategy && (
        <StrategySettingsModal
          strategy={selectedStrategy}
          onClose={() => {
            setShowSettingsModal(false);
            setSelectedStrategy(null);
            loadStrategies();
          }}
          onDelete={handleDeleteStrategy}
        />
      )}
    </div>
  );
}