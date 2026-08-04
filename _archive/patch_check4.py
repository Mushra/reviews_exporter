from pathlib import Path
text = Path("core/api.py").read_text()
idx = text.index('"nintendo switch":')
print('index', idx)
print(repr(text[idx:idx+200]))