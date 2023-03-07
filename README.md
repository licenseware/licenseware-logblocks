# licenseware-logblocks

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [licenseware-logblocks](#licenseware-logblocks)
  - [Installation](#installation)
  - [How it works?](#how-it-works)
  - [Requirements](#requirements)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Installation

```bash
pip install licenseware-logblocks
```

## How it works?

Having a log stream, you can read line by line and send it to logblocks:

```bash
log_stream() { while true; do echo $RANDOM; sleep 1; done; }
while IFS= read -r line; do echo $line | logblocks $line; done < <(log_stream)
```

`SLACK_TAGGED_USERS_IDS` will be tagged on all ERRORS

## Requirements

Environment variables:

- `SLACK_TAGGED_USERS_IDS` (ex: `export SLACK_TAGGED_USERS_IDS="<@U02CS9QL0JK>, <@U02U2KQ7N3Y>, <@U030JAJF5RV>, <@U02SDCAHJH3>, <@UHW04RBGT>"`);
- `SLACK_CHANNEL_WEBHOOK_URL` (ex: `export SLACK_CHANNEL_WEBHOOK_URL=https://hooks.slack.com/services/etc/etc/etc`)
