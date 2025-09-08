import json
import os
from datetime import datetime

from do.news import News


def write_to_file_news(news_list):
    # nome del file
    data_e_ora_correnti = datetime.now()
    formato_italiano_data = data_e_ora_correnti.strftime("%d-%m-%Y")
    nome_file = "oil_news_"+formato_italiano_data+".json"

    # cancello il file se esiste
    try:
        os.remove(nome_file)
        print(f"Il file '{nome_file}' è stato cancellato con successo.")
    except FileNotFoundError:
        print(f"Errore: Il file '{nome_file}' non esiste.")
    except Exception as e:
        print(f"Si è verificato un errore durante la cancellazione del file: {e}")

    # converto la lista di oggetti news in stringa e scrivo su file
    news_list_obj = [news.to_dict() for news in news_list]
    try:
        with open(nome_file, 'w', encoding='utf-8') as file_json:
            json.dump(news_list_obj, file_json, indent=len(news_list), ensure_ascii=False)
        print(f"Lista di news scritta con successo nel file ")
    except IOError as e:
        print(f"Errore durante la scrittura del file: {e}")


def write_to_file_analysis(str_analysis):
    # nome del file
    data_e_ora_correnti = datetime.now()
    formato_italiano_data = data_e_ora_correnti.strftime("%d-%m-%Y")
    nome_file = "oil_analysis_"+formato_italiano_data+".json"

    # cancello il file se esiste
    try:
        os.remove(nome_file)
        print(f"Il file '{nome_file}' è stato cancellato con successo.")
    except FileNotFoundError:
        print(f"Errore: Il file '{nome_file}' non esiste.")
    except Exception as e:
        print(f"Si è verificato un errore durante la cancellazione del file: {e}")

    try:
        with open(nome_file, 'w', encoding='utf-8') as file_json:
            file_json.write(str_analysis)
        print(f"Analisi scritta con successo nel file ")
    except IOError as e:
        print(f"Errore durante la scrittura del file: {e}")


def write_news_to_markdown_file(news_list: [News]):
    data_e_ora_correnti = datetime.now()
    formato_italiano_data = data_e_ora_correnti.strftime("%d-%m-%Y")
    nome_file = "./docs/crude_oil_news"+formato_italiano_data+".md"
    with open(nome_file, "w", encoding="utf-8") as f:
        for n in news_list:
            f.write(n.to_markdown_string())