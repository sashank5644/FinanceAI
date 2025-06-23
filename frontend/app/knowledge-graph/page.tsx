"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { apiClient } from "@/services/api";
import { formatNumber } from "@/lib/utils";
import { 
  Network, 
  Database, 
  GitBranch, 
  Layers,
  RefreshCw,
  Download,
  Filter,
  Sparkles,
  ArrowUpRight,
  Globe,
  Activity
} from "lucide-react";

// Dynamically import the 3D graph component to avoid SSR issues
const ForceGraph3D = dynamic(
  () => import("@/components/knowledge-graph/ForceGraph3D"),
  { 
    ssr: false,
    loading: () => (
      <div className="glass-card rounded-xl h-[600px] flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    )
  }
);

interface GraphStats {
  total_nodes: number;
  total_edges: number;
  node_types: { [key: string]: number };
  edge_types: { [key: string]: number };
}

interface GraphData {
  nodes: any[];
  links: any[];
}

export default function KnowledgeGraphPage() {
  const [stats, setStats] = useState<GraphStats | null>(null);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("visualization");
  const [selectedNode, setSelectedNode] = useState<any>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [statsResponse, graphResponse] = await Promise.all([
        apiClient.getKnowledgeGraphStats(),
        apiClient.getKnowledgeGraphVisualization()
      ]);

      if (statsResponse.success) {
        setStats(statsResponse.data);
      }

      if (graphResponse.success) {
        setGraphData(graphResponse.data);
      }
    } catch (error) {
      console.error("Failed to load graph data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNodeClick = (node: any) => {
    setSelectedNode(node);
  };

  const handleRefresh = () => {
    loadData();
  };

  const getNodeTypeIcon = (type: string) => {
    const icons: { [key: string]: any } = {
      Company: Network,
      Sector: Layers,
      Indicator: Database,
      Event: GitBranch
    };
    return icons[type] || Network;
  };

  const getNodeTypeGradient = (type: string) => {
    const gradients: { [key: string]: string } = {
      Company: "from-blue-500 to-blue-600",
      Sector: "from-green-500 to-green-600",
      Indicator: "from-purple-500 to-purple-600",
      Event: "from-orange-500 to-orange-600"
    };
    return gradients[type] || "from-gray-500 to-gray-600";
  };

  return (
    <div className="space-y-8 mt-20">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-purple-600 via-blue-600 to-cyan-600 p-8 md:p-12">
        <div className="absolute inset-0 bg-black/20" />
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-white/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-white/10 rounded-full blur-3xl" />
        
        <div className="relative">
          <div className="flex items-center space-x-2 mb-4">
            <Network className="h-5 w-5 text-yellow-300 animate-pulse" />
            <Badge className="bg-white/20 text-white border-white/30">
              Real-time Connections
            </Badge>
          </div>
          
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Knowledge Graph Explorer
          </h1>
          <p className="text-xl text-white/80 max-w-2xl">
            Visualize and explore complex relationships between companies, sectors, 
            and market indicators in an interactive 3D environment.
          </p>
          
          <div className="flex flex-wrap gap-4 mt-8">
            <Button 
              onClick={handleRefresh} 
              size="lg"
              className="bg-white text-gray-900 hover:bg-gray-100"
            >
              <RefreshCw className="h-5 w-5 mr-2" />
              Refresh Data
            </Button>
            <Button 
              size="lg" 
              variant="outline" 
              className="bg-white/10 text-white border-white/30 hover:bg-white/20"
            >
              <Download className="h-5 w-5 mr-2" />
              Export Graph
            </Button>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="glass-card rounded-xl p-6 appear-animation" style={{ animationDelay: "0.1s" }}>
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600">
              <Database className="h-6 w-6 text-white" />
            </div>
            <Badge variant="secondary" className="bg-blue-100 text-blue-700 border-0">
              Entities
            </Badge>
          </div>
          <div className="space-y-1">
            <div className="text-3xl font-bold">
              {isLoading ? (
                <div className="h-9 w-24 skeleton rounded" />
              ) : (
                formatNumber(stats?.total_nodes || 0)
              )}
            </div>
            <p className="text-sm text-gray-600">Total nodes in graph</p>
          </div>
        </div>

        <div className="glass-card rounded-xl p-6 appear-animation" style={{ animationDelay: "0.2s" }}>
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-lg bg-gradient-to-br from-green-500 to-green-600">
              <GitBranch className="h-6 w-6 text-white" />
            </div>
            <Badge variant="secondary" className="bg-green-100 text-green-700 border-0">
              Connections
            </Badge>
          </div>
          <div className="space-y-1">
            <div className="text-3xl font-bold">
              {isLoading ? (
                <div className="h-9 w-24 skeleton rounded" />
              ) : (
                formatNumber(stats?.total_edges || 0)
              )}
            </div>
            <p className="text-sm text-gray-600">Relationships mapped</p>
          </div>
        </div>

        <div className="glass-card rounded-xl p-6 appear-animation" style={{ animationDelay: "0.3s" }}>
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-lg bg-gradient-to-br from-purple-500 to-purple-600">
              <Layers className="h-6 w-6 text-white" />
            </div>
            <Badge variant="secondary" className="bg-purple-100 text-purple-700 border-0">
              Categories
            </Badge>
          </div>
          <div className="space-y-1">
            <div className="text-3xl font-bold">
              {isLoading ? (
                <div className="h-9 w-16 skeleton rounded" />
              ) : (
                Object.keys(stats?.node_types || {}).length
              )}
            </div>
            <p className="text-sm text-gray-600">Node types</p>
          </div>
        </div>

        <div className="glass-card rounded-xl p-6 appear-animation" style={{ animationDelay: "0.4s" }}>
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-lg bg-gradient-to-br from-orange-500 to-orange-600">
              <Activity className="h-6 w-6 text-white" />
            </div>
            <Badge variant="secondary" className="bg-orange-100 text-orange-700 border-0">
              Relations
            </Badge>
          </div>
          <div className="space-y-1">
            <div className="text-3xl font-bold">
              {isLoading ? (
                <div className="h-9 w-16 skeleton rounded" />
              ) : (
                Object.keys(stats?.edge_types || {}).length
              )}
            </div>
            <p className="text-sm text-gray-600">Relationship types</p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid grid-cols-3 w-full max-w-md mx-auto glass-card p-1">
          <TabsTrigger value="visualization">3D Visualization</TabsTrigger>
          <TabsTrigger value="statistics">Statistics</TabsTrigger>
          <TabsTrigger value="details">Node Details</TabsTrigger>
        </TabsList>

        <TabsContent value="visualization" className="mt-6">
          <div className="glass-card rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-semibold">Interactive Graph</h3>
                <p className="text-sm text-gray-600 mt-1">
                  Click and drag to rotate • Scroll to zoom • Click nodes for details
                </p>
              </div>
              <div className="flex items-center space-x-2">
                <Button variant="ghost" size="sm">
                  <Filter className="h-4 w-4 mr-2" />
                  Filter
                </Button>
                <Button variant="ghost" size="sm">
                  <Globe className="h-4 w-4 mr-2" />
                  Reset View
                </Button>
              </div>
            </div>
            
            {graphData ? (
              <ForceGraph3D 
                data={graphData} 
                onNodeClick={handleNodeClick}
              />
            ) : (
              <div className="h-[600px] flex items-center justify-center">
                <div className="text-center">
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
                    <Network className="h-8 w-8 text-gray-400" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">Loading Graph Data...</h3>
                  <p className="text-sm text-gray-500">
                    Please wait while we load the knowledge graph
                  </p>
                </div>
              </div>
            )}
          </div>
        </TabsContent>

        <TabsContent value="statistics" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Node Types Breakdown */}
            <div className="glass-card rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-6">Node Distribution</h3>
              <div className="space-y-4">
                {stats && Object.entries(stats.node_types).map(([type, count]) => {
                  const Icon = getNodeTypeIcon(type);
                  const gradient = getNodeTypeGradient(type);
                  return (
                    <div key={type} className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-all duration-200">
                      <div className="flex items-center space-x-3">
                        <div className={`p-2.5 rounded-lg bg-gradient-to-br ${gradient}`}>
                          <Icon className="h-5 w-5 text-white" />
                        </div>
                        <span className="font-medium">{type}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-2xl font-bold">{count}</span>
                        <ArrowUpRight className="h-4 w-4 text-gray-400" />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Relationship Types Breakdown */}
            <div className="glass-card rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-6">Relationship Types</h3>
              <div className="space-y-4">
                {stats && Object.entries(stats.edge_types).map(([type, count]) => (
                  <div key={type} className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-all duration-200">
                    <div className="flex items-center space-x-3">
                      <div className="w-1 h-8 bg-gradient-to-b from-blue-500 to-purple-500 rounded-full" />
                      <span className="font-medium">{type.replace(/_/g, ' ')}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-2xl font-bold">{count}</span>
                      <Badge variant="secondary" className="text-xs">
                        {((count / (stats.total_edges || 1)) * 100).toFixed(1)}%
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="details" className="mt-6">
          <div className="glass-card rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-6">Selected Node Details</h3>
            {selectedNode ? (
              <div className="space-y-6">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-2xl font-bold mb-2">{selectedNode.name}</h3>
                    <Badge className={`bg-gradient-to-r ${getNodeTypeGradient(selectedNode.group)} text-white border-0`}>
                      {selectedNode.group}
                    </Badge>
                  </div>
                  <Button variant="ghost" size="sm">
                    <Sparkles className="h-4 w-4 mr-2" />
                    Analyze
                  </Button>
                </div>
                
                {selectedNode.properties && (
                  <div className="space-y-3">
                    {Object.entries(selectedNode.properties).map(([key, value]) => (
                      <div key={key} className="flex justify-between py-3 border-b border-gray-100">
                        <span className="text-sm font-medium text-gray-600">
                          {key.replace(/_/g, ' ').split(' ').map(word => 
                            word.charAt(0).toUpperCase() + word.slice(1)
                          ).join(' ')}
                        </span>
                        <span className="text-sm font-medium">{String(value)}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-16">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
                  <Network className="h-8 w-8 text-gray-400" />
                </div>
                <p className="text-gray-500">Click on a node in the visualization to see its details</p>
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}