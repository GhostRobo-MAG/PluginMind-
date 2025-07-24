def get_input_method():
    print("Select input mode:")
    print("1 - Full sentence (e.g., 'Analyze ETH in 7d with $300')")
    print("2 - Form-style (enter each field manually)")
    choice = input("Enter 1 or 2: ")
    return choice

def get_sentence_input():
    return input("Enter your query (e.g., Analyze ETH in 7d with $300): ")

def get_form_input():
    coin = input("Enter coin symbol (e.g., ETH): ").upper()
    timeframe = input("Enter timeframe (e.g., 7d or 48h): ")
    budget = input("Enter budget (e.g., 300): ")
    return f"Analyze {coin} in {timeframe} with ${budget}"

#  FUTURE BACKEND IMPLEMENTATION PLACEHOLDER
# This script currently simulates frontend input processing locally.
# In the future, this logic will be wrapped inside a FastAPI endpoint:
#    POST /generate-prompt
# The backend will:
#   - Accept JSON payload with fields: coin, timeframe, budget
#   - Call the 4-D engine functions
#   - Return the generated prompt in JSON response

def deconstruct(user_input):
    words = user_input.lower().split()

    try:
        coin = words[1].upper()                    # e.g., DOGE
        timeframe = words[3]                       # e.g., 48h
        budget = words[5].replace('$', '')         # e.g., 500
    except IndexError:
        coin = "ETH"
        timeframe = "7d"
        budget = "300"

    return {
        "coin": coin,
        "timeframe": timeframe,
        "budget": budget
    }

def diagnose(parsed_input):
    # Mock validator: just returns as-is
    return parsed_input

def develop(final_input):
    return f"""You are an AI crypto assistant. Analyze {final_input['coin']} over the last {final_input['timeframe']} with an investment budget of ${final_input['budget']}.

Use Grok tools to return:
1. Sentiment from X (Twitter)
2. News overview from CoinGecko/CMC
3. Market snapshot (price, volume, volatility)
4. Buy/Sell Recommendation
5. Risk Score (1–10)

Disclaimer: This is not financial advice.
"""

def deliver(prompt):
    print("\n📤 Final Prompt:\n")
    print(prompt)

if __name__ == "__main__":
    mode = get_input_method()
    
    if mode == "1":
        user_input = get_sentence_input()
    elif mode == "2":
        user_input = get_form_input()
    else:
        print("Invalid option. Defaulting to form-style input.")
        user_input = get_form_input()

    parsed = deconstruct(user_input)
    checked = diagnose(parsed)
    prompt = develop(checked)
    deliver(prompt)
