def generate_prompt(coin, timeframe, budget):
    return f"""
You are an AI crypto assistant. Analyze {coin} over the last {timeframe} with an investment budget of ${budget}.

Use Grok tools to return:
1. Sentiment from X (Twitter)
2. News overview from CoinGecko/CMC
3. Market snapshot (price, volume, volatility)
4. Buy/Sell Recommendation
5. Risk Score (1–10)

Disclaimer: This is not financial advice.
"""

if __name__ == "__main__":
    coin = input("Enter coin name: ")
    timeframe = input("Enter timeframe (48h or 7d): ")
    budget = input("Enter budget ($): ")
    print(generate_prompt(coin, timeframe, budget))
