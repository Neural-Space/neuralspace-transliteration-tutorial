import json
import traceback
from time import sleep

import requests
import tweepy
from requests.exceptions import ChunkedEncodingError

from constants import (
    ACCESS_TOKEN_SECRET,
    BEARER_TOKEN,
    CONSUMER_KEY,
    CONSUMER_SECRET,
    NEURALSPACE_ACCESS_TOKEN,
    NEURALSPACE_TRANSLITERATION_URL,
    SRC_LANG,
    TGT_LANG,
    TWITTER_ACCESS_TOKEN,
    TWITTER_STREAM_RULES_URL,
    TWITTER_STREAM_URL,
)
from process_tweet import TweetProcessor


class KeyphraseListener:
    def __init__(self, keyphrase: str, config):
        twitter_config = config["twitter-auth"]
        neuralspace_config = config["neuralspace-auth"]
        language_config = config["languages"]
        self.keyphrase = keyphrase
        self.bearer_token = twitter_config[BEARER_TOKEN]
        self.consumer_key = twitter_config[CONSUMER_KEY]
        self.consumer_secret = twitter_config[CONSUMER_SECRET]
        self.access_token = twitter_config[TWITTER_ACCESS_TOKEN]
        self.access_token_secret = twitter_config[ACCESS_TOKEN_SECRET]
        self.neuralspace_access_token = neuralspace_config[NEURALSPACE_ACCESS_TOKEN]
        self.tgt_language = language_config[TGT_LANG]

    def bearer_oauth(self, r):
        """
        Method required by bearer token authentication.
        """

        r.headers["Authorization"] = f"Bearer {self.bearer_token}"
        r.headers["User-Agent"] = "v2FilteredStreamPython"
        return r

    def get_rules(self):
        response = requests.get(TWITTER_STREAM_RULES_URL, auth=self.bearer_oauth)
        if response.status_code != 200:
            raise Exception(
                "Cannot get rules (HTTP {}): {}".format(
                    response.status_code, response.text
                )
            )
        return response.json()

    def delete_all_rules(self, rules):
        if rules is None or "data" not in rules:
            return None

        ids = list(map(lambda rule: rule["id"], rules["data"]))
        payload = {"delete": {"ids": ids}}
        response = requests.post(
            TWITTER_STREAM_RULES_URL, auth=self.bearer_oauth, json=payload
        )
        if response.status_code != 200:
            raise Exception(
                "Cannot delete rules (HTTP {}): {}".format(
                    response.status_code, response.text
                )
            )
        print(json.dumps(response.json()))

    def post_to_twitter(
        self,
        consumer_key,
        consumer_secret,
        access_token,
        access_token_secret,
        text_to_tweet,
        tweet_id_to_reply_to,
    ):
        client = tweepy.Client(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
        )
        response = client.create_tweet(
            text=text_to_tweet, in_reply_to_tweet_id=tweet_id_to_reply_to
        )
        return response

    def process_transliterate_and_tweet(
        self, triggered_tweet_id, text_to_transliterate
    ):
        if text_to_transliterate is not None:
            if (
                self.keyphrase not in text_to_transliterate.lower()
                and self.keyphrase.lower() not in text_to_transliterate
                and self.keyphrase.lower() not in text_to_transliterate.lower()
            ):
                transliterated_text = TweetProcessor(
                    self.neuralspace_access_token
                ).transliterate_tweet(text_to_transliterate, self.tgt_language)
                response = self.post_to_twitter(
                    self.consumer_key,
                    self.consumer_secret,
                    self.access_token,
                    self.access_token_secret,
                    transliterated_text[:280],
                    triggered_tweet_id,
                )
            else:
                response = None
        return response

    def set_rules(self, delete):
        # You can adjust the rules if needed
        sample_rules = [{"value": f'"{self.keyphrase}"', "tag": "NeuralSpace"}]
        payload = {"add": sample_rules}
        response = requests.post(
            TWITTER_STREAM_RULES_URL, auth=self.bearer_oauth, json=payload
        )
        if response.status_code != 201:
            raise Exception(
                "Cannot add rules (HTTP {}): {}".format(
                    response.status_code, response.text
                )
            )
        print(json.dumps(response.json()))

    def get_tweet_response_from_id(self, tweet_id):
        response = requests.get(
            f"https://api.twitter.com/2/tweets/{tweet_id}?expansions=in_reply_to_user_id%2Cauthor_id%2Creferenced_tweets.id.author_id&media.fields=duration_ms%2Ctype",
            auth=self.bearer_oauth,
        )
        return response

    def get_tweet_id_and_parent_tweet_text(self, json_response):
        triggered_tweet_id = json_response["data"]["id"]
        response = self.get_tweet_response_from_id(triggered_tweet_id)
        text = json.loads(response.text)
        if "tweets" in text["includes"]:
            text_to_transliterate = text["includes"]["tweets"][0]["text"]
        else:
            text_to_transliterate = None

        return triggered_tweet_id, text_to_transliterate

    def get_stream(self, set):
        wait_time = 60
        downtime = 0

        run = 1
        while run:
            try:
                with requests.get(
                    TWITTER_STREAM_URL, auth=self.bearer_oauth, stream=True
                ) as response:
                    print(response.status_code)
                    print(downtime)
                    if response.status_code != 200:
                        raise Exception(
                            "Cannot get stream (HTTP {}): {}".format(
                                response.status_code, response.text
                            )
                        )
                    wait_time = 60
                    for response_line in response.iter_lines():
                        if response_line:
                            bot_trigger_response = json.loads(response_line)
                            print(
                                json.dumps(
                                    bot_trigger_response, indent=4, sort_keys=True
                                )
                            )

                            triggered_tweet_id, text_to_transliterate = self.get_tweet_id_and_parent_tweet_text(
                                bot_trigger_response
                            )
                            print(str(text_to_transliterate))
                            response = self.process_transliterate_and_tweet(
                                triggered_tweet_id, text_to_transliterate
                            )
                            print(response)

            except ChunkedEncodingError as chunkError:
                print(traceback.format_exc())
                print("chunked error. Connecting again in 10 seconds...")
                sleep(10)
                downtime += 10
                continue

            except Exception as e:

                # some other error occurred.. stop the loop
                print(
                    f"Some error occured. Connecting to stream in {wait_time} seconds..."
                )
                print(traceback.format_exc())
                print("-----")
                sleep(wait_time)
                downtime += wait_time
                wait_time = wait_time * 2
                continue
