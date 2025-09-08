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

'''
gestisco il driver selenium qui dentro in quanto utilizzare la stessa istanza con investing crea problemi
il sito blocca il traffico. utilizzando istanze diverse questo non accade
'''

'''
metodo che chiude il cookie banner
'''


def close_banner(driver: WebDriver, url: str):
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


class InvestingScraper(Scraper):

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
        driver.quit()
        print(f"trovate {str(len(return_list))} da investing")
        return return_list

    '''
    metodo che arricchisce la news
    '''

    def enrich_news(self, news: News) -> News:
        driver = get_driver()
        #chiudo i cookie banner
        close_banner(driver, news.link)

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


'''
metodo che tramite scraping recupera gli ultimi dati storici di chiusura dell'indice WTI
'''


def get_crude_oil_historical_data() -> [Data]:
    driver = get_driver()
    return_list: [Data] = []
    # inizio a parsare l' articoli
    try:
        driver.get(str_hist)
        time.sleep(0.2)

        link = driver.find_element(By.ID, "onetrust-accept-btn-handler")
        link.click()
        time.sleep(0.1)

        # click cookie popup
        link = driver.find_element(By.XPATH, "/html/body/div[4]/div/div/div/div[2]/svg/use")
        link.click()
        time.sleep(0.1)
    except Exception as ex:
        pass
        # print("eccezione box subrscription, proseguo")

    try:
        page_html = driver.page_source

        # Crea un oggetto BeautifulSoup per analizzare l'HTML
        soup = BeautifulSoup(page_html, 'html.parser')

        # ricavo i titolo cover-title e il body dov'è contenuto il corpo dell'articolo
        data_table = soup.find('table', class_='freeze-column-w-1')
        # ricavo i paragraph dell'articolo
        tr_table = data_table.find_all('tr')

        for y, tr_data in enumerate(tr_table):

            td_table = tr_data.find_all('td')
            str_date = ""
            str_price = ""
            str_quotation = ""
            str_quotation_open = ""
            volume = ""

            for i, price_data in enumerate(td_table):
                # recupero la data di riferimento
                if i == 0:
                    str_date = price_data.find('time').get_text()
                # recupero il prezzo di riferimento
                elif i == 6:
                    str_price = price_data.get_text()
                elif i == 1:
                    str_quotation = price_data.get_text()
                elif i == 2:
                    str_quotation_open = price_data.get_text()
                elif i == 5:
                    volume = price_data.get_text()
            if str_date != "" and str_price != "":
                hist_data: Data = Data(str_price, str_date, str_quotation, str_quotation_open, volume)
                return_list.append(hist_data)
        return return_list

    except Exception as ex:
        print("eccezione: " + ex.__str__())
    driver.quit()
    return return_list
