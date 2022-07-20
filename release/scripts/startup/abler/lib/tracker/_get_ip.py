from typing import Optional
from requests import get


def get_ip() -> Optional[str]:
    try:
        return get("https://api.ipify.org", timeout=3).text
    except ConnectionError:
        print("Unable to reach the ipify service")
    except:
        print("Non ipify related exception occured")


user_ip = get_ip()
