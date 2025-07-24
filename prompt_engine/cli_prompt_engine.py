def deconstruct(user_input):
    # Extract coin, timeframe, budget
    return {...}

def diagnose(parsed_input):
    # Validate + fill missing data
    return {...}

def develop(final_input):
    # Create mock prompt string
    return f"""You are a crypto AI...
    Coin: {final_input['coin']}
    Timeframe: {final_input['timeframe']}
    Budget: ${final_input['budget']}
    """

def deliver(prompt):
    print("\n📤 Final Prompt:\n")
    print(prompt)

if __name__ == "__main__":
    user_input = input("Enter your query (e.g., Analyze ETH in 7d with $300): ")
    parsed = deconstruct(user_input)
    checked = diagnose(parsed)
    prompt = develop(checked)
    deliver(prompt)
