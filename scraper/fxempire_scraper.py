import time

from bs4 import BeautifulSoup
from dateutil.parser import parse
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from do.news import News
from old.scrapers import Scraper
from utils.utils import get_driver

url_str = "https://www.fxempire.com/forecasts/wti-crude-oil"


def close_banner(driver: WebDriver, url: str):
    # gestione cookie bar
    try:
        #print(f"parsing {url}")
        driver.get(url)
        time.sleep(0.7)
        # click cookie popup
        link = driver.find_element(By.ID, "onetrust-accept-btn-handler")
        link.click()
        time.sleep(0.5)
    except Exception as ex:
        # eccezione navigazione, prosegue
        pass
        # print("eccezione cookies, proseguo")


class FxEmpireScraper(Scraper):

    def search_for_news(self) -> [News]:
        driver = get_driver()
        return_list: [News] = []

        close_banner(driver, url_str)

        page_html = driver.page_source

        # Crea un oggetto BeautifulSoup per analizzare l'HTML
        soup = BeautifulSoup(page_html, 'html.parser')

        # ricavo i titolo cover-title e il body dov'è contenuto il corpo dell'articolo
        news_container = soup.find_all('article')

        # metto il testo di tutti i paragrafi in un'unica variabile
        for n in news_container:
            news = News(n.find('h3').get_text(),
                     n.find('a').get('href'),
                     "",
                     "fxempire",
                     "")
            return_list.append(news)

        print(f"trovate {str(len(return_list))} da fxempire")
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
            element_title = soup.find('h1').get_text()
            element_body = soup.find('div', attrs={'display': 'grid'})
            element_time = soup.find('span', attrs={'display': 'inline-block'}).get_text().replace("Published: ","").replace("Updated: ","")
            dt_object = parse(element_time)

            # ricavo i paragraph dell'articolo
            paragraphs = element_body.find_all('p')
            body_text = []
            # metto il testo di tutti i paragrafi in un'unica variabile
            for p in paragraphs:
                body_text.append(p.get_text())
            # aggiorno corpo e titolo della news originale
            news.body = "".join(body_text)
            news.title = element_title
            news.date = dt_object.isoformat()

        except Exception as ex:
            print("scarto scraping errore : " + news.link)
        driver.quit()
        return news

