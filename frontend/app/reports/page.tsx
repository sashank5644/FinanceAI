"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { apiClient } from "@/services/api";
import { formatDate } from "@/lib/utils";
import { 
  FileText, 
  Download, 
  Eye, 
  Plus,
  Clock,
  BarChart3,
  TrendingUp,
  Globe,
  Briefcase,
  ChevronRight,
  FileDown,
  FileSpreadsheet,
  File,
  Sparkles,
  ArrowRight,
  Zap,
  BookOpen
} from "lucide-react";
import ReactMarkdown from "react-markdown";

interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  parameters: Record<string, string>;
}

interface GeneratedReport {
  id: string;
  type: string;
  title: string;
  created_at: string;
  word_count: number;
  sections: number;
}

export default function ReportsPage() {
  const [templates, setTemplates] = useState<ReportTemplate[]>([]);
  const [reports, setReports] = useState<GeneratedReport[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string>("");
  const [reportTitle, setReportTitle] = useState("");
  const [parameters, setParameters] = useState<Record<string, any>>({});
  const [isGenerating, setIsGenerating] = useState(false);
  const [activeTab, setActiveTab] = useState("generate");
  const [selectedReport, setSelectedReport] = useState<any>(null);
  const [previewContent, setPreviewContent] = useState("");
  const [isLoadingPreview, setIsLoadingPreview] = useState(false);

  useEffect(() => {
    loadTemplates();
    loadReports();
  }, []);

  const loadTemplates = async () => {
    const response = await apiClient.getReportTemplates();
    if (response.success && response.data) {
      setTemplates(response.data.templates);
    }
  };

  const loadReports = async () => {
    const response = await apiClient.getReports();
    if (response.success && response.data) {
      setReports(response.data.items || []);
    }
  };

  const handleTemplateSelect = (templateId: string) => {
    setSelectedTemplate(templateId);
    const template = templates.find(t => t.id === templateId);
    if (template) {
      const initialParams: Record<string, any> = {};
      Object.keys(template.parameters).forEach(key => {
        initialParams[key] = "";
      });
      setParameters(initialParams);
    }
  };

  const handleGenerateReport = async () => {
    if (!selectedTemplate || !reportTitle) return;

    setIsGenerating(true);
    try {
      const response = await apiClient.generateReport({
        report_type: selectedTemplate,
        title: reportTitle,
        parameters: parameters,
        format: "markdown"
      });

      if (response.success) {
        await loadReports();
        setActiveTab("library");
        setReportTitle("");
        setParameters({});
        setSelectedTemplate("");
      }
    } catch (error) {
      console.error("Failed to generate report:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handlePreview = async () => {
    if (!selectedTemplate || !reportTitle) return;

    setIsLoadingPreview(true);
    try {
      const response = await apiClient.previewReport({
        report_type: selectedTemplate,
        title: reportTitle,
        parameters: parameters
      });

      if (response.success && response.data) {
        setPreviewContent(response.data.preview);
      }
    } catch (error) {
      console.error("Failed to preview report:", error);
    } finally {
      setIsLoadingPreview(false);
    }
  };

  const handleViewReport = async (reportId: string) => {
    const response = await apiClient.getReport(reportId);
    if (response.success && response.data) {
      setSelectedReport(response.data.report);
      setActiveTab("view");
    }
  };

  const handleDownloadReport = async (reportId: string, format: string) => {
    const url = `${process.env.NEXT_PUBLIC_API_URL}${process.env.NEXT_PUBLIC_API_PREFIX}/reports/${reportId}/download?format=${format}`;
    window.open(url, "_blank");
  };

  const getTemplateIcon = (templateId: string) => {
    const icons: Record<string, any> = {
      research_summary: BarChart3,
      strategy_performance: TrendingUp,
      market_analysis: Globe,
      portfolio_review: Briefcase
    };
    return icons[templateId] || FileText;
  };

  const getTemplateGradient = (templateId: string) => {
    const gradients: Record<string, string> = {
      research_summary: "from-blue-500 to-blue-600",
      strategy_performance: "from-purple-500 to-purple-600",
      market_analysis: "from-green-500 to-green-600",
      portfolio_review: "from-orange-500 to-orange-600"
    };
    return gradients[templateId] || "from-gray-500 to-gray-600";
  };

  return (
    <div className="space-y-8 mt-20">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 p-8 md:p-12">
        <div className="absolute inset-0 bg-black/20" />
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-white/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-white/10 rounded-full blur-3xl" />
        
        <div className="relative">
          <div className="flex items-center space-x-2 mb-4">
            <Sparkles className="h-5 w-5 text-yellow-300 animate-pulse" />
            <Badge className="bg-white/20 text-white border-white/30">
              AI-Generated Reports
            </Badge>
          </div>
          
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Professional Investment Reports
          </h1>
          <p className="text-xl text-white/80 max-w-2xl">
            Generate comprehensive, AI-powered investment reports with real-time data, 
            analysis, and actionable insights in minutes.
          </p>
          
          <div className="flex flex-wrap gap-4 mt-8">
            <Button 
              size="lg"
              className="bg-white text-gray-900 hover:bg-gray-100"
              onClick={() => setActiveTab("generate")}
            >
              <Plus className="h-5 w-5 mr-2" />
              Generate Report
            </Button>
            <Button 
              size="lg" 
              variant="outline" 
              className="bg-white/10 text-white border-white/30 hover:bg-white/20"
              onClick={() => setActiveTab("library")}
            >
              <BookOpen className="h-5 w-5 mr-2" />
              View Library
            </Button>
          </div>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid grid-cols-3 w-full max-w-md mx-auto glass-card p-1">
          <TabsTrigger value="generate">Generate</TabsTrigger>
          <TabsTrigger value="library">Library</TabsTrigger>
          <TabsTrigger value="view">View</TabsTrigger>
        </TabsList>

        <TabsContent value="generate" className="space-y-6">
          {/* Template Selection */}
          <div className="glass-card rounded-xl p-6 appear-animation">
            <h3 className="text-lg font-semibold mb-6">Choose Report Template</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {templates.map((template, index) => {
                const Icon = getTemplateIcon(template.id);
                const gradient = getTemplateGradient(template.id);
                return (
                  <button
                    key={template.id}
                    onClick={() => handleTemplateSelect(template.id)}
                    className={`group relative p-6 rounded-xl text-left transition-all duration-300 hover-lift ${
                      selectedTemplate === template.id
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
                        <h3 className="font-semibold text-lg mb-1">{template.name}</h3>
                        <p className="text-sm text-gray-600">
                          {template.description}
                        </p>
                      </div>
                    </div>
                    {selectedTemplate === template.id && (
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

          {/* Report Configuration */}
          {selectedTemplate && (
            <div className="glass-card rounded-xl p-6 appear-animation">
              <h3 className="text-lg font-semibold mb-6">Configure Your Report</h3>
              <div className="space-y-6">
                <div>
                  <Label htmlFor="title" className="text-sm font-medium mb-2 block">
                    Report Title
                  </Label>
                  <Input
                    id="title"
                    placeholder="e.g., Q4 2024 Technology Sector Analysis"
                    value={reportTitle}
                    onChange={(e) => setReportTitle(e.target.value)}
                    className="bg-white/50 backdrop-blur-sm border-gray-200/50 focus:bg-white"
                  />
                </div>

                {/* Dynamic Parameters */}
                {templates.find(t => t.id === selectedTemplate)?.parameters &&
                  Object.entries(templates.find(t => t.id === selectedTemplate)!.parameters).map(
                    ([key, description]) => (
                      <div key={key}>
                        <Label htmlFor={key} className="text-sm font-medium mb-2 block">
                          {key.split("_").map(word => 
                            word.charAt(0).toUpperCase() + word.slice(1)
                          ).join(" ")}
                        </Label>
                        <p className="text-sm text-gray-600 mb-2">{description}</p>
                        {key.includes("ids") ? (
                          <Textarea
                            id={key}
                            placeholder="Enter comma-separated IDs"
                            value={parameters[key] || ""}
                            onChange={(e) => setParameters({ ...parameters, [key]: e.target.value })}
                            rows={2}
                            className="bg-white/50 backdrop-blur-sm border-gray-200/50 focus:bg-white"
                          />
                        ) : (
                          <Input
                            id={key}
                            value={parameters[key] || ""}
                            onChange={(e) => setParameters({ ...parameters, [key]: e.target.value })}
                            className="bg-white/50 backdrop-blur-sm border-gray-200/50 focus:bg-white"
                          />
                        )}
                      </div>
                    )
                  )}

                <div className="flex justify-between pt-6 border-t">
                  <Button
                    variant="outline"
                    onClick={handlePreview}
                    disabled={!reportTitle || isLoadingPreview}
                    className="hover:bg-gray-50"
                  >
                    {isLoadingPreview ? (
                      <>
                        <Spinner size="sm" className="mr-2" />
                        Loading Preview...
                      </>
                    ) : (
                      <>
                        <Eye className="h-4 w-4 mr-2" />
                        Preview
                      </>
                    )}
                  </Button>
                  <Button
                    onClick={handleGenerateReport}
                    disabled={!reportTitle || isGenerating}
                    className="btn-premium text-white min-w-[180px]"
                  >
                    {isGenerating ? (
                      <>
                        <Spinner size="sm" className="mr-2" />
                        Generating Report...
                      </>
                    ) : (
                      <>
                        <Zap className="h-4 w-4 mr-2" />
                        Generate Report
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Preview */}
          {previewContent && (
            <div className="glass-card rounded-xl p-6 appear-animation">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold">Report Preview</h3>
                <Badge variant="secondary">First 1000 characters</Badge>
              </div>
              <div className="prose prose-lg max-w-none">
                <ReactMarkdown>{previewContent}</ReactMarkdown>
              </div>
            </div>
          )}
        </TabsContent>

        <TabsContent value="library">
          <div className="glass-card rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold">Generated Reports</h3>
              <Badge variant="secondary">{reports.length} reports</Badge>
            </div>
            {reports.length > 0 ? (
              <div className="space-y-4">
                {reports.map((report, index) => {
                  const Icon = getTemplateIcon(report.type);
                  const gradient = getTemplateGradient(report.type);
                  return (
                    <div
                      key={report.id}
                      className="group flex items-center justify-between p-6 rounded-xl border border-gray-100 hover:border-gray-200 hover:shadow-lg transition-all duration-200 cursor-pointer appear-animation"
                      style={{ animationDelay: `${index * 0.1}s` }}
                    >
                      <div className="flex items-center space-x-4">
                        <div className={`p-3 rounded-xl bg-gradient-to-br ${gradient} group-hover:scale-110 transition-transform duration-200`}>
                          <Icon className="h-6 w-6 text-white" />
                        </div>
                        <div>
                          <h4 className="font-semibold text-lg">{report.title}</h4>
                          <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
                            <span className="flex items-center">
                              <Clock className="h-3.5 w-3.5 mr-1" />
                              {formatDate(report.created_at)}
                            </span>
                            <Badge variant="outline" className="text-xs">
                              {report.type.replace("_", " ")}
                            </Badge>
                            <span>{report.word_count.toLocaleString()} words</span>
                            <span>{report.sections} sections</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleViewReport(report.id);
                          }}
                          className="hover:bg-gray-100"
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDownloadReport(report.id, "markdown");
                          }}
                          className="hover:bg-gray-100"
                        >
                          <File className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDownloadReport(report.id, "html");
                          }}
                          className="hover:bg-gray-100"
                        >
                          <FileSpreadsheet className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-16">
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-gray-100 to-gray-200 mb-6">
                  <FileText className="h-10 w-10 text-gray-400" />
                </div>
                <h3 className="text-xl font-semibold mb-2">No reports yet</h3>
                <p className="text-gray-500 mb-6">Generate your first professional investment report</p>
                <Button
                  className="btn-premium text-white"
                  onClick={() => setActiveTab("generate")}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Generate Your First Report
                </Button>
              </div>
            )}
          </div>
        </TabsContent>

        <TabsContent value="view">
          {selectedReport ? (
            <div className="glass-card rounded-xl p-8">
              <div className="flex justify-between items-start mb-8">
                <div>
                  <h2 className="text-3xl font-bold mb-2">{selectedReport.title}</h2>
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    <span className="flex items-center">
                      <Clock className="h-4 w-4 mr-1" />
                      Generated on {formatDate(selectedReport.created_at)}
                    </span>
                    <Badge variant="secondary">
                      {selectedReport.type.replace("_", " ")}
                    </Badge>
                  </div>
                </div>
                <div className="flex space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDownloadReport(selectedReport.id, "markdown")}
                    className="hover:bg-gray-50"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Markdown
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDownloadReport(selectedReport.id, "html")}
                    className="hover:bg-gray-50"
                  >
                    <FileDown className="h-4 w-4 mr-2" />
                    HTML
                  </Button>
                </div>
              </div>
              <div className="prose prose-lg max-w-none">
                <ReactMarkdown>{selectedReport.content}</ReactMarkdown>
              </div>
            </div>
          ) : (
            <div className="glass-card rounded-xl p-8">
              <div className="text-center py-16">
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-gray-100 to-gray-200 mb-6">
                  <FileText className="h-10 w-10 text-gray-400" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Select a report to view</h3>
                <p className="text-gray-500 mb-6">
                  Choose a report from the library to read it here
                </p>
                <Button
                  variant="outline"
                  onClick={() => setActiveTab("library")}
                  className="hover:bg-gray-50"
                >
                  <ArrowRight className="h-4 w-4 mr-2" />
                  Go to Library
                </Button>
              </div>
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-card rounded-xl p-6 text-center appear-animation" style={{ animationDelay: "0.6s" }}>
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 mb-4">
            <Zap className="h-6 w-6 text-white" />
          </div>
          <h4 className="font-semibold mb-2">Instant Generation</h4>
          <p className="text-sm text-gray-600">
            Create comprehensive reports in minutes, not hours
          </p>
        </div>

        <div className="glass-card rounded-xl p-6 text-center appear-animation" style={{ animationDelay: "0.7s" }}>
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-purple-600 mb-4">
            <BarChart3 className="h-6 w-6 text-white" />
          </div>
          <h4 className="font-semibold mb-2">Data-Driven Insights</h4>
          <p className="text-sm text-gray-600">
            Real-time market data and AI-powered analysis
          </p>
        </div>

        <div className="glass-card rounded-xl p-6 text-center appear-animation" style={{ animationDelay: "0.8s" }}>
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-gradient-to-br from-green-500 to-green-600 mb-4">
            <FileSpreadsheet className="h-6 w-6 text-white" />
          </div>
          <h4 className="font-semibold mb-2">Multiple Formats</h4>
          <p className="text-sm text-gray-600">
            Export in Markdown, HTML, or PDF formats
          </p>
        </div>
      </div>
    </div>
  );
}