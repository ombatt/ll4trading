import json
import os
from datetime import date
from typing import List

from dotenv import load_dotenv
import google.generativeai as genai

from do.analysis import Analysis
from do.hist_data import Data
from utils.utils import clean_json_out, map_json_to_analysis, map_json_to_news_list
from utils.print_utils import print_progress
from do.news import News

'''
rimuove le news che non hanno rilevanza ai fini dell'analisi
'''


def filter_news(news_list: [News]) -> [News]:
    return_news_list: List[News] = []
    # filtro le dalla lista le notizie che hanno analisi = 0 e quindi non sono significative
    return_news_list = [n for n in news_list if int(n.analysis) > 0]
    print(f"news con peso > 0: {str(len(return_news_list))}")
    return return_news_list


'''
prima analisi llm per avere indicazione del trend
'''


def run_weight_analysis(news_list_temp: [News]) -> [News]:
    '''
    prendo la lista delle notizie e la sottopongo all'analisi gemini a stock di 4 news
    altrimenti l'output di gemini è troppo grande da gestire come json
    '''
    print("chiamo gemini per avere il peso delle news")
    news_list_for_analysis: List[News] = []
    i_max_i: int = 100
    check: bool = True
    idx: int = 0
    i_max: int = 0
    news_list_final: [News] = []
    while check:
        if idx + i_max_i > len(news_list_temp):
            i_max = len(news_list_temp)
            check = False
        else:
            i_max = idx + i_max_i

        if len(news_list_temp) < idx + i_max_i:
            print_progress(len(news_list_temp), len(news_list_temp))
        else:
            print_progress(idx + i_max_i, len(news_list_temp))
        '''
        chiamata a gemini per avere il peso della news
        '''
        # str_out: str = llm_weight_analysis(news_list_temp[idx:i_max])

        '''
        trasformo in lista oggetti News
        '''
        # news_list_final = map_json_to_news_list(str_out)

        # rimappo la lista di news originale con l'informazione relativa al peso appena calcolata
        news_list_tmp_en_an = llm_weight_analysis_title(news_list_temp[idx:i_max])
        news_list_tmp_en_an_dic = {nt.title: nt.analysis for nt in news_list_tmp_en_an}
        for n in news_list_temp:
            if n.title in news_list_tmp_en_an_dic:
                n.analysis = news_list_tmp_en_an_dic[n.title]

        '''
        aggiungo alla lista News finale
        '''
        # news_list_for_analysis.extend(news_list_final)

        '''
        aggiorno indice
        '''
        idx = i_max

    '''
    filtro le news che hanno analysis = 0
    '''
    # news_list_for_analysis = filter_news(news_list_for_analysis)
    news_list_for_analysis = filter_news(news_list_temp)

    return news_list_for_analysis


'''
metodo che chiama llm per avere l'analisi delle news
'''


def run_financial_analysis(news_list: [News], current_price: str, hist_data: [Data]) -> Analysis:
    str_out = llm_source_analysis(news_list, current_price, hist_data)
    analysis: Analysis = map_json_to_analysis(str_out)
    analysis.current_price = current_price

    return analysis


'''
vecchio metodo che eseguiva l'analisi
'''


def run_analysis_old(news_list_temp: [News]):
    '''
    prendo la lista delle notizie e la sottopongo all'analisi gemini a stock di 4 news
    altrimenti l'output di gemini è troppo grande da gestire come json
    '''
    print("chiamo gemini per avere il peso delle news")
    news_list_for_analysis: List[News] = []
    i_max_i: int = 1
    check: bool = True
    idx: int = 0
    i_max: int = 0
    news_list_final: [News] = []
    while check:
        if idx + i_max_i > len(news_list_temp):
            i_max = len(news_list_temp)
            check = False
        else:
            i_max = idx + i_max_i

        print_progress(idx + i_max_i, len(news_list_temp))
        '''
        chiamata a gemini per avere il peso della news
        '''
        str_out: str = llm_weight_analysis(news_list_temp[idx:i_max])

        '''
        trasformo in lista oggetti News
        '''
        news_list_final = map_json_to_news_list(str_out)

        '''
        aggiungo alla lista News finale
        '''
        news_list_for_analysis.extend(news_list_final)

        '''
        aggiorno indice
        '''
        idx = i_max

    '''
    filtro le news che hanno analysis = 0
    '''
    news_list_for_analysis = filter_news(news_list_for_analysis)

    '''
    chiamo llm per analisi
    '''
    str_out = llm_source_analysis(news_list_for_analysis)
    analysis: Analysis = map_json_to_analysis(str_out)

    return news_list_for_analysis, analysis


'''
metodo per ottenere il modello AI
'''


def get_geai():
    load_dotenv()
    API_KEY = os.getenv("GOOGLE_API_KEY")
    if API_KEY == "" or not API_KEY:
        print(
            "ERRORE: Inserisci la tua chiave API Gemini. Ottienila da Google AI Studio (aistudio.google.com/app/apikey).")
        print("Esci e modifica il codice.")
        exit()
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
    return model


'''
metodo che integra ogni news con l'informazione relativa al peso della news ai fini dell'analisi del trend
'''


