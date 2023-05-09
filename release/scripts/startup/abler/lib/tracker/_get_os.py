import platform


def get_os() -> str:
    """
    Returns the name of the operating system and architecture.
    :return: The name of the operating system and architecture.
    """
    full_info = platform.uname()
    if full_info.system == "Darwin":
        return "MacOS Intel" if full_info.machine == "x86_64" else "MacOS Silicon"
    elif full_info.system == "Windows":
        return "Windows"
    else:
        return "Unknown"


user_os = get_os()
