import json
from os import getenv
from typing import TypedDict, Any

import requests

from promptly_summary.common.const import Constant
from promptly_summary.common.io import Style, perr


class StandardMetrics(TypedDict):
    avg_original_score: float
    avg_improved_score: float
    avg_score_improvement: float


class StandardReport(TypedDict):
    summary: str
    common_mistakes: list[str]
    successful_patterns: list[str]
    developer_tips: list[str]
    metrics: StandardMetrics
    encouragement: str


def to_slack_blocks(report: StandardReport) -> dict[str, Any]:
    """Convert standard report to Slack blocks format."""
    blocks: list[Any] = [
        {"type": "header", "text": {"type": "plain_text", "text": "📊 Weekly Promptly Analysis", "emoji": True}},
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Executive Summary*"}},
        {"type": "section", "text": {"type": "mrkdwn", "text": report["summary"]}},
        {"type": "divider"},
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Common Mistakes in Original Prompts*"}},
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "\n".join(f"• {mistake}" for mistake in report["common_mistakes"])},
        },
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Patterns in Successful Improvements*"}},
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "\n".join(f"• {pattern}" for pattern in report["successful_patterns"])},
        },
        {"type": "divider"},
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Developer Tips* 💡"}},
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "\n".join(f"• {tip}" for tip in report["developer_tips"])},
        },
        {"type": "divider"},
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Impact Analysis* 📈"}},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"• *Average Original Score:* {report['metrics']['avg_original_score']:.2f}\n"
                    f"• *Average Improved Score:* {report['metrics']['avg_improved_score']:.2f}\n"
                    f"• *Average Score Improvement:* {report['metrics']['avg_score_improvement']:.2f}"
                ),
            },
        },
        {"type": "section", "text": {"type": "mrkdwn", "text": f"_{report['encouragement']}_ 🎯"}},
    ]

    return {"text": "Weekly Promptly Analysis Report", "blocks": blocks}


def to_html(report: StandardReport) -> str:
    """Convert standard report to HTML format for dashboard."""
    return f"""
    <div class="promptly-report">
        <h1>📊 Weekly Promptly Analysis</h1>

        <section class="executive-summary">
            <h2>Executive Summary</h2>
            <p>{report["summary"]}</p>
        </section>

        <section class="common-mistakes">
            <h2>Common Mistakes in Original Prompts</h2>
            <ul>
                {"".join(f"<li>{mistake}</li>" for mistake in report["common_mistakes"])}
            </ul>
        </section>

        <section class="successful-patterns">
            <h2>Patterns in Successful Improvements</h2>
            <ul>
                {"".join(f"<li>{pattern}</li>" for pattern in report["successful_patterns"])}
            </ul>
        </section>

        <section class="developer-tips">
            <h2>Developer Tips 💡</h2>
            <ul>
                {"".join(f"<li>{tip}</li>" for tip in report["developer_tips"])}
            </ul>
        </section>

        <section class="impact-analysis">
            <h2>Impact Analysis 📈</h2>
            <ul>
                <li><strong>Average Original Score:</strong> {report["metrics"]["avg_original_score"]:.2f}</li>
                <li><strong>Average Improved Score:</strong> {report["metrics"]["avg_improved_score"]:.2f}</li>
                <li><strong>Average Score Improvement:</strong> {report["metrics"]["avg_score_improvement"]:.2f}</li>
            </ul>
            <p class="encouragement"><em>{report["encouragement"]}</em> 🎯</p>
        </section>
    </div>
    """


def publish_to_slack(report: StandardReport) -> bool:
    """Publish report to Slack if webhook is configured."""
    webhook = getenv("SLACK_WEBHOOK")
    if webhook is None:
        print(f"{Style.YLW}Skipping Slack publish (no SLACK_WEBHOOK configured){Style.RES}")
        return True  # Not a failure, just skipped

    print(f"{Style.PNK}Sending message to Slack ...{Style.RES}")

    try:
        slack_data = to_slack_blocks(report)
        response = requests.post(
            webhook,
            json=slack_data,
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        response.raise_for_status()
        print(f"{Style.GRN}✓ Published to Slack{Style.RES}")
    except requests.exceptions.RequestException as e:
        perr(f"Failed to publish to Slack: {e}")
        return False
    else:
        return True


def publish_to_dashboard(report: StandardReport) -> bool:
    """Publish report to metrics dashboard (hardcoded URL)."""
    dashboard_url = Constant.TO_URL
    print(f"{Style.PNK}Sending update to metrics dashboard ... {Style.RES}")

    try:
        html_content = to_html(report)
        response = requests.post(
            dashboard_url,
            json={"text": html_content},
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        response.raise_for_status()
        print(f"{Style.GRN}✓ Published to metrics dashboard{Style.RES}")
    except requests.exceptions.RequestException as e:
        perr(f"Failed to publish to metrics dashboard: {e}")
        return False
    else:
        return True


def parse_ai_response(response: str) -> StandardReport | None:
    """Parse AI response into standard report format."""
    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        perr(f"Failed to parse AI response as JSON: {e}")
        return None
