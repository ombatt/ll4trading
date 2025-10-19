import math

from tinydb import TinyDB, Query
from dateutil.utils import today
from datetime import datetime, timedelta
from business.database.database_constants import DB_FILE_PATH_2

def get_vol_momentum():
    """
    metodo che rapporta la media dei volumi all'intervallo dei 5 minuti più prossimo (arrotondamento per eccesso)
    :param vol_avg:
    :param minute:
    :return:
    """
    vol_avg: float = get_avg_h_volume()
    minute = datetime.now().minute
    res: float = math.ceil(minute / 5)
    vol_rap: float = vol_avg / 12 * res
    return round(vol_rap, 2)

def get_avg_h_volume(hour=None):
    """
    calcola la media delle ultime 2 settimane dei volumi nella fascia oraria corrente
    :param hour:
    :return:
    """
    if hour is None:
        hour_0 = datetime.now()
        hour_0 = hour_0.replace(minute=0, second=0, microsecond=0)
        hour = hour_0.strftime("%H:%M:%S")

    # recupero i documenti
    docs: list = read_last_2_weeks_hist_data(hour)

    # calcolo la media
    vol_amount: float = 0
    for doc in docs:
        vol_amount += doc['volume']
    vol_avg = vol_amount / len(docs)

    print("volume average: ", vol_avg)
    return vol_avg



def read_last_2_weeks_hist_data(hour: str):
    """
    estraggo i dati delle ultime due settimane
    :param hour:
    :return:
    """
    # Carica il database
    db = TinyDB(DB_FILE_PATH_2)
    hist_database = db.table('historical_data')
    Data = Query()

    # Calcola la data di due settimane fa
    two_weeks_ago = datetime.now().date() - timedelta(weeks=2)

    # Filtra i documenti
    results = hist_database.search(
        (Data.time == hour) &
        (Data.date.test(lambda d: datetime.strptime(d, "%Y-%m-%d").date() >= two_weeks_ago))
    )

    return results