from business.database.hist_data_query import get_vol_momentum
from do.hist_data import Data


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


def get_volume_average(hist_data: list[Data]) -> float:
    """
    ritorna la media dei volumi dei dati storici passati in input
    :param hist_data:
    :return:
    """
    volume_average = sum(convert_string_to_number(o.volume) for o in hist_data) / len(hist_data)
    print(f"Volume average: {volume_average}")
    return volume_average


def normalized_volume(hist_data: list[Data], current_price: float) -> float:
    """
    calclo i volume normalizzato secondo la formula Volume / Volume Medio Storico * Segno(variazione prezzo) * coefficiente
    :param hist_data:
    :param current_price:
    :return:
    """
    # coefficiente da correggere
    coef = 10
    average = get_vol_momentum()
   # determino il segno del movimento (riazista, ribassista, neutro
    price_var = 0
    if float(current_price) - float(hist_data[0].quotation_open.replace(",",".")) > 0.1:
        price_var = 1
    elif float(current_price) - float(hist_data[0].quotation_open.replace(",",".")) < -0.1:
        price_var = -1
    print(f"Price var: {price_var}")
    normalized_volume_val = convert_string_to_number(hist_data[0].volume) / average * price_var * coef
    print(f"normalized_volume_val = {normalized_volume_val}")
    return normalized_volume_val


def momentum(price_current: float, price_forecast: float, p_open: float) -> float:
    '''
    funzione che calcolo il momenutum, indicatore cruciale per l'indicazione
    :param p_open:
    :param price_current:
    :param price_forecast:
    :return:
    '''
    delta_curr = (price_current - p_open) / p_open
    delta_for = (price_forecast - price_current) / price_current
    momentum_val: float = delta_for*0.7 + delta_curr*0.3
    print(f"momentum_val = {momentum_val}")
    return momentum_val

def limita_compatto(valore, minimo, massimo):
    """
    Limita un valore all'interno dell'intervallo [minimo, massimo] usando min/max.
    """
    # 1. max(valore, minimo) assicura che il risultato non sia mai inferiore a 'minimo'.
    # 2. min(risultato_1, massimo) assicura che il risultato non sia mai superiore a 'massimo'.
    return max(minimo, min(valore, massimo))


def sentiment(short_term: str, mid_term: str) -> float:
    '''
    funzione che restituisce una sintesi del sentiment tra breve e medio
    :param short_term:
    :param mid_term:
    :return:
    '''
    weight = {"2":20, "1":15, "-1":-15, "-2":-20, "0":0}
    short_const = 10
    mid_const = 3
    sentiment_val: float = (weight[str(short_term)]*short_const) + (weight[str(mid_term)]*mid_const)
    print(f"sentiment_val = {sentiment_val}")
    return sentiment_val

def get_advice(pres_val: float, momentum_val: float, sentiment_val: float) -> float:
    advice_index: float = round((0.3*pres_val) + (0.6*momentum_val) + (0.1*sentiment_val),2)
    print(f"advice_index = {advice_index}")
    return advice_index