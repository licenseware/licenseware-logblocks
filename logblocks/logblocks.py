import argparse
import json
import logging
import os
import re
import sys
from enum import Enum
from urllib import parse, request

parser = argparse.ArgumentParser(
    description="Post formatted log messages to slack, mentioning users when error ocurrs"
)
parser.add_argument(
    "rawinput",
    type=str,
    help="The raw log message",
    nargs="+",
    action="extend",
)
parser.add_argument(
    "-l", "--loglevel", type=str, help="The log level (default: INFO)", default="INFO"
)
parser.add_argument(
    "-u",
    "--url",
    type=str,
    default="",
    help="The slack channel webhook url (default: SLACK_TAGGED_USERS_IDS env var)",
)
parser.add_argument(
    "-m",
    "--mentions",
    type=str,
    default="",
    help="The slack users to mention (default: SLACK_CHANNEL_WEBHOOK_URL env var)",
)


logger = logging.getLogger(__name__)

SLACK_TAGGED_USERS_IDS = os.getenv("SLACK_TAGGED_USERS_IDS")
SLACK_CHANNEL_WEBHOOK_URL = os.getenv("SLACK_CHANNEL_WEBHOOK_URL")


class Emoji(str, Enum):
    __str__ = lambda self: str(self.value)

    DEBUG = ":bug:"
    INFO = ":information_source:"
    SUCCESS = ":white_check_mark:"
    WARNING = ":warning:"
    ERROR = ":x:"


def get_formated_slack_message(
    emoji: Emoji, log_level: str, rawinput: str, mentions: str
):
    msg = {
        "blocks": [
            {"type": "divider"},
        ]
    }

    special_mentions = emoji == Emoji.ERROR

    msg_title = (
        f"{emoji} {log_level} {'please investigate!' if special_mentions else ''}"
    )

    msg_header = {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": msg_title,
            "emoji": True,
        },
    }

    msg_content = {
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": f"```{rawinput}```",
            }
        ],
    }

    msg["blocks"].extend([msg_header, msg_content])

    if special_mentions:
        msg_mentions = {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f":military_helmet: *Special Mentions:* {mentions}",
                }
            ],
        }
        msg["blocks"].extend([msg_mentions])

    return msg


def found_error(rawinput: str):
    return bool(
        re.search("Traceback (most recent call last):", rawinput)
        or re.search("ERROR", rawinput)
    )


def found_debug(rawinput: str):
    return bool(re.search("DEBUG", rawinput))


def found_warning(rawinput: str):
    return bool(re.search("WARNING", rawinput))


def get_emoji_and_log_level(rawinput: str):
    if found_error(rawinput):
        return Emoji.ERROR, "ERROR"
    if found_debug(rawinput):
        return Emoji.DEBUG, "DEBUG"
    if found_warning(rawinput):
        return Emoji.WARNING, "WARNING"
    return Emoji.INFO, "INFO"


def get_slack_message(rawinput: str, mentions: str):
    emoji, log_level = get_emoji_and_log_level(rawinput)
    slack_message = get_formated_slack_message(emoji, log_level, rawinput, mentions)
    return slack_message


def post_message(message, webhook_url):
    """Post a message to slack using a webhook url."""

    json_body = json.dumps(message).encode("utf-8")
    query_params = parse.urlencode({"unfurl_media": "false", "unfurl_links": "false"})
    headers = {"Content-Type": "application/json"}
    url = f"{webhook_url}?{query_params}"

    with request.urlopen(
        request.Request(url=url, data=json_body, headers=headers)
    ) as response:
        result = response.read().decode("utf-8")

    logger.info(f"Sent message: {message}\nUrl: {url}\nResponse: {result}")


def main():
    parsed = parser.parse_args(sys.argv[1:])
    rawinput = " ".join(parsed.rawinput)
    loglevel = parsed.loglevel
    webhook_url = parsed.url or SLACK_CHANNEL_WEBHOOK_URL
    mentions = parsed.mentions or SLACK_TAGGED_USERS_IDS

    assert webhook_url, "Either pass --url or set SLACK_CHANNEL_WEBHOOK_URL env var"
    assert mentions, "Either pass --mentions or set SLACK_TAGGED_USERS_IDS env var"

    logger.setLevel(loglevel)

    try:
        slack_message = get_slack_message(rawinput=rawinput, mentions=mentions)
        post_message(message=slack_message, webhook_url=webhook_url)
    except Exception as err:
        logger.error(err)


if __name__ == "__main__":
    main()
