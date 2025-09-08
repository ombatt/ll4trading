
from datetime import datetime, timedelta
from datetime import date


'''
funzione di ricerca che restituisce i documenti che hanno il campo data uguale a oggi
'''


def is_same_date(stored_date_string, is_today=True):
    try:
        # Parse the stored string into a datetime object
        stored_date_obj = datetime.strptime(stored_date_string, '%Y-%m-%dT%H:%M:%S.%f%z')

        # Parse the search string into a date object
        # The date string you want to search for (we only care about the date part)
        today = date.today()
        search_date_string = today.strftime('%Y-%m-%d')
        search_date_obj = datetime.strptime(search_date_string, '%Y-%m-%d').date()

        # Compare the date parts (year, month, day)
        return stored_date_obj.date() == search_date_obj
    except Exception as ex:
        # Handle cases where the stored string is not in the expected format '2025-07-29T00:21:19+00:00'
        print("eccezione " + ex.__str__())
        return False


'''
restituisce la data di ieri
'''


def get_yesterday():
    today = date.today()
    one_day = timedelta(days=1)
    # Subtract one day from today's date to get yesterday's date
    yesterday = today - one_day
    search_date_string = yesterday.strftime('%Y-%m-%d')
    search_date_obj = datetime.strptime(search_date_string, '%Y-%m-%d').date()
    return search_date_obj


'''
restituisce la data di oggi
'''


def get_today():
    today = date.today()
    search_date_string = today.strftime('%Y-%m-%d')
    search_date_obj = datetime.strptime(search_date_string, '%Y-%m-%d').date()
    return search_date_obj



'''
funzione di ricerca che restituisce i documenti che hanno il campo data uguale a ieri
'''


def is_yesterday_date(stored_date_string, is_today=True):
    try:
        # Parse the stored string into a datetime object
        stored_date_obj = datetime.strptime(stored_date_string, '%Y-%m-%dT%H:%M:%S%z')  # %Y-%m-%dT%H:%M:%S
        # Compare the date parts (year, month, day)
        return stored_date_obj.date() == get_yesterday()
    except Exception as ex:
        # provo con 2 formati perchè sembra che l'api ogni tanto restituisca la data delle news con formati diversi
        print("eccezione " + ex.__str__() + "provo con altro formato")
        try:
            stored_date_obj = datetime.strptime(stored_date_string, '%Y-%m-%dT%H:%M:%S')
            # Compare the date parts (year, month, day)
            return stored_date_obj.date() == get_yesterday()
        except Exception as ex:
            print("eccezione finale " + ex.__str__())


def is_today_date(stored_date_string, is_today=True):
    try:
        # Parse the stored string into a datetime object
        stored_date_obj = datetime.strptime(stored_date_string, '%Y-%m-%dT%H:%M:%S%z')  # %Y-%m-%dT%H:%M:%S
        # Compare the date parts (year, month, day)
        return stored_date_obj.date() == get_today()
    except Exception as ex:
        # provo con 2 formati perchè sembra che l'api ogni tanto restituisca la data delle news con formati diversi
        print("eccezione " + ex.__str__() + "provo con altro formato")
        try:
            stored_date_obj = datetime.strptime(stored_date_string, '%Y-%m-%dT%H:%M:%S')
            # Compare the date parts (year, month, day)
            return stored_date_obj.date() == get_yesterday()
        except Exception as ex:
            print("eccezione finale " + ex.__str__())
