import json
import os
import shutil
import sys

import click
import yaml
from dateutil import parser
from loguru import logger

from twit2imgs import utils

logger.remove()
logger.add(sys.stdout, colorize=False, format="{time:YYYYMMDDHHmmss}|{level}|{message}")


@click.group()
def cli():
    pass

@cli.command()
@click.argument("conf_path")
def DAG(conf_path):
    
    # set up tmp dir
    if not os.path.exists('tmp'):
        os.makedirs("tmp/")
    
    # parse config
    logger.info('parsing config')
    cfg = yaml.load(open(f"conf/{conf_path}.yaml"), Loader=yaml.SafeLoader)
    cfg = utils.parse_cfg(cfg)
    
    # scrape tweets
    logger.info('scraping tweets')
    scraper = utils._indirect_cls(cfg.scraper.cls)(cfg)
    tweets = scraper.scrape()
    logger.info(f'Got {len(tweets)} tweets')
    
    # store tweet records and images to cloud
    logger.info('storing tweets')
    storer = utils._indirect_cls(cfg.storer.cls)(cfg)
    if storer is not None:
        storer.store(tweets)
        
    # for each target: preprocess, post_tweets, postprocess
    for target_key, target_params in cfg.targets.items():
        logger.info(f'updating album: {target_key}')
        target = utils._indirect_cls(target_params.cls)(target_params)
        target.preprocess()
        target.post_tweets(tweets)
        target.postprocess()
        
    # cleanup
    shutil.rmtree("tmp/")
    os.makedirs("tmp/")
        
    return 200

if __name__ == "__main__":
    cli()