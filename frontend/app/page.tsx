"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Spinner } from "@/components/ui/spinner";
import { apiClient } from "@/services/api";
import { formatDate, formatNumber, formatCurrency } from "@/lib/utils";
import { 
  TrendingUp, 
  Brain, 
  Network, 
  Activity,
  Clock,
  FileText,
  ArrowRight,
  Database,
  BarChart3,
  DollarSign,
  Users,
  Target,
  Zap,
  AlertCircle,
  CheckCircle,
  XCircle,
  ArrowUpRight,
  ArrowDownRight,
  Sparkles,
  ChevronRight,
  Globe
} from "lucide-react";
import Link from "next/link";
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from "recharts";

// Mock data remains the same
const performanceData = [
  { date: "Mon", value: 4200, benchmark: 4000 },
  { date: "Tue", value: 4800, benchmark: 4100 },
  { date: "Wed", value: 4600, benchmark: 4200 },
  { date: "Thu", value: 5200, benchmark: 4300 },
  { date: "Fri", value: 5800, benchmark: 4400 },
  { date: "Sat", value: 5600, benchmark: 4500 },
  { date: "Sun", value: 6200, benchmark: 4600 },
];

const strategyPerformance = [
  { name: "Momentum", return: 15.2, risk: 12.5 },
  { name: "Value", return: 10.8, risk: 8.2 },
  { name: "Growth", return: 18.5, risk: 16.3 },
  { name: "Market Neutral", return: 7.2, risk: 4.1 },
];

const assetAllocation = [
  { name: "Stocks", value: 60, color: "#3B82F6" },
  { name: "Bonds", value: 25, color: "#10B981" },
  { name: "Cash", value: 10, color: "#F59E0B" },
  { name: "Alternative", value: 5, color: "#8B5CF6" },
];

