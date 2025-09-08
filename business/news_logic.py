from datetime import datetime

from do.news import News


def create_markdown_from_json(results) -> [News]:
    return_list = []
    for item in results:
        date_obj = datetime.fromisoformat(item["date"])
        news = News(item["title"],
                    item["link"],
                    item["body"],
                    item["source"],
                    date_obj.__str__())
        news.analysis = item["analysis"]
        return_list.append(news)

    return return_list

