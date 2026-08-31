import sys

from models.review import Review

from core.filesystem import (
    load_json,
    save_parsed,
    get_raw_folder,
    get_youtube_transcripts_parsed_filename,
)
from core.normalize import compute_word_count
from core.youtube_transcript import group_into_segments
from core.logger import Logger


logger = Logger(__name__)


# ---------------------------------------------------------
# Parsing one raw transcript into segment items
# ---------------------------------------------------------

def parse_transcript_raw(raw_data, game):

    video_meta = raw_data.get("meta") or {}
    transcript = raw_data.get("transcript") or {}

    video_id = raw_data.get("video_id")

    segments = group_into_segments(transcript.get("snippets", []))

    items = []

    for index, segment in enumerate(segments):

        text = segment["text"]

        review = Review(

            id=f"youtube-transcript-{video_id}-{index}",

            game=game,

            source="youtube",

            type="transcript_segment",

            platform="youtube",

            author=video_meta.get("channel_title"),

            language=transcript.get("language"),

            date=video_meta.get("published_at", ""),

            # score/engagement/flags don't apply to a spoken transcript
            # line (no rating, no votes, no spoiler flag) - dropped from
            # the item below instead of populated with dead null fields.
            score={},

            text=text,

            text_completeness="full",

            word_count=compute_word_count(text),

            engagement={},

            flags={},

            source_meta={
                "external_url":
                    f"https://www.youtube.com/watch?v={video_id}"
                    f"&t={int(segment['start'])}s",
            },

        )

        data = review.__dict__

        del data["score"]
        del data["engagement"]
        del data["flags"]

        data["start"] = segment["start"]
        data["start_hms"] = segment["start_hms"]
        data["end"] = segment["end"]
        data["duration"] = segment["duration"]
        data["video_id"] = video_id
        data["video_title"] = video_meta.get("title")
        data["is_generated"] = transcript.get("is_generated")

        items.append(data)

    return items


# ---------------------------------------------------------
# File(s) : merge every transcript raw file for a game into one parsed file
# ---------------------------------------------------------

def find_transcript_raw_files(game):

    raw_folder = get_raw_folder(game)

    return sorted(raw_folder.glob(f"{game}_youtube_*_transcript_raw.json"))


def parse_and_merge(game, video_ids=None):

    files = find_transcript_raw_files(game)

    if not files:

        raise FileNotFoundError(
            f"No raw YouTube transcript file found for game {game}"
        )

    all_items = []
    videos_meta = []

    for file in files:

        logger.info(f"Reading : {file}")

        raw = load_json(file)

        items = parse_transcript_raw(raw, game)

        all_items.extend(items)

        video_meta = raw.get("meta") or {}
        transcript = raw.get("transcript") or {}

        videos_meta.append({
            "video_id": raw.get("video_id"),
            "video_title": video_meta.get("title"),
            "channel_title": video_meta.get("channel_title"),
            "language": transcript.get("language"),
            "is_generated": transcript.get("is_generated"),
            "segment_count": len(items),
        })

    if video_ids:

        found_ids = {video["video_id"] for video in videos_meta}

        for video_id in video_ids:

            if video_id not in found_ids:

                logger.warning(
                    f"No transcript raw file for requested video {video_id}"
                )

    meta = {

        "game": game,

        "source": "youtube",

        "type": "transcript",

        "platform": "youtube",

        "aggregate_score": None,

        "total_items": len(all_items),

        "videos": videos_meta,

    }

    output = save_parsed(
        game,
        get_youtube_transcripts_parsed_filename(game),
        meta,
        all_items,
    )

    logger.info(f"YouTube transcript segments parsed : {meta['total_items']}")

    for path in output:
        logger.info(f"Saved : {path}")

    return output


def main():

    if len(sys.argv) < 2:

        print(
            "Usage : "
            "python -m parsers.parse_youtube_transcripts "
            "<game> [video_id...]"
        )

        return

    game = sys.argv[1]
    video_ids = sys.argv[2:]

    parse_and_merge(game, video_ids)


if __name__ == "__main__":

    main()
