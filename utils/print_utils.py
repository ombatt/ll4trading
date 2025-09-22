import datetime
import textwrap

from business.database.analysis_query import read_last_analysis, read_last_analysis_dict
from do.analysis import Analysis
import pandas as pd
import matplotlib.pyplot as plt

'''
metodo di print dell'analisi
'''


def print_analysis(an):
    print("short : " + str(an['p_short']))
    print("medium: " + str(an['p_medium']))
    print("description:")
    righe = textwrap.wrap(an['summary'], width=100)
    for r in righe:
        print(r)

'''
metodo di print generico dell'avanzamento
'''

def print_progress(idx_cur, idx_all):
    '''times = int(round((idx_cur / idx_all * 100),0))
    str_print = "+" * times + " " + str(times) + "%"
    print(f"{str_print}")'''
    print(str(idx_cur) + " di " + str(idx_all))


def print_analysis_det():
    an_list: [Analysis] = read_last_analysis()
    #print(f"data\tora\tshort\tmedium\tcurrent_price\tclose_price\tclose_perc:")
    for an in an_list:
        date_object = datetime.datetime.fromisoformat(an.date)
        formatted_string = date_object.strftime("%d-%m-%Y\t%H:%M:%S")
        price_dif = round(an.price_dif,2) if an.price_dif is not None and an.price_dif != '' else 0
        p_open = an.p_open if an.p_open is not None and an.p_open != '' else 0
        volume = an.volume if an.volume is not None and an.volume != '' else 0
        print(f"ora: {formatted_string}\tshort: {an.p_short}\tmedium: {an.p_medium}\topen: {p_open}"
              f"\tcurrent: {an.current_price}\tdiff: {str(price_dif)}\tadvice: {an.advice}\tvolume: {volume}"
              f"\tclose: {an.close_price}\tclose %: {an.close_perc}")
        #print(f"{formatted_string}\t{an.p_short}\t{an.p_medium}\t{an.current_price}\t{an.close_price}\t{an.close_perc}")


def print_analysis_graph():
    an_list: [{}] = read_last_analysis_dict()
    # Converte in DataFrame
    df = pd.DataFrame(an_list)

    # Conversioni
    df["date"] = pd.to_datetime(df["date"])
    df["price_dif"] = pd.to_numeric(df["price_dif"], errors="coerce").round(2)
    df["p_short"] = pd.to_numeric(df["p_short"], errors="coerce")

    # Ordiniamo per data
    df = df.sort_values("date")

    # Creiamo la figura
    fig, ax1 = plt.subplots(figsize=(10, 5))

    # Primo asse (price_dif)
    ax1.plot(df["date"], df["price_dif"], color="tab:blue", marker="o", label="Price Dif")
    ax1.set_xlabel("Data")
    ax1.set_ylabel("Price Dif", color="tab:blue")
    ax1.tick_params(axis="y", labelcolor="tab:blue")

    # Secondo asse (p_short)
    ax2 = ax1.twinx()
    ax2.plot(df["date"], df["p_short"], color="tab:red", marker="s", label="p_short")
    ax2.set_ylabel("p_short", color="tab:red")
    ax2.tick_params(axis="y", labelcolor="tab:red")

    # Titolo e griglia
    plt.title("Andamento Price Dif e p_short nel tempo")
    fig.tight_layout()
    plt.show()
