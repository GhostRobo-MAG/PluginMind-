# --- 4-D Engine Simulation CLI ---  Proof of Concept
# This CLI simulates the CoinGrok input processing pipeline.
# It currently runs locally. Later this logic will move into a FastAPI backend.

def get_input_method():
    print("\n[Deconstruct] Select input mode:")
    print("1 - Full sentence (e.g., 'Analyze ETH in 7d with $300')")
    print("2 - Form-style (enter each field manually)")
    choice = input("Enter 1 or 2: ").strip()
    return choice

def get_sentence_input():
    print("[Deconstruct] Waiting for full-sentence query...")
    user_input = input("Enter your query (e.g., Analyze ETH in 7d with $300): ").strip()
    if user_input == "":
        print("[Diagnose] Empty input. Using default: Analyze ETH in 7d with $300")
        user_input = "Analyze ETH in 7d with $300"
    return user_input

def get_form_input():
    print("[Deconstruct] Collecting fields manually...")
    coin = input("Enter coin symbol (e.g., ETH): ").upper().strip() or "ETH"
    timeframe = input("Enter timeframe (e.g., 7d or 48h): ").strip() or "7d"
    budget = input("Enter budget (e.g., 300): ").strip() or "300"
    return f"Analyze {coin} in {timeframe} with ${budget}"


def deconstruct(user_input):
    print("[Deconstruct] Parsing input...")
    words = user_input.lower().split()

    try:
        coin = words[1].upper()
        timeframe = words[3]
        budget = words[5].replace('$', '')
    except IndexError:
        print("[Diagnose] Could not parse input, using defaults.")
        coin, timeframe, budget = "ETH", "7d", "300"

    return {
        "coin": coin,
        "timeframe": timeframe,
        "budget": budget
    }

def diagnose(parsed_input):
    print("[Diagnose] Validating parsed input...")
    # For now, just returns parsed input
    return parsed_input

def develop(final_input):
    print("[Develop] Building final prompt...")
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
    print("[Deploy] Delivering final prompt...\n")
    print("📤 Final Prompt:\n")
    print(prompt)

if __name__ == "__main__":
    mode = get_input_method()

    if mode == "1":
        user_input = get_sentence_input()
    elif mode == "2":
        user_input = get_form_input()
    else:
        print("[Diagnose] Invalid option. Defaulting to form-style input.")
        user_input = get_form_input()

    parsed = deconstruct(user_input)
    checked = diagnose(parsed)
    prompt = develop(checked)
    deliver(prompt)
