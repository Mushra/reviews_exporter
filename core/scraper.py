"""Generic press-article text extraction, used to enrich Metacritic critic
excerpts with the full review text from the publication's own site.

No per-site rules: publications are too varied (dozens seen in a single
game's critic list) for per-site scraping to be maintainable. Instead this
relies on trafilatura's boilerplate-removal heuristics, which work well on
mainstream press but will legitimately fail on JS-heavy sites, paywalls,
or unusual layouts - callers must treat None as an expected outcome, not
an error."""

import time

import requests
import trafilatura

from core.logger import Logger


logger = Logger(__name__)


HEADERS = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
}


def fetch_article_text(url: str, timeout: int = 20, retries: int = 2):

    if not url:
        return None

    html = None

    for attempt in range(retries):

        try:

            response = requests.get(
                url,
                headers=HEADERS,
                timeout=timeout,
            )

            response.raise_for_status()

            html = response.text

            break

        except Exception as error:

            logger.warning(
                f"Scraping error, attempt {attempt + 1}/{retries} : {url} ({error})"
            )

            time.sleep(1)

    if not html:
        return None

    try:

        text = trafilatura.extract(html, favor_recall=True)

    except Exception as error:

        logger.warning(f"Extraction error : {url} ({error})")

        return None

    if not text or not text.strip():
        return None

    return text.strip()
