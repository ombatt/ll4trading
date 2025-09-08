from tinydb import TinyDB, Query


def initdb():
    db = TinyDB('db.json')
    news = db.table('news')
    analysis = db.table('analysis')