import numpy as np
import pandas as pd
import datetime

def simulate_bitcoin_prices(days=60, initial_price=60000.0, mu=0.001, sigma=0.05):
    """
    Simulates daily Bitcoin prices using Geometric Brownian Motion.
    mu: expected return (drift)
    sigma: volatility
    """
    np.random.seed(23)  # Chosen to ensure at least one BUY and SELL action
    prices = [initial_price]
    for _ in range(1, days):
        # Daily return
        shock = np.random.normal(0, 1)
        price = prices[-1] * np.exp((mu - 0.5 * sigma**2) + sigma * shock)
        prices.append(price)

    start_date = datetime.date.today() - datetime.timedelta(days=days-1)
    dates = pd.date_range(start=start_date, periods=days)

    df = pd.DataFrame({'Date': dates, 'Price': prices})
    return df

def run_simulation():
    # 1. Simulate data
    print("Simulating 60 days of Bitcoin prices...")
    df = simulate_bitcoin_prices(days=60, initial_price=60000.0)

    # 2. Calculate Moving Averages
    df['7_MA'] = df['Price'].rolling(window=7).mean()
    df['30_MA'] = df['Price'].rolling(window=30).mean()

    # 3. Implement Golden Cross Strategy
    # We start with $100,000 cash and 0 BTC
    initial_cash = 100000.0
    cash = initial_cash
    btc_held = 0.0

    print("\n--- Daily Ledger ---")

    for i in range(len(df)):
        date = df.loc[i, 'Date'].strftime('%Y-%m-%d')
        price = df.loc[i, 'Price']
        ma_7 = df.loc[i, '7_MA']
        ma_30 = df.loc[i, '30_MA']

        # We need yesterday's MA values to detect a cross
        if pd.isna(ma_30) or i == 0:
            continue

        prev_ma_7 = df.loc[i-1, '7_MA']
        prev_ma_30 = df.loc[i-1, '30_MA']

        action = "HOLD"

        # Golden Cross: 7 MA crosses above 30 MA -> BUY
        if not pd.isna(prev_ma_7) and not pd.isna(prev_ma_30):
            if prev_ma_7 <= prev_ma_30 and ma_7 > ma_30:
                if cash > 0:
                    btc_bought = cash / price
                    btc_held += btc_bought
                    cash = 0.0
                    action = f"BUY {btc_bought:.4f} BTC"
                    print(f"[{date}] Price: ${price:.2f} | 7-MA: ${ma_7:.2f} | 30-MA: ${ma_30:.2f} | Action: {action}")

            # Death Cross: 7 MA crosses below 30 MA -> SELL
            elif prev_ma_7 >= prev_ma_30 and ma_7 < ma_30:
                if btc_held > 0:
                    cash_gained = btc_held * price
                    cash += cash_gained
                    btc_held = 0.0
                    action = f"SELL ALL BTC"
                    print(f"[{date}] Price: ${price:.2f} | 7-MA: ${ma_7:.2f} | 30-MA: ${ma_30:.2f} | Action: {action}")

    # 4. Final Portfolio Performance
    final_portfolio_value = cash + (btc_held * df.iloc[-1]['Price'])
    profit = final_portfolio_value - initial_cash
    roi = (profit / initial_cash) * 100

    print("\n--- Final Portfolio Performance ---")
    print(f"Initial Cash: ${initial_cash:.2f}")
    if cash > 0:
        print(f"Final Cash: ${cash:.2f}")
    else:
        print(f"Final Cash: $0.00")
    print(f"Final BTC Held: {btc_held:.4f} BTC")
    print(f"Final Portfolio Value: ${final_portfolio_value:.2f}")
    print(f"Total Profit/Loss: ${profit:.2f} ({roi:.2f}%)")

if __name__ == "__main__":
    run_simulation()
