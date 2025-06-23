// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// Agent Types
export interface AgentRequest {
  query: string;
  agent_type: 'research' | 'strategy' | 'backtest';
  parameters?: Record<string, any>;
}

export interface AgentResponse {
  request_id: string;
  status: 'pending' | 'completed' | 'failed';
  result?: {
    success: boolean;
    output?: string;
    intermediate_steps?: any[];
  };
  error?: string;
}

// Research Types
export interface Research {
  id: string;
  query: string;
  sources: string[];
  depth: 'quick' | 'standard' | 'comprehensive';
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  summary?: string;
  key_findings?: Record<string, any>;
  created_at: string;
  completed_at?: string;
  error_message?: string;
}

// Strategy Types
export interface Strategy {
  id: string;
  name: string;
  description?: string;
  type: 'long_only' | 'long_short' | 'market_neutral';
  status: string;
  rules?: Record<string, any>;
  expected_return?: number;
  expected_volatility?: number;
  created_at: string;
}

// Market Data Types
export interface StockData {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap?: number;
  high?: number;
  low?: number;
}

// Knowledge Graph Types
export interface GraphNode {
  id: string;
  type: 'company' | 'sector' | 'indicator' | 'event';
  properties: Record<string, any>;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
  weight?: number;
  properties?: Record<string, any>;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}
