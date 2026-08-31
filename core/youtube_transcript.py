import re

from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    RequestBlocked,
    IpBlocked,
    YouTubeTranscriptApiException,
)

from core.logger import Logger


logger = Logger(__name__)


# =============================================================
# Fetch
# =============================================================

def fetch_transcript(video_id: str):
    """Fetch the best available transcript track for a video : manually
    created first, then auto-generated (TranscriptList already yields
    manual tracks before generated ones), in whatever language happens to
    be available. Returns None if no track exists or the request is
    blocked/disabled - never raises, callers can treat it as "no
    transcript for this video" and move on."""

    try:

        transcript_list = YouTubeTranscriptApi().list(video_id)

        transcripts = list(transcript_list)

        if not transcripts:
            return None

        transcript = transcripts[0]

        fetched = transcript.fetch()

        return {
            "language": fetched.language_code,
            "is_generated": fetched.is_generated,
            "snippets": [
                {
                    "text": snippet.text,
                    "start": snippet.start,
                    "duration": snippet.duration,
                }
                for snippet in fetched
            ],
        }

    except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable):

        logger.warning(f"No transcript available for {video_id}")

        return None

    except (RequestBlocked, IpBlocked):

        logger.warning(f"Transcript request blocked for {video_id}")

        return None

    except YouTubeTranscriptApiException as error:

        logger.warning(f"Transcript error for {video_id} : {error}")

        return None


# =============================================================
# Segmentation : group snippets into citation-friendly chunks
# =============================================================

SENTENCES_PER_SEGMENT = 4

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?…])\s+")
_SENTENCE_END_RE = re.compile(r"[.!?…]\s*$")


def _split_into_fragments(snippets):
    """Break each snippet's text on sentence-ending punctuation, spreading
    the snippet's time span across its fragments proportionally to their
    length. Snippets without punctuation (common for auto-generated
    captions) simply come back as a single fragment."""

    fragments = []

    for snippet in snippets:

        text = (snippet.get("text") or "").replace("\n", " ").strip()

        if not text:
            continue

        start = float(snippet.get("start") or 0)
        duration = float(snippet.get("duration") or 0)
        end = start + duration

        pieces = [p.strip() for p in _SENTENCE_SPLIT_RE.split(text) if p.strip()]

        if not pieces:
            continue

        total_chars = sum(len(p) for p in pieces) or 1
        cursor = start

        for piece in pieces:

            if duration:
                piece_duration = duration * (len(piece) / total_chars)
                piece_start = cursor
                piece_end = piece_start + piece_duration
            else:
                piece_start = cursor
                piece_end = end

            fragments.append({
                "text": piece,
                "start": piece_start,
                "end": piece_end,
            })

            cursor = piece_end

    return fragments


def group_into_segments(snippets, max_chars=500, max_duration=45):
    """Group transcript snippets into citation-friendly segments of ~3-4
    sentences each. Falls back to max_chars/max_duration caps when no
    sentence punctuation is available at all, so a punctuation-less
    auto-generated track still gets split into multiple segments instead
    of one giant block."""

    fragments = _split_into_fragments(snippets)

    if not fragments:
        return []

    segments = []
    current = []
    current_chars = 0

    def flush():

        if not current:
            return

        seg_start = current[0]["start"]
        seg_end = current[-1]["end"]

        segments.append({
            "start": seg_start,
            "start_hms": format_hms(seg_start),
            "end": seg_end,
            "duration": max(seg_end - seg_start, 0.0),
            "text": " ".join(f["text"] for f in current),
        })

    for fragment in fragments:

        would_overflow = current and (
            current_chars + len(fragment["text"]) > max_chars
            or fragment["end"] - current[0]["start"] > max_duration
        )

        if would_overflow:
            flush()
            current = []
            current_chars = 0

        current.append(fragment)
        current_chars += len(fragment["text"])

        sentence_count = sum(
            1 for f in current if _SENTENCE_END_RE.search(f["text"])
        )

        if _SENTENCE_END_RE.search(fragment["text"]) and sentence_count >= SENTENCES_PER_SEGMENT:
            flush()
            current = []
            current_chars = 0

    flush()

    return segments


def format_hms(seconds) -> str:

    total_seconds = int(max(seconds or 0, 0))

    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
