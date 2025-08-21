from sys import exit as sys_exit

from promptly_summary.ai import send2claude
from promptly_summary.cli import fetch_analytics, parse_args
from promptly_summary.common._io import perr
from promptly_summary.common.errors import ErrCode
from promptly_summary.slack import publish2slack


def main() -> None:
    days = parse_args()
    data = fetch_analytics("http://localhost:4200", days=days)
    if data is None:
        perr("there was an error fetching promptly data")
        sys_exit(ErrCode.FETCH_ERROR)

    msg = send2claude(data)
    published = publish2slack(msg)
    sys_exit(ErrCode.SUCCESS if published else ErrCode.SLACK_PUBLISH_ERROR)


if __name__ == "__main__":
    main()
