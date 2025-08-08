import type { Metadata } from 'next'
import { GeistSans } from 'geist/font/sans'
import { GeistMono } from 'geist/font/mono'
import './globals.css'

export const metadata: Metadata = {
  title: 'CoinGrok - AI Crypto Analysis',
  description: 'CoinGrok transforms your simple crypto questions into deep, actionable insights using our 4-D Prompt Engine powered by Grok xAI and OpenAI.',
  generator: 'CoinGrok',
  keywords: 'crypto, cryptocurrency, AI, analysis, Bitcoin, Ethereum, trading, investment',
  authors: [{ name: 'CoinGrok' }],
  icons: {
    icon: '/logos/coingrok-logo-icon.png',
    shortcut: '/logos/coingrok-logo-icon.png',
    apple: '/logos/coingrok-logo-icon.png',
  },
  manifest: '/manifest.json',
  openGraph: {
    title: 'CoinGrok - AI Crypto Analysis',
    description: 'Transform your crypto questions into actionable insights with AI-powered analysis',
    url: 'https://coingrok.com',
    siteName: 'CoinGrok',
    images: [
      {
        url: '/logos/coingrok-logo-with-text.png',
        width: 1200,
        height: 630,
        alt: 'CoinGrok - AI Crypto Analysis',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'CoinGrok - AI Crypto Analysis',
    description: 'Transform your crypto questions into actionable insights with AI-powered analysis',
    images: ['/logos/coingrok-logo-with-text.png'],
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <head>
        <style>{`
            html {
              font-family: ${GeistSans.style.fontFamily};
              --font-sans: ${GeistSans.variable};
              --font-mono: ${GeistMono.variable};
            }
        `}</style>
      </head>
      <body>{children}</body>
    </html>
  )
}