def llm_weight_analysis(news_list: List[News]) -> str:
    model = get_geai()

    news_list_obj = [news.to_dict() for news in news_list]
    json_string = json.dumps(news_list_obj, indent=len(news_list))

    prompt = f"""Given as input a list of news items in json format, you must tell me whether you consider them useful for carrying out " \
                "an analysis for short-term investments in ETFs relating to oil (WTI, crude OIL)." \
                "You must provide the output by enriching the json provided as input with a new "analysis" attribute within " \ 
                which you report 0 if you don't consider it useful, 1 if you consider it partially useful and 2 if " \
                you consider it useful. The output must be a valid json format. Here you can find the list of news: {json_string}"""

    try:
        # Genera il contenuto basandosi sul prompt
        response = model.generate_content(prompt)

        # rimuovo i primi caratteri della string json '''json e gli ultimi ''' ```json ```
        # Stampa il risultato
        str_out = clean_json_out(response.text)
        # print("Analisi: " + str_out)
        '''str_out = response.text[7:]
        str_out = str_out[:-4]'''
        # print(str_out)
        return str_out
    except Exception as e:
        print(f"Si è verificato un errore durante la chiamata all'API: {e}")


'''
metodo che integra ogni news con l'informazione relativa al peso della news ai fini dell'analisi del trend
uguale al precedente ma restituisce solamente l'indicatore e il titolo della news in output
'''


def llm_weight_analysis_title(news_list: List[News]) -> [News]:
    model = get_geai()

    news_list_obj = [news.to_dict() for news in news_list]
    json_string = json.dumps(news_list_obj, indent=len(news_list))

    prompt = f"""
    ### Role
    You are an expert energy markets analyst with deep knowledge of the factors influencing crude oil (WTI) prices.
    
    ### Instructions  
    **Analysis:** Analyze the following list of news items in JSON format.  
    **Weighting:** Assess the importance of each news item. Assigns an indicator to each news item that indicates the relevance and 
    importance of the news in order to conduct a forecast analysis of the price of the WTI crude oil (0=low, 1=medium, 2=high).
    **Output** Provide the response strictly in JSON format. Do not include any other text or explanation outside of the JSON.
    
    ### Output Schema
    The JSON must have the following structure:
    ```json
    {{
      "title": "title of the news given in input",
      "analysis": "relevance of the news for forecast analysis (values: 0, 1, 2). Value must be provided as integer value, not string",
    }}
    
    ### Input data in JSON format:: {json_string}"""

    try:
        # Genera il contenuto basandosi sul prompt
        response = model.generate_content(prompt)

        # rimuovo i primi caratteri della string json '''json e gli ultimi ''' ```json ```
        # Stampa il risultato
        str_out = clean_json_out(response.text)
        news_list_final = map_json_to_news_list(str_out)
        # print(str_out)
        return news_list_final
    except Exception as e:
        print(f"Si è verificato un errore durante la chiamata all'API: {e}")


'''
metodo che fornisce l'analisi del trend in base alle news fornite
'''


def llm_source_analysis(news_list: List[News], current_price: str, hist_data: [Data]) -> str:
    # ottengo il modello
    model = get_geai()

    # data odierna
    today = date.today()
    date_string = today.strftime('%Y-%m-%d')

    # converto le news in stringa json per il prompt
    news_list_obj = [news.to_dict() for news in news_list]
    json_string_news = json.dumps(news_list_obj, indent=len(news_list))
    json_string_news = json_string_news[1:-1]

    # converto i dati storici in stringa json per il prompt
    data_list_obj = [data.to_dict() for data in hist_data]
    json_string_data_hist = json.dumps(data_list_obj, indent=len(hist_data))
    json_string_data_hist = json_string_data_hist[1:-1]

    json_string_final = "[" + json_string_news + "," + json_string_data_hist + ",{\"current_date\": \"" + date_string + "\"}" + ",{\"current_oil_price\": \"" + current_price + "\"}]"

    prompt = f"""### Role
    You are an expert energy markets analyst with deep knowledge of the factors influencing crude oil (WTI) prices.
    
    ### Instructions
    1.  **Analysis:** Analyze the following list of news items in JSON format.
    2.  **Weighting:** Assess the importance of each news item using the analysis field (0=low, 1=medium, 2=high). Give higher priority to more recent news, based on the news_date field.
    3.  **Forecast:** Based on the analysis, predict the trend of WTI crude oil prices in the short (in this case short means daily period) and medium term (in this case medium means weekly period).
    4.  **Output:** Provide the response strictly in JSON format. Do not include any other text or explanation outside of the JSON.
    
    ### Output Schema
    The JSON must have the following structure:
    ```json
    {{
      "p_short": "short-term forecast (values: -2, -1, 0, 1, ",
      "p_medium": "medium-term forecast (values: -2, -1, 0, 1, 2)",
      "summary": "summary in English of the reasoning",
      "summary_italian": "summary in Italian of the reasoning"
    }}
    
    ### Input data in JSON format:
    
    {json_string_final}

"""

    try:
        # Genera il contenuto basandosi sul prompt
        # print(prompt)
        response = model.generate_content(prompt)

        # Stampa il risultato
        # rimuovo i primi caratteri della string json '''json e gli ultimi '''
        str_out = clean_json_out(response.text)
        return str_out
    except Exception as e:
        print(f"Si è verificato un errore durante la chiamata all'API: {e}")
