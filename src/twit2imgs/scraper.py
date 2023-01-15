from abc import ABC

import tweepy

from twit2imgs import models


class Scraper(ABC):
    
    def scrape(self) -> List[models.Tweet]:
        pass
    
    
class UserScraper(Scraper):
    """ Scrape a users tweets with images."""
    
    def __init__(
        TWITTER_API_BEARER_TOKEN: str,
        user_id: str,
        tweet_fields: List[str],
        max_results: int,
    ):
        
        self.client = tweepy.Client(bearer_token=TWITTER_API_BEARER_TOKEN)
        self.user_id = user_id
        self.tweet_fields = tweet_fields
        self.max_results = max_results
        
    def scrape(self) -> List[models.Tweet]:
        
        response = self.client.get_users_tweets(
            self.user_id, 
            max_results=self.max_results, 
            tweet_fields=self.tweet_fields, 
            media_fields=['url'],
            expansions=["attachments.media_keys"]
        )
        
        img_urls = {el.media_key:el.url for el in response.includes['media']}
        
        return [Tweet(t, img_urls) for t in response.data]
        
class HashtagScraper(Scraper):
    """ Scrape a given hashtage for tweets with images."""
    
    def __init__(self):
        pass
    
    def scrape(self):
        pass
    


