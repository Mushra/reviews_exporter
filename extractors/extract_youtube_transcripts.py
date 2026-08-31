import sys
import traceback

from core.youtube_api import (
    parse_video_id,
    fetch_video_meta,
    YouTubeApiError,
)
from core.youtube_transcript import fetch_transcript
from core.filesystem import save_raw_json, get_youtube_transcript_raw_filename
from core.logger import Logger
from core.cancellation import check_cancelled


logger = Logger(__name__)


def extract_video_transcript(
    game: str,
    video_url_or_id: str,
    api_key: str,
    progress_callback=None,
    cancel_event=None,
):

    def report(message, ratio=None):

        if progress_callback:
            progress_callback(message, ratio=ratio)

    video_id = parse_video_id(video_url_or_id)

    if not video_id:

        logger.warning(f"Invalid YouTube URL/ID : {video_url_or_id}")

        return None

    logger.info(f"YouTube transcript extraction : {game} - video {video_id}")

    report(f"Video {video_id} : fetching metadata...", ratio=0.0)

    meta = fetch_video_meta(video_id, api_key)

    report(f"Video {video_id} : fetching transcript...", ratio=0.3)

    transcript = fetch_transcript(video_id)

    if transcript is None:

        logger.warning(f"No transcript available for {video_id} - skipping")

        report(f"Video {video_id} : no transcript", ratio=1.0)

        return None

    data = {
        "video_id": video_id,
        "source": "youtube",
        "kind": "transcript",
        "meta": meta,
        "transcript": transcript,
    }

    report(f"Video {video_id} : saving raw JSON...", ratio=0.9)

    output = save_raw_json(
        game,
        get_youtube_transcript_raw_filename(
            game,
            (meta or {}).get("channel_title"),
            (meta or {}).get("title") or video_id,
        ),
        data,
    )

    logger.info(f"Saved : {output}")

    report(f"Video {video_id} complete", ratio=1.0)

    return output


def extract_transcripts(
    game: str,
    video_urls: list,
    api_key: str,
    progress_callback=None,
    cancel_event=None,
):

    outputs = []

    total = len(video_urls) or 1

    for index, video_url in enumerate(video_urls):

        check_cancelled(cancel_event)

        def sub_report(message, ratio=None, index=index):

            if not progress_callback:
                return

            base_ratio = index / total

            if ratio is None:
                overall = base_ratio
            else:
                overall = base_ratio + (ratio / total)

            progress_callback(message, ratio=min(overall, 1.0))

        try:

            output = extract_video_transcript(
                game,
                video_url,
                api_key,
                progress_callback=sub_report,
                cancel_event=cancel_event,
            )

            if output:
                outputs.append(output)

        except YouTubeApiError as error:

            logger.error(f"YouTube error for {video_url} : {error}")

    return outputs


def main():

    if len(sys.argv) < 3:

        print(
            "Usage : "
            "python -m extractors.extract_youtube_transcripts "
            "<game> <api_key> <video_url_or_id> [video_url_or_id...]"
        )

        return

    game = sys.argv[1]
    api_key = sys.argv[2]
    video_urls = sys.argv[3:]

    try:

        extract_transcripts(game, video_urls, api_key)

    except Exception as error:

        logger.error(f"YouTube transcript extraction error : {error}")

        traceback.print_exc()


if __name__ == "__main__":

    main()
