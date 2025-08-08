"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { TrendingUp, TrendingDown, Activity, Users, Globe, Zap } from "lucide-react"

interface MarketInsightsProps {
  coin: string
}

export function MarketInsights({ coin }: MarketInsightsProps) {
  // Mock market data - in real app, this would come from APIs
  const marketData = {
    ETH: {
      fearGreedIndex: 45,
      socialSentiment: 67,
      whaleActivity: 78,
      networkActivity: 85,
      institutionalFlow: 23,
      developerActivity: 92,
      news: [
        { title: "Ethereum Shanghai Upgrade Scheduled", sentiment: "positive", impact: "high" },
        { title: "Major DeFi Protocol Launches on ETH", sentiment: "positive", impact: "medium" },
        { title: "Gas Fees Decrease 15% This Week", sentiment: "positive", impact: "medium" },
      ],
      keyMetrics: {
        stakingRatio: 15.2,
        burnRate: 2.1,
        activeAddresses: 645000,
        transactionCount: 1200000,
      },
    },
  }

  const data = marketData[coin as keyof typeof marketData] || marketData.ETH

  const getSentimentColor = (value: number) => {
    if (value >= 70) return "text-green-400"
    if (value >= 40) return "text-yellow-400"
    return "text-red-400"
  }

  const getSentimentBg = (value: number) => {
    if (value >= 70) return "bg-green-500/20 border-green-500/30"
    if (value >= 40) return "bg-yellow-500/20 border-yellow-500/30"
    return "bg-red-500/20 border-red-500/30"
  }

  return (
    <div className="space-y-6">
      {/* Market Sentiment Overview */}
      <Card className="bg-dark-navy/50 border-blue-500/20">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <Activity className="w-5 h-5 mr-2 text-purple-500" />
            Market Sentiment Analysis
          </CardTitle>
          <CardDescription className="text-slate-300">Real-time sentiment indicators for {coin}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-slate-300 text-sm">Fear & Greed</span>
                <span className={`font-semibold ${getSentimentColor(data.fearGreedIndex)}`}>{data.fearGreedIndex}</span>
              </div>
              <Progress value={data.fearGreedIndex} className="h-2" />
              <span className="text-xs text-slate-300">
                {data.fearGreedIndex >= 70 ? "Extreme Greed" : data.fearGreedIndex >= 40 ? "Neutral" : "Fear"}
              </span>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-slate-300 text-sm">Social Sentiment</span>
                <span className={`font-semibold ${getSentimentColor(data.socialSentiment)}`}>
                  {data.socialSentiment}%
                </span>
              </div>
              <Progress value={data.socialSentiment} className="h-2" />
              <span className="text-xs text-slate-300">Positive mentions trending</span>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-slate-300 text-sm">Whale Activity</span>
                <span className={`font-semibold ${getSentimentColor(data.whaleActivity)}`}>{data.whaleActivity}%</span>
              </div>
              <Progress value={data.whaleActivity} className="h-2" />
              <span className="text-xs text-slate-300">Large wallet accumulation</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Network Metrics */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card className="bg-dark-navy/50 border-blue-500/20">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <Globe className="w-5 h-5 mr-2 text-cyan-400" />
              Network Health
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-slate-300">Network Activity</span>
              <div className="flex items-center">
                <Progress value={data.networkActivity} className="w-20 h-2 mr-2" />
                <span className="text-purple-500 font-semibold">{data.networkActivity}%</span>
              </div>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-slate-300">Developer Activity</span>
              <div className="flex items-center">
                <Progress value={data.developerActivity} className="w-20 h-2 mr-2" />
                <span className="text-cyan-400 font-semibold">{data.developerActivity}%</span>
              </div>
            </div>

            <div className="pt-2 border-t border-blue-500/20 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-300">Active Addresses</span>
                <span className="text-white">{data.keyMetrics.activeAddresses.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-300">Daily Transactions</span>
                <span className="text-white">{(data.keyMetrics.transactionCount / 1000).toFixed(0)}K</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-300">Staking Ratio</span>
                <span className="text-purple-500">{data.keyMetrics.stakingRatio}%</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-dark-navy/50 border-blue-500/20">
          <CardHeader>
            <CardTitle className="text-white flex items-center">
              <Zap className="w-5 h-5 mr-2 text-blue-500" />
              Recent News Impact
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {data.news.map((item, index) => (
              <div key={index} className="flex items-start space-x-3 p-2 bg-dark-navyer/30 rounded">
                <div
                  className={`w-2 h-2 rounded-full mt-2 ${
                    item.sentiment === "positive"
                      ? "bg-green-400"
                      : item.sentiment === "negative"
                        ? "bg-red-400"
                        : "bg-yellow-400"
                  }`}
                />
                <div className="flex-1">
                  <p className="text-white text-sm font-medium">{item.title}</p>
                  <div className="flex items-center space-x-2 mt-1">
                    <Badge
                      className={`text-xs ${
                        item.sentiment === "positive"
                          ? "bg-green-500/20 text-green-400 border-green-500/30"
                          : item.sentiment === "negative"
                            ? "bg-red-500/20 text-red-400 border-red-500/30"
                            : "bg-yellow-500/20 text-yellow-400 border-yellow-500/30"
                      }`}
                    >
                      {item.sentiment}
                    </Badge>
                    <Badge className="text-xs bg-blue-500/20 text-blue-500 border-blue-500/30">
                      {item.impact} impact
                    </Badge>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Institutional Flow */}
      <Card className="bg-dark-navy/50 border-blue-500/20">
        <CardHeader>
          <CardTitle className="text-white flex items-center">
            <Users className="w-5 h-5 mr-2 text-purple-500" />
            Institutional Activity
          </CardTitle>
          <CardDescription className="text-slate-300">
            Large-scale investment flows and institutional sentiment
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between mb-4">
            <span className="text-slate-300">Net Institutional Flow (7d)</span>
            <div className="flex items-center">
              {data.institutionalFlow > 0 ? (
                <TrendingUp className="w-4 h-4 text-green-400 mr-1" />
              ) : (
                <TrendingDown className="w-4 h-4 text-red-400 mr-1" />
              )}
              <span className={`font-semibold ${data.institutionalFlow > 0 ? "text-green-400" : "text-red-400"}`}>
                {data.institutionalFlow > 0 ? "+" : ""}
                {data.institutionalFlow}%
              </span>
            </div>
          </div>
          <div className="bg-dark-navyer/50 rounded-lg p-4">
            <p className="text-slate-300 text-sm leading-relaxed">
              Institutional investors show {data.institutionalFlow > 0 ? "accumulation" : "distribution"} patterns with{" "}
              {Math.abs(data.institutionalFlow)}% net flow over the past week. This indicates{" "}
              {data.institutionalFlow > 0 ? "growing confidence" : "cautious sentiment"}
              among large-scale investors.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
