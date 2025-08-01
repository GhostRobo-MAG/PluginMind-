"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip } from "@/components/ui/chart"
import { Area, AreaChart, ResponsiveContainer, XAxis, YAxis, Line, LineChart } from "recharts"
import { TrendingUp, TrendingDown } from "lucide-react"
import { Badge } from "@/components/ui/badge"

interface CryptoChartProps {
  coin: string
  timeframe: string
}

// Enhanced mock data generator with realistic ETH price movements
const generateMockData = (coin: string, timeframe: string) => {
  const coinData = {
    ETH: { basePrice: 2420, volatility: 0.08, trend: 0.02 },
    BTC: { basePrice: 45000, volatility: 0.06, trend: 0.015 },
    ADA: { basePrice: 0.45, volatility: 0.12, trend: 0.01 },
  }

  const config = coinData[coin as keyof typeof coinData] || coinData.ETH
  const days = timeframe.includes("d")
    ? Number.parseInt(timeframe)
    : timeframe.includes("m")
      ? Number.parseInt(timeframe) * 30
      : 7

  const data = []
  let currentPrice = config.basePrice

  // Generate realistic price movements with trend
  for (let i = 0; i < days * 24; i++) {
    // Hourly data points
    const trendFactor = config.trend * (i / (days * 24))
    const volatilityFactor = (Math.random() - 0.5) * config.volatility * 0.1
    const cyclicalFactor = Math.sin(i * 0.1) * 0.02 // Add some cyclical movement

    currentPrice = currentPrice * (1 + trendFactor + volatilityFactor + cyclicalFactor)

    // Only add data points for display (every 4 hours for 7 days = ~42 points)
    if (i % 4 === 0) {
      const date = new Date(Date.now() - (days * 24 - i) * 60 * 60 * 1000)
      data.push({
        date: date.toLocaleDateString("en-US", { month: "short", day: "numeric" }),
        time: date.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }),
        price: Math.round(currentPrice * 100) / 100,
        volume: Math.random() * 2000000000 + 500000000, // 0.5B to 2.5B volume
        marketCap: currentPrice * 120000000, // ~120M ETH supply
        change24h: (Math.random() - 0.5) * 10, // ±5% daily change
      })
    }
  }

  return data
}

// Add this after the existing data generation
const addTechnicalIndicators = (data: any[]) => {
  // Simple Moving Average (SMA)
  const smaWindow = 20
  return data.map((item, index) => {
    if (index >= smaWindow - 1) {
      const smaSum = data.slice(index - smaWindow + 1, index + 1).reduce((sum, d) => sum + d.price, 0)
      item.sma20 = Math.round((smaSum / smaWindow) * 100) / 100
    }

    // RSI calculation (simplified)
    if (index >= 14) {
      const gains = []
      const losses = []
      for (let i = index - 13; i <= index; i++) {
        const change = data[i].price - data[i - 1]?.price || 0
        if (change > 0) gains.push(change)
        else losses.push(Math.abs(change))
      }
      const avgGain = gains.reduce((a, b) => a + b, 0) / 14
      const avgLoss = losses.reduce((a, b) => a + b, 0) / 14
      const rs = avgGain / avgLoss
      item.rsi = Math.round((100 - 100 / (1 + rs)) * 100) / 100
    }

    return item
  })
}

const chartConfig = {
  price: {
    label: "Price",
    color: "hsl(var(--crypto-primary))",
  },
  volume: {
    label: "Volume",
    color: "hsl(var(--crypto-secondary))",
  },
}

