import math
from datetime import datetime, timedelta, date

import pandas as pd
import yfinance as yf
from isoduration.parser.util import is_week
from tinydb import TinyDB, Query
from yfinance.scrapers.quote import Quote

from business.database.database_constants import DB_FILE_PATH, DB_FILE_PATH_2
from business.database.hist_data_query import read_last_days_hist_data


def get_wti_price() -> str:
    """
    ritorno il prezzo del wti aggiornato
    :return:
    """
    try:
        ticker = yf.Ticker("CL=F")  # WTI Crude Oil futures
        data = ticker.history(period="1d", interval="1h")
        # print(data.__str__())
        current_price = data['Close'].iloc[-1]
        print(f'current price: {str(round(float(current_price),2))}')
        return str(round(float(current_price),2))
    except Exception as e:
        print(f"Errore durante la chiamata all'api yahoo per prezzo corrente: {e}")
    return "not possibile to get the current price"


def write_hist_data():
    """
    recupero i dati di chiusura storici dell'indice
    :return:
    """
    # verifico se oggi ho popolato il database
    docs: list = read_last_days_hist_data("00:00:00", 0)

    if len(docs) == 0:
        try:
            ticker = yf.Ticker("CL=F")  # WTI Crude Oil futures
            data = ticker.history(period="1d", interval="1h")
            list_q = []
            for d in data.iloc:
                timestamp = d.name
                dt = timestamp.date()
                is_week_end = dt.weekday() >= 5
                print("recupero dati storici, timestamp:", timestamp)
                '''
                print("Data:", dt)
                print("Ora:", timestamp.time())
                print("is_week_end:", is_week_end)
                print(d)
                '''
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
    """
    persisto i dati storici a database
    :param list_q:
    :return:
    """

    try:
        db = TinyDB(DB_FILE_PATH_2)
        news_db = db.table('historical_data')
        # rimuovo tutti i dati di storico
        news_db.truncate()
        # faccio insert di tutti i documenti
        for hdata in list_q:
            news_db.insert(hdata)

    except Exception as e:
        print(f"Errore durante la scrittura a db: {e}")


def get_volume_mean():
    """
    recupero i dati di chiusura storici dell'indice
    :return:
    """

    try:
        ticker = yf.Ticker("CL=F")  # WTI Crude Oil futures
        data = ticker.history(period="14d", interval="1h")
        # tolgo sabato e domenica
        # condizione_lavorativa = (data.index.dayofweek >= 0) & (data.index.dayofweek <= 4)
        # data_filtrato = data[condizione_lavorativa]


        # condizione esclusione oggi e data corrente
        # timestamp attuale consapevole del fuso orario UTC
        adesso_utc = pd.Timestamp.now(tz='Europe/Rome')
        data.index = data.index.tz_convert('Europe/Rome')
        #fuso orario di New York
        #new_york_tz = 'America/New_York'
        #DEST_TZ = 'Europe/Rome'
        #adesso_new_york = adesso_utc.tz_convert(new_york_tz)

        adesso_ora = adesso_utc.hour
        adesso_new_york_ora_fuso = False

        # creo le condizioni con data diversa da oggi e orario minore
        condizione_esclusione_oggi = data.index.date != adesso_utc.date()
        condizione_ora = data.index.hour <= adesso_ora
        #condizione_ora = data.index.hour
        condizione_finale = condizione_esclusione_oggi & condizione_ora
        data_filtrato_no_oggi = data[condizione_finale]

        '''for d in data.iloc:
            timestamp = d.name
            dt = timestamp.date()
            d['day'] = d['day'].astype(str)
            d['day'] = dt.strftime("YYYY-MM-DD")
            is_week_end = dt.weekday() >= 5'''
        # condizione inclusione oggi e ora corrente
        # oggi = pd.to_datetime(date.today())
        # condizione_inclusione_oggi = data.index.date == oggi.date()
        # condizione_finale = condizione_inclusione_oggi & condizione_ora
        # data_filtrato_oggi = data[condizione_inclusione_oggi]

        # calcolo la media del volume nella stessa fascia oraria nelle 2 settimana precedenti (oggi escluso)
        # vol_avg = data_filtrato_no_oggi["Volume"].sum() / data_filtrato_no_oggi.shape[0]
        # numero_righe = data_filtrato_no_oggi.shape[0]

        # aggrego i dati del dataframe per giorno e calcolo la media
        df = data_filtrato_no_oggi.resample('D').sum()
        vol_avg = df["Volume"].median()

        # rapporto i volumi orari attuali ai 5 minuti dell'ora corrente
        # vol_h = data_filtrato_oggi["Volume"].item()
        # vol_avg_today_h = get_vol_h_normalized(data_filtrato_oggi["Volume"].item())
        print("vol_avg: ", vol_avg)
        return vol_avg
    except Exception as e:
        print(f"Errore durante la chiamata all'api yahoo per prezzo corrente: {e}")
    return "not possibile to get the current price"


def get_vol_h_normalized(vol_avg: float):
    """
    metodo che rapporta la media dei volumi all'intervallo dei 5 minuti più prossimo (arrotondamento per eccesso)
    :param vol_avg:
    :param minute:
    :return:
    """
    minute = datetime.now().minute
    res: float = math.ceil(minute / 5)
    vol_rap: float = vol_avg / 12 * res
    return round(vol_rap, 2)