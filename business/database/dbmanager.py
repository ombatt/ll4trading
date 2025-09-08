import json
import os
from datetime import timezone, datetime

from tinydb import TinyDB, Query

from utils.print_utils import print_analysis
from do.analysis import Analysis
from do.news import News
from business.database.database_constants import DB_FILE_PATH

'''
scrive la news a database
'''


def write_news(news: News):
    try:
        db = TinyDB(DB_FILE_PATH)
        news_db = db.table('news')
        news_db.insert(news.to_dict())
    except Exception as e:
        print(f"Errore durante la scrittura a db: {e}")


'''
scrive le news a db ma partendo dalla lista di news
'''


def write_news_list(news_list: [News]):
    try:
        for news in news_list:
            db = TinyDB(DB_FILE_PATH)
            news_db = db.table('news')
            news_db.insert(news.to_dict())
    except Exception as e:
        print(f"Errore durante la scrittura a db: {e}")


'''
scrive il titolo della news a database
'''


def write_news_title(news: News):
    try:
        db = TinyDB(DB_FILE_PATH)
        news_db = db.table('news_title')
        news_db.insert(news.to_dict_title())
    except Exception as e:
        print(f"Errore durante la scrittura a db: {e}")


def write_analysis(obj_analysis: Analysis):
    try:
        db = TinyDB(DB_FILE_PATH)
        news_db = db.table('analysis')
        news_db.insert(obj_analysis.to_dict())
        db.close()
        if not os.path.exists(DB_FILE_PATH):
            print(f"ERRORE: Il file {DB_FILE_PATH} NON esiste! Il percorso è sbagliato o non è stato creato.")
            exit(-1)

        db = TinyDB(DB_FILE_PATH)
        an_table = db.table('analysis')
        all_news = an_table.all()
        if all_news:  # Assicurati che il database non sia vuoto
            highest_doc = max(an_table, key=lambda doc: doc.doc_id)
            print("risultato analisi:")
            print_analysis(highest_doc)
        else:
            print("Il database è vuoto.")
    except Exception as e:
        print(f"Errore durante la lettura del db: {e}")


def read_db():
    db = TinyDB(DB_FILE_PATH)
    all_documents = db.all()
    print("Tutti i documenti nel database:")
    for doc in all_documents:
        print(doc)
