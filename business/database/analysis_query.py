'''
restituisce i doc_id delle analisi del giorno corrente
'''
import sys
from datetime import datetime, timedelta
from typing import List

from dateutil import tz
from dateutil.parser import parse
from tinydb import TinyDB, Query
from tinydb.table import Document

from business.database.database_constants import DB_FILE_PATH
from business.database.query_utils import is_same_date
from do.analysis import Analysis
from do.hist_data import Data
from do.news import News


def get_today_analysis():
    db = TinyDB(DB_FILE_PATH)
    news_db = db.table('analysis')
    qr = Query()

    # Perform the search using the custom function
    results = news_db.search(qr.date.test(is_same_date))

    # Print the results
    for item in results:
        print(item.doc_id)


'''
rimuove i doc_id delle analisi del giorno corrente
'''


def delete_doc_analysis_current_date():
    db = TinyDB(DB_FILE_PATH)
    news_db = db.table('analysis')
    qr = Query()

    # eseguo la funzione is_same_date su ogni documento e prende in considerazione come primo argomento la chiave date
    results = news_db.search(qr.date.test(is_same_date))

    # Print the results
    for item in results:
        print("rimuovo analisi data in quanto viene aggiornata " + item['date'])
        news_db.remove(qr.date == item['date'])
    db.close()


'''
recupera le entry di analisi più recenti
'''


def read_analysis() -> [{}]:
    db = TinyDB(DB_FILE_PATH)
    analysis_table = db.table("analysis")
    all_documents = analysis_table.all()

    # 3. Ordina i documenti in base all'ID in ordine decrescente
    sorted_documents = sorted(all_documents, key=lambda doc: doc.doc_id, reverse=True)

    # 4. Seleziona i primi 10 (gli ultimi inseriti)
    last_documents = sorted_documents[:10]

    return last_documents


'''
funzione che aggiorna le entry di analisi con l'effettivo andamamento dell'indice.
Per i giorni passati aggiorna con la quotaizone di chiusura e sulla base di quello calcola l'indicatore di giornata:
 - intervallo tra -0.5 e +0.5 neutro (0), tra 0.5 e 1.5 buy (1), oltre strong buy (1.5). Stessa scala al negativo
'''


def update_analysis_real_index(hist_data: [Data]):
    db = TinyDB(DB_FILE_PATH)
    an_table = db.table('analysis')

    # recupero gli ultimi documenti di analisi
    last_ana_documents: [{}] = read_analysis()

    # parsing degli ultimi dati storici
    for h_data in hist_data:
        # ciclo sugli ultimi record nella tabella delle analisi
        for doc in last_ana_documents:
            # converto la data nel formato yyyy.MM.dd per confrontarla coni dati storici
            # print(f"ID: {doc.doc_id}, data: {doc['date']}, position: {doc['p_short']}")
            data_stringa = doc['date']
            formato_originale = '%Y-%m-%dT%H:%M:%S.%f%z'
            oggetto_data = datetime.strptime(data_stringa, formato_originale)
            formato_desiderato = '%Y.%m.%d'
            data_formattata = oggetto_data.strftime(formato_desiderato)
            # print(f"data_formattata: {data_formattata}, h_data.date.strftime: {h_data.date.strftime('%Y.%m.%d')}")
            # se trovo una data uguale tra dati storici e ultime analisi e nel documento di analisi non sono presenti
            # i dati di chiusura allora aggiorno il record con la quota di chiusura e il mio esito
            if h_data.date.strftime('%Y.%m.%d') == data_formattata:  # and 'close' not in doc
                close: str = h_data.close[:-1]

                # Aggiorna il documento usando update() e il doc_id
                # L'espressione doc_id == doc_id_to_update trova il documento specifico.
                an_table.update({'close_price': float(h_data.quotation.replace(",", ".")), 'close_perc': float(close)},
                                doc_ids=[doc.doc_id])

                updated_doc = an_table.get(doc_id=doc.doc_id)
                # print("doc aggiornato: " + updated_doc.__str__())

    # calcolo la differenza di prezzo rispetto all'analisi precedente
    current_price = last_ana_documents[0]['current_price'] if 'current_price' in last_ana_documents[0] else 0
    previous_price = last_ana_documents[1]['current_price'] if 'current_price' in last_ana_documents[1] else 0
    price_dif = round(float(current_price), 2) - float(previous_price)

    current_p_shor = last_ana_documents[0]['p_short'] if 'p_short' in last_ana_documents[0] else 0
    previous_p_short = last_ana_documents[1]['p_short'] if 'p_short' in last_ana_documents[1] else 0

    quotation_open = last_ana_documents[0]['quotation_open'] if 'quotation_open' in last_ana_documents[0] else 0
    volume = last_ana_documents[0]['volume'] if 'volume' in last_ana_documents[0] else 0

    # calcolo l'indicatore BUY / SELL
    advice = "FLAT"
    if int(current_p_shor) > int(previous_p_short) and price_dif < 0.5:
        advice = "BUY"
    elif int(current_p_shor) < int(previous_p_short) and price_dif > -0.5:
        advice = "SELL"

    # arricchisco l'ultimo record di analisi (quindi quello appena calcolato al passaggio precedente) con le informazioni
    # relative a BUY/SELL, prezzo apertura, volume e differenza di prezzo rispetto all'analisi precedente
    an_table.update({'price_dif': round(float(current_price), 2) - float(previous_price),
                     'advice': advice, 'p_open': quotation_open, 'volume': volume},
                    doc_ids=[len(an_table)])


