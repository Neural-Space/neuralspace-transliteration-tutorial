from dataclasses import dataclass


TWITTER_STREAM_URL = "https://api.twitter.com/2/tweets/search/stream"
TWITTER_STREAM_RULES_URL = "https://api.twitter.com/2/tweets/search/stream/rules"
NEURALSPACE_TRANSLITERATION_URL = (
    "https://platform-dev.neuralspace.ai/api/transliteration/v1/transliterate"
)
NEURALSPAC_LANGUAGE_DETECTION_URL = (
    "https://platform-dev.neuralspace.ai/api/language-detection/v1/detect"
)
TWITTER_AUTH = "twitter-auth"
NEURALSPACE_AUTH = "neuralspace-auth"
BEARER_TOKEN = "BEARER_TOKEN"
CONSUMER_KEY = "CONSUMER_KEY"
CONSUMER_SECRET = "CONSUMER_SECRET"
TWITTER_ACCESS_TOKEN = "TWITTER_ACCESS_TOKEN"
ACCESS_TOKEN_SECRET = "ACCESS_TOKEN_SECRET"
NEURALSPACE_ACCESS_TOKEN = "NEURALSPACE_ACCESS_TOKEN"
SRC_LANG = "SRC_LANG"
TGT_LANG = "TGT_LANG"


@dataclass
class UnicodeRange:
    start: str
    end: str


LanguageToUnicodeRange = {
    "hi": UnicodeRange("\u0900", "\u097f"),
    "mr": UnicodeRange("\u0900", "\u097f"),
    "bn": UnicodeRange("\u0980", "\u09ff"),
    "ta": UnicodeRange("\u0b80", "\u0bff"),
    "te": UnicodeRange("\u0c00", "\u0c7f"),
    "kn": UnicodeRange("\u0c80", "\u0cff"),
    "pa": UnicodeRange("\u0a00", "\u0a7f"),
    "ar": UnicodeRange("\u0680", "\u06ff"),
    "ml": UnicodeRange("\u0d00", "\u0d7f"),
    "gu": UnicodeRange("\u0a80", "\u0aff"),
    "ru": UnicodeRange("\u0400", "\u04ff"),
    "uk": UnicodeRange("\u0400", "\u04ff"),
    "bg": UnicodeRange("\u0400", "\u04ff"),
    "mk": UnicodeRange("\u0400", "\u04ff"),
    "sr": UnicodeRange("\u0400", "\u04ff"),
    "el": UnicodeRange("\u0370", "\u03ff"),
    "en": UnicodeRange("\u0000", "\u007f"),
}
