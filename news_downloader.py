import datetime
import json
from typing import Any
from zoneinfo import ZoneInfo

import pytz
import yfinance as yf
import pandas as pd
from selenium.webdriver.chrome.webdriver import WebDriver
from tinydb import TinyDB, Query
from tinydb.table import Document

from business.database.database_constants import DB_FILE_PATH
from business.database.dbmanager import write_news_list
from do.news import News
from llm.llm import get_geai
from scraper.investing_scraper import InvestingScraper
from scraper.investing_scraper_bulk import search_for_news_bulk, enrich_news_bulk
from utils.utils import get_driver

URL_STR_NEWS = "https://www.investing.com/commodities/crude-oil-news"
URL_STR_ANL = "https://www.investing.com/commodities/crude-oil-opinion"

def write_page_log(page: int, news: News):
    db = TinyDB("database/db_downloader.json")
    news_db = db.table('news_downloader_log')
    obj = {'page': page, 'news_link': news.link}
    news_db.insert(obj)

def write_news_list_bulk(news_list: list[News], db_file_path: str = None):
    try:
        db_file_path = DB_FILE_PATH if db_file_path is None else db_file_path
        query_news = Query()
        for news in news_list:
            db = TinyDB(db_file_path)
            news_db = db.table('news')
            if not news_db.get(query_news.link == news.link):
                news_db.insert(news.to_dict())
            else:
                print("scartata: ", news.link)
    except Exception as e:
        print(f"Errore durante la scrittura a db: {e}")

def get_max_page():
    # 🥇 Proprietà da massimizzare
    campo_cercato = 'page'

    # 1. Recupera tutti i documenti
    db = TinyDB("database/db_downloader.json")
    tutti_i_documenti = db.table('news_downloader_log').all()

    # 2. Usa max() per trovare il documento con il punteggio più alto
    # L'argomento 'key' dice a max() di confrontare i documenti in base al valore di 'punteggio'
    if tutti_i_documenti:
        documento_max = max(
            tutti_i_documenti,
            key=lambda doc: doc[campo_cercato]
        )
        return int(documento_max[campo_cercato])
    else:
        return 1

def get_oldest_news():
    # 🥇 Proprietà da massimizzare
    campo_cercato = 'date'

    # 1. Recupera tutti i documenti
    db = TinyDB("database/db_downloader.json")
    tutti_i_documenti = db.table('news').all()

    # 2. Usa max() per trovare il documento con il punteggio più alto
    # L'argomento 'key' dice a max() di confrontare i documenti in base al valore di 'punteggio'
    if tutti_i_documenti:
        documento_max = min(
            tutti_i_documenti,
            key=lambda doc: doc[campo_cercato]
        )
        print(documento_max[campo_cercato])
        return documento_max[campo_cercato]
    else:
        return "no data"

def download_news_bulk():
    r: int = get_max_page()
    f_r: int = r + 40

    for i in range(r,f_r):
        url = URL_STR_NEWS + "/" + str(i)
        print(f"scraping {url}")
        tmp_list: list[News] = search_for_news_bulk(url)
        tmp_list_enriched: list[News] = []
        for idx, news in enumerate(tmp_list):
            tmp_list_enriched.append(enrich_news_bulk(news))
            print(f"inserita: {i} - {idx}")
        write_news_list_bulk(tmp_list_enriched, "database/db_downloader.json")
        print(f"last news write: {tmp_list_enriched[len(tmp_list_enriched)-1].link} ##### at page {i}")
        write_page_log(i, tmp_list_enriched[len(tmp_list_enriched)-1])


def merge_tables():
    '''
    unisce due p più file tinydb in un unico file (nuovo)
    :return:
    '''

    # Definisci i file sorgente e il nuovo file di destinazione
    FILE_DESTINAZIONE = 'database/db_downloader_final.json'
    file_sorgenti = ['database/db_downloader.json', 'database/db_downloader_1.json']

    # 1. Apri il database di destinazione (se non esiste, viene creato vuoto)
    db_destinazione = TinyDB(FILE_DESTINAZIONE)
    print(f"Creato o aperto il database di destinazione: {FILE_DESTINAZIONE}")

    # 2. Itera su ciascun file sorgente
    for sorgente_path in file_sorgenti:
        print(f"\nElaborazione sorgente: {sorgente_path}")

        try:
            db_sorgente = TinyDB(sorgente_path)
        except Exception as e:
            print(f"⚠️ Errore nell'apertura del database sorgente {sorgente_path}: {e}")
            continue

        # Ottieni tutti i nomi delle tabelle presenti nel sorgente
        nomi_tabelle = db_sorgente.tables()

        # 3. Itera su ciascuna tabella
        for nome_tabella in nomi_tabelle:
            tabella_sorgente = db_sorgente.table(nome_tabella)
            tabella_destinazione = db_destinazione.table(nome_tabella)

            # Recupera tutti i documenti
            documenti = tabella_sorgente.all()

            if documenti:
                # 4. Inserisci i documenti nella tabella di destinazione
                tabella_destinazione.insert_multiple(documenti)
                print(f"   ✅ Copiati {len(documenti)} documenti nella tabella '{nome_tabella}'.")
            else:
                print(f"   Nessun documento nella tabella '{nome_tabella}'.")

    # Chiudi tutti i database
    db_destinazione.close()
    # I database sorgente vengono implicitamente chiusi qui

    print("\n---")
    print(f"Unione completata. I dati sono ora in {FILE_DESTINAZIONE}")

