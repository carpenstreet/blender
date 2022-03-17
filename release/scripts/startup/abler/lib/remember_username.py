from typing import Optional
import bpy, pickle, os


path = bpy.utils.resource_path("USER")
path_cookiesFolder = os.path.join(path, "cookies")
path_cookies_username = os.path.join(path_cookiesFolder, "username")


def remember_username(username: str) -> None:
    with open(path_cookies_username, "wb") as cookies_username:
        pickle.dump(username, cookies_username)


def read_remembered_username() -> Optional[str]:
    if not os.path.isfile(path_cookies_username):
        return ""
    with open(path_cookies_username, "rb") as fr:
        data = pickle.load(fr)
    return data


def delete_remembered_username() -> None:
    if os.path.isfile(path_cookies_username):
        os.remove(path_cookies_username)


def read_remembered_checkbox() -> bool:
    return os.path.isfile(path_cookies_username)
