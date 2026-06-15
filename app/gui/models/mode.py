from dataclasses import dataclass
from enum import StrEnum
from enum import auto


class Mode(StrEnum):
    HIDE = auto()
    REVEAL = auto()


@dataclass
class WindowModel:
    mode: Mode = Mode.HIDE
    text: str = ""
    secret: str = ""
    image_path: str = ""
