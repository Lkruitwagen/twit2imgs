from abc import ABC

from twit2imgs.image_utils import beautiful_s2_to_16_9_labelled
from twit2imgs.google_photos_client import GooglePhotosClient

class Target(ABC):
    
    def __init__(self):
        pass
    
    def preprocess(self):
        pass
    
    def post_tweets(self):
        pass
    
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