export function CryptoChart({ coin, timeframe }: CryptoChartProps) {
  const data = addTechnicalIndicators(generateMockData(coin, timeframe))
  const currentPrice = data[data.length - 1]?.price || 0
  const previousPrice = data[data.length - 2]?.price || 0
  const priceChange = currentPrice - previousPrice
  const priceChangePercent = ((priceChange / previousPrice) * 100).toFixed(2)
  const isPositive = priceChange >= 0

  return (
    <div className="space-y-6">
      {/* Enhanced Price Chart with Technical Indicators */}
      <Card className="bg-crypto-dark/50 border-crypto-accent/20">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-white flex items-center text-xl">
                {coin} Price Chart
                <Badge className="ml-3 bg-crypto-primary/20 text-crypto-primary border-crypto-primary/30">
                  {timeframe}
                </Badge>
              </CardTitle>
              <div className="flex items-center space-x-4 mt-2">
                <Badge
                  className={`${isPositive ? "bg-green-500/20 text-green-400 border-green-500/30" : "bg-red-500/20 text-red-400 border-red-500/30"}`}
                >
                  {isPositive ? <TrendingUp className="w-3 h-3 mr-1" /> : <TrendingDown className="w-3 h-3 mr-1" />}
                  {priceChangePercent}%
                </Badge>
                <span className="text-crypto-light text-sm">
                  Vol: ${(data[data.length - 1]?.volume / 1000000000).toFixed(2)}B
                </span>
                <span className="text-crypto-light text-sm">
                  MCap: ${(data[data.length - 1]?.marketCap / 1000000000).toFixed(1)}B
                </span>
              </div>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-white">${currentPrice.toLocaleString()}</div>
              <div className={`text-lg ${isPositive ? "text-green-400" : "text-red-400"}`}>
                {isPositive ? "+" : ""}${priceChange.toFixed(2)}
              </div>
              <div className="text-sm text-crypto-light">
                24h Range: ${Math.min(...data.slice(-6).map((d) => d.price)).toFixed(0)} - $
                {Math.max(...data.slice(-6).map((d) => d.price)).toFixed(0)}
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <ChartContainer config={chartConfig}>
            <ResponsiveContainer width="100%" height={400}>
              <AreaChart data={data}>
                <defs>
                  <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--crypto-primary))" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="hsl(var(--crypto-primary))" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="date"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "hsl(var(--crypto-light))", fontSize: 12 }}
                />
                <YAxis
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "hsl(var(--crypto-light))", fontSize: 12 }}
                  tickFormatter={(value) => `$${value.toLocaleString()}`}
                  domain={["dataMin - 50", "dataMax + 50"]}
                />
                <ChartTooltip
                  content={({ active, payload, label }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload
                      return (
                        <div className="bg-crypto-darker border border-crypto-accent/20 rounded-lg p-3 shadow-lg">
                          <p className="text-white font-semibold">{label}</p>
                          <p className="text-crypto-primary">Price: ${data.price?.toLocaleString()}</p>
                          <p className="text-crypto-light text-sm">Volume: ${(data.volume / 1000000).toFixed(1)}M</p>
                          {data.sma20 && (
                            <p className="text-crypto-secondary text-sm">SMA20: ${data.sma20.toLocaleString()}</p>
                          )}
                          {data.rsi && <p className="text-crypto-accent text-sm">RSI: {data.rsi.toFixed(1)}</p>}
                        </div>
                      )
                    }
                    return null
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="price"
                  stroke="hsl(var(--crypto-primary))"
                  strokeWidth={3}
                  fill="url(#priceGradient)"
                />
                {/* Add SMA line if data exists */}
                <Line
                  type="monotone"
                  dataKey="sma20"
                  stroke="hsl(var(--crypto-secondary))"
                  strokeWidth={2}
                  dot={false}
                  strokeDasharray="5 5"
                />
              </AreaChart>
            </ResponsiveContainer>
          </ChartContainer>
        </CardContent>
      </Card>

      {/* Volume and RSI Charts */}
      <div className="grid lg:grid-cols-2 gap-6">
        <Card className="bg-crypto-dark/50 border-crypto-accent/20">
          <CardHeader>
            <CardTitle className="text-white">Trading Volume</CardTitle>
            <CardDescription className="text-crypto-light">
              {timeframe} volume analysis • Avg: $
              {(data.reduce((sum, d) => sum + d.volume, 0) / data.length / 1000000).toFixed(0)}M
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer config={chartConfig}>
              <ResponsiveContainer width="100%" height={250}>
                <AreaChart data={data}>
                  <defs>
                    <linearGradient id="volumeGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="hsl(var(--crypto-secondary))" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="hsl(var(--crypto-secondary))" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis
                    dataKey="date"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: "hsl(var(--crypto-light))", fontSize: 11 }}
                  />
                  <YAxis
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: "hsl(var(--crypto-light))", fontSize: 11 }}
                    tickFormatter={(value) => `${(value / 1000000).toFixed(0)}M`}
                  />
                  <ChartTooltip
                    content={({ active, payload, label }) => {
                      if (active && payload && payload.length) {
                        return (
                          <div className="bg-crypto-darker border border-crypto-accent/20 rounded-lg p-3">
                            <p className="text-white font-semibold">{label}</p>
                            <p className="text-crypto-secondary">
                              Volume: ${((payload[0].value as number) / 1000000).toFixed(1)}M
                            </p>
                          </div>
                        )
                      }
                      return null
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="volume"
                    stroke="hsl(var(--crypto-secondary))"
                    strokeWidth={2}
                    fill="url(#volumeGradient)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </ChartContainer>
          </CardContent>
        </Card>

        <Card className="bg-crypto-dark/50 border-crypto-accent/20">
          <CardHeader>
            <CardTitle className="text-white">RSI Indicator</CardTitle>
            <CardDescription className="text-crypto-light">
              Relative Strength Index • Current: {data[data.length - 1]?.rsi?.toFixed(1) || "N/A"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer config={chartConfig}>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={data.filter((d) => d.rsi)}>
                  <XAxis
                    dataKey="date"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: "hsl(var(--crypto-light))", fontSize: 11 }}
                  />
                  <YAxis
                    domain={[0, 100]}
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: "hsl(var(--crypto-light))", fontSize: 11 }}
                  />
                  <ChartTooltip
                    content={({ active, payload, label }) => {
                      if (active && payload && payload.length) {
                        const rsi = payload[0].value as number
                        const condition = rsi > 70 ? "Overbought" : rsi < 30 ? "Oversold" : "Neutral"
                        return (
                          <div className="bg-crypto-darker border border-crypto-accent/20 rounded-lg p-3">
                            <p className="text-white font-semibold">{label}</p>
                            <p className="text-crypto-accent">RSI: {rsi.toFixed(1)}</p>
                            <p className="text-crypto-light text-sm">{condition}</p>
                          </div>
                        )
                      }
                      return null
                    }}
                  />
                  {/* Overbought/Oversold lines */}
                  <Line y={70} stroke="hsl(var(--destructive))" strokeDasharray="3 3" />
                  <Line y={30} stroke="hsl(var(--destructive))" strokeDasharray="3 3" />
                  <Line type="monotone" dataKey="rsi" stroke="hsl(var(--crypto-accent))" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </ChartContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
