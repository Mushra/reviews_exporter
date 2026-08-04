import subprocess
import sys


platforms = [
    "nintendo-switch-2",
    "pc",
    "playstation-4",
    "playstation-5",
    "xbox-series-x"
]


for platform in platforms:

    print("\n==============================")
    print("Extraction :", platform)
    print("==============================")

    subprocess.run(
        [
            sys.executable,
            "extract_critic_platform.py",
            platform
        ]
    )
