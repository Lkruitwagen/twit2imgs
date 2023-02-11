import os
import shutil
import sys

import click
import yaml
from dotmap import DotMap
from loguru import logger

from twit2imgs import utils
from twit2imgs.slackbot import SlackBot

logger.remove()
logger.add(sys.stdout, colorize=False, format="{time:YYYYMMDDHHmmss}|{level}|{message}")


def parse_cfg(cfg: dict) -> dict:
    cfg = utils.walk_dict(cfg, utils.maybe_parse_environ)

    return DotMap(cfg)


@click.group()
def cli():
    pass


@cli.command()
@click.argument("conf_path")
def DAG(conf_path):
    # set up tmp dir
    if not os.path.exists("tmp"):
        os.makedirs("tmp/")

    slack_token = os.environ.get("SLACKBOT_TOKEN")
    slack_channel = os.environ.get("SLACKBOT_CHANNEL")
    if slack_token is not None and slack_channel is not None:
        slackbot = SlackBot(token=slack_token, channel=slack_channel, name="twit2imgs")
    else:
        slackbot = None

    msg = {}

    # run the DAG, optionally logging errors to Slack
    try:
        # parse config
        logger.info("parsing config")
        cfg = yaml.load(open(f"conf/{conf_path}.yaml"), Loader=yaml.SafeLoader)
        cfg = parse_cfg(cfg)

        # scrape tweets
        logger.info("scraping tweets")
        scraper = utils._indirect_cls(cfg.scraper.cls)(**cfg.scraper.params)
        tweets = scraper.scrape()
        logger.info(f"Got {len(tweets)} tweets")
        msg["scraped_tweets"] = len(tweets)

        # store tweet records and images to cloud
        logger.info("storing tweets")
        storer = utils._indirect_cls(cfg.storer.cls)(**cfg.storer.params)
        if storer is not None:
            storer.store(tweets)
            msg["storer"] = cfg.storer.cls.split(".")[-1]

        # for each target: preprocess, post_tweets, postprocess
        msg["targets"] = []
        for target_key, target_params in cfg.targets.items():
            logger.info(f"updating target: {target_key}")
            target = utils._indirect_cls(target_params.cls)(**target_params.params)
            target.preprocess()
            target.post_tweets(tweets)
            target.postprocess()
            msg["targets"].append(target_key)

        # cleanup
        shutil.rmtree("tmp/")
        os.makedirs("tmp/")

        if slackbot is not None:
            slackbot.post(msg)
    except Exception as e:
        if slackbot is not None:
            msg = {"ERROR": repr(e), "MESSAGE": str(e)}
            slackbot.post(msg)
        raise e

    return 200


if __name__ == "__main__":
    cli()