def get_distinct_dates():
    """
    Estrae l'insieme di tutte le date distinte nel formato YYYY-MM-DD
    dal campo 'date' dei documenti TinyDB.

    :param db: L'istanza di TinyDB.
    :return: Un set (insieme) di stringhe di date distinte.
    """

    # Insieme vuoto per memorizzare le date uniche (i set eliminano automaticamente i duplicati)
    distinct_dates = set()

    # Recupera tutti i documenti dal database
    # 1. Recupera tutti i documenti
    db = TinyDB("database/db_downloader.json")
    all_documents = db.table('news').all()

    for doc in all_documents:
        # 1. Recupera la stringa di data/ora
        date_time_str = doc.get("date")

        if date_time_str:
            try:
                # 2. Estrai solo la parte della data (i primi 10 caratteri)
                # "2025-10-03T16:44:02+00:00" -> "2025-10-03"
                date_only_str = date_time_str[:10]

                # 3. Aggiungi la stringa della data al set.
                # Se la data è già presente, il set la ignorerà (gestione dei duplicati).
                distinct_dates.add(date_only_str)
            except Exception as e:
                print(f"Errore nell'elaborazione del campo data '{date_time_str}': {e}")

    print(f"distinct dates: {distinct_dates}")
    return distinct_dates


def categorize_news_bulk():
    '''
    recupera le news nelle precedenti 24 ore rispetto a uno specifico timestamp, le completa con il riassunto
    delle news e il prezzo del WTI a fine giornata. Successivamente salva tutte le informazioni a db su tabella
    dedicata
    :return:
    '''
    date_l: set = get_distinct_dates()
    # le 8 e le 14 UTC sono il riferimento, sono relative all'orario di apertura delle borse europee e USA
    hour_dict = {1: 8, 2: 14}
    minute_dict = {1: 00, 2: 00}
    chiavi_da_mantenere = ['date', 'body', 'type']
    classified_documents: list[Any] = []
    for date in date_l:
        for range in (1,2):
            filtered_documents = []
            date_str: str = date
            date_format = "%Y-%m-%d"
            base_datetime = datetime.datetime.strptime(date_str, date_format)
            final_datetime = base_datetime.replace(
                hour=hour_dict[range],
                minute=minute_dict[range],
                second=0,
                microsecond=0,
                tzinfo=ZoneInfo("UTC")   # Imposta il fuso orario
            )

            start_time = final_datetime - datetime.timedelta(hours=24)

            # 3. Converti i limiti dell'intervallo in stringhe ISO 8601 per il confronto
            # Il fuso orario deve essere incluso per coerenza con il database.
            start_time_str = start_time.isoformat()
            end_time_str = final_datetime.isoformat()

            # 4. Filtra i documenti (TinyDB non supporta la query diretta su data/ora)
            db = TinyDB("database/db_downloader.json")
            all_documents = db.table('news').all()

            # Utilizziamo il confronto di stringhe che funziona grazie al formato ISO 8601
            # aggiungo le news relative al dato timestamp
            for doc in all_documents:
                doc_date_str = doc.get("date")
                if doc_date_str:
                    # Verifica se la data del documento è >= start_time E < end_time
                    # Usiamo '<' per escludere l'esatto momento 'end_time', creando un intervallo [start, end]
                    if start_time_str <= doc_date_str < end_time_str:
                        # estraggo solamente il body e la data della notizia
                        news_list_obj = {chiave: doc[chiave] for chiave in chiavi_da_mantenere}
                        filtered_documents.append(news_list_obj)


            # chiamo llm per fare il riassunto delle news
            s_content = {"type": "summary", "body": llm_summarize_news(filtered_documents)}
            filtered_documents.append(s_content)

            # ottengo il prezzo di riferimento del wti alle 8 e alle 14 UTC e il prezzo di chiusura
            price_open, price_close = get_wti_price_bulk(final_datetime)
            p_content_o = {"type": "price_open", "body": round(price_open, 2)}
            p_content_c = {"type": "price_close", "body": round(price_close, 2)}
            filtered_documents.append(p_content_o)
            filtered_documents.append(p_content_c)

            # creo il dict da salvare a db
            main_doc = {
                "timestamp": end_time_str,
                "data": filtered_documents,
            }

            # aggiungo i 2 nuovi item
            classified_documents.append(main_doc)

            # salvo il dataset
            save_dataset(classified_documents)

    return classified_documents


