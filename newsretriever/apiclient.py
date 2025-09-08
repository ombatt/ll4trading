from datetime import datetime, timedelta
from typing import List

import requests

from do.news import News

API_KEY = "b86e58cdd4e9412c8514a33eecba8386"
def get_news_from_newsapi(api_key, query, language='en', page_size=10):
    """
    Recupera articoli di notizie da News API.

    Args:
        api_key (str): La tua chiave API di News API.
        query (str): La parola chiave o la frase da cercare (es. "tecnologia", "economia").
        language (str, optional): Il linguaggio degli articoli (es. 'en' per inglese, 'it' per italiano).
                                  Default a 'en'.
        page_size (int, optional): Il numero massimo di articoli da restituire per richiesta.
                                  Default a 10.

    Returns:
        dict or None: Un dizionario contenente i dati JSON degli articoli se la richiesta ha successo,
                      altrimenti None.
    """
    base_url = "https://newsapi.org/v2/everything"  # O "top-headlines" a seconda delle tue esigenze

    # ottengo la fata per il riferimento alle notizie. Con questa versione di news api ho le notizie del giorno prima
    data_corrente = datetime.now()
    data_corrente = data_corrente - timedelta(days=1)
    stringa_data = data_corrente.strftime('%Y-%m-%d')

    data_corrente.strftime('%Y-%m-%d')

    params = {
        "q": query,
        "language": language,
        "pageSize": page_size,
        "apiKey": api_key,
        "sortBy": "relevancy,publishedAt",
        "from": stringa_data
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Solleva un'eccezione per codici di stato HTTP errati (4xx o 5xx)
        news_data = response.json()
        return news_data
    except requests.exceptions.RequestException as e:
        print(f"Errore durante la richiesta a News API: {e}")
        return None


def get_news(key_words: str) -> List[News]:
    if not API_KEY:
        raise Exception("wrong api key")

    # lista di ritorno
    return_list: [News] = []
    # recuper le news
    trade_news = get_news_from_newsapi(API_KEY, query=key_words, language='en', page_size=100)

    # parsing notizie creo la lista di oggetti news
    if trade_news and trade_news['status'] == 'ok':
        print(f"Trovati {trade_news['totalResults']} articoli.")
        for i, article in enumerate(trade_news['articles']):
            news = News(article.get('title', 'N/A'),
                        article.get('url', 'N/A'),
                        article.get('description', 'N/A'),
                        article['source']['name'] if 'source' in article and 'name' in article['source'] else 'N/A',
                        article.get('publishedAt', 'N/A'))
            return_list.append(news)
    elif trade_news:
        print(f"Errore da News API: {trade_news.get('message', 'Messaggio non disponibile')}")
    else:
        print("Impossibile recuperare le notizie.")

    return return_list


def get_crude_oil_news() -> List[News]:
    return get_news("Crude OIL")


def get_WTI_news() -> List[News]:
    return get_news("WTI")
