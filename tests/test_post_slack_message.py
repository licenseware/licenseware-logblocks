import os

from logblocks.logblocks import get_slack_message, post_message


def test_post_message():
    test_webhook_url = os.environ["TEST_WEBHOOK_URL"]
    user_ids = os.environ["SLACK_TAGGED_USERS_IDS"]

    message = get_slack_message("THIS IS A TEST MESSAGE", user_ids)
    response = post_message(message, test_webhook_url)
    assert response.status_code == 200
    assert response.body == "ok"
