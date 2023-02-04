from abc import ABC
from typing import List, Optional

import tweepy

from twit2imgs import models, utils
from twit2imgs.image_utils import null_url_parser
from loguru import logger


class Scraper(ABC):
    
    def scrape(self) -> List[models.Tweet]:
        pass
    
    
class UserScraper(Scraper):
    """ Scrape a users tweets with images."""
    
    def __init__(
        self,
        TWITTER_API_BEARER_TOKEN: str,
        user_id: str,
        tweet_fields: List[str],
        max_results: int,
        url_parser: Optional[str] = None
    ):
        
        self.client = tweepy.Client(bearer_token=TWITTER_API_BEARER_TOKEN)
        self.user_id = user_id
        self.tweet_fields = tweet_fields
        self.max_results = max_results
        self.url_parser = utils._indirect_cls(url_parser) if url_parser else null_url_parser
        
    def scrape(self) -> List[models.Tweet]:
        
        response = self.client.get_users_tweets(
            self.user_id, 
            max_results=self.max_results, 
            tweet_fields=self.tweet_fields, 
            media_fields=['url'],
            expansions=["attachments.media_keys"]
        )
        
        img_urls = {el.media_key:self.url_parser(el.url) for el in response.includes['media']}
        
        return [models.Tweet(t, img_urls) for t in response.data]
        
class HashtagScraper(Scraper):
    """ Scrape a given hashtage for tweets with images."""
    
    def __init__(self):
        pass
    
    def scrape(self):
        pass
    


