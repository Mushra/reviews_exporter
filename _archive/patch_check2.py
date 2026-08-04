from pathlib import Path
text = Path("core/api.py").read_text()
idx = text.index("def normalize_platform(")
print(repr(text[idx-50:idx+20]))
idx2 = text.index("# =============================================================\r\n# HTTP\r\n# =============================================================")
print(idx2)
print(repr(text[idx2-20:idx2+60]))