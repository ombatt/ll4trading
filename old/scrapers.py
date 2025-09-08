import json
from abc import ABC
import time
from typing import List

from bs4 import BeautifulSoup
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from do.news import News
import utils as utils
from utils.utils import get_driver


class Scraper(ABC):

    # data una lista di links parsa il contenuto e ne ricava la news
    def get_news(self, newsLink: News, driver: WebDriver) -> News:
        pass

    def enrich_news(self, newsLink: News) -> News:
        pass

    def search_for_news(self) -> [News]:
        pass

    def iterate_over_news(self, news_list):
        pass


class YahooFinanceScraper(Scraper):

    def get_news(self, news: News, driver: WebDriver) -> News:
        news_list = []
        # inizio a parsare l' articoli
        try:
            driver.get(news.link)
            time.sleep(0.1)

            # click cookie popup
            link = driver.find_element(By.ID, "scroll-down-btn")
            link.click()
            time.sleep(0.1)
            link = driver.find_element(By.CLASS_NAME, "reject-all")
            link.click()
            time.sleep(0.1)
        except Exception as ex:
            print("eccezione cookies, proseguo")

        try:
            page_html = driver.page_source

            # Crea un oggetto BeautifulSoup per analizzare l'HTML
            soup = BeautifulSoup(page_html, 'html.parser')

            # ricavo i titolo cover-title e il body dov'è contenuto il corpo dell'articolo
            element_title = soup.find('h1', class_='cover-title').get_text()
            element_body = soup.find('div', class_='atoms-wrapper')
            # ricavo i paragraph dell'articolo
            paragraphs = element_body.find_all('p')
            body_text = []
            # metto il testo di tutti i paragrafi in un'unica variabile
            for p in paragraphs:
                body_text.append(p.get_text())
            # aggiorno corpo e titolo della news originale
            news.body = "".join(body_text)
            news.title = element_title
        except Exception as ex:
            print("eccezione: " + ex.__str__())
        return news


class BarchartScraper(Scraper):
    def get_news(self, news: News, driver: WebDriver) -> News:
        news_list = []
        # inizio a parsare l' articoli
        try:
            driver.get(news.link)
            time.sleep(0.1)
        except Exception as ex:
            print("eccezione cookies, proseguo")

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
            news.body = soup.find('p').get_text()
            news.title = news_object['title']
        except Exception as ex:
            print("eccezione: " + ex.__str__())
        return news


class EtfDailyNewsScraper(Scraper):

    def get_news(self, news: News, driver: WebDriver) -> News:
        news_list = []
        # inizio a parsare l' articoli
        try:
            driver.get(news.link)
            time.sleep(0.1)

            # click cookie popup
            link = driver.find_element(By.CLASS_NAME, "ub-emb-close")
            link.click()
            time.sleep(0.1)
            link = driver.find_element(By.CLASS_NAME, "fc-primary-button")
            link.click()
            time.sleep(0.1)
        except Exception as ex:
            print("eccezione cookies, proseguo")

        try:
            page_html = driver.page_source

            # Crea un oggetto BeautifulSoup per analizzare l'HTML
            soup = BeautifulSoup(page_html, 'html.parser')

            # ricavo i titolo cover-title e il body dov'è contenuto il corpo dell'articolo
            element_title = soup.find('h1', class_='page-title').get_text()
            element_body = soup.find('div', class_='entry')
            # ricavo i paragraph dell'articolo
            paragraphs = element_body.find_all('p')
            body_text = []
            # metto il testo di tutti i paragrafi in un'unica variabile
            for p in paragraphs:
                body_text.append(p.get_text())
            # aggiorno corpo e titolo della news originale
            news.body = "".join(body_text)
            news.title = element_title
        except Exception as ex:
            print("eccezione: " + ex.__str__())
        return news


class FinancialPostScraper(Scraper):

    def get_news(self, news: News, driver: WebDriver) -> News:
        news_list = []
        # inizio a parsare l' articoli
        try:
            driver.get(news.link)
            time.sleep(0.1)

            # click cookie popup
            '''link = driver.find_element(By.CLASS_NAME, "ub-emb-close")
            link.click()
            time.sleep(0.1)
            link = driver.find_element(By.CLASS_NAME, "fc-primary-button")
            link.click()
            time.sleep(0.1)'''
        except Exception as ex:
            print("eccezione, proseguo")

        try:
            page_html = driver.page_source

            # Crea un oggetto BeautifulSoup per analizzare l'HTML
            soup = BeautifulSoup(page_html, 'html.parser')

            # ricavo i titolo cover-title e il body dov'è contenuto il corpo dell'articolo
            element_title = soup.find('h1', class_='article-title').get_text()
            # ricavo le sezioni
            element_body = soup.find_all('section', class_='article-content__content-group--story')
            body_text = []
            # ricavo il paragraph di tutte le sezioni
            for el in element_body:
                p = el.find('p')
                if p:
                    body_text.append(el.find('p').get_text())

            # aggiorno corpo e titolo della news originale
            news.body = "".join(body_text)
            news.title = element_title
        except Exception as ex:
            print("eccezione: " + ex.__str__())
        return news


