from enum import StrEnum


class Style(StrEnum):
    PNK = "\033[38;2;255;121;198m"
    GRN = "\033[38;2;80;250;123m"
    PRP = "\033[38;2;189;147;249m"
    BLU = "\033[38;2;139;233;253m"
    YLW = "\033[38;2;241;250;140m"
    RES = "\033[0m"
    RED = "\033[91m"
    BLD = "\033[1m"
    DIM = "\033[2m"


def perr(msg: str) -> None:
    print(f"{Style.RED}{Style.BLD}Error:{Style.RES} {msg}")