export default function DashboardPage() {
  const [health, setHealth] = useState<any>(null);
  const [graphStats, setGraphStats] = useState<any>(null);
  const [researchHistory, setResearchHistory] = useState<any>(null);
  const [strategies, setStrategies] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      const [healthRes, graphRes, historyRes, strategiesRes] = await Promise.all([
        apiClient.checkHealth(),
        apiClient.getKnowledgeGraphStats(),
        apiClient.getResearchHistory(5),
        apiClient.getStrategies(5)
      ]);

      if (healthRes.success) setHealth(healthRes.data);
      if (graphRes.success) setGraphStats(graphRes.data);
      if (historyRes.success) setResearchHistory(historyRes.data);
      if (strategiesRes.success) setStrategies(strategiesRes.data);
    } catch (error) {
      console.error("Error loading dashboard data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "healthy":
      case "completed":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "warning":
      case "running":
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      case "error":
      case "failed":
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-8 mt-20">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 p-8 md:p-12">
        <div className="absolute inset-0 bg-black/20" />
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-white/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-white/10 rounded-full blur-3xl" />
        
        <div className="relative">
          <div className="flex items-center space-x-2 mb-4">
            <Sparkles className="h-5 w-5 text-yellow-300 animate-pulse" />
            <Badge className="bg-white/20 text-white border-white/30">
              AI-Powered Intelligence
            </Badge>
          </div>
          
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Welcome back to FinanceAI
          </h1>
          <p className="text-xl text-white/80 max-w-2xl">
            Your intelligent financial research companion is ready to analyze markets, 
            generate strategies, and uncover opportunities.
          </p>
          
          <div className="flex flex-wrap gap-4 mt-8">
            <Link href="/research">
              <Button size="lg" className="bg-white text-gray-900 hover:bg-gray-100">
                <Brain className="h-5 w-5 mr-2" />
                Start Research
              </Button>
            </Link>
            <Link href="/reports">
              <Button size="lg" variant="outline" className="bg-white/10 text-white border-white/30 hover:bg-white/20">
                <FileText className="h-5 w-5 mr-2" />
                View Reports
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Key Metrics Cards - Premium Glass Effect */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="glass-card rounded-xl p-6 appear-animation" style={{ animationDelay: "0.1s" }}>
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600">
              {getStatusIcon(health?.status)}
            </div>
            <Badge 
              variant="secondary" 
              className="bg-blue-100 text-blue-700 border-0"
            >
              System
            </Badge>
          </div>
          <div className="space-y-1">
            <div className="text-2xl font-bold">
              {isLoading ? (
                <div className="h-8 w-32 skeleton rounded" />
              ) : (
                health?.status === "healthy" ? "All Systems Go" : "Issues Detected"
              )}
            </div>
            <p className="text-sm text-gray-600">
              {health?.environment || "Development"} • v{health?.version || "0.1.0"}
            </p>
          </div>
        </div>

        <div className="glass-card rounded-xl p-6 appear-animation" style={{ animationDelay: "0.2s" }}>
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 rounded-lg bg-gradient-to-br from-purple-500 to-purple-600">
              <Network className="h-5 w-5 text-white" />
            </div>
            <Badge 
              variant="secondary" 
              className="bg-purple-100 text-purple-700 border-0"
            >
              Graph
            </Badge>
          </div>
          <div className="space-y-1">
            <div className="text-2xl font-bold">
              {isLoading ? (
                <div className="h-8 w-24 skeleton rounded" />
              ) : (
                formatNumber(graphStats?.total_nodes || 0)
              )}
            </div>
            <p className="text-sm text-gray-600">
              Entities • {formatNumber(graphStats?.total_edges || 0)} connections
            </p>
            <div className="mt-2">
              <Progress value={75} className="h-1.5 bg-purple-100" />
            </div>
          </div>
        </div>

        <div className="glass-card rounded-xl p-6 appear-animation" style={{ animationDelay: "0.3s" }}>
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 rounded-lg bg-gradient-to-br from-green-500 to-green-600">
              <Brain className="h-5 w-5 text-white" />
            </div>
            <Badge 
              variant="secondary" 
              className="bg-green-100 text-green-700 border-0"
            >
              Research
            </Badge>
          </div>
          <div className="space-y-1">
            <div className="text-2xl font-bold">
              {formatNumber(researchHistory?.total || 0)}
            </div>
            <div className="flex items-center text-sm">
              <ArrowUpRight className="h-4 w-4 text-green-500 mr-1" />
              <span className="text-green-600 font-medium">+12%</span>
              <span className="text-gray-600 ml-1">this week</span>
            </div>
          </div>
        </div>

        <div className="glass-card rounded-xl p-6 appear-animation" style={{ animationDelay: "0.4s" }}>
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 rounded-lg bg-gradient-to-br from-orange-500 to-orange-600">
              <Target className="h-5 w-5 text-white" />
            </div>
            <Badge 
              variant="secondary" 
              className="bg-orange-100 text-orange-700 border-0"
            >
              Strategies
            </Badge>
          </div>
          <div className="space-y-1">
            <div className="text-2xl font-bold">
              {formatNumber(strategies?.total || 0)}
            </div>
            <div className="flex items-center text-sm">
              <Zap className="h-4 w-4 text-yellow-500 mr-1" />
              <span className="text-gray-600">
                {strategies?.items?.filter((s: any) => s.status === "active").length || 0} active
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Section - Modern Design */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Performance Chart */}
        <div className="lg:col-span-2 glass-card rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold">Performance Overview</h3>
              <p className="text-sm text-gray-600 mt-1">Portfolio vs S&P 500 Benchmark</p>
            </div>
            <Button variant="ghost" size="sm" className="text-gray-500">
              <Globe className="h-4 w-4 mr-2" />
              View Details
            </Button>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={performanceData}>
              <defs>
                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorBenchmark" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#9CA3AF" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#9CA3AF" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" stroke="#888" fontSize={12} />
              <YAxis stroke="#888" fontSize={12} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: "rgba(255, 255, 255, 0.95)", 
                  border: "1px solid #e5e7eb", 
                  borderRadius: "8px",
                  backdropFilter: "blur(10px)"
                }}
                labelStyle={{ color: "#111827", fontWeight: 600 }}
              />
              <Area 
                type="monotone" 
                dataKey="benchmark" 
                stroke="#9CA3AF" 
                fillOpacity={1}
                fill="url(#colorBenchmark)"
                strokeWidth={2}
              />
              <Area 
                type="monotone" 
                dataKey="value" 
                stroke="#3B82F6" 
                fillOpacity={1}
                fill="url(#colorValue)"
                strokeWidth={3}
              />
              <Legend />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Asset Allocation - Modern Donut Chart */}
        <div className="glass-card rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-2">Asset Allocation</h3>
          <p className="text-sm text-gray-600 mb-6">Current portfolio distribution</p>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={assetAllocation}
                cx="50%"
                cy="50%"
                labelLine={false}
                innerRadius={60}
                outerRadius={90}
                fill="#8884d8"
                dataKey="value"
              >
                {assetAllocation.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: "rgba(255, 255, 255, 0.95)", 
                  border: "none", 
                  borderRadius: "8px",
                  backdropFilter: "blur(10px)"
                }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="grid grid-cols-2 gap-2 mt-4">
            {assetAllocation.map((item) => (
              <div key={item.name} className="flex items-center space-x-2">
                <div 
                  className="w-3 h-3 rounded-full" 
                  style={{ backgroundColor: item.color }}
                />
                <span className="text-sm text-gray-600">{item.name}</span>
                <span className="text-sm font-medium ml-auto">{item.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content Tabs - Modern Style */}
      <Tabs defaultValue="activity" className="space-y-6">
        <TabsList className="grid grid-cols-3 w-full max-w-md mx-auto glass-card p-1">
          <TabsTrigger value="activity">Recent Activity</TabsTrigger>
          <TabsTrigger value="strategies">Strategies</TabsTrigger>
          <TabsTrigger value="system">System</TabsTrigger>
        </TabsList>

        <TabsContent value="activity" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Recent Research - Modern Cards */}
            <div className="glass-card rounded-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold">Recent Research</h3>
                <Link href="/research">
                  <Button variant="ghost" size="sm" className="hover:bg-gray-100">
                    View All
                    <ArrowRight className="h-4 w-4 ml-1" />
                  </Button>
                </Link>
              </div>
              {isLoading ? (
                <div className="space-y-3">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="h-16 skeleton rounded-lg" />
                  ))}
                </div>
              ) : researchHistory?.items?.length > 0 ? (
                <div className="space-y-3 stagger-animation">
                  {researchHistory.items.slice(0, 5).map((research: any) => (
                    <div
                      key={research.id}
                      className="group flex items-center justify-between p-4 rounded-lg border border-gray-100 hover:border-gray-200 hover:shadow-md transition-all duration-200 cursor-pointer"
                    >
                      <div className="flex items-center space-x-3">
                        <div className={`p-2.5 rounded-lg ${
                          research.status === "completed" ? "bg-green-100" : 
                          research.status === "running" ? "bg-blue-100" : "bg-gray-100"
                        } group-hover:scale-110 transition-transform duration-200`}>
                          <FileText className={`h-4 w-4 ${
                            research.status === "completed" ? "text-green-600" : 
                            research.status === "running" ? "text-blue-600" : "text-gray-600"
                          }`} />
                        </div>
                        <div className="min-w-0">
                          <p className="font-medium text-sm truncate">{research.query}</p>
                          <div className="flex items-center space-x-2 text-xs text-gray-500 mt-1">
                            <Clock className="h-3 w-3" />
                            <span>{formatDate(research.created_at)}</span>
                          </div>
                        </div>
                      </div>
                      <ChevronRight className="h-4 w-4 text-gray-400 group-hover:text-gray-600 group-hover:translate-x-1 transition-all duration-200" />
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
                    <Brain className="h-8 w-8 text-gray-400" />
                  </div>
                  <p className="text-gray-500 mb-4">No research tasks yet</p>
                  <Link href="/research">
                    <Button className="btn-premium text-white">
                      Start Your First Research
                    </Button>
                  </Link>
                </div>
              )}
            </div>

            {/* Top Strategies - Modern Cards */}
            <div className="glass-card rounded-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold">Top Strategies</h3>
                <Link href="/strategies">
                  <Button variant="ghost" size="sm" className="hover:bg-gray-100">
                    View All
                    <ArrowRight className="h-4 w-4 ml-1" />
                  </Button>
                </Link>
              </div>
              {strategies?.items?.length > 0 ? (
                <div className="space-y-3 stagger-animation">
                  {strategies.items.slice(0, 5).map((strategy: any) => (
                    <div
                      key={strategy.id}
                      className="group flex items-center justify-between p-4 rounded-lg border border-gray-100 hover:border-gray-200 hover:shadow-md transition-all duration-200 cursor-pointer"
                    >
                      <div className="flex items-center space-x-3">
                        <div className="p-2.5 rounded-lg bg-gradient-to-br from-purple-100 to-purple-200 group-hover:scale-110 transition-transform duration-200">
                          <TrendingUp className="h-4 w-4 text-purple-600" />
                        </div>
                        <div>
                          <p className="font-medium text-sm">{strategy.name}</p>
                          <div className="flex items-center space-x-2 mt-1">
                            <Badge variant="outline" className="text-xs">
                              {strategy.type}
                            </Badge>
                            <span className="text-xs text-gray-500">
                              {strategy.risk_level}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-semibold text-green-600">
                          +12.5%
                        </p>
                        <p className="text-xs text-gray-500">YTD</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
                    <Target className="h-8 w-8 text-gray-400" />
                  </div>
                  <p className="text-gray-500 mb-4">No strategies created yet</p>
                  <Link href="/strategies">
                    <Button className="btn-premium text-white">
                      Create Your First Strategy
                    </Button>
                  </Link>
                </div>
              )}
            </div>
          </div>

          {/* Quick Access Cards - Premium Design */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Link href="/reports" className="group">
              <div className="glass-card rounded-xl p-6 hover-lift cursor-pointer h-full">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 group-hover:scale-110 transition-transform duration-200">
                    <FileText className="h-6 w-6 text-white" />
                  </div>
                  <ArrowUpRight className="h-5 w-5 text-gray-400 group-hover:text-gray-600 group-hover:translate-x-1 group-hover:-translate-y-1 transition-all duration-200" />
                </div>
                <h3 className="text-lg font-semibold mb-2">Generate Reports</h3>
                <p className="text-sm text-gray-600">
                  Create professional investment reports with AI-powered insights
                </p>
              </div>
            </Link>

            <Link href="/knowledge-graph" className="group">
              <div className="glass-card rounded-xl p-6 hover-lift cursor-pointer h-full">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 rounded-xl bg-gradient-to-br from-green-500 to-green-600 group-hover:scale-110 transition-transform duration-200">
                    <Network className="h-6 w-6 text-white" />
                  </div>
                  <ArrowUpRight className="h-5 w-5 text-gray-400 group-hover:text-gray-600 group-hover:translate-x-1 group-hover:-translate-y-1 transition-all duration-200" />
                </div>
                <h3 className="text-lg font-semibold mb-2">Knowledge Graph</h3>
                <p className="text-sm text-gray-600">
                  Explore relationships between companies and market sectors
                </p>
              </div>
            </Link>

            <Link href="/strategies" className="group">
              <div className="glass-card rounded-xl p-6 hover-lift cursor-pointer h-full">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 group-hover:scale-110 transition-transform duration-200">
                    <BarChart3 className="h-6 w-6 text-white" />
                  </div>
                  <ArrowUpRight className="h-5 w-5 text-gray-400 group-hover:text-gray-600 group-hover:translate-x-1 group-hover:-translate-y-1 transition-all duration-200" />
                </div>
                <h3 className="text-lg font-semibold mb-2">Backtesting</h3>
                <p className="text-sm text-gray-600">
                  Test your strategies against historical market data
                </p>
              </div>
            </Link>
          </div>
        </TabsContent>

        <TabsContent value="strategies">
          <div className="glass-card rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-6">Strategy Risk/Return Analysis</h3>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={strategyPerformance}>
                <defs>
                  <linearGradient id="returnGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#10B981" stopOpacity={0.8}/>
                    <stop offset="100%" stopColor="#10B981" stopOpacity={0.3}/>
                  </linearGradient>
                  <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#F59E0B" stopOpacity={0.8}/>
                    <stop offset="100%" stopColor="#F59E0B" stopOpacity={0.3}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="name" stroke="#888" fontSize={12} />
                <YAxis stroke="#888" fontSize={12} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: "rgba(255, 255, 255, 0.95)", 
                    border: "none", 
                    borderRadius: "8px",
                    backdropFilter: "blur(10px)"
                  }}
                />
                <Legend />
                <Bar dataKey="return" fill="url(#returnGradient)" name="Return %" radius={[8, 8, 0, 0]} />
                <Bar dataKey="risk" fill="url(#riskGradient)" name="Risk %" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </TabsContent>

        <TabsContent value="system" className="space-y-6">
          <div className="glass-card rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-6">System Components</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {health?.components && 
                Object.entries(health.components).map(([component, status]) => (
                  <div
                    key={component}
                    className="flex items-center justify-between p-4 rounded-lg border border-gray-100 hover:border-gray-200 hover:shadow-md transition-all duration-200"
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`p-3 rounded-lg ${
                        status === "healthy" ? "bg-green-100" : "bg-red-100"
                      }`}>
                        <Database className={`h-5 w-5 ${
                          status === "healthy" ? "text-green-600" : "text-red-600"
                        }`} />
                      </div>
                      <div>
                        <span className="font-medium capitalize">{component}</span>
                        <p className="text-xs text-gray-500 mt-1">
                          {component === "postgres" && "Primary database"}
                          {component === "neo4j" && "Knowledge graph database"}
                          {component === "redis" && "Cache & queue"}
                          {component === "pinecone" && "Vector search"}
                        </p>
                      </div>
                    </div>
                    <Badge
                      variant={status === "healthy" ? "default" : "destructive"}
                      className={status === "healthy" ? "bg-green-100 text-green-700 border-0" : ""}
                    >
                      {status as string}
                    </Badge>
                  </div>
                ))}
            </div>
          </div>

          {/* API Performance - Modern Stats */}
          <div className="glass-card rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-6">API Performance</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center p-6 rounded-lg bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
                <p className="text-3xl font-bold text-green-600">98.5%</p>
                <p className="text-sm text-gray-600 mt-2">Uptime</p>
              </div>
              <div className="text-center p-6 rounded-lg bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
                <p className="text-3xl font-bold text-blue-600">45ms</p>
                <p className="text-sm text-gray-600 mt-2">Avg Response Time</p>
              </div>
              <div className="text-center p-6 rounded-lg bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
                <p className="text-3xl font-bold text-purple-600">1.2K</p>
                <p className="text-sm text-gray-600 mt-2">Requests/Hour</p>
              </div>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}