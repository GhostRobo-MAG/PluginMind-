"use client"

import React, { useRef, useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { TrendingUp, TrendingDown, AlertTriangle, Target, Brain, Shield, BarChart3 } from "lucide-react"

interface AnalysisData {
  coin: string
  timeframe: string
  investment: number
  analysis: string
  recommendation: string
  riskLevel: "low" | "medium" | "high"
  priceTarget: number
  confidence: number
  additionalMetrics?: {
    expectedReturn: number
    volatility: number
    sharpeRatio: number
    winRate: number
    maxDrawdown: number
    avgHoldingPeriod: string
  }
}

interface AnalysisSection {
  title: string
  content: string
}

interface AnalysisResultProps {
  data: AnalysisData
  parsedSections?: AnalysisSection[]
}

// Animation utility hook for intersection observer
function useBottomAppear(ref: React.RefObject<HTMLElement> | null, delay: number = 0) {
  const [visible, setVisible] = useState(false)
  useEffect(() => {
    if (ref == null || !ref.current) return
    const node = ref.current
    let timeout: NodeJS.Timeout | null = null
    const observer = new window.IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          timeout = setTimeout(() => setVisible(true), delay)
          observer.disconnect()
        }
      },
      { threshold: 0.1 }
    )
    observer.observe(node)
    return () => {
      observer.disconnect()
      if (timeout) clearTimeout(timeout)
    }
  }, [ref, delay])
  return visible
}

function AnimatedCard({
  children,
  className,
  delay = 0,
  ...props
}: React.ComponentProps<typeof Card> & { delay?: number }) {
  const cardRef = useRef<HTMLDivElement>(null)
  const visible = useBottomAppear(cardRef, delay)
  return (
    <Card
      ref={cardRef}
      className={
        `${className ?? ""} transition-all duration-700 ease-out
        ${visible
          ? "opacity-100 translate-y-0"
          : "opacity-0 translate-y-16 pointer-events-none"}`
      }
      {...props}
    >
      {children}
    </Card>
  )
}

