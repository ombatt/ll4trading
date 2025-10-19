import yfinance as yf
from isoduration.parser.util import is_week
from tinydb import TinyDB
from yfinance.scrapers.quote import Quote

from business.database.database_constants import DB_FILE_PATH, DB_FILE_PATH_2


def get_wti_price():
    try:
        ticker = yf.Ticker("CL=F")  # WTI Crude Oil futures
        data = ticker.history(period="1d", interval="1m")
        # print(data.__str__())
        current_price = data['Close'].iloc[-1]
        print(f'current price: {str(round(float(current_price),2))}')
        return str(round(float(current_price),2))
    except Exception as e:
        print(f"Errore durante la chiamata all'api yahoo per prezzo corrente: {e}")
    return "not possibile to get the current price"

def write_hist_data():
    try:
        ticker = yf.Ticker("CL=F")  # WTI Crude Oil futures
        data = ticker.history(period="2d", interval="1h")
        list_q = []
        for d in data.iloc:
            timestamp = d.name
            dt = timestamp.date()
            is_week_end = dt.weekday() >= 5
            print("Data:", dt)
            print("Ora:", timestamp.time())
            print("is_week_end:", is_week_end)
            print(d)
            q_dict = {
                "open": d['Open'].item(),
                "high": d['High'].item(),
                "low": d['Low'].item(),
                "close": d['Close'].item(),
                "volume": d['Volume'].item(),
                "date": dt.strftime("%Y-%m-%d"),
                "time": timestamp.strftime("%H:%M:%S")
            }
            if not is_week_end:
                list_q.append(q_dict)
        write_histdata(list_q)
    except Exception as e:
        print(f"Errore durante la chiamata all'api yahoo per prezzo corrente: {e}")
    return "not possibile to get the current price"


def write_histdata(list_q):
    try:
        db = TinyDB(DB_FILE_PATH_2)
        news_db = db.table('historical_data')
        for hdata in list_q:
            news_db.insert(hdata)
    except Exception as e:
        print(f"Errore durante la scrittura a db: {e}")