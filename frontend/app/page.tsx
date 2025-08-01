import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ArrowRight, Brain, TrendingUp, Zap, BarChart3, Shield, Sparkles } from "lucide-react"

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-crypto-dark via-crypto-darker to-black">
      {/* Header */}
      <header className="border-b border-crypto-accent/20 bg-crypto-dark/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-crypto-primary to-crypto-secondary rounded-lg flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-white">CoinGrok</span>
          </div>
          <nav className="hidden md:flex items-center space-x-6">
            <Link href="#features" className="text-crypto-light hover:text-crypto-primary transition-colors">
              Features
            </Link>
            <Link href="#how-it-works" className="text-crypto-light hover:text-crypto-primary transition-colors">
              How it Works
            </Link>
            <Button
              asChild
              variant="outline"
              className="border-crypto-primary text-crypto-primary hover:bg-crypto-primary hover:text-white bg-transparent"
            >
              <Link href="/analyze">Try Now</Link>
            </Button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto text-center">
          <Badge className="mb-6 bg-crypto-primary/20 text-crypto-primary border-crypto-primary/30">
            <Sparkles className="w-4 h-4 mr-1" />
            AI-Powered Crypto Analysis
          </Badge>
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
            Unlock Crypto Insights with{" "}
            <span className="bg-gradient-to-r from-crypto-primary to-crypto-secondary bg-clip-text text-transparent">
              AI Intelligence
            </span>
          </h1>
          <p className="text-xl text-crypto-light mb-8 max-w-3xl mx-auto leading-relaxed">
            CoinGrok transforms your simple crypto questions into deep, actionable insights using our 4-D Prompt Engine
            powered by Grok xAI and OpenAI. Just ask naturally, and get professional-grade analysis.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button
              asChild
              size="lg"
              className="bg-gradient-to-r from-crypto-primary to-crypto-secondary hover:from-crypto-primary/90 hover:to-crypto-secondary/90 text-white px-8 py-3 text-lg"
            >
              <Link href="/analyze">
                Start Analysis <ArrowRight className="ml-2 w-5 h-5" />
              </Link>
            </Button>
            <Button
              variant="outline"
              size="lg"
              className="border-crypto-accent text-crypto-light hover:bg-crypto-accent/10 px-8 py-3 text-lg bg-transparent"
            >
              Watch Demo
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 bg-crypto-darker/50">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Powerful Features</h2>
            <p className="text-crypto-light text-lg max-w-2xl mx-auto">
              Everything you need to make informed crypto investment decisions
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="bg-crypto-dark/50 border-crypto-accent/20 hover:border-crypto-primary/50 transition-all duration-300">
              <CardHeader>
                <Brain className="w-12 h-12 text-crypto-primary mb-4" />
                <CardTitle className="text-white">4-D Prompt Engine</CardTitle>
                <CardDescription className="text-crypto-light">
                  Deconstruct → Diagnose → Develop → Deliver. Our AI transforms simple queries into comprehensive
                  analysis.
                </CardDescription>
              </CardHeader>
            </Card>
            <Card className="bg-crypto-dark/50 border-crypto-accent/20 hover:border-crypto-primary/50 transition-all duration-300">
              <CardHeader>
                <TrendingUp className="w-12 h-12 text-crypto-secondary mb-4" />
                <CardTitle className="text-white">Real-time Data</CardTitle>
                <CardDescription className="text-crypto-light">
                  Live crypto prices, market trends, and historical data integrated seamlessly into your analysis.
                </CardDescription>
              </CardHeader>
            </Card>
            <Card className="bg-crypto-dark/50 border-crypto-accent/20 hover:border-crypto-primary/50 transition-all duration-300">
              <CardHeader>
                <BarChart3 className="w-12 h-12 text-crypto-accent mb-4" />
                <CardTitle className="text-white">Interactive Charts</CardTitle>
                <CardDescription className="text-crypto-light">
                  Beautiful, interactive charts that visualize price movements, trends, and technical indicators.
                </CardDescription>
              </CardHeader>
            </Card>
            <Card className="bg-crypto-dark/50 border-crypto-accent/20 hover:border-crypto-primary/50 transition-all duration-300">
              <CardHeader>
                <Zap className="w-12 h-12 text-crypto-primary mb-4" />
                <CardTitle className="text-white">Natural Language</CardTitle>
                <CardDescription className="text-crypto-light">
                  Just ask "Analyze ETH in 7d with $300" and get instant, comprehensive insights.
                </CardDescription>
              </CardHeader>
            </Card>
            <Card className="bg-crypto-dark/50 border-crypto-accent/20 hover:border-crypto-primary/50 transition-all duration-300">
              <CardHeader>
                <Shield className="w-12 h-12 text-crypto-secondary mb-4" />
                <CardTitle className="text-white">Risk Assessment</CardTitle>
                <CardDescription className="text-crypto-light">
                  Advanced risk analysis and portfolio recommendations based on your investment goals.
                </CardDescription>
              </CardHeader>
            </Card>
            <Card className="bg-crypto-dark/50 border-crypto-accent/20 hover:border-crypto-primary/50 transition-all duration-300">
              <CardHeader>
                <Sparkles className="w-12 h-12 text-crypto-accent mb-4" />
                <CardTitle className="text-white">AI-Powered Insights</CardTitle>
                <CardDescription className="text-crypto-light">
                  Leverage the power of Grok xAI and OpenAI for cutting-edge crypto market analysis.
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* How it Works Section */}
      <section id="how-it-works" className="py-20 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">How CoinGrok Works</h2>
            <p className="text-crypto-light text-lg max-w-2xl mx-auto">
              Our 4-D Prompt Engine transforms your questions into actionable insights
            </p>
          </div>
          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-r from-crypto-primary to-crypto-secondary rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-xl">1</span>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Deconstruct</h3>
              <p className="text-crypto-light">Break down your query into key components and parameters</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-r from-crypto-secondary to-crypto-accent rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-xl">2</span>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Diagnose</h3>
              <p className="text-crypto-light">Analyze market conditions and identify key factors</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-r from-crypto-accent to-crypto-primary rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-xl">3</span>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Develop</h3>
              <p className="text-crypto-light">Generate comprehensive analysis and recommendations</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-r from-crypto-primary to-crypto-secondary rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-xl">4</span>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Deliver</h3>
              <p className="text-crypto-light">Present insights with charts and actionable advice</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-to-r from-crypto-primary/20 to-crypto-secondary/20">
        <div className="container mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-4">Ready to Unlock Crypto Insights?</h2>
          <p className="text-crypto-light text-lg mb-8 max-w-2xl mx-auto">
            Join thousands of traders who trust CoinGrok for their crypto analysis needs
          </p>
          <Button
            asChild
            size="lg"
            className="bg-gradient-to-r from-crypto-primary to-crypto-secondary hover:from-crypto-primary/90 hover:to-crypto-secondary/90 text-white px-8 py-3 text-lg"
          >
            <Link href="/analyze">
              Start Your Analysis <ArrowRight className="ml-2 w-5 h-5" />
            </Link>
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-crypto-accent/20 bg-crypto-darker py-12 px-4">
        <div className="container mx-auto text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <div className="w-8 h-8 bg-gradient-to-r from-crypto-primary to-crypto-secondary rounded-lg flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-white">CoinGrok</span>
          </div>
          <p className="text-crypto-light">© 2024 CoinGrok. AI-powered crypto analysis for the modern trader.</p>
        </div>
      </footer>
    </div>
  )
}