class OilPriceScraper(Scraper):

    def get_news(self, news: News, driver: WebDriver) -> News:
        news_list = []
        # inizio a parsare l' articoli
        try:
            driver.get(news.link)
            time.sleep(0.1)
        except Exception as ex:
            print("eccezione, proseguo")

        try:
            page_html = driver.page_source

            # Crea un oggetto BeautifulSoup per analizzare l'HTML
            soup = BeautifulSoup(page_html, 'html.parser')

            # ricavo i titolo cover-title e il body dov'è contenuto il corpo dell'articolo
            element_title = soup.find('h1', class_='speakable').get_text()
            # Usa find() per trovare la prima occorrenza
            script_tag = soup.find('script', type='application/ld+json')
            if script_tag:
                # 3. Estrai il contenuto testuale del tag script
                json_ld_string = script_tag.string
                try:
                    # 4. Parsa la stringa JSON in un oggetto Python (dizionario)
                    data = json.loads(json_ld_string)

                    # 5. Accedi al valore di 'articleBody'
                    if 'articleBody' in data:
                        news.body = data['articleBody']
                        print("Valore di 'articleBody' recuperato con successo:")
                        print(news.body)
                    else:
                        print("L'attributo 'articleBody' non è presente nei dati JSON-LD.")

                except json.JSONDecodeError as e:
                    print(f"Errore nel parsing del JSON-LD: {e}")
                except Exception as e:
                    print(f"Si è verificato un errore inatteso: {e}")
            else:
                print("Nessun tag <script type=\"application/ld+json\"> trovato nella pagina.")

            news.title = element_title
        except Exception as ex:
            print("eccezione: " + ex.__str__())
        return news


class AbcNewsScraper(Scraper):
    def get_news(self, news: News, driver: WebDriver) -> News:
        news_list = []
        # inizio a parsare l' articoli
        try:
            driver.get(news.link)
            time.sleep(0.1)
        except Exception as ex:
            print("eccezione cookies, proseguo")

        try:
            page_html = driver.page_source

            # Crea un oggetto BeautifulSoup per analizzare l'HTML
            soup = BeautifulSoup(page_html, 'html.parser')

            # la notizia non è direttamente dentro l'html , ma viene caricata da un elemento div che
            # contiene i valori in un attributo data-news-item
            article_body_div = soup.find(attrs={"data-testid": "prism-article-body"})
            article_p = article_body_div.find_all('p')
            body_text = []
            for p in article_p:
                str_p = p.find('p').get_text
                body_text.append(str_p)
            # aggiorno corpo e titolo della news originale
            news.body = "".join(body_text)
            news.title = soup.find('div', class_="prism-headline").find('h1').find('span').get_text()
        except Exception as ex:
            print("eccezione: " + ex.__str__())
        return news


class InvestingScraper(Scraper):

    def get_news(self, news: News, driver: WebDriver) -> News:
        news_list = []
        # inizio a parsare l' articoli
        try:
            driver.get(news.link)
            time.sleep(0.1)

            # click cookie popup
            link = driver.find_element(By.ID, "onetrust-accept-btn-handler")
            link.click()
            time.sleep(0.1)
        except Exception as ex:
            print("eccezione cookies, proseguo")

        try:
            page_html = driver.page_source

            # Crea un oggetto BeautifulSoup per analizzare l'HTML
            soup = BeautifulSoup(page_html, 'html.parser')

            # ricavo i titolo cover-title e il body dov'è contenuto il corpo dell'articolo
            article_body_div = soup.find('div', class_='article_container')
            # ricavo i paragraph dell'articolo
            paragraphs = article_body_div.find_all('p')
            body_text = []
            # metto il testo di tutti i paragrafi in un'unica variabile
            for p in paragraphs:
                body_text.append(p.get_text())
            # aggiorno corpo e titolo della news originale
            news.body = "".join(body_text)
            news.title = soup.find('div', class_="articleTitle").find('h1').find('span').get_text()

        except Exception as ex:
            print("eccezione: " + ex.__str__())
        return news
