from abc import ABC, abstractmethod

from twit2imgs.google_photos_client import GooglePhotosClient
from twit2imgs.image_utils import beautiful_s2_to_16_9_labelled


class Target(ABC):
    @abstractmethod
    def preprocess(self):
        pass

    @abstractmethod
    def post_tweets(self):
        pass

    @abstractmethod
    def postprocess(self):
        pass


class GooglePhotosTarget(Target):
    def __init__(self, album_name, client_params):
        self.client = GooglePhotosClient(**client_params)
        self.album_id = self.client._get_album_id(album_name)

    def preprocess(self):
        # clear the google bucket
        self.client.clear_album(self.album_id)

    def post_tweets(self, tweets):
        # post images to the google bucket
        formatted_images = []
        for t in tweets:
            formatted_images.append(beautiful_s2_to_16_9_labelled(t.image, t.text))

        self.client.upload_images(self.album_id, formatted_images)

    def postprocess(self):
        pass
