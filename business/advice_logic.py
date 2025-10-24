from business.database.hist_data_query import get_vol_momentum
from configuration.configuration import Configuration
from do.hist_data import Data
from newsretriever.api_price import get_volume_mean


def convert_string_to_number(s):
    """
    Converte una stringa come '102,75K' o '1.2M' in un numero float.
    Supporta i suffissi:
    - K = migliaia
    - M = milioni
    - B = miliardi
    """
    # Rimuove spazi e sostituisce la virgola con il punto
    s = s.strip().replace(',', '.')

    multiplier = 1
    if s.endswith('K'):
        multiplier = 1_000
        s = s[:-1]
    elif s.endswith('M'):
        multiplier = 1_000_000
        s = s[:-1]
    elif s.endswith('B'):
        multiplier = 1_000_000_000
        s = s[:-1]

    try:
        return float(s) * multiplier
    except ValueError:
        raise ValueError(f"Formato non valido: '{s}'")


'''
def get_volume_average(hist_data: list[Data]) -> float:
    """
    ritorna la media dei volumi dei dati storici passati in input
    :param hist_data:
    :return:
    """
    volume_average = sum(convert_string_to_number(o.volume) for o in hist_data) / len(hist_data)
    print(f"Volume average: {volume_average}")
    return volume_average
'''

def normalized_volume(hist_data_volume: str, hist_data_open: str, current_price: float) -> float:
    """
    calclo i volume normalizzato secondo la formula Volume / Volume Medio Storico * Segno(variazione prezzo) * coefficiente
    :param hist_data_open:
    :param hist_data_volume:
    :param current_price:
    :return:
    """
    configuration: Configuration = Configuration()

    max_val = configuration.config["normalized_volume_max_val"]
    # coefficiente da correggere
    coef = configuration.config["normalized_volume_coef"]
    average = get_volume_mean()
    hist_data_volume = convert_string_to_number(hist_data_volume)
    print(f"hist_data_volume: {hist_data_volume}")
   # determino il segno del movimento (rialzista, ribassista, neutro
    price_var = 0
    if float(current_price) - float(hist_data_open.replace(",",".")) > configuration.config["normalized_volume_positive_limit"]:
        price_var = 1
    elif float(current_price) - float(hist_data_open.replace(",",".")) < configuration.config["normalized_volume_negative_limit"]:
        price_var = -1
    print(f"Price var: {price_var}")
    normalized_volume_val = hist_data_volume / average * price_var * coef
    normalized_volume_val = limita_compatto(normalized_volume_val / max_val)
    print(f"normalized_volume_val = {normalized_volume_val}")
    return normalized_volume_val


def momentum(price_current: float, price_forecast: float, p_open: float) -> float:
    """
    funzione che calcolo il momenutum, indicatore cruciale per l'indicazione
    :param p_open:
    :param price_current:
    :param price_forecast:
    :return:
    """
    configuration: Configuration = Configuration()
    max_val: float = configuration.config["momentum_max_val"]
    delta_curr = (price_current - p_open) / p_open
    delta_for = (price_forecast - price_current) / price_current
    momentum_val: float = delta_for * configuration.config["momentum_delta_forecast"] + delta_curr * configuration.config["momentum_delta_current"]
    momentum_val = limita_compatto(momentum_val / max_val)
    print(f"momentum_val = {momentum_val}")
    return momentum_val

def limita_compatto(valore, minimo: float=-1, massimo: float=1):
    """
    Limita un valore all'interno dell'intervallo [minimo, massimo] usando min/max.
    """
    # 1. max(valore, minimo) assicura che il risultato non sia mai inferiore a 'minimo'.
    # 2. min(risultato_1, massimo) assicura che il risultato non sia mai superiore a 'massimo'.
    return max(minimo, min(valore, massimo))


def sentiment(short_term: str, mid_term: str) -> float:
    """
    funzione che restituisce una sintesi del sentiment tra breve e medio
    :param short_term:
    :param mid_term:
    :return:
    """
    configuration: Configuration = Configuration()
    max_val: float = configuration.config["sentiment_max_val"]

    weight = {"2":configuration.config["setiment_matrix_2"],
              "1":configuration.config["setiment_matrix_1"],
              "-1":configuration.config["setiment_matrix_m1"],
              "-2":configuration.config["setiment_matrix_m2"],
              "0":configuration.config["setiment_matrix_0"]}

    short_const = configuration.config["sentiment_short_const"]
    mid_const = configuration.config["sentiment_middle_const"]

    sentiment_val: float = (weight[str(short_term)]*short_const) + (weight[str(mid_term)]*mid_const)
    sentiment_val = limita_compatto(sentiment_val/max_val)
    print(f"sentiment_val = {sentiment_val}")
    return sentiment_val

def get_advice(pres_val: float, momentum_val: float, sentiment_val: float) -> float:
    """
    funzione che calcolo l'indice advice complessivo
    :param pres_val:
    :param momentum_val:
    :param sentiment_val:
    :return:
    """
    configuration: Configuration = Configuration()

    advice_index: float = round((configuration.config["advice_pres_val"]*pres_val) +
                                (configuration.config["advice_momentum_val"]*momentum_val) +
                                (configuration.config["advice_sentiment_val"]*sentiment_val),2)

    print(f"advice_index = {advice_index}")
    return advice_index