def enrich_analysis(hist_data: [Data], analysis: Analysis) -> Analysis:
    db = TinyDB(DB_FILE_PATH)
    an_table = db.table('analysis')

    # recupero gli ultimi documenti di analisi
    last_ana_documents: [{}] = read_analysis()

    # parsing degli ultimi dati storici
    for h_data in hist_data:
        # ciclo sugli ultimi record nella tabella delle analisi

        # converto la data nel formato yyyy.MM.dd per confrontarla coni dati storici
        # print(f"ID: {doc.doc_id}, data: {doc['date']}, position: {doc['p_short']}")
        data_stringa = analysis.date
        formato_originale = '%Y-%m-%dT%H:%M:%S.%f%z'
        oggetto_data = datetime.strptime(data_stringa, formato_originale)
        formato_desiderato = '%Y.%m.%d'
        data_formattata = oggetto_data.strftime(formato_desiderato)
        # print(f"data_formattata: {data_formattata}, h_data.date.strftime: {h_data.date.strftime('%Y.%m.%d')}")
        # se trovo una data uguale tra dati storici e ultime analisi e nel documento di analisi non sono presenti
        # i dati di chiusura allora aggiorno il record con la quota di chiusura e il mio esito
        if h_data.date.strftime('%Y.%m.%d') == data_formattata:  # and 'close' not in doc
            analysis.close_perc = float(h_data.close[:-1])
            analysis.close_price = float(h_data.quotation.replace(",", "."))
            analysis.volume = h_data.volume
            analysis.p_open = h_data.quotation_open

    # calcolo la differenza di prezzo rispetto all'analisi precedente
    check_b: bool = True if len(last_ana_documents) > 0 else False
    current_price = analysis.current_price if analysis.current_price else 0
    previous_price = last_ana_documents[0]['current_price'] if check_b else 0
    price_dif = round(float(current_price), 2) - float(previous_price)

    current_p_shor = analysis.p_short if analysis.p_short else 0
    previous_p_short = last_ana_documents[0]['p_short'] if check_b else 0

    # calcolo l'indicatore BUY / SELL
    # TODO da implementare bene
    advice = "FLAT"
    if int(current_p_shor) > int(previous_p_short):  # and price_dif < 0.5:
        advice = "BUY"
    elif int(current_p_shor) < int(previous_p_short):  # and price_dif > -0.5:
        advice = "SELL"

    # arricchisco l'oggetto di analisi con le informazioni
    # relative a BUY/SELL, prezzo apertura, volume e differenza di prezzo rispetto all'analisi precedente
    analysis.price_dif = round(float(current_price), 2) - float(previous_price)
    analysis.advice = advice

    return analysis


def read_last_analysis() -> [Analysis]:
    return_list = []
    try:
        db = TinyDB(DB_FILE_PATH)
        news_database = db.table('analysis')

        # recupero le analisi degli ultimi 2 giorni
        _days = datetime.now(tz.UTC) - timedelta(days=2)
        recent_an = news_database.search(Query().date.test(lambda date_str: parse(date_str) > _days))

        # le ordino per data decrescente
        sorted_an = sorted(
            recent_an,
            key=lambda doc: parse(doc["date"]),
            reverse=True
        )

        for item in sorted_an:
            date_obj = datetime.fromisoformat(item["date"].replace('Z', '+00:00'))
            ana = Analysis(item["p_short"],
                           item["p_medium"],
                           item["summary"],
                           date_obj.__str__(),
                           item["current_price"] if "current_price" in item else "",
                           item["close_price"] if "close_price" in item else "",
                           item["close_perc"] if "close_perc" in item else "",
                           item["price_dif"] if "price_dif" in item else "",
                           item["advice"] if "advice" in item else "",
                           item["p_open"] if "p_open" in item else "",
                           item["volume"] if "volume" in item else "")
            return_list.append(ana)

    except Exception as e:
        print(f"Errore durante la lettura del db: {e}")
        sys.exit(1)

    return return_list


def read_last_analysis_dict() -> [Analysis]:
    try:
        db = TinyDB(DB_FILE_PATH)
        news_database = db.table('analysis')

        # recupero le analisi degli ultimi 2 giorni
        _days = datetime.now(tz.UTC) - timedelta(days=2)
        recent_an = news_database.search(Query().date.test(lambda date_str: parse(date_str) > _days))

        # le ordino per data decrescente
        sorted_an = sorted(
            recent_an,
            key=lambda doc: parse(doc["date"]),
            reverse=True
        )

    except Exception as e:
        print(f"Errore durante la lettura del db: {e}")
        sys.exit(1)

    return recent_an
