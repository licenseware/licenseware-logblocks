import argparse
import logging
import os
import re
import sys
from enum import Enum

from slack_sdk import WebhookClient
from slack_sdk.models.blocks import ContextBlock, DividerBlock, HeaderBlock
from slack_sdk.models.blocks.basic_components import MarkdownTextObject, PlainTextObject

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
    special_mentions = emoji == Emoji.ERROR

    msg_title = (
        f"{emoji} {log_level} {'please investigate!' if special_mentions else ''}"
    )

    header = HeaderBlock(
        block_id="hd-id1", text=PlainTextObject(text=msg_title, emoji=True)
    )

    content = ContextBlock(
        block_id="cn-id1", elements=[MarkdownTextObject(text=f"```{rawinput}```")]
    )
    blocks = [DividerBlock(block_id="d1"), header, content]

    if special_mentions:
        mentions_block = ContextBlock(
            block_id="cn-id2",
            elements=[
                MarkdownTextObject(
                    text=f":military_helmet: *Special Mentions:* {mentions}"
                )
            ],
        )
        blocks.append(mentions_block)

    return blocks


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

    headers = {"Content-Type": "application/json"}

    webhook = WebhookClient(url=webhook_url)
    response = webhook.send(blocks=message, unfurl_links=False, unfurl_media=False)

    logger.info(
        f"Sent message: {message}\nUrl: {webhook_url}\nResponse: {response.body}"
    )

    return response


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
