from requests import get


def get_ip() -> str:
    try:
        return get("https://api.ipify.org").text
    except ConnectionError:
        # If you get here, then some ipify exception occurred.
        print("Unable to reach the ipify service")
    except:
        # If you get here, some non-ipify related exception occurred.
        print("Non ipify related exception occured")
