from datetime import datetime


class Data:
    def __init__(self, close: float, date: str, p_quotation: float, p_quotation_open: float, volume: str):
        self.close = close
        dt_object = datetime.strptime(date, '%d.%m.%Y').date()
        self.date = dt_object
        self.quotation = p_quotation
        self.quotation_open = p_quotation_open
        self.volume = volume
        # self.__str__()

    def __str__(self):
        print(f"close: {self.close}")
        print(f"date: {self.date}")
        return str(self.close) + " " + str(self.date)

    def to_dict(self):
        # Questo metodo converte l'istanza dell'oggetto in un dizionario
        return {
            "type": "historical data",
            "close_perc": self.close,
            "close_price": self.quotation,
            "date": self.date.strftime("%Y-%m-%d"),
            "description": "closing price day " + self.date.strftime("%Y-%m-%d"),
            "p_quotation": self.quotation,
            "p_quotation_open": self.quotation_open,
            "volume": self.volume
        }

    def to_markdown_string(self):
        return f"""\
                **Type:** historical quotation
                **Description**: on {self.date.strftime("%Y-%m-%d")} WTI closing price was {self.p_quota} 
                ---\n"""
