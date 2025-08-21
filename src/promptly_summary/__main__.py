from sys import exit as sys_exit

from promptly_summary.ai import send2claude
from promptly_summary.cli import fetch_analytics, parse_args
from promptly_summary.common.errors import ErrCode
from promptly_summary.common.io import perr
from promptly_summary.publishers import parse_ai_response, publish_to_dashboard, publish_to_slack


def main() -> None:
    days = parse_args()
    print("Attempting to fetch analytics ...")
    data = fetch_analytics(days)
    if data is None:
        perr("no promptly data found!")
        sys_exit(ErrCode.FETCH_ERROR)

    # Get AI response in standard format
    print("Attempting to analyze data ...")
    ai_response = send2claude(str(data))
    report = parse_ai_response(ai_response)

    if report is None:
        perr("Failed to parse AI response")
        sys_exit(ErrCode.FETCH_ERROR)

    # Publish to both targets
    slack_success = publish_to_slack(report)
    dashboard_success = publish_to_dashboard(report)

    # Exit with appropriate code
    if not slack_success and not dashboard_success:
        sys_exit(ErrCode.PUBLISH_ERROR)
    elif not dashboard_success:
        sys_exit(ErrCode.DASHBOARD_PUBLISH_ERROR)
    else:
        sys_exit(ErrCode.SUCCESS)


if __name__ == "__main__":
    main()
