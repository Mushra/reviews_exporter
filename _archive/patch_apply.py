from pathlib import Path
path = Path("core/api.py")
text = path.read_text()
old = """    \"nintendo switch\":
        \"nintendo-switch\"

}


def normalize_platform(
"""
new = """    \"nintendo switch\":
        \"nintendo-switch\"

}

ALL_API_PLATFORMS = [
    \"pc\",
    \"playstation-5\",
    \"playstation-4\",
    \"xbox-series-x\",
    \"xbox-one\",
    \"nintendo-switch\"
]


def normalize_platform(
"""
if old not in text:
    raise SystemExit('old not found 1')
text = text.replace(old, new, 1)
path.write_text(text)