import sys

from langchain_community.vectorstores import Chroma

from business.database.analysis_query import update_analysis_real_index, enrich_analysis
from business.database.news_query import get_last_news_num, get_last_100_news_titles
from business.rag.rag import load_and_split_markdown, create_vector_store, create_rag_chain_with_custom_prompt
from do.hist_data import Data
from llm.llm import run_weight_analysis, run_financial_analysis

from newsretriever.api_price import get_wti_price
from scraper.fxempire_scraper import FxEmpireScraper
from scraper.investing_scraper import InvestingScraper, get_crude_oil_historical_data
from scraper.yahoo_scraper import YahooScraper
from scraper.barchart_scraper import BarChartScraper
from utils.print_utils import print_progress
from old.scrapers import Scraper
from business.database.dbmanager import write_analysis, write_news_title, write_news_list
from langchain_core.documents import Document

'''
def run_2():
    print("init")
    docs: [Document] = load_and_split_markdown()
    vector_db: Chroma = create_vector_store(docs)
    rag_chain = create_rag_chain_with_custom_prompt(vector_db)
    result = rag_chain.invoke(user_query)
    print(result)'''

def retrieve_news():
    print("inizio .... ")
    news_list_temp = []

    '''
    inizializzo i vari scraper
    '''
    scraper_list: [Scraper] = []
    yscraper: Scraper = YahooScraper()
    iscraper: Scraper = InvestingScraper()
    bcscraper: Scraper = BarChartScraper()
    fxscraper: Scraper = FxEmpireScraper()
    '''
    append degli scraper
    '''
    scraper_list.append(yscraper)
    scraper_list.append(iscraper)
    scraper_list.append(bcscraper)
    scraper_list.append(fxscraper)

    '''
    recupero le news più recenti già presenti nella knowledge base
    '''
    news_doc_db = get_last_100_news_titles()
    title_to_remove = []
    if news_doc_db and len(news_doc_db) > 0:
        title_to_remove = [ndb['title'] for ndb in news_doc_db]
    '''
    scraping di tutte le news dalla relativa fonte
    '''
    for s in scraper_list:
        print(f"scraping nuova fonte")
        news_list = s.search_for_news()

        '''
        se non ho news da una fonte esco
        '''
        if len(news_list) == 0: sys.exit(2)

        '''
        arricchisco ogni news trovata
        '''
        for idx, n in enumerate(news_list):
            print_progress(idx + 1, len(news_list))
            # arricchisco e aggiungo la news solo se non già presente a db
            if n.title.strip() not in title_to_remove:
                print("arricchisco la news: " + n.link)
                news_list_temp.append(s.enrich_news(n))
                '''
                aggiorno la tabella dei titoli per scartare eventuali news uguali derivati da futuri scraping
                '''
                write_news_title(n)
            else:
                print("non arricchisco, già presente: " + n.link)

    '''
    ripulisco dalle news che non sono state arricchite
    '''
    news_list_enriched = [n for n in news_list_temp if n.body != ""]

    '''
    se non ho news arricchite esco
    '''
    if len(news_list_enriched) == 0: sys.exit(1)

    print(f"{len(news_list_enriched)} news arricchite")

    '''
    chiamo llm per avere il peso delle news ai fini dell'analisi. l'informazione viene salvata a db
    '''
    news_list_enriched = run_weight_analysis(news_list_enriched)

    '''
    write updated news to tinydb
    prima cancello le news eventualmente presente con la stessa data
    dato che il programma viene eseguito più volte al giorno per non duplicare le news a db cancello le news odierne
    eventualmente già salvate e le riscrivo (è da aggiornare e scrivere solo le news non presenti a db)
    '''
    # delete_doc_news_by_tile(news_list_enriched)
    write_news_list(news_list_enriched)

    '''
    scrivo le news anche nel relativo file markdown
    '''
    # write_news_to_markdown_file(news_list_enriched)


'''
metodo che recupera le news più recenti ed esegue l'analisi finanziaria tramite llm tramite prompt enrichment
'''


def retrieve_financial_analysis_prompt():
    '''
    recupero le news per effettuare l'analisi
    '''
    news_list_retrieved = get_last_news_num()
    print(f"recuperate {str(len(news_list_retrieved))} news")


    '''
    recupero i dati di chiusura storici
    '''
    hist_data: [Data] = get_crude_oil_historical_data()

    '''
    eseguo l'analisi di trend
    '''
    current_price = get_wti_price()

    '''
    eseguo l'analisi di trend
    '''
    analysis = run_financial_analysis(news_list_retrieved, current_price, hist_data)


    # TODO da cambiare, prima calcolo tutti i dati di analisi e poi scrivo il record invece di prima scrivere e poi
    # aggiornare il record con i dati che mi mancano. Invece di fare la query a db devo passare l'oggetto analisi
    # appena creato
    '''
    persistenza dell'analisi su db
    '''
    #delete_doc_analysis_current_date()
    enrich_analysis(hist_data, analysis)
    write_analysis(analysis)
    # write_to_file_analysis(str_out)

    '''
    aggiorna le analisi con i dati relativi a volume, differenza di prezzo, apertura e chiusura
    '''
    # update_analysis_real_index(hist_data)


'''
metodo che recupera le news più recenti ed esegue l'analisi finanziaria tramite llm tramite prompt RAG
'''


def retrieve_financial_analysis_rag():
    '''
    recupero le news per effettuare l'analisi
    '''
    news_list_retrieved = get_last_news_num()
    print(f"recuperate {str(len(news_list_retrieved))} news")

    '''
    eseguo l'analisi di trend
    '''
    analysis = run_financial_analysis(news_list_retrieved)

    '''
    persistenza dell'analisi su db
    '''
    write_analysis(analysis)
    # write_to_file_analysis(str_out)

    '''
    aggiorna le analisi con i dati di chiusura
    '''
    update_analysis_real_index()