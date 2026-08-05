import sys

from models.review import Review

from core.filesystem import load_json, save_parsed, get_youtube_filename, get_raw_folder
from core.normalize import compute_word_count, detect_language
from core.paths import get_data_directory
from core.logger import Logger


logger = Logger(__name__)


# ---------------------------------------------------------
# Parsing item
# ---------------------------------------------------------

def parse_item(item, game, video_meta, index, in_reply_to_text=None):

    snippet = item.get("snippet", {})

    text = snippet.get("textOriginal", snippet.get("textDisplay", ""))

    is_reply = item.get("is_reply", False)

    likes = snippet.get("likeCount")

    review = Review(

        id=f"youtube-{item.get('id', index)}",

        game=game,

        source="youtube",

        type="reply" if is_reply else "comment",

        platform="youtube",

        author=snippet.get("authorDisplayName"),

        language=detect_language(text),

        date=snippet.get("publishedAt", ""),

        score={
            "raw": None,
            "scale": "not_applicable",
            "normalized": None,
        },

        text=text,

        text_completeness="full",

        word_count=compute_word_count(text),

        engagement={

            "votes_up": None,

            "votes_down": None,

            "likes": likes,

            "weighted_score": None,

        },

        flags={

            "spoiler": None,

            "refunded": None,

            "recommended": None,

        },

        source_meta={

            "publication":
                video_meta.get("channel_title") if video_meta else None,

            "external_url":
                f"https://www.youtube.com/watch?v={video_meta.get('video_id')}"
                f"&lc={item.get('id')}"
                if video_meta else None,

            "primarily_steam_deck": None,

        },

    )

    data = review.__dict__

    if is_reply:
        data["in_reply_to_text"] = in_reply_to_text

    return data


# ---------------------------------------------------------
# Collection : rebuild the flat comment+reply array into a tree so a
# reply carries its parent comment inline instead of only a parent_id.
# ---------------------------------------------------------

def parse_comments(raw_data, game):

    video_meta = raw_data.get("meta", {})

    items = raw_data.get("items", [])

    top_level = []
    replies_by_parent = {}

    for index, item in enumerate(items):

        if item.get("is_reply"):
            replies_by_parent.setdefault(item.get("parent_id"), []).append((index, item))
        else:
            top_level.append((index, item))

    comments = []

    for index, item in top_level:

        comment = parse_item(item, game, video_meta, index)

        parent_text = comment["text"]

        replies = []

        for reply_index, reply_item in replies_by_parent.get(item.get("id"), []):

            replies.append(
                parse_item(
                    reply_item,
                    game,
                    video_meta,
                    reply_index,
                    in_reply_to_text=parent_text,
                )
            )

        comment["replies"] = replies

        comments.append(comment)

    return comments


# ---------------------------------------------------------
# File-level meta
# ---------------------------------------------------------

def build_file_meta(game, video_meta, comments):

    total_items = len(comments) + sum(len(c.get("replies", [])) for c in comments)

    return {

        "game": game,

        "game_title": video_meta.get("title") if video_meta else None,

        "source": "youtube",

        "type": "comment",

        "platform": "youtube",

        "aggregate_score": None,

        "total_items": total_items,

        "video_id": video_meta.get("video_id") if video_meta else None,

        "channel_title": video_meta.get("channel_title") if video_meta else None,

    }


# ---------------------------------------------------------
# File(s)
# ---------------------------------------------------------

def find_raw_file(game, video_id):

    raw_folder = get_raw_folder(game)

    for file in raw_folder.glob(f"{game}_youtube_*_raw.json"):

        try:
            data = load_json(file)
        except Exception:
            continue

        if data.get("video_id") == video_id:
            return file

    return None


def parse_file(game, video_id):

    input_file = find_raw_file(game, video_id)

    if input_file is None:

        raise FileNotFoundError(
            f"No raw YouTube file found for video {video_id}"
        )

    logger.info(f"Reading : {input_file}")

    raw = load_json(input_file)

    video_meta = raw.get("meta") or {}

    comments = parse_comments(raw, game)

    meta = build_file_meta(game, video_meta, comments)

    output = save_parsed(
        game,
        get_youtube_filename(
            game,
            video_meta.get("channel_title"),
            video_meta.get("title") or video_id,
            "parsed"
        ),
        meta,
        comments,
    )

    logger.info(f"YouTube comments parsed : {meta['total_items']}")

    logger.info(f"Saved : {output}")

    return output


def parse_files(game, video_ids):

    outputs = []

    for video_id in video_ids:

        try:

            outputs.append(parse_file(game, video_id))

        except FileNotFoundError:

            logger.warning(f"Raw file missing for video {video_id}")

    return outputs


def main():

    if len(sys.argv) < 3:

        print(
            "Usage : "
            "python -m parsers.parse_youtube_api "
            "<game> <video_id> [video_id...]"
        )

        return

    game = sys.argv[1]
    video_ids = sys.argv[2:]

    parse_files(game, video_ids)


if __name__ == "__main__":

    main()
