import re
import time
from urllib.parse import urlparse, parse_qs

import requests

from core.logger import Logger
from core.cancellation import check_cancelled


logger = Logger(__name__)


VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
COMMENT_THREADS_URL = "https://www.googleapis.com/youtube/v3/commentThreads"
COMMENTS_URL = "https://www.googleapis.com/youtube/v3/comments"

DEFAULT_MAX_RESULTS = 100

HEADERS = {
    "Accept": "application/json",
}


class YouTubeApiError(Exception):
    pass


class CommentsDisabledError(YouTubeApiError):
    pass


# =============================================================
# Video ID parsing
# =============================================================

_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{11}$")


def parse_video_id(url_or_id: str):

    value = (url_or_id or "").strip()

    if not value:
        return None

    if _ID_PATTERN.match(value):
        return value

    try:

        parsed = urlparse(value)

        if parsed.hostname in ("youtu.be",):

            candidate = parsed.path.lstrip("/")

            if _ID_PATTERN.match(candidate):
                return candidate

        if parsed.hostname and "youtube.com" in parsed.hostname:

            if parsed.path == "/watch":

                query = parse_qs(parsed.query)

                candidate = query.get("v", [None])[0]

                if candidate and _ID_PATTERN.match(candidate):
                    return candidate

            for prefix in ("/shorts/", "/live/", "/embed/"):

                if parsed.path.startswith(prefix):

                    candidate = parsed.path[len(prefix):].split("/")[0]

                    if _ID_PATTERN.match(candidate):
                        return candidate

    except Exception:
        pass

    return None


# =============================================================
# HTTP
# =============================================================

def _request_json(url: str, params: dict, retries: int = 3):

    last_error = None

    for attempt in range(retries):

        try:

            response = requests.get(
                url,
                params=params,
                headers=HEADERS,
                timeout=30,
            )

            if response.status_code == 403:

                body = response.json() if response.content else {}

                reasons = {
                    error.get("reason")
                    for error in body.get("error", {}).get("errors", [])
                }

                if "commentsDisabled" in reasons:
                    raise CommentsDisabledError("Comments disabled")

                raise YouTubeApiError(
                    f"Access denied (invalid key or quota exceeded) : {body}"
                )

            response.raise_for_status()

            return response.json()

        except CommentsDisabledError:

            raise

        except Exception as error:

            last_error = error

            logger.warning(
                f"YouTube API error, attempt {attempt + 1}/{retries} : {error}"
            )

            time.sleep(2)

    raise YouTubeApiError(f"Could not fetch : {url} ({last_error})")


# =============================================================
# Video metadata
# =============================================================

def fetch_video_meta(video_id: str, api_key: str):

    if not api_key:
        raise YouTubeApiError("Missing YouTube API key")

    params = {
        "part": "snippet,statistics",
        "id": video_id,
        "key": api_key,
    }

    data = _request_json(VIDEOS_URL, params)

    items = data.get("items", [])

    if not items:
        raise YouTubeApiError(f"Video not found : {video_id}")

    item = items[0]

    snippet = item.get("snippet", {})
    statistics = item.get("statistics", {})

    return {
        "video_id": video_id,
        "title": snippet.get("title"),
        "channel_title": snippet.get("channelTitle"),
        "published_at": snippet.get("publishedAt"),
        "view_count": statistics.get("viewCount"),
        "like_count": statistics.get("likeCount"),
        "comment_count": statistics.get("commentCount"),
    }


# =============================================================
# Comments extraction
# =============================================================

def _fetch_all_replies(
    parent_id: str,
    api_key: str,
    max_results: int = DEFAULT_MAX_RESULTS,
    cancel_event=None,
):

    """
    commentThreads only embeds up to 5 replies per thread, even when
    snippet.totalReplyCount is higher. Page through the comments
    endpoint directly to retrieve every reply for a truncated thread.
    """

    replies = []
    page_token = None

    while True:

        check_cancelled(cancel_event)

        params = {
            "part": "snippet",
            "parentId": parent_id,
            "maxResults": max_results,
            "textFormat": "plainText",
            "key": api_key,
        }

        if page_token:
            params["pageToken"] = page_token

        data = _request_json(COMMENTS_URL, params)

        replies.extend(data.get("items", []))

        page_token = data.get("nextPageToken")

        if not page_token:
            break

    return replies


def _flatten_thread(thread, api_key, cancel_event=None):

    top_comment = (
        thread.get("snippet", {})
        .get("topLevelComment", {})
    )

    top_comment_id = top_comment.get("id")

    comments = [{
        **top_comment,
        "is_reply": False,
        "parent_id": None,
    }]

    total_reply_count = thread.get("snippet", {}).get("totalReplyCount", 0)
    embedded_replies = thread.get("replies", {}).get("comments", [])

    if total_reply_count > len(embedded_replies):

        replies = _fetch_all_replies(top_comment_id, api_key, cancel_event=cancel_event)

    else:

        replies = embedded_replies

    for reply in replies:

        comments.append({
            **reply,
            "is_reply": True,
            "parent_id": top_comment_id,
        })

    return comments


def fetch_comments(
    video_id: str,
    api_key: str,
    max_results: int = DEFAULT_MAX_RESULTS,
    progress_callback=None,
    cancel_event=None,
):

    def report(message, ratio=None):

        if progress_callback:
            progress_callback(message, ratio=ratio)

    if not api_key:
        raise YouTubeApiError("Missing YouTube API key")

    comments = []
    page_token = None
    total = None

    logger.info(f"YouTube extraction : comments for {video_id}")

    while True:

        check_cancelled(cancel_event)

        params = {
            "part": "snippet,replies",
            "videoId": video_id,
            "maxResults": max_results,
            "textFormat": "plainText",
            "key": api_key,
        }

        if page_token:
            params["pageToken"] = page_token

        data = _request_json(COMMENT_THREADS_URL, params)

        if total is None:
            total = data.get("pageInfo", {}).get("totalResults")

        for thread in data.get("items", []):

            check_cancelled(cancel_event)

            comments.extend(_flatten_thread(thread, api_key, cancel_event))

        report(
            f"{video_id} : {len(comments)} comments",
            ratio=None,
        )

        page_token = data.get("nextPageToken")

        if not page_token:
            break

    return comments
