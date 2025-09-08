from datetime import datetime


class News:
    def __init__(self, title: str, link: str, body: str, source: str, date: str, tp="news"):
        self.type = tp
        self.title = title
        self.link = link
        self.body = body
        self.source = source
        self.date = date
        if date is not None and date != "":
            dt_object = datetime.fromisoformat(date.replace('Z', '+00:00')).isoformat()
            self.date = dt_object
        self.analysis = None
        # self.__str__()

    def __str__(self):
        print(f"news_title:\n {self.title}")
        print(f"news_date:\n {self.date}")
        print(f"news_body: \n {self.body}")
        print(f"source:\n {self.source}")
        print(f"link:\n {self.link}")
        return self.source + " " + self.link + self.date + self.title + self.body

    def to_dict(self):
        # Questo metodo converte l'istanza dell'oggetto in un dizionario
        return {
            "type": self.type,
            "title": self.title,
            "source": self.source,
            "link": self.link,
            "date": self.date,
            "body": self.body,
            "analysis": self.analysis,
        }

    def to_dict_title(self):
        # Questo metodo converte l'istanza dell'oggetto in un dizionario
        return {
            "title": self.title
        }

    def to_markdown_string(self):
        return f"""\
                **type:** news
                **Title:** {self.title}
                **Date:** {self.date}
                **Source:** {self.source}
                **Body:** {self.body}
                ---\n"""
