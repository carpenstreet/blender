from enum import Enum, auto


class StateUI(Enum):
    check = auto()
    no_release = auto()
    update_launcher = auto()
    update_abler = auto()
    execute = auto()
    error = auto()
