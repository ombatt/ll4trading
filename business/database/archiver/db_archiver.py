from datetime import datetime

import pandas as pd
from tinydb import TinyDB

from business.database.database_constants import DB_FILE_PATH

# Numero massimo di record da mantenere nel DB live
MAX_RECORDS = 100

def run_archiver():
    # Database
    live_db = TinyDB(DB_FILE_PATH)

    '''
    creo il file db di archivio
    '''
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d_%H:%M:%S")
    archive_db = TinyDB("db_1_"+now_str+".json")

    '''
    gestisco la cancellazione del db dei titoli delle news (non le archivio, le cancello)
    '''
    news_title_db = live_db.table('news_title')
    news_title_docs = news_title_db.all()

    # Se il numero di documenti supera la soglia
    if len(news_title_docs) > MAX_RECORDS:
        # Calcola quanti spostare
        num_to_move = len(news_title_docs) - MAX_RECORDS
        docs_to_archive = news_title_docs[:num_to_move]  # i più vecchi

        # Inserisci nello storico
        archive_db.insert_multiple(docs_to_archive)

        # Cancella dal live i documenti spostati
        for doc in docs_to_archive:
            news_title_db.remove(doc_ids=[doc.doc_id])

        print(f"🏷️ Cancellati {num_to_move} news_title da db_1.json")
    else:
        print("✅ Nessun documento da spostare")


    '''
    gestisco la cancellazione e la storicizzazione delle news (non le archivio, le cancello)
    '''
    news_db = live_db.table('news')
    news_docs = news_db.all()

    # Se il numero di documenti supera la soglia
    if len(news_docs) > MAX_RECORDS:
        # Calcola quanti spostare
        num_to_move = len(news_docs) - MAX_RECORDS
        docs_to_archive = sorted(news_docs, key=lambda d: d["date"])
        docs_to_archive = docs_to_archive[:num_to_move]  # i più vecchi

        # Inserisci nello storico
        archive_db_news = archive_db.table('news')
        archive_db_news.insert_multiple(docs_to_archive)

        # Cancella dal live i documenti spostati
        for doc in docs_to_archive:
            news_db.remove(doc_ids=[doc.doc_id])

        print(f"🏷️ Cancellati {num_to_move} news da db_1.json")
    else:
        print("✅ Nessun documento news da spostare")


    '''
    gestisco la cancellazione delle analisi (non le archivio, le cancello)
    '''
    analysis_db = live_db.table('analysis')
    analysis_docs = analysis_db.all()

    # Se il numero di documenti supera la soglia
    if len(analysis_docs) > MAX_RECORDS:
        # Calcola quanti spostare
        num_to_move = len(analysis_docs) - MAX_RECORDS
        docs_to_archive = sorted(analysis_docs, key=lambda d: d["date"])
        docs_to_archive = docs_to_archive[:num_to_move]  # i più vecchi

        # Inserisci nello storico
        archive_db_analysis = archive_db.table('analysis')
        archive_db_analysis.insert_multiple(docs_to_archive)

        # Cancella dal live i documenti spostati
        for doc in docs_to_archive:
            news_db.remove(doc_ids=[doc.doc_id])

        print(f"🏷️ Cancellati {num_to_move} analysis da db_1.json")
    else:
        print("✅ Nessun documento analysis da spostare")

def export_to_csv(database: str, table: str):
    db = TinyDB(database)
    analysis_db = db.table(table)
    analysis_docs = analysis_db.all()
    df = pd.DataFrame.from_records(analysis_docs)
    df.to_csv(table+"-"+database.replace(".json","")+'.csv', index=False)