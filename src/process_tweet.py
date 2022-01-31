import json
import re
import requests

from constants import NEURALSPACE_TRANSLITERATION_URL


class TweetProcessor:
    def __init__(self,
        neuralspace_transliteration_URL: str,
        neuralspace_access_token: str
    ):
        self.neuralspace_transliteration_URL = neuralspace_transliteration_URL
        self.neuralspace_access_token = neuralspace_access_token

    def is_hindi(self, word):
        maxchar = max(word)
        if u'\u0900' <= maxchar <= u'\u097f':
            return True
        else:
            return False

    def clean_tweet(self, tweet):
        '''
		Utility function to clean tweet text by removing links, special 
        characters using simple regex statements.
		'''
        tweet = re.sub("@[A-Za-z0-9_]+","",tweet)
        tweet = re.sub("@[A-Za-z0-9_]+","", tweet)
        tweet = re.sub("#[A-Za-z0-9_]+","", tweet)
        tweet = re.sub(r"(?:\@|http?\://|https?\://|www)\S+", "", tweet)
        tweet = tweet.replace(",","")
        tweet = " ".join(tweet.split())
        return tweet

    def transliterate_sentence(self, text, src_language: str, tgt_language: str):
        text = text.rstrip()
        transliteration_headers ={
                        'Authorization': self.neuralspace_access_token,
                        'Content-Type': 'application/json'
                    }
        transliteration_payload = json.dumps({
            "text": text,
            "sourceLanguage": src_language,
            "targetLanguage": tgt_language,
            "suggestionCount": 2
            })
        transliteration_response =requests.post(
            self.neuralspace_transliteration_URL, 
            headers=transliteration_headers, 
            data=transliteration_payload)

        transliteration_response_text = json.loads(transliteration_response.text)
        transliterated_text = (transliteration_response_text["data"]["transliterated_text"])
        return transliterated_text
        
    def split_sentences(self, text):
        sentences = []
        sentences = text.split("।")
        return sentences


    def transliterate_tweet(self, text, src_language: str, tgt_language: str):

        text = self.clean_tweet(text)
        transliterated_sentences = []

        sentences = self.split_sentences(text)
        for sentence in sentences:
            phrase_to_transliterate = ""
            transliterated_phase = ""
            transliterated_text = ""

            for word in sentence.split():
                if self.is_hindi(word):
                    phrase_to_transliterate+=word
                    phrase_to_transliterate+=" "
                else:
                    if phrase_to_transliterate is not "":
                        transliterated_phase = self.transliterate_sentence(phrase_to_transliterate, src_language, tgt_language)
                        phrase_to_transliterate = ""
                        transliterated_text+=transliterated_phase
                        transliterated_text+= " "
                    transliterated_text+=word
                    transliterated_text+=" "

            if phrase_to_transliterate is not "":
                transliterated_phase = self.transliterate_sentence(phrase_to_transliterate, src_language, tgt_language)
                phrase_to_transliterate = ""
                transliterated_text+=transliterated_phase
            transliterated_sentences.append(transliterated_text.rstrip())
        transliterated_tweet = (". ").join(transliterated_sentences)
            
        return transliterated_tweet
    
