from time import sleep
import click
import requests
import os
import json
import re
from constants import NEURALSPACE_AUTH, TWITTER_AUTH
from keyword_listener import KeyphraseListener
from process_tweet import TweetProcessor
import tweepy
import yaml

@click.command()
@click.option(
    "-k",
    "--keyword",
    type=click.STRING,
    required=True,
    prompt=True,
    help="Keyword which will trigger the bot",
)
def main(keyword: str): 
    with open("config.yaml", "r") as yamlfile:
        config = yaml.load(yamlfile, Loader=yaml.FullLoader)

    listener = KeyphraseListener(keyword, config)
    rules = listener.get_rules()
    delete = listener.delete_all_rules(rules)
    set = listener.set_rules(delete)
    listener.get_stream(set)



if __name__ == "__main__":
    main()

