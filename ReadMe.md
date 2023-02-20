# licenseware-logblocks


## How it works?

Given a continuous log producer:

```bash
while true; do echo $RANDOM | tee -a /tmp/awesome-app.log; sleep 1; done
```

When `tail` is called on generated log file push strings into `licenseware_logblocks.py` parse them and publish formated message to slack.

```bash
tail -f /tmp/awesome-app.log | python3 licenseware_log_blocks.py
```

SLACK_TAGGED_USERS_IDS - will be tagged on all ERRORS


# Requirements

Environment variables:
- `SLACK_TAGGED_USERS_IDS` (ex: `export SLACK_TAGGED_USERS_IDS="<@U02CS9QL0JK>, <@U02U2KQ7N3Y>, <@U030JAJF5RV>, <@U02SDCAHJH3>, <@UHW04RBGT>"`);
- `SLACK_CHANNEL_WEBHOOK_URL` (ex: `export SLACK_CHANNEL_WEBHOOK_URL=https://hooks.slack.com/services/etc/etc/etc`)    


