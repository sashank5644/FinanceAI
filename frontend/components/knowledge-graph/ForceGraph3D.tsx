// components/knowledge-graph/ForceGraph3D.tsx
"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import dynamic from "next/dynamic";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { 
  Search, 
  ZoomIn, 
  ZoomOut, 
  Maximize2, 
  Info,
  X
} from "lucide-react";

// Types for the graph data
interface GraphNode {
  id: string;
  name: string;
  group: string;
  properties?: any;
  x?: number;
  y?: number;
  z?: number;
}

interface GraphLink {
  source: string;
  target: string;
  type: string;
  value?: number;
}

interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

// Props for the component
interface ForceGraph3DProps {
  data: GraphData;
  onNodeClick?: (node: GraphNode) => void;
  onLinkClick?: (link: GraphLink) => void;
}

// This will be imported dynamically
let ForceGraph3D: any = null;

export default function ForceGraph3DComponent({ 
  data, 
  onNodeClick, 
  onLinkClick 
}: ForceGraph3DProps) {
  const graphRef = useRef<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [highlightNodes, setHighlightNodes] = useState(new Set());
  const [highlightLinks, setHighlightLinks] = useState(new Set());
  const [hoverNode, setHoverNode] = useState<GraphNode | null>(null);

  // Load the ForceGraph3D library dynamically
  useEffect(() => {
    import("react-force-graph-3d").then((module) => {
      ForceGraph3D = module.default;
      setIsLoading(false);
    });
  }, []);

  // Center graph on load
  useEffect(() => {
    if (graphRef.current && data.nodes.length > 0) {
      // Auto-rotate initially for a nice effect
      graphRef.current.cameraPosition({ x: 0, y: 0, z: 300 }, 1000);
      
      // Optional: Add some initial rotation
      let angle = 0;
      const rotateCamera = setInterval(() => {
        angle += 0.02;
        if (angle > Math.PI / 4) { // Stop after 45 degrees
          clearInterval(rotateCamera);
          return;
        }
        const distance = 300;
        graphRef.current.cameraPosition({
          x: distance * Math.sin(angle),
          y: 0,
          z: distance * Math.cos(angle)
        });
      }, 50);

      return () => clearInterval(rotateCamera);
    }
  }, [data, isLoading]);

  // Handle search
  const handleSearch = useCallback(() => {
    const query = searchQuery.toLowerCase();
    if (!query) {
      setHighlightNodes(new Set());
      setHighlightLinks(new Set());
      return;
    }

    const matchingNodes = new Set();
    const matchingLinks = new Set();

    data.nodes.forEach(node => {
      if (node.name.toLowerCase().includes(query) || 
          node.id.toLowerCase().includes(query)) {
        matchingNodes.add(node.id);
      }
    });

    data.links.forEach(link => {
      if (matchingNodes.has(link.source) || matchingNodes.has(link.target)) {
        matchingLinks.add(link);
      }
    });

    setHighlightNodes(matchingNodes);
    setHighlightLinks(matchingLinks);
  }, [searchQuery, data]);

  // Node color based on type
  const getNodeColor = (node: GraphNode) => {
    const colors: { [key: string]: string } = {
      Company: "#3B82F6",      // Blue
      Sector: "#10B981",       // Green
      Indicator: "#F59E0B",    // Yellow
      Event: "#EF4444",        // Red
      Unknown: "#6B7280"       // Gray
    };
    
    if (highlightNodes.has(node.id)) {
      return "#F59E0B"; // Highlight color
    }
    
    return colors[node.group] || colors.Unknown;
  };

  // Link color based on type
  const getLinkColor = (link: GraphLink) => {
    const colors: { [key: string]: string } = {
      BELONGS_TO: "#9CA3AF",      // Gray
      COMPETITOR_OF: "#EF4444",    // Red
      SUPPLIER_OF: "#3B82F6",      // Blue
      PARTNER_WITH: "#10B981",     // Green
      CORRELATES_WITH: "#8B5CF6", // Purple
    };
    
    return colors[link.type] || "#9CA3AF";
  };

  // Handle node click
  const handleNodeClick = useCallback((node: GraphNode) => {
    setSelectedNode(node);
    
    // Highlight connected nodes
    const connectedNodes = new Set([node.id]);
    const connectedLinks = new Set();
    
    data.links.forEach(link => {
      if (link.source === node.id || link.target === node.id) {
        connectedNodes.add(link.source === node.id ? link.target : link.source);
        connectedLinks.add(link);
      }
    });
    
    setHighlightNodes(connectedNodes);
    setHighlightLinks(connectedLinks);
    
    if (onNodeClick) {
      onNodeClick(node);
    }
  }, [data, onNodeClick]);

  // Graph controls
  const handleZoomIn = () => {
    if (graphRef.current) {
      const distance = graphRef.current.camera().position.length();
      graphRef.current.cameraPosition({ z: distance * 0.8 }, 1000);
    }
  };

  const handleZoomOut = () => {
    if (graphRef.current) {
      const distance = graphRef.current.camera().position.length();
      graphRef.current.cameraPosition({ z: distance * 1.2 }, 1000);
    }
  };

  const handleResetView = () => {
    if (graphRef.current) {
      graphRef.current.cameraPosition({ x: 0, y: 0, z: 300 }, 1000);
    }
    setHighlightNodes(new Set());
    setHighlightLinks(new Set());
    setSelectedNode(null);
    setSearchQuery("");
  };

  if (isLoading || !ForceGraph3D) {
    return (
      <Card className="h-[600px] flex items-center justify-center">
        <Spinner size="lg" />
      </Card>
    );
  }

  return (
    <div className="relative">
      {/* Controls */}
      <div className="absolute top-4 left-4 z-10 space-y-2">
        <div className="flex space-x-2">
          <Input
            placeholder="Search nodes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSearch()}
            className="w-64 bg-white/90 backdrop-blur"
          />
          <Button onClick={handleSearch} size="icon" variant="secondary">
            <Search className="h-4 w-4" />
          </Button>
        </div>
        
        <div className="flex space-x-2">
          <Button onClick={handleZoomIn} size="icon" variant="secondary">
            <ZoomIn className="h-4 w-4" />
          </Button>
          <Button onClick={handleZoomOut} size="icon" variant="secondary">
            <ZoomOut className="h-4 w-4" />
          </Button>
          <Button onClick={handleResetView} size="icon" variant="secondary">
            <Maximize2 className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Legend */}
      <div className="absolute top-4 right-4 z-10 bg-white/90 backdrop-blur p-4 rounded-lg">
        <h3 className="font-semibold mb-2">Legend</h3>
        <div className="space-y-1 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full" />
            <span>Company</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full" />
            <span>Sector</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-1 h-3 bg-gray-400" />
            <span>Belongs To</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-1 h-3 bg-red-500" />
            <span>Competitor</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-1 h-3 bg-blue-500" />
            <span>Supplier</span>
          </div>
        </div>
      </div>

      {/* Selected Node Info */}
      {selectedNode && (
        <div className="absolute bottom-4 left-4 z-10 bg-white/90 backdrop-blur p-4 rounded-lg max-w-sm">
          <div className="flex justify-between items-start mb-2">
            <h3 className="font-semibold">{selectedNode.name}</h3>
            <Button 
              size="icon" 
              variant="ghost" 
              className="h-6 w-6"
              onClick={() => setSelectedNode(null)}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          <Badge className="mb-2">{selectedNode.group}</Badge>
          {selectedNode.properties && (
            <div className="text-sm space-y-1 mt-2">
              {selectedNode.properties.symbol && (
                <p><span className="font-medium">Symbol:</span> {selectedNode.properties.symbol}</p>
              )}
              {selectedNode.properties.sector && (
                <p><span className="font-medium">Sector:</span> {selectedNode.properties.sector}</p>
              )}
              {selectedNode.properties.market_cap && (
                <p><span className="font-medium">Market Cap:</span> ${(selectedNode.properties.market_cap / 1e9).toFixed(0)}B</p>
              )}
            </div>
          )}
        </div>
      )}

      {/* Graph Container */}
      <Card className="h-[600px] overflow-hidden relative">
        <div className="absolute inset-0">
          <ForceGraph3D
            ref={graphRef}
            graphData={data}
            nodeLabel="name"
            nodeColor={getNodeColor}
            nodeOpacity={0.9}
            nodeRelSize={6}
            linkColor={getLinkColor}
            linkOpacity={0.6}
            linkWidth={2}
            linkDirectionalParticles={2}
            linkDirectionalParticleSpeed={0.005}
            onNodeClick={handleNodeClick}
            onNodeHover={setHoverNode}
            enableNodeDrag={true}
            enableNavigationControls={true}
            showNavInfo={false}
            backgroundColor="#f9fafb"
            width={undefined}
            height={undefined}
          />
        </div>
      </Card>

      {/* Hover tooltip */}
      {hoverNode && (
        <div className="absolute pointer-events-none" style={{
          left: "50%",
          top: "10px",
          transform: "translateX(-50%)",
          zIndex: 20
        }}>
          <div className="bg-black/80 text-white px-3 py-1 rounded text-sm">
            {hoverNode.name}
          </div>
        </div>
      )}
    </div>
  );
}