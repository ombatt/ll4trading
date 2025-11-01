import time
from datetime import datetime

from bs4 import BeautifulSoup
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from do.news import News
from do.hist_data import Data
from old.scrapers import Scraper
from utils.utils import get_driver

url_str = "https://www.investing.com/commodities/crude-oil-news"
str_hist = "https://it.investing.com/commodities/crude-oil-historical-data"

def close_banner_bulk(driver: WebDriver, url: str):
    try:
        #print(f"parsing {url}")
        driver.get(url)
        time.sleep(0.1)

        # click cookie popup
        link = driver.find_element(By.ID, "onetrust-accept-btn-handler")
        link.click()
        time.sleep(0.1)
    except Exception as ex:
        pass
        # print("eccezione cookies, proseguo")


def search_for_news_bulk(str_link: str) -> list[News]:
    return_list: list[News] = []

    # chiudo il banner
    driver = get_driver()
    s_link = str_link if str_link else url_str
    close_banner_bulk(driver, s_link)

    try:
        page_html = driver.page_source

        # Crea un oggetto BeautifulSoup per analizzare l'HTML
        soup = BeautifulSoup(page_html, 'html.parser')

        # ricavo i titolo cover-title e il body dov'è contenuto il corpo dell'articolo
        articles = soup.find(attrs={"data-test": "news-list"})
        # ricavo i paragraph dell'articolo
        articles_det = articles.find_all('article')

        for i, article in articles_det:
            article_det = article.find('a', attrs={"data-test": "article-title-link"})
            article_time = article.find('time', attrs={"data-test": "article-publish-date"})

            # Stringa di data e ora originale
            datetime_str = article_time['datetime']
            # Formato della stringa originale
            original_format = "%Y-%m-%d %H:%M:%S"
            # Analizza la stringa per ottenere un oggetto datetime
            dt_object = datetime.strptime(datetime_str, original_format)
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
                        "investing",
                        converted_datetime_str)
            return_list.append(news)
            time.sleep(0.1)

    except Exception as ex:
        print("eccezione: " + ex.__str__())
    print(f"trovate {str(len(return_list))} da investing")
    driver.quit()
    return return_list

'''
metodo che arricchisce la news
'''

def enrich_news_bulk(news: News) -> News:
    #chiudo i cookie banner
    driver = get_driver()
    close_banner_bulk(driver, news.link)

    try:
        page_html = driver.page_source

        # Crea un oggetto BeautifulSoup per analizzare l'HTML
        soup = BeautifulSoup(page_html, 'html.parser')

        # ricavo i titolo cover-title e il body dov'è contenuto il corpo dell'articolo
        element_title = soup.find(id="articleTitle").text
        element_body = soup.find(id="article")
        # element_time = soup.find('time').get('datetime')
        # dt_object = datetime.fromisoformat(date.replace('Z', '+00:00')).isoformat()

        # ricavo i paragraph dell'articolo
        paragraphs = element_body.find_all('p')
        body_text = []
        # metto il testo di tutti i paragrafi in un'unica variabile
        for p in paragraphs:
            body_text.append(p.get_text())
        # aggiorno corpo e titolo della news originale
        news.body = "".join(body_text)
        news.title = element_title
        # news.date = element_time

    except Exception as ex:
        print("scarto news : " + news.link)
    driver.quit()
    return news