export function AnalysisResult({ data, parsedSections }: AnalysisResultProps) {
  const getRiskColor = (risk: string) => {
    switch (risk) {
      case "low":
        return "bg-green-500/20 text-green-400 border-green-500/30"
      case "medium":
        return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30"
      case "high":
        return "bg-red-500/20 text-red-400 border-red-500/30"
      default:
        return "bg-crypto-accent/20 text-crypto-accent border-crypto-accent/30"
    }
  }

  const getRiskIcon = (risk: string) => {
    switch (risk) {
      case "low":
        return <Shield className="w-4 h-4" />
      case "medium":
        return <AlertTriangle className="w-4 h-4" />
      case "high":
        return <AlertTriangle className="w-4 h-4" />
      default:
        return <Shield className="w-4 h-4" />
    }
  }

  const getRecommendationIcon = (rec: string) => {
    if (rec.toLowerCase().includes("buy")) return <TrendingUp className="w-4 h-4 text-green-400" />
    if (rec.toLowerCase().includes("sell")) return <TrendingDown className="w-4 h-4 text-red-400" />
    return <Target className="w-4 h-4 text-crypto-accent" />
  }

  function renderSectionContent(content: string) {
    // Split into lines
    const lines = content.split(/\r?\n/).filter(line => line.trim() !== "");
    const elements: React.ReactNode[] = [];
    let listItems: string[] = [];

    function renderLineWithBold(line: string) {
      // Replace **bold** with <strong>bold</strong>
      const parts = line.split(/(\*\*[^*]+\*\*)/g);
      return parts.map((part, i) => {
        if (/^\*\*[^*]+\*\*$/.test(part)) {
          return <strong key={i}>{part.slice(2, -2)}</strong>;
        }
        return part;
      });
    }

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (/^\s*- /.test(line)) {
        listItems.push(line.replace(/^\s*- /, ""));
      } else {
        if (listItems.length > 0) {
          elements.push(
            <ul className="list-disc pl-6 mb-2" key={`ul-${i}`}>{
              listItems.map((item, idx) => <li key={idx}>{renderLineWithBold(item)}</li>)
            }</ul>
          );
          listItems = [];
        }
        elements.push(<div className="mb-2" key={i}>{renderLineWithBold(line)}</div>);
      }
    }
    if (listItems.length > 0) {
      elements.push(
        <ul className="list-disc pl-6 mb-2" key={`ul-last`}>{
          listItems.map((item, idx) => <li key={idx}>{renderLineWithBold(item)}</li>)
        }</ul>
      );
    }
    return elements;
  }

  // For staggered animation, cards at the bottom have less delay
  // We'll reverse the order for delays so the bottom cards appear first
  // For main analysis, the first card is at the top, so we reverse delays
  const getStaggeredDelay = (idx: number, total: number, base = 120) => (total - idx - 1) * base

  return (
    <div className="space-y-6">
      {/* Header */}
      <AnimatedCard className="bg-gradient-to-r from-crypto-primary/10 to-crypto-secondary/10 border-crypto-primary/30" delay={0}>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl flex items-center">
                <Brain className="w-6 h-6 mr-2 text-crypto-primary" />
                Analysis Complete
              </CardTitle>
              <CardDescription className="text-crypto-light text-lg">
                {data.coin} • {data.timeframe} • ${data.investment.toLocaleString()} investment
              </CardDescription>
            </div>
            <Badge className="bg-crypto-primary/20 text-crypto-primary border-crypto-primary/30 text-lg px-4 py-2 text-medium">
              {data.confidence}% Confidence
            </Badge>
          </div>
        </CardHeader>
      </AnimatedCard>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Main Analysis */}
        <div className="lg:col-span-2 space-y-6">
          {parsedSections && parsedSections.length > 0 ? (
            parsedSections.map((section, idx) => (
              <AnimatedCard
                key={idx}
                className="bg-crypto-dark/50 border-crypto-accent/20"
                delay={getStaggeredDelay(idx, parsedSections.length)}
              >
                <CardHeader>
                  <CardTitle className="text-white flex items-center">
                    <BarChart3 className="w-5 h-5 mr-2 text-crypto-primary" />
                    {section.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-crypto-light leading-relaxed text-lg whitespace-pre-line">{renderSectionContent(section.content)}</div>
                </CardContent>
              </AnimatedCard>
            ))
          ) : (
            <>
              <AnimatedCard className="bg-crypto-dark/50 border-crypto-accent/20" delay={120}>
                <CardHeader>
                  <CardTitle className="text-white flex items-center">
                    <Brain className="w-5 h-5 mr-2 text-crypto-primary" />
                    AI Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-crypto-light leading-relaxed text-lg">{data.analysis}</p>
                </CardContent>
              </AnimatedCard>
              <AnimatedCard className="bg-crypto-dark/50 border-crypto-accent/20" delay={0}>
                <CardHeader>
                  <CardTitle className="text-white flex items-center">
                    {getRecommendationIcon(data.recommendation)}
                    <span className="ml-2">Recommendation</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-crypto-light leading-relaxed text-lg">{data.recommendation}</p>
                </CardContent>
              </AnimatedCard>
            </>
          )}
        </div>

        {/* Metrics Sidebar */}
        <div className="space-y-6">
          {/* Sidebar cards: bottom-most card appears first */}
          <AnimatedCard className="bg-crypto-dark/50 border-crypto-accent/20" delay={360}>
            <CardHeader>
              <CardTitle className="text-white text-lg">Risk Assessment</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-crypto-light">Risk Level</span>
                <Badge className={getRiskColor(data.riskLevel)}>
                  {getRiskIcon(data.riskLevel)}
                  <span className="ml-1 capitalize">{data.riskLevel}</span>
                </Badge>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-crypto-light">Confidence</span>
                  <span className="text-white font-semibold">{data.confidence}%</span>
                </div>
                <Progress value={data.confidence} className="h-2 bg-crypto-darker" />
              </div>
            </CardContent>
          </AnimatedCard>

          {data.priceTarget > 0 && (
            <AnimatedCard className="bg-crypto-dark/50 border-crypto-accent/20" delay={240}>
              <CardHeader>
                <CardTitle className="text-white text-lg flex items-center">
                  <Target className="w-5 h-5 mr-2 text-crypto-secondary" />
                  Price Target
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center">
                  <div className="text-3xl font-bold text-crypto-primary">${data.priceTarget.toLocaleString()}</div>
                  <div className="text-crypto-light text-sm mt-1">{data.timeframe} target</div>
                </div>
              </CardContent>
            </AnimatedCard>
          )}

          <AnimatedCard className="bg-crypto-dark/50 border-crypto-accent/20" delay={120}>
            <CardHeader>
              <CardTitle className="text-white text-lg">Investment Summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <span className="text-crypto-light">Asset</span>
                <span className="text-white font-semibold">{data.coin}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-crypto-light">Timeframe</span>
                <span className="text-white font-semibold">{data.timeframe}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-crypto-light">Investment</span>
                <span className="text-white font-semibold">${data.investment.toLocaleString()}</span>
              </div>
            </CardContent>
          </AnimatedCard>
          {data.additionalMetrics && (
            <AnimatedCard className="bg-crypto-dark/50 border-crypto-accent/20" delay={0}>
              <CardHeader>
                <CardTitle className="text-white text-lg flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2 text-crypto-accent" />
                  Performance Metrics
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div className="text-center p-2 bg-crypto-darker/50 rounded">
                    <div className="text-lg font-bold text-crypto-primary">
                      +{data.additionalMetrics.expectedReturn.toFixed(1)}%
                    </div>
                    <div className="text-xs text-crypto-light">Expected Return</div>
                  </div>
                  <div className="text-center p-2 bg-crypto-darker/50 rounded">
                    <div className="text-lg font-bold text-crypto-secondary">
                      {data.additionalMetrics.volatility.toFixed(1)}%
                    </div>
                    <div className="text-xs text-crypto-light">Volatility</div>
                  </div>
                  <div className="text-center p-2 bg-crypto-darker/50 rounded">
                    <div className="text-lg font-bold text-crypto-accent">
                      {data.additionalMetrics.sharpeRatio.toFixed(2)}
                    </div>
                    <div className="text-xs text-crypto-light">Sharpe Ratio</div>
                  </div>
                  <div className="text-center p-2 bg-crypto-darker/50 rounded">
                    <div className="text-lg font-bold text-crypto-light">{data.additionalMetrics.winRate}%</div>
                    <div className="text-xs text-crypto-light">Win Rate</div>
                  </div>
                </div>
                <div className="pt-2 border-t border-crypto-accent/20">
                  <div className="flex justify-between text-sm">
                    <span className="text-crypto-light">Max Drawdown</span>
                    <span className="text-red-400">{data.additionalMetrics.maxDrawdown.toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between text-sm mt-1">
                    <span className="text-crypto-light">Avg Hold Period</span>
                    <span className="text-crypto-accent">{data.additionalMetrics.avgHoldingPeriod}</span>
                  </div>
                </div>
              </CardContent>
            </AnimatedCard>
          )}
        </div>
      </div>
    </div>
  )
}
