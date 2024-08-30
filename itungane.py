import yfinance as yf
import pandas as pd
import numpy as np

# Fungsi untuk menghitung EMA
def calculate_ema(data, span):
    return data.ewm(span=span, adjust=False).mean()

# Fungsi untuk menghitung Bollinger Bands
def calculate_bollinger_bands(data, window, no_of_std):
    rolling_mean = data.rolling(window=window).mean()
    rolling_std = data.rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * no_of_std)
    lower_band = rolling_mean - (rolling_std * no_of_std)
    return upper_band, lower_band

# Fungsi untuk menghitung RSI
def calculate_rsi(data, window):
    delta = data.diff(1)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=window).mean()
    avg_loss = pd.Series(loss).rolling(window=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Fungsi untuk menghitung Fibonacci Retracement
def calculate_fibonacci_retracement(data):
    max_price = data.max()
    min_price = data.min()
    diff = max_price - min_price
    levels = {
        '0.236': max_price - 0.236 * diff,
        '0.382': max_price - 0.382 * diff,
        '0.500': max_price - 0.500 * diff,
        '0.618': max_price - 0.618 * diff,
        '0.786': max_price - 0.786 * diff
    }
    return levels

# Fungsi untuk menghitung kecepatan pergerakan harga
def calculate_price_movement_speed(data):
    recent_prices = data['Close'].tail(30)  # Menggunakan 30 hari terakhir sebagai sampel
    pct_changes = recent_prices.pct_change().dropna()
    avg_daily_change = pct_changes.mean()
    return avg_daily_change

# Fungsi untuk menghitung target harga berdasarkan analisis
def determine_target_price(signal, current_price, fib_levels=None):
    if signal == "Buy":
        return current_price * 1.05  # Target kenaikan 5%
    elif signal == "Sell":
        return current_price * 0.95  # Target penurunan 5%
    elif fib_levels and signal in fib_levels:
        return fib_levels[signal]
    else:
        return current_price

# Fungsi untuk menghitung berapa hari lagi kira-kira bisa untung
def estimate_days_to_profit(data, signal, fib_levels=None):
    current_price = data['Close'].iloc[-1]
    avg_daily_change = calculate_price_movement_speed(data)
    
    target_price = determine_target_price(signal, current_price, fib_levels)
    
    if avg_daily_change > 0:
        days_to_profit = int((target_price - current_price) / (avg_daily_change * current_price))
    else:
        days_to_profit = None
    
    return days_to_profit

# Fungsi untuk memberikan sinyal beli, jual, atau hold berdasarkan EMA
def analyze_ema(data):
    last_close = data['Close'].iloc[-1]
    last_ema6 = data['EMA6'].iloc[-1]
    last_ema26 = data['EMA26'].iloc[-1]
    
    signal = "Hold"
    overbought = False
    
    if last_ema6 > last_ema26:
        signal = "Buy"
        if (last_ema6 - last_ema26) / last_ema26 > 0.05:  # Misalnya, jika EMA 6 lebih dari 5% di atas EMA 26
            overbought = True
    elif last_ema6 < last_ema26:
        signal = "Sell"
    
    days_to_profit = estimate_days_to_profit(data, signal)
    
    return last_close, signal, last_ema6, last_ema26, overbought, days_to_profit

# Fungsi untuk memberikan sinyal beli, jual, atau hold berdasarkan RSI
def analyze_rsi(data):
    last_rsi = data['RSI'].iloc[-1]
    signal = "Hold"
    overbought = False
    
    if last_rsi < 30:
        signal = "Buy"
    elif last_rsi > 70:
        signal = "Sell"
        overbought = True
    
    days_to_profit = estimate_days_to_profit(data, signal)
    
    return last_rsi, signal, overbought, days_to_profit

# Fungsi untuk analisis Bollinger Bands
def analyze_bollinger_bands(data):
    last_close = data['Close'].iloc[-1]
    upper_band = data['Upper_Band'].iloc[-1]
    lower_band = data['Lower_Band'].iloc[-1]
    
    signal = "Hold"
    overbought = False
    
    if last_close > upper_band:
        signal = "Sell"
        overbought = True
    elif last_close < lower_band:
        signal = "Buy"
    
    days_to_profit = estimate_days_to_profit(data, signal)
    
    return signal, overbought, days_to_profit

# Fungsi untuk analisis Fibonacci Retracement
def analyze_fibonacci(data):
    last_close = data['Close'].iloc[-1]
    fib_levels = calculate_fibonacci_retracement(data['Close'])
    
    signal = "Hold"
    overbought = False
    
    if last_close > fib_levels['0.236']:
        signal = "Sell"
        overbought = True
    elif last_close < fib_levels['0.786']:
        signal = "Buy"
    
    days_to_profit = estimate_days_to_profit(data, signal, fib_levels)
    
    fib_analysis = {}
    for level, price in fib_levels.items():
        if last_close > price:
            fib_analysis[level] = "Above"
        elif last_close < price:
            fib_analysis[level] = "Below"
        else:
            fib_analysis[level] = "At"
    
    return signal, fib_analysis, overbought, days_to_profit

# Fungsi untuk mengevaluasi persentase kesesuaian sinyal
def evaluate_analysis(data, signals):
    results = {'Buy': 0, 'Sell': 0, 'Hold': 0}
    correct_signals = {'Buy': 0, 'Sell': 0, 'Hold': 0}
    
    for i in range(len(data) - 1):
        current_signal = signals['EMA']
        future_close = data['Close'].iloc[i+1]
        current_close = data['Close'].iloc[i]
        
        if current_signal == "Buy" and future_close > current_close:
            correct_signals['Buy'] += 1
        elif current_signal == "Sell" and future_close < current_close:
            correct_signals['Sell'] += 1
        elif current_signal == "Hold":
            correct_signals['Hold'] += 1
        
        results[current_signal] += 1
    
    accuracy = {signal: (correct_signals[signal] / results[signal] * 100 if results[signal] > 0 else 0) for signal in results}
    return accuracy

# Fungsi utama untuk mengelola input dan output
def analyze_stock(ticker):
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
    
    # Menampilkan hasil analisis
    print(f"Ticker: {ticker}")
    print(f"Harga saat ini: {last_close:.2f}")
    
    print(f"\nAnalisis EMA:")
    print(f" - Sinyal: {signal_ema}")
    print(f" - EMA 6: {ema6:.2f}, EMA 26: {ema26:.2f}")
    print(f" - Overbought: {'Yes' if overbought_ema else 'No'}")
    if days_to_profit_ema is not None:
        print(f" - Perkiraan hari untuk untung: {days_to_profit_ema} hari")
    
    print(f"\nAnalisis RSI:")
    print(f" - RSI: {rsi:.2f}")
    print(f" - Sinyal: {signal_rsi}")
    print(f" - Overbought: {'Yes' if overbought_rsi else 'No'}")
    if days_to_profit_rsi is not None:
        print(f" - Perkiraan hari untuk untung: {days_to_profit_rsi} hari")
    
    print(f"\nAnalisis Bollinger Bands:")
    print(f" - Sinyal: {signal_bollinger}")
    print(f" - Overbought: {'Yes' if overbought_bollinger else 'No'}")
    if days_to_profit_bollinger is not None:
        print(f" - Perkiraan hari untuk untung: {days_to_profit_bollinger} hari")
    
    print(f"\nAnalisis Fibonacci Retracement:")
    print(f" - Sinyal: {signal_fibonacci}")
    print(f" - Overbought: {'Yes' if overbought_fibonacci else 'No'}")
    if days_to_profit_fibonacci is not None:
        print(f" - Perkiraan hari untuk untung: {days_to_profit_fibonacci} hari")
    print(f" - Fibonacci Levels: ")
    for level, status in fib_analysis.items():
        print(f"   - Level {level}: {status}")

    # Menggabungkan sinyal untuk evaluasi
    signals = {
        'EMA': signal_ema,
        'RSI': signal_rsi,
        'Bollinger': signal_bollinger,
        'Fibonacci': signal_fibonacci
    }
    
    accuracy = evaluate_analysis(data, signals)
    
    # Menampilkan hasil evaluasi persentase kesesuaian sinyal
    print(f"\nEvaluasi Kesimpulan:")
    for method, percent in accuracy.items():
        print(f" - {method}: {percent:.2f}% Akurasi")

# Memasukkan kode saham
ticker = input("Masukkan kode perusahaan saham (misalnya 'AAPL' untuk Apple): ")
analyze_stock(ticker)
