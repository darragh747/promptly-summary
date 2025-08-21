import json
from os import getenv
from sys import exit as sys_exit

import requests

from promptly_summary.common.errors import ErrCode
from promptly_summary.common.io import Style, perr


def publish2slack(slack_msg: str) -> bool:
    key = getenv("SLACK_WEBHOOK")
    if key is None:
        perr(f"missing {Style.PRP}`SLACK_WEBHOOK`{Style.RES}")
        sys_exit(ErrCode.MISSING_WEBHOOK)

    webhook_url = key
    print(f"{Style.PNK}Sending message to Slack ...{Style.RES}\n")

    try:
        data = json.loads(slack_msg)
        print(data)

        response = requests.post(
            webhook_url,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        response.raise_for_status()
    except json.JSONDecodeError as e:
        perr(f"failed to parse Slack message JSON -- {e}")
        # Fallback to plain text if JSON parsing fails
        try:
            response = requests.post(
                webhook_url,
                json={"text": slack_msg},
                headers={"Content-Type": "application/json"},
                timeout=15,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as fallback_e:
            perr(f"fallback also failed -- {fallback_e}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"failed to publish to Slack -- {e}")
        return False
    else:
        return True
