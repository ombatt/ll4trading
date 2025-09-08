'''
def scraper_factory(news_list: [News]) -> [News]:
    # istanzio il driver (uguale per tutti gli scraper)
    driver = get_driver()

    # lista di news che viene arricchita con le info complete
    news_list_temp: [News] = []
    # lista di news che viene scartata in quanto non c'è lo scraper
    news_list_shifted: [News] = []

    # variabile per debug e impostare un limite alle notizie
    check: int = 0
    # parso tutta la lista di news
    for n in news_list:
        # imposto limite a 50 news
        if check > 50:
            break
        scraper: Scraper = None
        if "yahoo" in n.link:
            scraper: Scraper = YahooFinanceScraper()
        elif "financialpost" in n.link:
            scraper: Scraper = FinancialPostScraper()
        elif "barchart" in n.link:
            scraper: Scraper = BarchartScraper()
        elif "etfdailynews" in n.link:
            scraper: Scraper = EtfDailyNewsScraper()
        elif "oilprice.com" in n.link:
            scraper: Scraper = OilPriceScraper()
        elif "abcnews" in n.link:
            scraper: Scraper = AbcNewsScraper()
        else:
            news_list_shifted.append(n.link)

        # procedo con lo scraping specifico
        if scraper:
            scraper.get_news(n, driver)
            print(f"news aggiornata: {n.body}")
            news_list_temp.append(n)
            check += 1

    # close selenium driver
    driver.close()
    return news_list_temp, news_list_shifted

'''