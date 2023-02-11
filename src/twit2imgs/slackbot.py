import json
import os

import requests


class SlackBot:
    def __init__(self, token, channel, name):
        self.token = token
        self.channel = channel
        self.name = name

    def post(self, message:dict):

        data = {
            "token": self.token,
            "channel": self.channel,
            "as_user": True,
            "text": f"{self.name}: {json.dumps(message)}",
        }

        r = requests.post(url="https://slack.com/api/chat.postMessage", data=data)

        return r.status_code