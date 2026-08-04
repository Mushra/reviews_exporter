from pathlib import Path
path = Path('core/api.py')
text = path.read_text()
print('len', len(text))
print('contains nintendo switch', '"nintendo switch":' in text)
print('contains def normalize_platform', 'def normalize_platform(' in text)
print('contains HTTP comment', '# =============================================================\n# HTTP\n# =============================================================' in text)