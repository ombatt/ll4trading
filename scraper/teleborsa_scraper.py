import time
from datetime import datetime, timezone

from bs4 import BeautifulSoup
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from do.news import News
from old.scrapers import Scraper
from utils.utils import get_driver

url_str = "https://www.teleborsa.it/materie-prime/wti-crude-oil-future-clxx-NDQuQ0xYWA/analisi?tab=2"  # "https://finance.yahoo.com/quote/CL=F/" https://finance.yahoo.com/quote/CL%3DF/news/


def close_banner(driver: WebDriver, url: str):
    # gestione cookie bar
    try:
        #print(f"parsing {url}")
        driver.get(url)
        # click cookie popup
        try:
            link = driver.find_element(By.ID, "pt-accept-all")
            time.sleep(0.5)
            link.click()
        except Exception as ex:
            # eccezione navigazione, prosegue
            pass
        time.sleep(0.3)
    except Exception as ex:
        # eccezione navigazione, prosegue
        pass
        # print("eccezione cookies, proseguo")


class TeleBorsaScraper(Scraper):

    '''
    per teleborsa non ricerco le news, parso solamente la pagina dell'analisi tecnica giornaliera.
    Creo quindi una sola news con il titolo relativo alla chiusura dell'ultima data come riportato dal sito. Es: Chiusura del 10 ottobre
    '''
    def search_for_news(self) -> list[News]:
        driver = get_driver()
        return_list: list[News] = []

        close_banner(driver, url_str)

        page_html = driver.page_source

        # Crea un oggetto BeautifulSoup per analizzare l'HTML
        soup = BeautifulSoup(page_html, 'html.parser')

        # ricavo i titolo cover-title e il body dov'è contenuto il corpo dell'articolo
        news_container = soup.find('div', class_='scheda-analisi-tecnica')
        news = news_container.find('div', class_='section-title')
        title = news_container.find('span').get_text()

        # solo una news
        n = News(title, url_str, "", "teleborsa.it", "")
        return_list.append(n)

        print(f"trovate {str(len(return_list))} da teleborsa")
        driver.quit()

        return return_list

    '''
    arricchimento delle news
    '''

    def enrich_news(self, news: News) -> News:
        # inizio a parsare l' articoli
        driver = get_driver()
        close_banner(driver, news.link)

        try:
            page_html = driver.page_source

            # Crea un oggetto BeautifulSoup per analizzare l'HTML
            soup = BeautifulSoup(page_html, 'html.parser')

            # ricavo i titolo cover-title e il body dov'è contenuto il corpo dell'articolo
            news_container = soup.find('div', class_='scheda-analisi-tecnica')
            #news = news_container.find('div', class_='section-title')
            title = news_container.find('span').get_text()

            element_body = news_container.find_all('p')

            # ricavo i paragraph dell'articolo
            body_text = []
            # metto il testo di tutti i paragrafi in un'unica variabile
            for p in element_body:
                body_text.append(p.get_text())
            # aggiorno corpo e titolo della news originale
            news.body = "".join(body_text)
            news.title = title

            now = datetime.now(timezone.utc)
            formatted_time = now.isoformat()
            news.date = str(formatted_time)

        except Exception as ex:
            print("scarto scraping errore : " + news.link)
        driver.quit()
        return news

