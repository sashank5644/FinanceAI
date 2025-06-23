"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useHealthCheck } from "@/hooks/useApi";
import { 
  Activity, 
  Brain, 
  TrendingUp, 
  Network,
  BarChart3,
  Menu,
  X,
  Settings,
  Moon,
  Sun
} from "lucide-react";

const navigation = [
  { name: "Dashboard", href: "/", icon: BarChart3 },
  { name: "Research", href: "/research", icon: Brain },
  { name: "Strategies", href: "/strategies", icon: TrendingUp },
  { name: "Knowledge Graph", href: "/knowledge-graph", icon: Network },
];

export function Header() {
  const pathname = usePathname();
  const { data: health } = useHealthCheck();
  const isHealthy = health?.data?.status === "healthy";
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <header 
      className={cn(
        "fixed top-0 left-0 right-0 z-50 transition-all duration-300",
        isScrolled 
          ? "bg-white/80 backdrop-blur-xl shadow-lg shadow-black/5" 
          : "bg-transparent"
      )}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center group">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 blur-lg opacity-50 group-hover:opacity-75 transition-opacity" />
              <Brain className="relative h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-3">
              <span className="text-xl font-bold gradient-text">
                FinanceAI
              </span>
              <span className="block text-xs text-gray-500 font-medium">
                Research Agent
              </span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-1">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "group relative px-4 py-2 rounded-lg transition-all duration-200",
                    isActive 
                      ? "text-gray-900" 
                      : "text-gray-600 hover:text-gray-900"
                  )}
                >
                  <div className="flex items-center space-x-2">
                    <Icon className={cn(
                      "h-4 w-4 transition-transform duration-200",
                      "group-hover:scale-110"
                    )} />
                    <span className="font-medium">{item.name}</span>
                  </div>
                  {isActive && (
                    <div className="absolute bottom-0 left-4 right-4 h-0.5 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full" />
                  )}
                  {!isActive && (
                    <div className="absolute bottom-0 left-4 right-4 h-0.5 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full scale-x-0 group-hover:scale-x-100 transition-transform duration-300" />
                  )}
                </Link>
              );
            })}
          </nav>

          {/* Right side items */}
          <div className="flex items-center space-x-3">
            {/* Status Badge */}
            <div className="relative group">
              <div className={cn(
                "absolute inset-0 rounded-full blur-md transition-opacity duration-300",
                isHealthy ? "bg-green-400 opacity-50" : "bg-red-400 opacity-50",
                "group-hover:opacity-75"
              )} />
              <Badge
                variant={isHealthy ? "default" : "destructive"}
                className={cn(
                  "relative flex items-center space-x-1.5 px-3 py-1",
                  isHealthy 
                    ? "bg-green-500/10 text-green-700 border-green-200" 
                    : "bg-red-500/10 text-red-700 border-red-200"
                )}
              >
                <div className={cn(
                  "w-2 h-2 rounded-full",
                  isHealthy ? "bg-green-500" : "bg-red-500",
                  "animate-pulse"
                )} />
                <span className="font-medium text-xs">
                  {isHealthy ? "Online" : "Offline"}
                </span>
              </Badge>
            </div>

            {/* Theme Toggle */}
            <Button
              variant="ghost"
              size="icon"
              className="relative group"
              onClick={() => setIsDark(!isDark)}
            >
              <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
              <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
              <span className="sr-only">Toggle theme</span>
            </Button>
            
            {/* Settings Button */}
            <Button 
              variant="ghost" 
              size="icon"
              className="relative group"
            >
              <Settings className="h-4 w-4 transition-transform duration-300 group-hover:rotate-90" />
              <span className="sr-only">Settings</span>
            </Button>

            {/* Mobile menu button */}
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              {isMobileMenuOpen ? (
                <X className="h-5 w-5" />
              ) : (
                <Menu className="h-5 w-5" />
              )}
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      <div className={cn(
        "md:hidden absolute top-full left-0 right-0 bg-white/95 backdrop-blur-xl shadow-lg",
        "transition-all duration-300 ease-in-out",
        isMobileMenuOpen 
          ? "opacity-100 translate-y-0" 
          : "opacity-0 -translate-y-4 pointer-events-none"
      )}>
        <nav className="px-4 py-4 space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                onClick={() => setIsMobileMenuOpen(false)}
                className={cn(
                  "flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200",
                  isActive 
                    ? "bg-gradient-to-r from-blue-50 to-purple-50 text-blue-700" 
                    : "text-gray-600 hover:bg-gray-50"
                )}
              >
                <Icon className="h-5 w-5" />
                <span className="font-medium">{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}