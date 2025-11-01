import json
import textwrap
from datetime import datetime, timezone
from typing import List

from configuration.configuration import Configuration
from do.analysis import Analysis
from do.hist_data import Data
from do.news import News
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def get_driver():
    configuration: Configuration = Configuration()

    # scraping delle news
    chrome_options = Options()
    chrome_options.add_argument("--disk-cache-size=0")
    # chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")

    if configuration.config["headless_mode_flag"]:
        chrome_options.add_argument("--headless=new")  # Abilita la modalità headless
    else:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        chrome_options.add_argument(f'user-agent={user_agent}')
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    chrome_options.add_argument("--no-sandbox")  # Opzionale: utile in ambienti Docker/CI
    chrome_options.add_argument("--disable-dev-shm-usage")  # Opzionale: risolve problemi in Docker
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script('Object.defineProperty(navigator, "webdriver", {get: () => undefined})')
    driver.set_window_size(100, 100)
    return driver


'''
metodo che mappa il json di output di analisi di trend nell'oggetto Analysis
'''


def map_json_to_analysis(json_string: str) -> Analysis | None:
    try:
        data = json.loads(json_string)
        analysis: Analysis = Analysis(
            data['p_short'],
            data['p_medium'],
            data['summary'],
            float(data['forecast_price']),
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