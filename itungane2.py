import yfinance as yf
import pandas as pd

# Fungsi utama untuk mengelola input dan output untuk beberapa saham
def analyze_multiple_stocks(tickers):
    results = []

    for ticker in tickers:
        stock = yf.Ticker(ticker)
        data = stock.history(period="1y")

        # Menghitung indikator
        data['EMA6'] = calculate_ema(data['Close'], 6)
        data['EMA26'] = calculate_ema(data['Close'], 26)
        data['Upper_Band'], data['Lower_Band'] = calculate_bollinger_bands(data['Close'], 20, 2)
        data['RSI'] = calculate_rsi(data['Close'], 14)

        # Analisis berdasarkan EMA
        last_close, signal_ema, ema6, ema26, overbought_ema, days_to_profit_ema = analyze_ema(data)

        # Analisis berdasarkan RSI
        rsi, signal_rsi, overbought_rsi, days_to_profit_rsi = analyze_rsi(data)

        # Analisis berdasarkan Bollinger Bands
        signal_bollinger, overbought_bollinger, days_to_profit_bollinger = analyze_bollinger_bands(data)

        # Analisis berdasarkan Fibonacci Retracement
        signal_fibonacci, fib_analysis, overbought_fibonacci, days_to_profit_fibonacci = analyze_fibonacci(data)

        # Menyimpan hasil analisis
        results.append({
            'ticker': ticker,
            'last_close': last_close,
            'signal_ema': signal_ema,
            'signal_rsi': signal_rsi,
            'signal_bollinger': signal_bollinger,
            'signal_fibonacci': signal_fibonacci,
            'days_to_profit_ema': days_to_profit_ema,
            'days_to_profit_rsi': days_to_profit_rsi,
            'days_to_profit_bollinger': days_to_profit_bollinger,
            'days_to_profit_fibonacci': days_to_profit_fibonacci
        })

    # Seleksi saham terbaik berdasarkan sinyal beli dan potensi keuntungan
    potential_buys = [res for res in results if res['signal_ema'] == 'Buy' or res['signal_rsi'] == 'Buy' or res['signal_bollinger'] == 'Buy' or res['signal_fibonacci'] == 'Buy']
    sorted_buys = sorted(potential_buys, key=lambda x: min(filter(None, [x['days_to_profit_ema'], x['days_to_profit_rsi'], x['days_to_profit_bollinger'], x['days_to_profit_fibonacci']])))
    top_picks = sorted_buys[:2]

    # Menampilkan hasil analisis untuk dua saham teratas
    for pick in top_picks:
        print(f"Ticker: {pick['ticker']}")
        print(f"Harga saat ini: {pick['last_close']:.2f}")
        print(f"Sinyal EMA: {pick['signal_ema']}, Sinyal RSI: {pick['signal_rsi']}, Sinyal Bollinger: {pick['signal_bollinger']}, Sinyal Fibonacci: {pick['signal_fibonacci']}")
        print(f"Perkiraan hari untuk untung (berdasarkan EMA/RSI/Bollinger/Fibonacci): {min(filter(None, [pick['days_to_profit_ema'], pick['days_to_profit_rsi'], pick['days_to_profit_bollinger'], pick['days_to_profit_fibonacci']]))} hari")
        print("-" * 40)

# Misalnya, daftar ticker saham yang ingin dianalisis
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']  # Bisa disesuaikan
analyze_multiple_stocks(tickers)