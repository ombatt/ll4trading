import time

from bs4 import BeautifulSoup
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from do.news import News
from old.scrapers import Scraper
from utils.utils import get_driver

url_str = "https://finance.yahoo.com/quote/CL=F/"  # "https://finance.yahoo.com/quote/CL=F/" https://finance.yahoo.com/quote/CL%3DF/news/


def close_banner(driver: WebDriver, url: str):
    # gestione cookie bar
    try:
        #print(f"parsing {url}")
        driver.get(url)
        time.sleep(0.7)
        # click cookie popup
        link = driver.find_element(By.ID, "scroll-down-btn")
        link.click()
        time.sleep(0.5)
        link = driver.find_element(By.CLASS_NAME, "reject-all")
        link.click()
        time.sleep(0.3)
    except Exception as ex:
        # eccezione navigazione, prosegue
        pass
        # print("eccezione cookies, proseguo")


class YahooScraper(Scraper):

    def search_for_news(self) -> [News]:
        driver = get_driver()
        return_list: [News] = []

        close_banner(driver, url_str)

        page_html = driver.page_source

        # Crea un oggetto BeautifulSoup per analizzare l'HTML
        soup = BeautifulSoup(page_html, 'html.parser')

        # ricavo i titolo cover-title e il body dov'è contenuto il corpo dell'articolo
        news_container = soup.find('div', class_='filtered-stories')
        news = news_container.find_all('a', {'class': 'titles', 'title': True})

        # metto il testo di tutti i paragrafi in un'unica variabile
        for n in news:
            n = News(n.get('title'), n.get('href'), "", "finance.yahoo", "")
            return_list.append(n)

        print(f"trovate {str(len(return_list))} da yahoo")
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
            element_title = soup.find('h1', class_='cover-title').get_text()
            element_body = soup.find('div', class_='atoms-wrapper')
            element_time = soup.find('time').get('datetime')
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
            news.date = element_time

        except Exception as ex:
            print("scarto scraping errore : " + news.link)
        driver.quit()
        return news

