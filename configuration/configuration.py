import json


class Configuration:
    def __init__(self):
        self.nome_file = './configuration/conf.json'
        with open(self.nome_file, 'r', encoding='utf-8') as file:
            # 2. Carica il contenuto JSON in una variabile Python
            self.config = json.load(file)