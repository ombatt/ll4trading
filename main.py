import os

from dotenv import load_dotenv

from command import newsCommand
from configuration.configuration import Configuration
from utils.print_utils import print_analysis_det, print_time

load_dotenv()

# Imposta la chiave API
os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_time("INIZIO ESECUZIONE")

    configuration: Configuration = Configuration()

    if configuration.config["read_news_flag"]:
        newsCommand.retrieve_news()

    newsCommand.retrieve_financial_analysis_prompt(configuration)
    # hist_data: [Data] = get_crude_oil_historical_data()
    # update_analysis_real_index(hist_data) ..
    print_analysis_det()
    print_time("FINE ESECUZIONE")
