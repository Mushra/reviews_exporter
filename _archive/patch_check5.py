from pathlib import Path
text = Path("core/api.py").read_text()
old = """    \"nintendo switch\":
        \"nintendo-switch\"

}


def normalize_platform(
"""
idx = text.index('"nintendo switch":')
segment = text[idx:idx+len(old)]
print('len old', len(old))
print('len seg', len(segment))
print('equal', old == segment)
print(repr(segment))