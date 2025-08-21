from enum import IntEnum, auto


class ErrCode(IntEnum):
    SUCCESS = auto()
    INVALID_ARGS = auto()
    FETCH_ERROR = auto()
    MISSING_API_KEY = auto()
    MISSING_WEBHOOK = auto()
    SLACK_PUBLISH_ERROR = auto()

