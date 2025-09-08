import json
import textwrap
from datetime import datetime, timezone
from typing import List

from do.analysis import Analysis
from do.news import News
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disk-cache-size=0")
    # chrome_options.add_argument("--headless")  # Abilita la modalità headless
    chrome_options.add_argument("--no-sandbox")  # Opzionale: utile in ambienti Docker/CI
    chrome_options.add_argument("--disable-dev-shm-usage")  # Opzionale: risolve problemi in Docker
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    return driver


'''
metodo che mappa il json di output di analisi di trend nell'oggetto Analysis
'''


def map_json_to_analysis(json_string: str) -> Analysis:
    try:
        data = json.loads(json_string)
        analysis: Analysis = Analysis(
            data['p_short'],
            data['p_medium'],
            data['summary'],
            datetime.now(timezone.utc).isoformat()
        )
        return analysis
    except Exception as e:
        print(f"map_json_to_analysis: {e}")


'''
metodo che mappa il json di output di analisi dei pesi nell'oggetto news
'''


def map_json_to_news_list(json_string: str) -> List[News]:
    news_list = []
    try:
        data = json.loads(json_string)
        for item in data:
            # Parse the date string into a datetime object
            date_obj = None
            if "date" in item:
                date_obj = datetime.fromisoformat(item["date"].replace('Z', '+00:00'))
            news = News(item["title"],
                        item["link"] if "link" in item else "",
                        item["body"] if "body" in item else "",
                        item["source"] if "source" in item else "",
                        date_obj.__str__() if date_obj is not None else "")
            news.analysis = int(str(item["analysis"]))

            news_list.append(news)
    except Exception as e:
        print(f"Errore map_json_to_news_list: {e} scarto news {json_string}")
    return news_list


'''
metodo di pulizia del json output dell'llm Gemini
'''


def clean_json_out(str_json: str) -> str:
    sequenza_inizio = "```json"
    sequenza_fine = "```"
    indice_inizio = str_json.find(sequenza_inizio)
    inizio_contenuto = indice_inizio + len(sequenza_inizio)
    indice_fine = str_json.find(sequenza_fine, inizio_contenuto)
    str_out = str_json[inizio_contenuto:indice_fine]
    return str_out

