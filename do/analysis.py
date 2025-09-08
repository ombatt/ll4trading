from datetime import datetime


class Analysis:
    def __init__(self, p_short: str, p_medium: str, summary: str, date: str, current_price="", close_price="", close_perc="", price_dif="", advice="", p_open="", volume=""):
        self.p_short = p_short
        self.p_medium = p_medium
        self.summary = summary
        dt_object = datetime.fromisoformat(date.replace('Z', '+00:00')).isoformat()
        self.date = dt_object
        # quotazione dell'indice al momento dell'analisi
        self.current_price = current_price
        self.close_price = close_price
        self.close_perc = close_perc
        self.price_dif = price_dif
        self.advice = advice
        self.p_open = p_open
        self.volume = volume

    def __str__(self):
        print(f"p_short:\n {self.p_short}")
        print(f"p_medium:\n {self.p_medium}")
        print(f"date:\n {self.date}")
        print(f"summary:\n {self.summary}")
        return str(self.p_short) + " " + str(self.p_medium) + str(self.date) + str(self.summary)

    def to_dict(self):
        # Questo metodo converte l'istanza dell'oggetto in un dizionario
        return {
            "p_short": self.p_short,
            "p_medium": self.p_medium,
            "date": self.date,
            "summary": self.summary,
            "current_price": self.current_price,
            "close_price": self.close_price,
            "close_perc": self.close_perc,
            "price_dif": self.close_perc,
            "advice": self.close_perc,
            "p_open": self.p_open,
            "volume": self.volume
        }
