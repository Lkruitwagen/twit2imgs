from twit2imgs import utils

class Storer(ABC):
    
    def store(self, tweets: List[models.Tweet]) -> bool:
        pass
    
class GCPStore(Storer):
    
    def __init__(self, bucket):
        self.bucket = bucket
        self.record_prefix = record_prefix
        self.img_prefix = img_prefix
        
        
    def store(self, tweets: List[models.Tweet]) -> bool:
        
        for tweet in tweets:
            # write to file
            tweet.image.save(f'tmp/{tweet.id}.png')
            tweet.write_record(f'tmp/{tweet.id}.record')
            
            # upload blob
            utils.upload_blob(f'tmp/{tweet.id}.png', f'{self.bucket}/{self.img_prefix}/{tweet.id}.png')
            utils.upload_blob(f'tmp/{tweet.id}.record', f'{self.bucket}/{self.record_prefix}/{tweet.id}.record')
            
        return True