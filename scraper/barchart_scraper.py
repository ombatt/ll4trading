import json
import nt
import time
from datetime import datetime

from bs4 import BeautifulSoup
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from do.news import News
from do.hist_data import Data
from old.scrapers import Scraper
from utils.utils import get_driver

url_str = "https://www.barchart.com/news/commodities/energy"

'''
gestisco il driver selenium qui dentro in quanto utilizzare la stessa istanza con investing crea problemi
il sito blocca il traffico. utilizzando istanze diverse questo non accade
'''

'''
metodo che chiude il cookie banner
'''


def close_banner(driver: WebDriver, url: str):
    try:
        # print(f"parsing {url}")
        driver.get(url)
        time.sleep(0.2)
        # page_src = driver.page_source
        # print(page_src)
        # click cookie popup
        # link = driver.find_element(By.ID, "cmpwelcomebtnyes")
        # link.click()
        # time.sleep(0.1)
    except Exception as ex:
        pass
        # print("eccezione cookies, proseguo")


class BarChartScraper(Scraper):

    def search_for_news(self):
        return_list: [News] = []

        # chiudo il banner
        driver = get_driver()
        close_banner(driver, url_str)

        try:
            page_html = driver.page_source

            # Crea un oggetto BeautifulSoup per analizzare l'HTML
            soup = BeautifulSoup(page_html, 'html.parser')

            # ricavo i titolo cover-title e il body dov'è contenuto il corpo dell'articolo
            articles = soup.find('div', class_='stories-list')
            # ricavo i paragraph dell'articolo
            articles_det = articles.find_all('div', class_='story')

            for article in articles_det:
                try:
                    article_det = article.find('a', class_='story-link')
                    article_time = article.find('span', class_='story-meta').text

                    # Stringa di data e ora originale
                    datetime_str = article_time.replace(" CDT", "")
                    datetime_str = datetime_str.replace("Barchart -", "").strip()
                    datetime_str = datetime_str.replace("Blue Line Futures -", "").strip()

                    # Formato della stringa originale
                    original_format = "%a %b %d, %I:%M%p"
                    # Analizza la stringa per ottenere un oggetto datetime
                    dt_object = datetime.strptime(datetime_str, original_format).replace(year=datetime.now().year)
                    # Formato ISO 8601 con fuso orario UTC
                    new_format = "%Y-%m-%dT%H:%M:%S.%fZ"  # "%Y-%m-%dT%H:%M:%S+00:00"
                    # Formatta l'oggetto datetime nella nuova stringa
                    converted_datetime_str = dt_object.strftime(new_format)

                    '''
                    creo la news, inserisco anche la data in quanto dal dettaglio della news è difficile ricavarla
                    '''
                    news = News(article_det.get_text(),
                                article_det.get('href'),
                                "",
                                "barchart",
                                converted_datetime_str)
                    return_list.append(news)
                except Exception as ex:
                    print("scarto news : " + ex.__str__())
                time.sleep(0.1)

        except Exception as ex:
            print("eccezione: " + ex.__str__())
        driver.quit()
        print(f"trovate {str(len(return_list))} da barchart")
        return return_list

    '''
    metodo che arricchisce la news
    '''

    def enrich_news(self, news: News) -> News:
        driver = get_driver()
        close_banner(driver, news.link)
        try:
            page_html = driver.page_source

            # Crea un oggetto BeautifulSoup per analizzare l'HTML
            soup = BeautifulSoup(page_html, 'html.parser')

            # la notizia non è direttamente dentro l'html , ma viene caricata da un elemento div che
            # contiene i valori in un attributo data-news-item
            news_item_element = soup.find(lambda tag: tag.has_attr('data-news-item'))

            # estraggo l'attributo di interesse
            news_map = news_item_element['data-news-item']

            # converto il valore stringa dell'attributo in un dizionario
            news_object = json.loads(news_map)
            soup = BeautifulSoup(news_object['content'], 'html.parser')

            # aggiorno corpo e titolo della news originale
            paragraphs = soup.find_all('p')
            body_text = []
            for p in paragraphs:
                body_text.append(p.get_text())
            # aggiorno corpo e titolo della news originale
            news.body = "".join(body_text)
            news.title = news_object['title']
        except Exception as ex:
            print("scarto scraping errore: " + news.link)
        driver.quit()
        return news
