from typing import Optional
from requests import get


def get_ip() -> Optional[str]:
    try:
        # https://www.ipify.org/에서 제공하는 IPv4 / IPv6 Universal API를 사용
        # 참조: https://carpenstreet.atlassian.net/browse/SWTASK-84
        return get("https://api64.ipify.org", timeout=3).text
    except ConnectionError:
        print("Unable to reach the ipify service")
    except:
        print("Non ipify related exception occured")


user_ip = get_ip()