def get_wti_price_bulk(target_dt: datetime.datetime) -> tuple[float, float]:
    """
    Restituisce la riga del dataframe corrispondente alla data e ora specificata
    (nel fuso orario Europe/Rome), oppure quella più vicina se non esatta.
    """
    data = pd.read_csv("database/wti.csv", index_col=0, parse_dates=True )

    # Trova l’indice più vicino
    if target_dt not in data.index:
        nearest_idx = data.index.get_indexer([target_dt], method="nearest")[0]
        nearest_time = data.index[nearest_idx]
        print(f"⚠️ Nessun dato esatto per {target_dt}, uso il più vicino: {nearest_time}")
        return data.loc[nearest_time]['Open'], data.loc[nearest_time]['Close']
    else:
        return data.loc[target_dt]['Open'], data.loc[target_dt]['Close']


def llm_summarize_news(news_list: list[Any]) -> str | None:
    '''
    prende in pasto le news sul WTI e crea un riassunto utile per la valutazione sull'andamento dell'indice
    che verrà usata per la successiva valutazione previsionale di andamento dell'indice
    :param news_list:
    :return:
    '''
    model = get_geai()
    '''chiavi_da_mantenere = ['date', 'body']
    news_list_obj = [
        {chiave: news[chiave] for chiave in chiavi_da_mantenere}
        for news in news_list
    ]'''
    json_string = json.dumps(news_list, indent=len(news_list))

    prompt = f"""Given a list of news items relating to the WTI index, \
    you must summarise them in a useful way so that the information \
    can be used to conduct an analysis of the forecast trend of the WTI index. \
    Avoid to specify recommendations for further analysis, just specify the key concepts of the news to \
    produce an analysis \
    Here you can find the list of news in json format: {json_string}"""

    try:
        # Genera il contenuto basandosi sul prompt
        response = model.generate_content(prompt)

        # rimuovo i primi caratteri della string json '''json e gli ultimi ''' ```json ```
        # Stampa il risultato
        str_out = response.text
        # print("Analisi: " + str_out)
        '''str_out = response.text[7:]
        str_out = str_out[:-4]'''
        # print(str_out)
        return str_out
    except Exception as e:
        print(f"Si è verificato un errore durante la chiamata all'API: {e}")



def download_wti_data() -> pd.DataFrame:
    '''
    scarica e salva in un file csv i dati storici di quotazione del wti presi da investing
    :return:
    '''
    try:
        ticker = yf.Ticker("CL=F")
        end = datetime.datetime.now() - datetime.timedelta(days=365*2)
        start = end - datetime.timedelta(days=365 * 2)
        # data = ticker.history(period="1d", interval="1h", start=datetime.datetime(2023, 1, 1))
        data = ticker.history(start=start, end=end, interval="1h")

        # Assicurati che l'indice sia un DatetimeIndex
        if not isinstance(data.index, pd.DatetimeIndex):
            data.index = pd.to_datetime(data.index)

        # Gestione del fuso orario
        if data.index.tz is None:
            data.index = data.index.tz_localize("UTC")
        data.index = data.index.tz_convert("UTC")

        data.to_csv("database/wti1.csv", index=True)
        # df1 = pd.read_csv("database/wti.csv")
        # df_final = pd.concat([df1, data], ignore_index=False)
        # df_final.to_csv("database/wti_full.csv", index=True)
        print("✅ Dati salvati in wti.csv")
    except Exception as e:
        print(f"Errore: {e.__str__()}")

    return data


def save_dataset(documenti_da_salvare: list):
    '''
    salva il dataset che sarà utilizzato per il training in un database
    :param documenti_da_salvare:
    :return:
    '''
    # Apri o crea il database
    db = TinyDB('database/dataset.json')
    Elemento = Query()  # Oggetto Query per le ricerche

    # Itera sui documenti convertiti e salvali
    for doc in documenti_da_salvare:
        timestamp_corrente = doc['timestamp']

        # Condizione: cerca un documento con lo stesso timestamp
        condizione_ricerca = Elemento.timestamp == timestamp_corrente

        # upsert: Se il documento ESISTE, aggiornalo con i nuovi dati (doc).
        # Altrimenti, INSERISCI il nuovo documento (doc).
        db.upsert(doc, condizione_ricerca)


if __name__ == "__main__":
    print("1 - download_news_bulk")
    print("2 - categorize_news_bulk")
    print("3 - get_wti_price_bulk")
    print("4 - download_wti_data")
    print("5 - get_oldest_news")
    print("6 - merge_tables")
    ins = input("operazione: ")
    #get_distinct_dates()
    if ins == "1":
        download_news_bulk()
    elif ins == "2":
        categorize_news_bulk()
    elif ins == "3":
        get_wti_price_bulk()
    elif ins == "4":
        download_wti_data()
    elif ins == "5":
        get_oldest_news()
    elif ins == "6":
        merge_tables()
