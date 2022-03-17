import os
from typing import Optional
from dotenv import load_dotenv


def find_dotenv() -> Optional[str]:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    last_dir = None
    while last_dir != current_dir:
        check_path = os.path.join(current_dir, ".env")
        if os.path.isfile(check_path):
            return check_path

        parent_dir = os.path.abspath(os.path.join(current_dir, os.path.pardir))
        last_dir, current_dir = current_dir, parent_dir


load_dotenv(dotenv_path=find_dotenv())
