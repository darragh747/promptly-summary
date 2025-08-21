from sys import argv
from sys import exit as sys_exit
from typing import TypedDict

import requests

from promptly_summary.__init__ import __version__
from promptly_summary.common.const import Constant
from promptly_summary.common.errors import ErrCode
from promptly_summary.common.io import Style, perr

help_msg = f"""{Style.PNK}
{Style.BLD}promptly-summary{Style.RES}
  {Style.RES}Generate promptly summaries with important prompting tips for devs

{Style.GRN}{Style.BLD}Flags{Style.RES}
  {Style.PRP}-h{Style.RES}, {Style.PRP}--help{Style.RES}        Show this help message & quit
  {Style.PRP}-v{Style.RES}, {Style.PRP}--version{Style.RES}     Show program version & quit
"""


ver_msg = f"{Style.PNK}{Style.BLD}promptly-summary{Style.RES} {Style.GRN}v{__version__}{Style.RES}"


class AnalyticEntry(TypedDict):
    original_prompt: str
    improved_prompt: str
    original_score: float
    improved_score: float
    score_improvement: float


class Analytics(TypedDict):
    entries: list[AnalyticEntry]
    total_count: int


class AnalyticsWithSummary(TypedDict):
    entries: list[AnalyticEntry]
    total_count: int
    avg_original_score: float
    avg_improved_score: float
    avg_score_improvement: float


def phelp() -> None:
    print(help_msg)


def pver() -> None:
    print(ver_msg)


def parse_args() -> None:
    invalid: set[str] = set()

    for each in argv[1:]:
        if each in {"-h", "--help"}:
            phelp()
            sys_exit(ErrCode.SUCCESS)

        if each in {"-v", "--version"}:
            pver()
            sys_exit(ErrCode.SUCCESS)

        invalid.add(each)

    if invalid:
        perr("invalid args -- {}".format("/".join(f"{Style.PRP}{arg}{Style.RES}" for arg in invalid)))
        sys_exit(ErrCode.INVALID_ARGS)


def fetch_analytics() -> Analytics | None:
    try:
        r = requests.get(Constant.SRC_URL, params={"days": Constant.DAYS}, timeout=15)
        r.raise_for_status()
        json = r.json()
        return add_summary(json)
    except requests.RequestException as e:
        perr(str(e))
        return None


def add_summary(raw: Analytics, top_n: int = 50, max_prompt_length: int = 1000) -> AnalyticsWithSummary:
    # Filter out entries with prompts exceeding the character limit
    filtered_entries = [
        entry
        for entry in raw["entries"]
        if len(entry["original_prompt"]) <= max_prompt_length and len(entry["improved_prompt"]) <= max_prompt_length
    ]

    # Sort filtered entries by score improvement difference (improved - original), descending
    sorted_entries = sorted(
        filtered_entries,
        key=lambda e: e["improved_score"] - e["original_score"],
        reverse=True,
    )

    # Take only the top N most significant improvements
    top_entries = sorted_entries[:top_n]

    # Calculate averages only for the top entries
    if not top_entries:
        return {
            "entries": raw["entries"],
            "total_count": raw["total_count"],
            "avg_original_score": 0.0,
            "avg_improved_score": 0.0,
            "avg_score_improvement": 0.0,
        }

    total_original_score = sum(entry["original_score"] for entry in top_entries)
    total_improved_score = sum(entry["improved_score"] for entry in top_entries)
    total_score_improvement = sum(entry["score_improvement"] for entry in top_entries)

    entry_count = len(top_entries)

    return {
        "entries": raw["entries"],
        "total_count": raw["total_count"],
        "avg_original_score": total_original_score / entry_count,
        "avg_improved_score": total_improved_score / entry_count,
        "avg_score_improvement": total_score_improvement / entry_count,
    }
