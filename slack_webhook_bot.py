import json
import re
import logging
import requests
import traceback

log = logging.getLogger(__name__)

emoji_map = {
    "DEBUG": ":bug:",
    "INFO": ":information_source:",
    "SUCCESS": ":white_check_mark:",
    "WARNING": ":warning:",
    "ERROR": ":x:",
}


def compose_message_block(event: dict) -> json:
    """
    Compose a message block for Slack.
    """
    message_block = {"type": "section", "text": {"type": "mrkdwn", "text": ""}}
    for log_event in event["logEvents"]:
        empty_message = re.findall(
            r"^\d{2}:\d{2}:\d{2}\s+web\.\d{1}\s+\|\s*$", log_event["message"]
        )
        if empty_message:
            continue
        message_block = parse_message(event["logGroup"], log_event["message"])
        yield json.dumps(message_block, default=str)


def parse_message(log_group, log_message):
    app_id = (
        log_group[log_group.rfind("-", 0, log_group.rfind("-")) + 1 :].lstrip().rstrip()
    )
    try:
        log_level = re.search(r"\[([A-Z]+)\]", log_message).group(1)
        emoji = emoji_map.get(log_level, ":question:")
    except Exception:
        log.warning(traceback.format_exc())
        log_level = None

    try:
        log_metadata = re.search(r"\[\++ METADATA: ({.*}) \++\]", log_message).group(1)
        log_metadata = log_metadata.replace("'", '"').replace("None", "null").strip()
        meta_dict = json.loads(log_metadata)
    except Exception:
        log.warning(traceback.format_exc())
        meta_dict = None

    try:
        message = re.search(r"\[\*+ MESSAGE: (.*)", log_message).group(1)
    except Exception:
        log.warning(traceback.format_exc())
        message = log_message

    try:
        code_location = re.search(r"\[\-+ (\S+) -+\]", log_message).group(1)
    except Exception:
        log.warning(traceback.format_exc())
        code_location = "-"

    if meta_dict:
        message_blocks = return_message_block(
            emoji, app_id, log_level, message, code_location, meta_dict
        )
    else:
        message_blocks = return_normal_message(message)

    message_blocks = tag_message(message, message_blocks, log_group)
    return message_blocks


def parse_metadata(log_metadata):
    """Convert metadata dictionary to beautified markdown string"""
    md_string = ""
    for key, value in log_metadata.items():
        md_string += f"*{key}:* {str(value)}\n"
    return md_string


def return_message_block(emoji, app_id, log_level, message, code_location, meta_dict):
    message_block = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} {log_level} on {app_id.upper()}",
                    "emoji": True,
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f" :mag_right: *Code Location:* {code_location}",
                    }
                ],
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": parse_metadata(meta_dict),
                        "unfurl_links": False,
                        "unfurl_media": False,
                    }
                ],
            },
            {"type": "section", "text": {"type": "mrkdwn", "text": f"```{message}```"}},
            {"type": "divider"},
        ]
    }
    return message_block


def return_normal_message(message):
    return {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```{message}```",
                },
            },
        ]
    }


def return_special_mentions():
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": ":tada: A user is processing data on production.",
                "emoji": True,
            },
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": ":military_helmet: *Special Mentions:* \
                            <@UJ7EEGX88>, <@UHW04RBGT>, <@U01SAMHA2LR>",
                }
            ],
        },
    ]
    return blocks


def return_error_alert():
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": ":x: An error has occurred!",
                "emoji": True,
            },
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": " :military_helmet: *Special Mentions:* <@U02CS9QL0JK> \
                            , <@U02U2KQ7N3Y>, <@U030JAJF5RV>, <@U02SDCAHJH3>, \
                            <@UHW04RBGT>",
                }
            ],
        },
    ]
    return blocks


def tag_message(message, message_blocks, log_group):
    error_regexes = [
        r".*Traceback.*",
        r".*Exception:.*",
        r".*Error:.*",
        r".*Warning:.*",
        r".*failsafe_decorator\.py.*",
    ]

    uploads_regexes = [
        r".*APP PROCESSING EVENT.*",
    ]

    if (
        any(re.search(regex, message) for regex in error_regexes)
        and "prod" in log_group
    ):

        error_blocks = return_error_alert()
        message_blocks["blocks"].extend(error_blocks)

    if (
        any(re.search(regex, message) for regex in uploads_regexes)
        and "prod" in log_group
    ):

        uploads_blocks = return_special_mentions()
        message_blocks["blocks"].extend(uploads_blocks)

    return message_blocks


def post_message(url, message):
    """Post a message to slack using a webhook url."""
    response = requests.post(
        url,
        json=message,
        headers={"Content-Type": "application/json"},
        params={"unfurl_media": "false", "unfurl_links": "false"},
    )
    log.info("Sent message: %s\nUrl: %s\nResponse: %s", message, url, response.text)
    return response.status_code == 200
