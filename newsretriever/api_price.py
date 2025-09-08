import yfinance as yf


def get_wti_price():
    try:
        ticker = yf.Ticker("CL=F")  # WTI Crude Oil futures
        data = ticker.history(period="1d", interval="1m")
        current_price = data['Close'].iloc[-1]
        return str(round(float(current_price),2))
    except Exception as e:
        print(f"Errore durante la chiamata all'api yahoo per prezzo corrente: {e}")
    return "not possibile to get the current price"

