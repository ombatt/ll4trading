'''
funzione che restituisce i titoli delle ultime 100 news inserite
'''
import sys
from datetime import datetime, timedelta, date

from dateutil import tz
from dateutil.parser import parse
from tinydb import TinyDB, Query

from business.database.database_constants import DB_FILE_PATH
from business.database.query_utils import is_yesterday_date, is_today_date
from do.news import News


def get_last_100_news_titles() -> [{}]:
    # Connetti al tuo database
    db = TinyDB(DB_FILE_PATH)
    title_table = db.table("news_title")

    # Ottieni il numero totale di documenti, che corrisponde all'ID del documento più recente
    max_doc_id = len(title_table)

    # Calcola il doc_id di partenza. Assicurati che non sia inferiore a 1.
    start_doc_id = max(1, max_doc_id - 99)

    # Inizializza una lista per i risultati
    ultimi_documenti = []

    # Cicla dall'ultimo doc_id fino a quello di partenza
    # range() esclude il valore di fine, quindi usiamo (start_doc_id - 1)
    for doc_id in range(max_doc_id, start_doc_id - 1, -1):
        doc = title_table.get(doc_id=doc_id)
        if doc:  # Aggiungiamo un controllo nel caso l'ID non esista
            ultimi_documenti.append(doc)

    # Stampa i documenti recuperati
    print(f"Recuperati {len(ultimi_documenti)} titoli già presenti.")
    return ultimi_documenti


'''
recupera le ultime news più recenti (default 50) e le ordina per timestamp decrescente
'''


def get_last_news_num(numerber_of_news=50) -> [News]:
    return_list = []
    try:
        db = TinyDB(DB_FILE_PATH)
        news_database = db.table('news')

        # recupero le news degli ultimi 2 giorni
        _l_days = datetime.now(tz.UTC) - timedelta(days=2)
        recent_news = news_database.search(Query().date.test(lambda date_str: parse(date_str) > _l_days))

        # le ordino per data decrescente
        sorted_news = sorted(
            recent_news,
            key=lambda doc: parse(doc["date"]),
            reverse=True
        )

        # filtro le ultime numerber_of_news
        counter = 0
        for item in sorted_news:
            if counter >= numerber_of_news: break
            date_obj = datetime.fromisoformat(item["date"].replace('Z', '+00:00'))
            news = News(item["title"],
                        item["link"],
                        item["body"],
                        item["source"],
                        date_obj.__str__())
            news.analysis = item["analysis"]
            return_list.append(news)
            counter = +1

    except Exception as e:
        print(f"Errore durante la lettura del db: {e}")
        sys.exit(1)

    return return_list


'''
cancella dal db le news che hanno data di oggi
'''


def delete_doc_news_current_date_1():
    db = TinyDB(DB_FILE_PATH)
    news_db = db.table('news')
    qr = Query()

    # le news fanno riferimento al giorno precedente rispetto alla data odierna
    # eseguo la funzione is_same_date su ogni documento e prende in considerazione come primo argomento la chiave date
    results = news_db.search(qr.date.test(is_today_date))

    # Print the results
    for item in results:
        print("cancello analisi " + item['date'])
        news_db.remove(qr.date == item['date'])
    db.close()


'''
rimuove le news del giorno corrente (quindi di ieri)
'''


def delete_doc_news_current_date():
    db = TinyDB(DB_FILE_PATH)
    news_db = db.table('news')
    qr = Query()

    # le news fanno riferimento al giorno precedente rispetto alla data odierna
    # eseguo la funzione is_same_date su ogni documento e prende in considerazione come primo argomento la chiave date
    results = news_db.search(qr.date.test(is_yesterday_date))

    # Print the results
    for item in results:
        print("removing " + item['date'])
        news_db.remove(qr.date == item['date'])
    db.close()


'''
cancella dal db le news che hanno lo stesso titolo delle news passate in input
'''


def delete_doc_news_by_tile(news: [News]):
    db = TinyDB(DB_FILE_PATH)
    news_db = db.table('news')
    qr = Query()

    # le news fanno riferimento al giorno precedente rispetto alla data odierna
    # eseguo la funzione is_same_date su ogni documento e prende in considerazione come primo argomento la chiave date
    for n in news:
        results = news_db.search(qr.title == n.title)
        if len(results) > 0:
            docs_to_del = [r.doc_id for r in results]
            print(f"eliminazioni eventuali news duplicate {docs_to_del}")
            news_db.remove(doc_ids=docs_to_del)
    db.close()

    '''
    recupero le news di oggi
    '''


def get_news_today() -> [News]:
    return_list: [News] = []
    try:
        db = TinyDB(DB_FILE_PATH)
        news_database = db.table('news')

        # recupero dal db le news che hanno data oggi
        data_odierna = date.today()
        filtro_data = data_odierna.isoformat()
        results = news_database.search(lambda doc: doc.get('date', '').startswith(filtro_data))

        # converto i documenti in news
        for item in results:
            date_obj = datetime.fromisoformat(item["date"].replace('Z', '+00:00'))
            news = News(item["title"],
                        item["link"],
                        item["body"],
                        item["source"],
                        date_obj.__str__())
            news.analysis = item["analysis"]
            return_list.append(news)

        db.close()

        return return_list
    except Exception as e:
        print(f"Errore durante la lettura del db: {e}")


'''
recupero le news degli ultimi 3 giorni
'''


def get_news_recent():
    try:
        db = TinyDB(DB_FILE_PATH)
        news_database = db.table('news')

        # le news fanno riferimento al giorno precedente rispetto alla data odierna
        # eseguo la funzione is_same_date su ogni documento e prende in considerazione come primo argomento la chiave date
        data_odierna = date.today()
        filtro_data = data_odierna.isoformat()
        data_di_ieri = data_odierna - timedelta(days=1)
        data_di_lieri = data_odierna - timedelta(days=2)
        filtro_data_1 = data_di_ieri.isoformat()
        filtro_data_2 = data_di_lieri.isoformat()
        results = news_database.search(lambda doc: doc.get('date', '').startswith(filtro_data)
                                                   or doc.get('date', '').startswith(filtro_data_1)
                                                   or doc.get('date', '').startswith(filtro_data_2))

        db.close()

        return results
    except Exception as e:
        print(f"Errore durante la lettura del db: {e}")


'''
recupera le 50 news più recenti
'''


def get_last_50_news() -> [News]:
    # Connetti al tuo database
    db = TinyDB(DB_FILE_PATH)
    title_table = db.table("news")

    # Ottieni il numero totale di documenti, che corrisponde all'ID del documento più recente
    max_doc_id = len(title_table)

    # Calcola il doc_id di partenza. Assicurati che non sia inferiore a 1.
    start_doc_id = max(1, max_doc_id - 50)

    # Inizializza una lista per i risultati
    return_list = []

    # Cicla dall'ultimo doc_id fino a quello di partenza
    # range() esclude il valore di fine, quindi usiamo (start_doc_id - 1)
    for doc_id in range(max_doc_id, start_doc_id - 1, -1):
        item = title_table.get(doc_id=doc_id)
        if item:  # Aggiungiamo un controllo nel caso l'ID non esista
            # converto i documenti in news
            date_obj = datetime.fromisoformat(item["date"].replace('Z', '+00:00'))
            news = News(item["title"],
                        item["link"],
                        item["body"],
                        item["source"],
                        date_obj.__str__())
            news.analysis = item["analysis"]
            return_list.append(news)

    # Stampa i documenti recuperati
    print(f"Recuperate {len(return_list)} news per l'analisi.")
    return return_list
