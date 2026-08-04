from pipeline.runner import run_pipeline


def progress(
    percent,
    message
):

    print(
        percent,
        "%",
        message
    )



run_pipeline(
    "elden-ring",
    "pc",
    extract_user=True,
    extract_critic=True,
    process_user=True,
    process_critic=True,
    progress_callback=progress
)