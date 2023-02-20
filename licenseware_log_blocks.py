import os
import re
import json
import logging
from enum import Enum
from urllib import request, parse

log = logging.getLogger(__name__)
log.setLevel(level=logging.INFO)

SLACK_TAGGED_USERS_IDS = os.environ["SLACK_TAGGED_USERS_IDS"]
SLACK_CHANNEL_WEBHOOK_URL = os.environ["SLACK_CHANNEL_WEBHOOK_URL"]


class Emoji(str, Enum):
    DEBUG = ":bug:"
    INFO = ":information_source:"
    SUCCESS = ":white_check_mark:"
    WARNING = ":warning:"
    ERROR = ":x:"


def get_formated_slack_message(emoji: Emoji, log_level: str, rawinput: str):

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
                    "text": f":military_helmet: *Special Mentions:* {SLACK_TAGGED_USERS_IDS}",
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


def get_slack_message(rawinput: str):
    emoji, log_level = get_emoji_and_log_level(rawinput)
    slack_message = get_formated_slack_message(emoji, log_level, rawinput)
    return slack_message


def post_message(message):
    """Post a message to slack using a webhook url."""

    json_body = json.dumps(message).encode("utf-8")
    query_params = parse.urlencode({"unfurl_media": "false", "unfurl_links": "false"})
    headers = {"Content-Type": "application/json"}
    url = f"{SLACK_CHANNEL_WEBHOOK_URL}?{query_params}"

    with request.urlopen(
        request.Request(url=url, data=json_body, headers=headers)
    ) as response:
        result = response.read().decode("utf-8")

    log.info(f"Sent message: {message}\nUrl: {url}\nResponse: {result}")


if __name__ == "__main__":
    import sys

    try:
        rawinput = sys.argv[0]
        slack_message = get_slack_message(rawinput)
        post_message(slack_message)
    except Exception as err:
        log.error(err)
