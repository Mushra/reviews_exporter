"""Shared normalization helpers used by all parsers to keep the parsed
JSON schema consistent across Metacritic, Steam and YouTube sources."""

from datetime import datetime, timezone

from langdetect import detect, LangDetectException


MIN_WORDS_FOR_LANGUAGE_DETECTION = 3


# Steam self-reports the review language as a Steam-specific name rather
# than an ISO 639-1 code. Mapping it keeps the `language` field consistent
# with the codes langdetect returns for Metacritic/YouTube text.
STEAM_LANGUAGE_TO_ISO = {
    "arabic": "ar",
    "bulgarian": "bg",
    "brazilian": "pt",
    "czech": "cs",
    "danish": "da",
    "dutch": "nl",
    "english": "en",
    "finnish": "fi",
    "french": "fr",
    "german": "de",
    "greek": "el",
    "hungarian": "hu",
    "indonesian": "id",
    "italian": "it",
    "japanese": "ja",
    "koreana": "ko",
    "latam": "es",
    "norwegian": "no",
    "polish": "pl",
    "portuguese": "pt",
    "romanian": "ro",
    "russian": "ru",
    "schinese": "zh",
    "spanish": "es",
    "swedish": "sv",
    "tchinese": "zh",
    "thai": "th",
    "turkish": "tr",
    "ukrainian": "uk",
    "vietnamese": "vi",
}


def compute_word_count(text: str) -> int:

    if not text:
        return 0

    return len(text.split())


def detect_language(text: str):

    if not text or len(text.split()) < MIN_WORDS_FOR_LANGUAGE_DETECTION:
        return None

    try:
        return detect(text)
    except LangDetectException:
        return None


def steam_language_to_iso(steam_language: str):

    if not steam_language:
        return None

    return STEAM_LANGUAGE_TO_ISO.get(steam_language.strip().lower())


def date_only_to_iso(date_str: str) -> str:
    """Metacritic dates arrive as day-only ("2026-07-01") - normalize to
    a full ISO 8601 UTC timestamp so all sources share one date format."""

    if not date_str:
        return ""

    if "T" in date_str:
        return date_str

    return f"{date_str}T00:00:00Z"


def timestamp_to_iso(timestamp) -> str:

    if not timestamp:
        return ""

    return (
        datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
        .strftime("%Y-%m-%dT%H:%M:%SZ")
    )
