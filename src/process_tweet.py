from gettext import textdomain
import json
import re
from matplotlib.pyplot import text
import requests
from sqlalchemy import true

from constants import (
    NEURALSPAC_LANGUAGE_DETECTION_URL,
    NEURALSPACE_TRANSLITERATION_URL,
    LanguageToUnicodeRange,
)


class TweetProcessor:
    def __init__(self, neuralspace_access_token: str, target_language: str):
        self.neuralspace_access_token = neuralspace_access_token
        self.target_language = target_language

    def is_language(self, word, src_language):

        maxchar = max(word)
        if (
            LanguageToUnicodeRange.get(src_language).start
            <= maxchar
            <= LanguageToUnicodeRange.get(src_language).end
        ):
            return True
        else:
            return False

    def clean_tweet(self, tweet):
        """
                Utility function to clean tweet text by removing links, special
        characters using simple regex statements.
        """
        tweet = re.sub(r"(http?\://|https?\://|www)\S+", "", tweet)
        tweet = (
            tweet.replace(",", "").replace("'", "").replace("...", "").replace('"', "")
        )
        tweet = " ".join(tweet.split())
        return tweet

    def split_text_to_chunks(self, string, length):
        words = string.split()
        grouped_words = [
            " ".join(words[i : i + length]) for i in range(0, len(words), length)
        ]
        return grouped_words

    def transliterate_sentence(self, text, src_language: str, tgt_language: str):
        transliterated_phrases = []
        text = text.rstrip()
        text = text.lstrip()
        phrases = self.split_text_to_chunks(text, 5)
        transliteration_headers = {
            "Authorization": self.neuralspace_access_token,
            "Content-Type": "application/json",
        }

        for phrase in phrases:
            transliteration_payload = json.dumps(
                {
                    "text": phrase,
                    "sourceLanguage": src_language,
                    "targetLanguage": tgt_language,
                    "suggestionCount": 1,
                }
            )
            transliteration_response = requests.post(
                NEURALSPACE_TRANSLITERATION_URL,
                headers=transliteration_headers,
                data=transliteration_payload,
            )
            transliteration_response_text = json.loads(transliteration_response.text)
            transliterated_phrase = transliteration_response_text["data"][
                "transliterated_text"
            ]
            transliterated_phrases.append(transliterated_phrase)

        transliterated_text = (" ").join(transliterated_phrases)
        return transliterated_text

    def split_sentences(self, text):
        sentences = []
        sentences = re.split("\. | ।", text)
        return sentences

    def detect_language(self, text_to_transliterate):
        headers = {
            "Authorization": self.neuralspace_access_token,
            "Content-Type": "application/json",
        }
        text_to_transliterate = self.clean_tweet(text_to_transliterate)
        payload = json.dumps({"text": text_to_transliterate})
        response = requests.post(
            NEURALSPAC_LANGUAGE_DETECTION_URL, headers=headers, data=payload
        )
        response_text = json.loads(response.text)
        print(response_text)
        detected_language = response_text["data"]["detected_languages"][0]["language"]
        return detected_language

    def remove_target_language_from_text(self, text):
        clean_text = ""
        for word in text.split():
            if not self.is_language(word, self.target_language):
                clean_text += word
                clean_text += " "
        return clean_text

    def transliterate_tweet(self, text, tgt_language: str):
        text_without_target_language = self.remove_target_language_from_text(text)
        src_language = self.detect_language(text_without_target_language)
        lines = text.splitlines(True)
        transliterated_tweetlines = []

        for line in lines:
            if line[-1] == "\n":
                line = line[:-1]
            transliterated_sentences = []
            sentences = self.split_sentences(line)
            print("------splits------------")
            print(sentences)
            for sentence in sentences:
                sentence = self.clean_tweet(sentence)
                phrase_to_transliterate = ""
                transliterated_phase = ""
                transliterated_text = ""

                for word in sentence.split():

                    if self.is_language(word, src_language):
                        phrase_to_transliterate += word
                        phrase_to_transliterate += " "
                    else:
                        if phrase_to_transliterate is not "":
                            transliterated_phase = self.transliterate_sentence(
                                phrase_to_transliterate, src_language, tgt_language
                            )
                            phrase_to_transliterate = ""
                            transliterated_text += transliterated_phase
                            transliterated_text += " "
                        transliterated_text += word
                        transliterated_text += " "

                if phrase_to_transliterate is not "":
                    transliterated_phase = self.transliterate_sentence(
                        phrase_to_transliterate, src_language, tgt_language
                    )
                    phrase_to_transliterate = ""
                    transliterated_text += transliterated_phase
                transliterated_sentences.append(transliterated_text.rstrip())

            transliterated_line = (". ").join(transliterated_sentences)
            transliterated_tweetlines.append(transliterated_line)
        transliterated_tweet = ("\n").join(transliterated_tweetlines)

        return transliterated_tweet
