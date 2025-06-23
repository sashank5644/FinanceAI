"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { useExecuteAgent } from "@/hooks/useApi";
import { formatDate } from "@/lib/utils";
import { 
  Send, 
  Brain,
  Sparkles,
  FileText,
  TrendingUp,
  Building2,
  Globe,
  AlertCircle,
  Clock,
  Zap,
  MessageSquare,
  ArrowRight,
  Lightbulb,
  Share2,
  Download,
  Copy,
  CheckCircle2
} from "lucide-react";

const exampleQueries = [
  {
    icon: TrendingUp,
    text: "What is Apple's current stock price and recent performance?",
    category: "Stock Analysis",
    gradient: "from-blue-500 to-blue-600"
  },
  {
    icon: Building2,
    text: "Analyze Microsoft's competitive position in cloud computing",
    category: "Company Research",
    gradient: "from-purple-500 to-purple-600"
  },
  {
    icon: Globe,
    text: "What are the latest trends in the semiconductor industry?",
    category: "Market Analysis",
    gradient: "from-green-500 to-green-600"
  },
  {
    icon: FileText,
    text: "Find recent news about Tesla and analyze market sentiment",
    category: "News & Sentiment",
    gradient: "from-orange-500 to-orange-600"
  }
];

export default function ResearchPage() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [copied, setCopied] = useState(false);
  const { mutate: executeAgent } = useExecuteAgent();

  const handleSubmit = () => {
    if (!query.trim() || isAnalyzing) return;

    setIsAnalyzing(true);
    setResult(null);

    executeAgent(
      {
        query,
        agent_type: "research",
      },
      {
        onSuccess: (response) => {
          if (response.data) {
            setResult(response.data);
          }
          setIsAnalyzing(false);
        },
        onError: (error) => {
          console.error("Research failed:", error);
          setResult({
            status: "failed",
            error: "Failed to execute research. Please try again."
          });
          setIsAnalyzing(false);
        },
      }
    );
  };

  const handleExampleClick = (exampleText: string) => {
    setQuery(exampleText);
  };

  const handleCopyResult = () => {
    if (result?.result?.output) {
      const textContent = Array.isArray(result.result.output)
        ? result.result.output.map((item: any) => 
            typeof item === "string" ? item : item?.text || ""
          ).join("\n")
        : typeof result.result.output === "object" && "text" in result.result.output
          ? result.result.output.text
          : result.result.output;
      
      navigator.clipboard.writeText(textContent);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const RateLimitInfo = ({ info }: { info: any }) => {
    if (!info) return null;
    
    return (
      <div className="flex items-center space-x-2 text-sm text-gray-600">
        <Clock className="h-4 w-4" />
        <span>
          {info.requests_remaining} requests remaining 
          {info.reset_in_seconds && ` (resets in ${info.reset_in_seconds}s)`}
        </span>
      </div>
    );
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 mt-20">
      {/* Hero Section */}
      <div className="text-center space-y-4 appear-animation">
        <div className="flex items-center justify-center space-x-2 mb-4">
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 blur-xl opacity-50" />
            <Brain className="relative h-12 w-12 text-blue-600" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold gradient-text">
            Research Agent
          </h1>
        </div>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Ask me anything about stocks, companies, markets, and financial news. 
          I'll analyze real-time data and provide intelligent insights.
        </p>
        <div className="flex items-center justify-center space-x-4 text-sm">
          <Badge variant="secondary" className="bg-blue-100 text-blue-700 border-0">
            <Zap className="h-3 w-3 mr-1" />
            Powered by Gemini AI
          </Badge>
          <Badge variant="secondary" className="bg-green-100 text-green-700 border-0">
            <Clock className="h-3 w-3 mr-1" />
            4 queries/minute
          </Badge>
        </div>
      </div>

      {/* Query Input Card */}
      <div className="glass-card rounded-2xl p-8 appear-animation" style={{ animationDelay: "0.1s" }}>
        <div className="space-y-6">
          <div className="relative">
            <Textarea
              placeholder="Ask me anything about financial markets, companies, or investment strategies..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="min-h-[120px] resize-none bg-white/50 backdrop-blur-sm border-gray-200/50 focus:bg-white focus:border-blue-300 transition-all duration-200"
              disabled={isAnalyzing}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && e.metaKey) {
                  handleSubmit();
                }
              }}
            />
            <div className="absolute bottom-4 right-4 text-xs text-gray-400">
              Press ⌘+Enter to submit
            </div>
          </div>
          
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <MessageSquare className="h-4 w-4" />
              <span>{query.length} / 500 characters</span>
            </div>
            <Button 
              onClick={handleSubmit}
              disabled={!query.trim() || isAnalyzing}
              className="btn-premium text-white min-w-[160px]"
              size="lg"
            >
              {isAnalyzing ? (
                <>
                  <Spinner size="sm" className="mr-2" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Send className="h-4 w-4 mr-2" />
                  Research
                </>
              )}
            </Button>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {isAnalyzing && (
        <div className="glass-card rounded-2xl p-12 appear-animation">
          <div className="flex flex-col items-center space-y-6">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 blur-2xl opacity-30 animate-pulse" />
              <Spinner size="lg" className="relative" />
            </div>
            <div className="text-center space-y-2">
              <p className="text-lg font-medium text-gray-800">Analyzing your query...</p>
              <p className="text-sm text-gray-500">
                Searching multiple data sources and generating insights
              </p>
            </div>
            <div className="flex items-center space-x-8 text-sm text-gray-500">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                <span>Fetching data</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" />
                <span>Processing</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <span>Generating insights</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Example Queries */}
      {!result && !isAnalyzing && (
        <div className="appear-animation" style={{ animationDelay: "0.2s" }}>
          <div className="flex items-center justify-center space-x-2 mb-6">
            <Lightbulb className="h-5 w-5 text-yellow-500" />
            <h3 className="text-lg font-semibold">Popular Research Topics</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {exampleQueries.map((example, index) => {
              const Icon = example.icon;
              return (
                <button
                  key={index}
                  onClick={() => handleExampleClick(example.text)}
                  className="group glass-card rounded-xl p-6 text-left hover-lift transition-all duration-300"
                  style={{ animationDelay: `${0.3 + index * 0.1}s` }}
                >
                  <div className="flex items-start space-x-4">
                    <div className={`p-3 rounded-lg bg-gradient-to-br ${example.gradient} group-hover:scale-110 transition-transform duration-200`}>
                      <Icon className="h-5 w-5 text-white" />
                    </div>
                    <div className="flex-1">
                      <Badge variant="secondary" className="mb-2">
                        {example.category}
                      </Badge>
                      <p className="text-sm text-gray-700 font-medium">
                        {example.text}
                      </p>
                    </div>
                    <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-gray-600 group-hover:translate-x-1 transition-all duration-200" />
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Results */}
      {result && !isAnalyzing && (
        <div className="glass-card rounded-2xl p-8 appear-animation">
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className={`p-2 rounded-lg ${
                  result.status === "completed" ? "bg-green-100" : 
                  result.status === "rate_limited" ? "bg-yellow-100" : 
                  "bg-red-100"
                }`}>
                  <Brain className={`h-5 w-5 ${
                    result.status === "completed" ? "text-green-600" : 
                    result.status === "rate_limited" ? "text-yellow-600" : 
                    "text-red-600"
                  }`} />
                </div>
                <div>
                  <h3 className="text-lg font-semibold">Research Results</h3>
                  <p className="text-sm text-gray-500">
                    Generated on {formatDate(new Date())}
                  </p>
                </div>
              </div>
              <Badge 
                variant={
                  result.status === "completed" ? "default" : 
                  result.status === "rate_limited" ? "warning" : 
                  "destructive"
                }
                className={
                  result.status === "completed" ? "bg-green-100 text-green-700 border-0" : 
                  result.status === "rate_limited" ? "bg-yellow-100 text-yellow-700 border-0" : 
                  ""
                }
              >
                {result.status}
              </Badge>
            </div>
            
            {result.rate_limit_info && (
              <RateLimitInfo info={result.rate_limit_info} />
            )}

            <div className="prose prose-lg max-w-none">
              {result.status === "rate_limited" ? (
                <div className="flex items-start space-x-3 p-4 rounded-lg bg-yellow-50 border border-yellow-200">
                  <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5" />
                  <div>
                    <p className="font-medium text-yellow-800">Rate Limit Reached</p>
                    <p className="text-sm mt-1 text-yellow-700">{result.error}</p>
                  </div>
                </div>
              ) : result.result?.output ? (
                <div className="space-y-4">
                  <div className="p-6 rounded-lg bg-gray-50 border border-gray-200">
                    <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
                      {Array.isArray(result.result.output)
                        ? result.result.output.map((item: { text?: string } | string, idx: number) => (
                            <div key={idx} className="mb-4 last:mb-0">
                              {typeof item === "string" ? item : item?.text || ""}
                            </div>
                          ))
                        : typeof result.result.output === "object" && "text" in result.result.output
                          ? <div>{result.result.output.text || ""}</div>
                          : <div>{result.result.output}</div>}
                    </div>
                  </div>
                </div>
              ) : result.error ? (
                <div className="flex items-start space-x-3 p-4 rounded-lg bg-red-50 border border-red-200">
                  <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
                  <div>
                    <p className="font-medium text-red-800">Error</p>
                    <p className="text-sm mt-1 text-red-700">{result.error}</p>
                  </div>
                </div>
              ) : (
                <div className="text-gray-500 text-center py-8">
                  No results available
                </div>
              )}
            </div>
            
            <div className="flex items-center justify-between pt-6 border-t">
              <Button
                variant="outline"
                onClick={() => {
                  setResult(null);
                  setQuery("");
                }}
                className="hover:bg-gray-50"
              >
                <Sparkles className="h-4 w-4 mr-2" />
                New Research
              </Button>
              
              <div className="flex items-center space-x-2">
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={handleCopyResult}
                  disabled={!result?.result?.output}
                >
                  {copied ? (
                    <>
                      <CheckCircle2 className="h-4 w-4 mr-2 text-green-500" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="h-4 w-4 mr-2" />
                      Copy
                    </>
                  )}
                </Button>
                <Button variant="ghost" size="sm">
                  <Share2 className="h-4 w-4 mr-2" />
                  Share
                </Button>
                <Button variant="ghost" size="sm">
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
        <div className="glass-card rounded-xl p-6 text-center appear-animation" style={{ animationDelay: "0.6s" }}>
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 mb-4">
            <Zap className="h-6 w-6 text-white" />
          </div>
          <h4 className="font-semibold mb-2">Real-time Analysis</h4>
          <p className="text-sm text-gray-600">
            Get up-to-date information from multiple financial data sources
          </p>
        </div>

        <div className="glass-card rounded-xl p-6 text-center appear-animation" style={{ animationDelay: "0.7s" }}>
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-purple-600 mb-4">
            <Brain className="h-6 w-6 text-white" />
          </div>
          <h4 className="font-semibold mb-2">AI-Powered Insights</h4>
          <p className="text-sm text-gray-600">
            Advanced language models provide deep financial analysis
          </p>
        </div>

        <div className="glass-card rounded-xl p-6 text-center appear-animation" style={{ animationDelay: "0.8s" }}>
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-gradient-to-br from-green-500 to-green-600 mb-4">
            <Globe className="h-6 w-6 text-white" />
          </div>
          <h4 className="font-semibold mb-2">Comprehensive Coverage</h4>
          <p className="text-sm text-gray-600">
            From individual stocks to entire market sectors and trends
          </p>
        </div>
      </div>
    </div>
  );
}