from typing import Optional
from requests import get
import platform


def get_ip() -> Optional[str]:
    try:
        # https://www.ipify.org/에서 제공하는 IPv4 / IPv6 Universal API를 사용
        # 참조: https://carpenstreet.atlassian.net/browse/SWTASK-84
        return get("https://api64.ipify.org", timeout=3).text
    except ConnectionError:
        print("Unable to reach the ipify service")
    except Exception as e:
        print("Non ipify related exception occurred.\n", e)


def get_os() -> str:
    """
    :return: The name of the operating system and architecture.
    """
    full_info = platform.uname()
    if full_info.system == "Darwin":
        return "MacOS Intel" if full_info.machine == "x86_64" else "MacOS Silicon"
    elif full_info.system == "Windows":
        return "Windows"
    else:
        return "Unknown"


user_ip = get_ip()
user_os = get_os()
