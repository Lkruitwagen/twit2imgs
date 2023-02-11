import json
from io import BytesIO

import requests
import tweepy
from PIL import Image


class Tweet:
    def __init__(self, ttweet, img_urls):
        self.id: str = ttweet.id
        self.text: str = ttweet.text
        self.image_url: str = img_urls[ttweet.attachments["media_keys"][0]]
        self.ttweet: tweepy.tweet.Tweet = ttweet

        r = requests.get(self.image_url, timeout=60)
        r.raise_for_status()

        self.image = Image.open(BytesIO(r.content))

    def write_record(self, fpath):
        record = dict(
            id=self.id,
            text=self.text,
            url=self.image_url,
        )

        json.dump(record, open(fpath, "w"))

        return 1
