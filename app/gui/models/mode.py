from dataclasses import dataclass
from enum import StrEnum
from enum import auto


class Mode(StrEnum):
    ENCRYPT = auto()
    DECRYPT = auto()


@dataclass
class WindowModel:
    mode: Mode = Mode.ENCRYPT
    text: str = ""
    secret: str = ""
    image_path: str = ""
